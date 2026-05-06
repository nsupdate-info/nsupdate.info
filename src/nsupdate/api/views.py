# -*- coding: utf-8 -*-
"""
Views for the (usually non-interactive, automated) web API.
"""

import logging

from ..utils.dns_updater import strip_ip, update_or_delete

logger = logging.getLogger(__name__)

import json
import base64
import binascii
from importlib import import_module

from django.http import HttpResponse
from django.conf import settings
from django.views.generic.base import View
from django.contrib.auth.hashers import verify_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..utils import log
from ..main.models import Host
from ..main.dnstools import (check_ip, put_ip_into_session)
from ..main.iptools import normalize_ip
from .utils import get_session_key_from_token


def Response(content, status=200):
    """
    Shortcut for a text/plain HttpResponse.

    :param content: Plain-text content for the response
    :return: HttpResponse object
    """
    return HttpResponse(content, status=status, content_type='text/plain')


@log.logger(__name__)
def myip_view(request, logger=None):
    """
    Return the IP address (IPv4 or IPv6) of the client requesting this view.

    :param request: Django request object
    :return: HttpResponse object
    """
    # Note: keeping this as a function-based view, as it is frequently used -
    # maybe it is slightly more efficient than class-based.
    ipaddr = normalize_ip(request.META['REMOTE_ADDR'])
    logger.debug("detected remote ip address: %s" % ipaddr)
    return Response(ipaddr)


class DetectIpView(View):
    @log.logger(__name__)
    def get(self, request, token, logger=None):
        """
        Put the IP address (IPv4 or IPv6) of the client requesting this view
        into the client's session.

        :param request: Django request object
        :param token: Temporary token used to find the correct session without a session cookie
        :return: HttpResponse object
        """
        sessionid = get_session_key_from_token(token)
        if sessionid is None:
            logger.debug("no session found for token %s" % token)
            return HttpResponse(status=204)
        engine = import_module(settings.SESSION_ENGINE)
        # We do not have the session as usual, as this is a different host,
        # so the session cookie is not received here; thus we access it via
        # the session ID:
        s = engine.SessionStore(session_key=sessionid)
        ipaddr = normalize_ip(request.META['REMOTE_ADDR'])
        # As this is NOT the session automatically established and
        # also saved by the framework, we need to use save=True here.
        put_ip_into_session(s, ipaddr, save=True)
        logger.debug("detected remote address: %s for session %s (token %s)" % (ipaddr, sessionid, token))
        return HttpResponse(status=204)


class AjaxGetIps(View):
    @log.logger(__name__)
    def get(self, request, logger=None):
        """
        Get the client's IP addresses from the session via AJAX
        (so we don't need to reload the view in case we just invalidated stale IPs
        and triggered new detection).

        :param request: Django request object
        :return: HttpResponse object
        """
        response = dict(
            ipv4=request.session.get('ipv4', ''),
            ipv4_rdns=request.session.get('ipv4_rdns', ''),
            ipv6=request.session.get('ipv6', ''),
            ipv6_rdns=request.session.get('ipv6_rdns', ''),
        )
        logger.debug("ajax_get_ips response: %r" % (response,))
        return HttpResponse(json.dumps(response), content_type='application/json')


def basic_challenge(realm, content='Authorization Required'):
    """
    Construct a 401 response requesting HTTP Basic Auth.

    :param realm: Realm string (displayed by the browser)
    :param content: Request body content
    :return: HttpResponse object
    """
    response = Response(content)
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm,)
    response.status_code = 401
    return response


def basic_authenticate(auth):
    """
    Get username and password from an HTTP Basic Auth string.

    :param auth: HTTP Basic Auth string (str)
    :return: (username, password) tuple on success; None on invalid/malformed headers
    """
    assert isinstance(auth, str)
    try:
        authmeth, payload = auth.split(' ', 1)
    except ValueError:
        # invalid auth header format
        return
    if authmeth.lower() != 'basic':
        return
    try:
        decoded_bytes = base64.b64decode(payload.strip())
    except (binascii.Error, ValueError):
        return
    decoded = decoded_bytes.decode('utf-8', errors='ignore')
    if ':' not in decoded:
        return
    username, password = decoded.split(':', 1)
    return username, password


