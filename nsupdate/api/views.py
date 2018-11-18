# -*- coding: utf-8 -*-
"""
views for the (usually non-interactive, automated) web api
"""

import logging
logger = logging.getLogger(__name__)

import json
import base64
from importlib import import_module

from netaddr import IPAddress, IPNetwork
from netaddr.core import AddrFormatError

from django.http import HttpResponse
from django.conf import settings
from django.views.generic.base import View
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..utils import log, ddns_client
from ..main.models import Host
from ..main.dnstools import (FQDN, update, delete, check_ip, put_ip_into_session,
                             SameIpError, DnsUpdateError, NameServerNotAvailable)
from ..main.iptools import normalize_ip


def Response(content):
    """
    shortcut for text/plain HttpResponse

    :param content: plain text content for the response
    :return: HttpResonse object
    """
    return HttpResponse(content, content_type='text/plain')


@log.logger(__name__)
def myip_view(request, logger=None):
    """
    return the IP address (can be v4 or v6) of the client requesting this view.

    :param request: django request object
    :return: HttpResponse object
    """
    # Note: keeping this as a function-based view, as it is frequently used -
    # maybe it is slightly more efficient than class-based.
    ipaddr = normalize_ip(request.META['REMOTE_ADDR'])
    logger.debug("detected remote ip address: %s" % ipaddr)
    return Response(ipaddr)


class DetectIpView(View):
    @log.logger(__name__)
    def get(self, request, sessionid, logger=None):
        """
        Put the IP address (can be v4 or v6) of the client requesting this view
        into the client's session.

        :param request: django request object
        :param sessionid: sessionid from url used to find the correct session w/o session cookie
        :return: HttpResponse object
        """
        engine = import_module(settings.SESSION_ENGINE)
        # we do not have the session as usual, as this is a different host,
        # so the session cookie is not received here - thus we access it via
        # the sessionid:
        s = engine.SessionStore(session_key=sessionid)
        ipaddr = normalize_ip(request.META['REMOTE_ADDR'])
        # as this is NOT the session automatically established and
        # also saved by the framework, we need to use save=True here
        put_ip_into_session(s, ipaddr, save=True)
        logger.debug("detected remote address: %s for session %s" % (ipaddr, sessionid))
        return HttpResponse(status=204)


class AjaxGetIps(View):
    @log.logger(__name__)
    def get(self, request, logger=None):
        """
        Get the IP addresses of the client from the session via AJAX
        (so we don't need to reload the view in case we just invalidated stale IPs
        and triggered new detection).

        :param request: django request object
        :return: HttpResponse object
        """
        response = dict(
            ipv4=request.session.get('ipv4', ''),
            ipv4_rdns=request.session.get('ipv4_rdns', ''),
            ipv6=request.session.get('ipv6', ''),
            ipv6_rdns=request.session.get('ipv6_rdns', ''),
        )
        logger.debug("ajax_get_ips response: %r" % (response, ))
        return HttpResponse(json.dumps(response), content_type='application/json')


def basic_challenge(realm, content='Authorization Required'):
    """
    Construct a 401 response requesting http basic auth.

    :param realm: realm string (displayed by the browser)
    :param content: request body content
    :return: HttpResponse object
    """
    response = Response(content)
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm, )
    response.status_code = 401
    return response


def basic_authenticate(auth):
    """
    Get username and password from http basic auth string.

    :param auth: http basic auth string [str on py2, str on py3]
    :return: username, password [unicode on py2, str on py3]
    """
    assert isinstance(auth, str)
    authmeth, auth = auth.split(' ', 1)
    if authmeth.lower() != 'basic':
        return
    # we ignore bytes that do not decode. username (hostname) and password
    # (update secret) both have to be ascii, everything else is a configuration
    # error on user side.
    auth = base64.b64decode(auth.strip()).decode('utf-8', errors='ignore')
    username, password = auth.split(':', 1)
    return username, password


