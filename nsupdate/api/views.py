# -*- coding: utf-8 -*-
"""
views for the (usually non-interactive, automated) web api
"""

import logging
logger = logging.getLogger(__name__)

import json

from django.http import HttpResponse
from django.conf import settings
from django.views.generic.base import View
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.backends.db import SessionStore
from django.utils.decorators import method_decorator

from ..utils import log, ddns_client
from ..main.models import Host
from ..main.dnstools import update, SameIpError, DnsUpdateError, NameServerNotAvailable, check_ip, put_ip_into_session


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
    ipaddr = request.META['REMOTE_ADDR']
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
        # we do not have the session as usual, as this is a different host,
        # so the session cookie is not received here - thus we access it via
        # the sessionid:
        s = SessionStore(session_key=sessionid)
        ipaddr = request.META['REMOTE_ADDR']
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

    :param auth: http basic auth string
    :return: username, password
    """
    authmeth, auth = auth.split(' ', 1)
    if authmeth.lower() != 'basic':
        return
    auth = auth.strip().decode('base64')
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
        host = Host.filter_by_fqdn(fqdn)
    except ValueError:
        return None
    if host is None or not check_password(password, host.update_secret):
        return None
    return host


def check_session_auth(user, hostname):
    """
    Check our database whether the hostname is owned by the user.

    :param user: django user object
    :param hostname: fqdn
    :return: host object if hostname is owned by this user, None otherwise.
    """
    fqdn = hostname
    try:
        host = Host.filter_by_fqdn(fqdn, created_by=user)
    except ValueError:
        return None
    # we have specifically looked for a host of the logged in user,
    # we either have one now and return it, or we have None and return that.
    return host


class NicUpdateView(View):
    @log.logger(__name__)
    def get(self, request, logger=None):
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
            logger.warning("rejecting to update wrong host %s (given in query string) "
                           "[instead of %s (given in basic auth)]" % (hostname, username))
            host.register_client_fault()
            return Response(result)
        agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        if agent in settings.BAD_AGENTS:
            logger.warning('%s - received update from bad user agent' % (hostname, ))
            host.register_client_fault()
            return Response('badagent')
        ipaddr = request.GET.get('myip')
        if ipaddr is None:
            ipaddr = request.META.get('REMOTE_ADDR')
        ssl = request.is_secure()
        return _update(host, hostname, ipaddr, ssl, logger=logger)


class AuthorizedNicUpdateView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthorizedNicUpdateView, self).dispatch(*args, **kwargs)

    @log.logger(__name__)
    def get(self, request, logger=None):
        """
        similar to NicUpdateView, but the client is not a router or other dyndns client,
        but the admin browser who is currently logged into the nsupdate.info site.

        Example URLs:

        https://nsupdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

        :param request: django request object
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
            ipaddr = request.META.get('REMOTE_ADDR')
        ssl = request.is_secure()
        return _update(host, hostname, ipaddr, ssl, logger=logger)


def _update(host, hostname, ipaddr, ssl=False, logger=None):
    """
    common code shared by the 2 update views

    :param host: host object
    :param hostname: hostname (fqdn)
    :param ipaddr: new ip addr (v4 or v6)
    :param ssl: True if we use SSL/https
    :param logger: a logger object
    :return: Response object with dyndns2 response
    """
    # we are doing abuse / available checks rather late, so the client might
    # get more specific responses (like 'badagent' or 'notfqdn') by earlier
    # checks. it also avoids some code duplication if done here:
    if host.abuse or host.abuse_blocked:
        return Response('abuse')
    if not host.available:
        # not available is like it doesn't exist
        return Response('nohost')
    ipaddr = str(ipaddr)  # bug in dnspython: crashes if ipaddr is unicode, wants a str!
                          # https://github.com/rthalley/dnspython/issues/41
                          # TODO: reproduce and submit traceback to issue 41
    kind = check_ip(ipaddr, ('ipv4', 'ipv6'))
    host.poke(kind, ssl)
    try:
        update(hostname, ipaddr)
        logger.info('%s - received good update -> ip: %s ssl: %r' % (hostname, ipaddr, ssl))
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
        return Response('good %s' % ipaddr)
    except SameIpError:
        logger.warning('%s - received no-change update, ip: %s ssl: %r' % (hostname, ipaddr, ssl))
        host.register_client_fault()
        return Response('nochg %s' % ipaddr)
    except (DnsUpdateError, NameServerNotAvailable) as e:
        msg = str(e)
        logger.error('%s - received update that resulted in a dns error [%s], ip: %s ssl: %r' % (
                     hostname, msg, ipaddr, ssl))
        host.register_server_fault()
        return Response('dnserr')