@log.logger(__name__)
def check_api_auth(username, password, logger=None):
    """
    Check the username and password against our database.

    :param username: HTTP Basic Auth username (== FQDN)
    :param password: Update password
    :return: Host object if authenticated, None otherwise.
    """
    fqdn = username
    try:
        host = Host.get_by_fqdn(fqdn)
    except ValueError:
        # logging this at debug level because otherwise it fills our logs...
        logger.debug('%s - received bad credentials (auth username == dyndns hostname not in our hosts DB)' % (fqdn,))
        return None
    if host is not None:
        ok, must_update = verify_password(password, host.update_secret, preferred='weakargon2')
        if ok and must_update:
            # If password is correct but uses a not desired hasher, change it now to the desired one.
            host.generate_secret(password)

        success_msg = ('failure', 'success')[ok]
        msg = "api authentication %s. [hostname: %s (given in basic auth)]" % (success_msg, fqdn,)
        host.register_api_auth_result(msg, fault=not ok)
        if ok:
            return host
        # in case this fills our logs and we never see valid credentials, we can just kill
        # the DB entry and this will fail earlier and get logged at debug level, see above.
        logger.warning('%s - received bad credentials (password does not match)' % (fqdn,))
    return None


def check_session_auth(user, hostname):
    """
    Check our database whether the hostname is owned by the user.

    :param user: Django user object
    :param hostname: FQDN
    :return: Host object if the hostname is owned by this user, None otherwise.
    """
    fqdn = hostname
    try:
        host = Host.get_by_fqdn(fqdn, created_by=user)
    except ValueError:
        return None
    # we have specifically looked for a host of the logged in user,
    # we either have one now and return it, or we have None and return that.
    return host


def _make_response(results):
    """
    The extension to myip=ip1,ip2 is a bit problematic as the dyndns2 standard
    does neither define that nor how the response shall look like.
    """
    single_results = 'abuse', 'badagent', 'badauth', 'notfqdn', 'nohost', 'dnserr'
    for code in single_results:
        if code in results:
            return Response(code)
    nochg_ips = []
    updated_ips = []
    deleted_records = []
    for result in results:
        if result.startswith('nochg '):
            nochg_ips.append(result[6:])
        elif result.startswith('good '):
            updated_ips.append(result[5:])
        elif result.startswith('deleted '):
            deleted_records.append(result[8:])
        else:
            raise ValueError(f"unexpected result: {result!r}")
    len_results = len(results)
    # clean cases, all the same
    if len_results == len(nochg_ips):
        return Response('nochg ' + ','.join(nochg_ips))  # nothing changed
    if len_results == len(deleted_records):
        return Response('deleted ' + ','.join(deleted_records))  # deleted all records
    if len_results == len(updated_ips):
        return Response('good ' + ','.join(updated_ips))  # all updated
    # mixed cases, need to return all results
    response_lines = []
    [response_lines.append('good %s' % updated_ip) for updated_ip in updated_ips]
    [response_lines.append('nochg %s' % nochg_ip) for nochg_ip in nochg_ips]
    [response_lines.append('deleted %s' % deleted_record) for deleted_record in deleted_records]
    return Response('\n'.join(response_lines))