def check_api_auth(username, password):
    """
    Check username and password against our database.

    :param username: http basic auth username (== fqdn)
    :param password: update password
    :return: host object if authenticated, None otherwise.
    """
    fqdn = username
    try:
        host = Host.get_by_fqdn(fqdn)
    except ValueError:
        return None
    if host is not None:
        ok = check_password(password, host.update_secret)
        success_msg = ('failure', 'success')[ok]
        msg = "api authentication %s. [hostname: %s (given in basic auth)]" % (success_msg, fqdn, )
        host.register_api_auth_result(msg, fault=not ok)
        if ok:
            return host
    return None


def check_session_auth(user, hostname):
    """
    Check our database whether the hostname is owned by the user.

    :param user: django user object
    :param hostname: fqdn
    :return: host object if hostname is owned by this user, None otherwise.
    """
    fqdn = hostname
    try:
        host = Host.get_by_fqdn(fqdn, created_by=user)
    except ValueError:
        return None
    # we have specifically looked for a host of the logged in user,
    # we either have one now and return it, or we have None and return that.
    return host


class NicUpdateView(View):
    @log.logger(__name__)
    def get(self, request, logger=None, delete=False):
        """
        dyndns2 compatible /nic/update API.

        Example URLs:

        Will request username (fqdn) and password (secret) from user,
        for interactive testing / updating:
        https://nsupdate.info/nic/update

        You can put it also into the url, so the browser will automatically
        send the http basic auth with the request:
        https://fqdn:secret@nsupdate.info/nic/update

        If the request does not come from the correct IP, you can give it as
        a query parameter.
        You can also give the hostname/fqdn as a query parameter (this is
        supported for api compatibility only), but then it MUST match the fqdn
        used for http basic auth's username part, because the secret only
        allows you to update this single fqdn).
        https://fqdn:secret@nsupdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

        :param request: django request object
        :param delete: False means update, True means delete - used by NicDeleteView
        :return: HttpResponse object
        """
        hostname = request.GET.get('hostname')
        auth = request.META.get('HTTP_AUTHORIZATION')
        if auth is None:
            logger.warning('%s - received no auth' % (hostname, ))
            return basic_challenge("authenticate to update DNS", 'badauth')
        username, password = basic_authenticate(auth)
        if '.' not in username:  # username MUST be the fqdn
            # specifically point to configuration errors on client side
            return Response('notfqdn')
        host = check_api_auth(username, password)
        if host is None:
            logger.warning('%s - received bad credentials, username: %s' % (hostname, username, ))
            return basic_challenge("authenticate to update DNS", 'badauth')
        logger.info("authenticated by update secret for host %s" % username)
        if hostname is None:
            # as we use update_username == hostname, we can fall back to that:
            hostname = username
        elif hostname != username:
            if '.' not in hostname:
                # specifically point to configuration errors on client side
                result = 'notfqdn'
            else:
                # maybe this host is owned by same person, but we can't know.
                result = 'nohost'  # or 'badauth'?
            msg = ("rejecting to update wrong host %s (given in query string) "
                   "[instead of %s (given in basic auth)]" % (hostname, username))
            logger.warning(msg)
            host.register_client_result(msg, fault=True)
            return Response(result)
        agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        if agent in settings.BAD_AGENTS:
            msg = '%s - received update from bad user agent %r' % (hostname, agent)
            logger.warning(msg)
            host.register_client_result(msg, fault=True)
            return Response('badagent')
        ipaddr = request.GET.get('myip')
        if not ipaddr:  # None or ''
            ipaddr = normalize_ip(request.META.get('REMOTE_ADDR'))
        secure = request.is_secure()
        return _update_or_delete(host, ipaddr, secure, logger=logger, _delete=delete)


class NicDeleteView(NicUpdateView):
    @log.logger(__name__)
    def get(self, request, logger=None, delete=True):
        """
        /nic/delete API - delete a A or AAAA record.

        API is pretty much the same as for /nic/update, but it does not update
        the A or AAAA record, but deletes it.
        The ip address given via myip= param (or determined via REMOTE_ADDR)
        is used to determine the record type for deletion, but is otherwise
        ignored (so you can e.g. give myip=0.0.0.0 for A and myip=:: for AAAA).

        :param request: django request object
        :return: HttpResponse object
        """
        return super(NicDeleteView, self).get(request, logger=logger, delete=delete)