class NicUpdateView(View):
    @log.logger(__name__)
    def get(self, request, logger=None, delete=False):
        """
        DynDNS2-compatible /nic/update API.

        Example URLs:

        Will request username (FQDN) and password (secret) from the user,
        for interactive testing/updating:
        https://nsupdate.info/nic/update

        You can also include it in the URL, so the browser will automatically
        send the HTTP Basic Auth with the request:
        https://fqdn:secret@nsupdate.info/nic/update

        If the request does not come from the correct IP, you can give it as
        a query parameter.
        You can also give the hostname/FQDN as a query parameter (this is
        supported for API compatibility only), but then it MUST match the FQDN
        used for HTTP Basic Auth's username part, because the secret only
        allows you to update this single FQDN).
        https://fqdn:secret@nsupdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

        :param request: Django request object
        :param delete: False means update, True means delete - used by NicDeleteView
        :return: HttpResponse object
        """
        hostname = request.GET.get('hostname')
        if hostname in settings.BAD_HOSTS:
            return Response('abuse', status=403)
        auth = request.headers.get('authorization')
        if auth is None:
            # logging this at debug level because otherwise it fills our logs...
            logger.debug('%s - received no auth' % (hostname,))
            return basic_challenge("authenticate to update DNS", 'badauth')
        creds = basic_authenticate(auth)
        if not creds:
            logger.debug('%s - received malformed auth header' % (hostname,))
            return basic_challenge("authenticate to update DNS", 'badauth')
        username, password = creds
        if '.' not in username:  # username MUST be the fqdn
            # specifically point to configuration errors on client side
            return Response('notfqdn')
        if username in settings.BAD_HOSTS:
            return Response('abuse', status=403)
        host = check_api_auth(username, password)
        if host is None:
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
        agent = request.headers.get('user-agent', 'unknown')
        if agent in settings.BAD_AGENTS:
            msg = '%s - received update from bad user agent %r' % (hostname, agent)
            logger.warning(msg)
            host.register_client_result(msg, fault=True)
            return Response('badagent')
        remote_addr = normalize_ip(request.META.get('REMOTE_ADDR'))
        ipaddr = request.GET.get('myip')
        if not ipaddr:  # None or ''
            ipaddrs = [remote_addr, ]
        else:
            # handle multiple comma-separated IPs, see issue 501
            # we should update all valid IP addresses it gets.
            # usually it will be 1 (v4 or v6) or 2 (v4 and v6) addresses.
            ipaddrs = []
            for ip in ipaddr.split(','):
                ip = strip_ip(ip)
                try:
                    check_ip(ip)
                    ipaddrs.append(ip)
                except ValueError:
                    return Response('dnserr')
            if not ipaddrs:
                # if none of the given IPs are valid, we update to the remote_addr
                ipaddrs = [remote_addr, ]
        secure = request.is_secure()
        results = [update_or_delete(host, ip, secure, logger=logger, _delete=delete) for ip in ipaddrs]
        return _make_response(results)


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
            logger.warning('%s - is not owned by user: %s' % (hostname, request.user.username,))
            return Response('nohost')
        logger.info("authenticated by session as user %s, creator of host %s" % (request.user.username, hostname))
        # note: we do not check the user agent here as this is interactive
        # and logged-in usage - thus misbehaved user agents are no problem.
        remote_addr = normalize_ip(request.META.get('REMOTE_ADDR'))
        ipaddr = request.GET.get('myip')
        if not ipaddr:  # None or empty string
            ipaddrs = [remote_addr, ]
        else:
            # handle multiple comma-separated IPs, see issue 501
            # we should update all valid IP addresses it gets.
            # usually it will be 1 (v4 or v6) or 2 (v4 and v6) addresses.
            ipaddrs = []
            for ip in ipaddr.split(','):
                ip = strip_ip(ip)
                try:
                    check_ip(ip)
                    ipaddrs.append(ip)
                except ValueError:
                    continue
            if not ipaddrs:
                ipaddrs = [remote_addr, ]
        secure = request.is_secure()
        results = [update_or_delete(host, ip, secure, logger=logger, _delete=delete) for ip in ipaddrs]
        return _make_response(results)


class AuthorizedNicDeleteView(AuthorizedNicUpdateView):

    @log.logger(__name__)
    def get(self, request, logger=None, delete=True):
        """
        /nic/delete API - for logged-in admin browser.

        :param request: django request object
        :return: HttpResponse object
        """
        return super(AuthorizedNicDeleteView, self).get(request, logger=logger, delete=delete)