class AuthorizedNicUpdateView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthorizedNicUpdateView, self).dispatch(*args, **kwargs)

    @log.logger(__name__)
    def get(self, request, logger=None, delete=False):
        """
        similar to NicUpdateView, but the client is not a router or other dyndns client,
        but the admin browser who is currently logged into the nsupdate.info site.

        Example URLs:

        https://nsupdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

        :param request: django request object
        :param delete: False means update, True means delete - used by AuthorizedNicDeleteView
        :return: HttpResponse object
        """
        hostname = request.GET.get('hostname')
        if hostname is None:
            return Response('nohost')
        host = check_session_auth(request.user, hostname)
        if host is None:
            logger.warning('%s - is not owned by user: %s' % (hostname, request.user.username, ))
            return Response('nohost')
        logger.info("authenticated by session as user %s, creator of host %s" % (request.user.username, hostname))
        # note: we do not check the user agent here as this is interactive
        # and logged-in usage - thus misbehaved user agents are no problem.
        ipaddr = request.GET.get('myip')
        if not ipaddr:  # None or empty string
            ipaddr = normalize_ip(request.META.get('REMOTE_ADDR'))
        secure = request.is_secure()
        return _update_or_delete(host, ipaddr, secure, logger=logger, _delete=delete)


class AuthorizedNicDeleteView(AuthorizedNicUpdateView):

    @log.logger(__name__)
    def get(self, request, logger=None, delete=True):
        """
        /nic/delete API - for logged-in admin browser.

        :param request: django request object
        :return: HttpResponse object
        """
        return super(AuthorizedNicDeleteView, self).get(request, logger=logger, delete=delete)


def _update_or_delete(host, ipaddr, secure=False, logger=None, _delete=False):
    """
    common code shared by the 2 update/delete views

    :param host: host object
    :param ipaddr: ip addr (v4 or v6)
    :param secure: True if we use TLS/https
    :param logger: a logger object
    :param _delete: True for delete, False for update
    :return: Response object with dyndns2 response
    """
    mode = ('update', 'delete')[_delete]
    # we are doing abuse / available checks rather late, so the client might
    # get more specific responses (like 'badagent' or 'notfqdn') by earlier
    # checks. it also avoids some code duplication if done here:
    fqdn = host.get_fqdn()
    if host.abuse or host.abuse_blocked:
        msg = '%s - received %s for host with abuse / abuse_blocked flag set' % (fqdn, mode, )
        logger.warning(msg)
        host.register_client_result(msg, fault=False)
        return Response('abuse')
    if not host.available:
        # not available is like it doesn't exist
        msg = '%s - received %s for unavailable host' % (fqdn, mode, )
        logger.warning(msg)
        host.register_client_result(msg, fault=False)
        return Response('nohost')
    try:
        # bug in dnspython: crashes if ipaddr is unicode, wants a str!
        # https://github.com/rthalley/dnspython/issues/41
        # TODO: reproduce and submit traceback to issue 41
        ipaddr = str(ipaddr)
        kind = check_ip(ipaddr, ('ipv4', 'ipv6'))
        rdtype = 'A' if kind == 'ipv4' else 'AAAA'
        IPNetwork(ipaddr)  # raise AddrFormatError here if there is an issue with ipaddr, see #394
    except (ValueError, UnicodeError, AddrFormatError):
        # invalid ip address string
        # some people manage to even give a non-ascii string instead of an ip addr
        msg = '%s - received bad ip address: %r' % (fqdn, ipaddr)
        logger.warning(msg)
        host.register_client_result(msg, fault=True)
        return Response('dnserr')  # there should be a better response code for this
    if mode == 'update' and ipaddr in settings.BAD_IPS_HOST:
        msg = '%s - received %s to blacklisted ip address: %r' % (fqdn, mode, ipaddr)
        logger.warning(msg)
        host.abuse = True
        host.abuse_blocked = True
        host.register_client_result(msg, fault=True)
        return Response('abuse')
    host.poke(kind, secure)
    try:
        if _delete:
            delete(fqdn, rdtype)
        else:
            update(fqdn, ipaddr)
    except SameIpError:
        msg = '%s - received no-change update, ip: %s tls: %r' % (fqdn, ipaddr, secure)
        logger.warning(msg)
        host.register_client_result(msg, fault=True)
        return Response('nochg %s' % ipaddr)
    except (DnsUpdateError, NameServerNotAvailable) as e:
        msg = str(e)
        msg = '%s - received %s that resulted in a dns error [%s], ip: %s tls: %r' % (
            fqdn, mode, msg, ipaddr, secure)
        logger.error(msg)
        host.register_server_result(msg, fault=True)
        return Response('dnserr')
    else:
        if _delete:
            msg = '%s - received delete for record %s, tls: %r' % (fqdn, rdtype, secure)
        else:
            msg = '%s - received good update -> ip: %s tls: %r' % (fqdn, ipaddr, secure)
        logger.info(msg)
        host.register_client_result(msg, fault=False)
        if _delete:
            # XXX unclear what to do for "other services" we relay updates to
            return Response('deleted %s' % rdtype)
        else:  # update
            _on_update_success(host, fqdn, kind, ipaddr, secure, logger)
            return Response('good %s' % ipaddr)


def _on_update_success(host, fqdn, kind, ipaddr, secure, logger):
    """after updating the host in dns, do related other updates"""
    # update related hosts
    rdtype = 'A' if kind == 'ipv4' else 'AAAA'
    for rh in host.relatedhosts.all():
        if rh.available:
            if kind == 'ipv4':
                ifid = rh.interface_id_ipv4
                netmask = host.netmask_ipv4
            else:  # kind == 'ipv6':
                ifid = rh.interface_id_ipv6
                netmask = host.netmask_ipv6
            ifid = ifid.strip() if ifid else ifid
            _delete = not ifid  # leave ifid empty if you don't want this rh record
            try:
                rh_fqdn = FQDN(rh.name + '.' + fqdn.host, fqdn.domain)
                if not _delete:
                    ifid = IPAddress(ifid)
                    network = IPNetwork("%s/%d" % (ipaddr, netmask))
                    rh_ipaddr = str(IPAddress(network.network) + int(ifid))
            except (IndexError, AddrFormatError, ValueError) as e:
                logger.warning("trouble computing address of related host %s [%s]" % (rh, e))
            else:
                if not _delete:
                    logger.info("updating related host %s -> %s" % (rh_fqdn, rh_ipaddr))
                else:
                    logger.info("deleting related host %s" % (rh_fqdn, ))
                try:
                    if not _delete:
                        update(rh_fqdn, rh_ipaddr)
                    else:
                        delete(rh_fqdn, rdtype)
                except SameIpError:
                    msg = '%s - related hosts no-change update, ip: %s tls: %r' % (rh_fqdn, rh_ipaddr, secure)
                    logger.warning(msg)
                    host.register_client_result(msg, fault=True)
                except (DnsUpdateError, NameServerNotAvailable) as e:
                    msg = str(e)
                    if not _delete:
                        msg = '%s - related hosts update that resulted in a dns error [%s], ip: %s tls: %r' % (
                            rh_fqdn, msg, rh_ipaddr, secure)
                    else:
                        msg = '%s - related hosts deletion that resulted in a dns error [%s], tls: %r' % (
                            rh_fqdn, msg, secure)
                    logger.error(msg)
                    host.register_server_result(msg, fault=True)

    # now check if there are other services we shall relay updates to:
    for hc in host.serviceupdaterhostconfigs.all():
        if (kind == 'ipv4' and hc.give_ipv4 and hc.service.accept_ipv4
            or
            kind == 'ipv6' and hc.give_ipv6 and hc.service.accept_ipv6):
            kwargs = dict(
                name=hc.name, password=hc.password,
                hostname=hc.hostname, myip=ipaddr,
                server=hc.service.server, path=hc.service.path, secure=hc.service.secure,
            )
            try:
                ddns_client.dyndns2_update(**kwargs)
            except Exception:
                # we never want to crash here
                kwargs.pop('password')
                logger.exception("the dyndns2 updater raised an exception [%r]" % kwargs)
