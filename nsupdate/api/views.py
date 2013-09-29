# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.backends.db import SessionStore

from main.models import Host
import dns.inet
import os

from main.dnstools import update, SameIpError


def MyIpView(request):
    """
    return the IP address (can be v4 or v6) of the client requesting this view.

    :param request: django request object
    :return: HttpResponse object
    """
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")


def DetectIpView(request, secret=None):
    """
    Put the IP address (can be v4 or v6) of the client requesting this view
    into the client's session.

    :param request: django request object
    :param secret: session key used to find the correct session w/o session cookie
    :return: HttpResponse object
    """
    # we do not have the session as usual, as this is a different host,
    # so the session cookie is not received here - thus we access it via
    # the secret:
    s = SessionStore(session_key=secret)
    ipaddr = request.META['REMOTE_ADDR']
    af = dns.inet.af_for_address(ipaddr)
    key = 'ipv4' if af == dns.inet.AF_INET else 'ipv6'
    s[key] = ipaddr
    s.save()
    with open(os.path.join(settings.STATIC_ROOT, "1px.gif"), "rb") as f:
        image_data = f.read()
    return HttpResponse(image_data, mimetype="image/png")


def basic_challenge(realm, content='Authorization Required'):
    """
    Construct a 401 response requesting http basic auth.

    :param realm: realm string (displayed by the browser)
    :param content: request body content
    :return: HttpResponse object
    """
    response = HttpResponse(content, content_type="text/plain")
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
    :return: True if authenticated, False otherwise.
    """
    fqdn = username
    hosts = Host.filter_by_fqdn(fqdn)
    num_hosts = len(hosts)
    if num_hosts == 0:
        return False
    if num_hosts > 1:
        logging.error("fqdn %s has multiple entries" % fqdn)
        return False
    password_hash = hosts[0].update_secret
    return check_password(password, password_hash)


def check_session_auth(user, hostname):
    """
    Check our database whether the hostname is owned by the user.

    :param user: django user object
    :param hostname: fqdn
    :return: True if hostname is owned by this user, False otherwise.
    """
    fqdn = hostname
    hosts = Host.filter_by_fqdn(fqdn, created_by=user)
    num_hosts = len(hosts)
    if num_hosts == 0:
        return False
    if num_hosts > 1:
        logging.error("fqdn %s has multiple entries" % fqdn)
        return False
    return True


def Response(content):
    """
    shortcut for plaintext response

    :param content: plain text content for the response
    :return: HttpResonse object
    """
    return HttpResponse(content, content_type='text/plain')


def NicUpdateView(request):
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
    a query parameter, you can also give the hostname (then it won't use
    the username from http basic auth as the fqdn:
    https://fqdn:secret@nsupdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

    :param request: django request object
    :return: HttpResponse object
    """
    hostname = request.GET.get('hostname')
    auth = request.META.get('HTTP_AUTHORIZATION')
    if auth is None:
        logger.warning('%s - received no auth' % (hostname, ))
        return basic_challenge("authenticate to update DNS", 'noauth')
    username, password = basic_authenticate(auth)
    if not check_api_auth(username, password):
        logger.info('%s - received bad credentials, username: %s' % (hostname, username, ))
        return basic_challenge("authenticate to update DNS", 'badauth')
    if hostname is None:
        # as we use update_username == hostname, we can fall back to that:
        hostname = username
    ipaddr = request.GET.get('myip')
    if ipaddr is None:
        ipaddr = request.META.get('REMOTE_ADDR')
    agent = request.META.get('HTTP_USER_AGENT')
    if agent in settings.BAD_AGENTS:
        logger.info('%s - received update from bad user agent %s' % (hostname, agent, ))
        return Response('badagent')
    return _update(hostname, ipaddr)


@login_required
def AuthorizedNicUpdateView(request):
    """
    similar to NicUpdateView, but the client is not a router or other dyndns client,
    but the admin browser who is currently logged into the nsupdate.info site.

    Example URLs:

    https://supdate.info/nic/update?hostname=fqdn&myip=1.2.3.4

    :param request: django request object
    :return: HttpResponse object
    """
    hostname = request.GET.get('hostname')
    if hostname is None:
        return Response('nohost')
    if not check_session_auth(request.user, hostname):
        logger.info('%s - is not owned by user: %s' % (hostname, request.user.username, ))
        return Response('nohost')
    ipaddr = request.GET.get('myip')
    if ipaddr is None:
        ipaddr = request.META.get('REMOTE_ADDR')
    return _update(hostname, ipaddr)


def _update(hostname, ipaddr):
    ipaddr = str(ipaddr)  # XXX bug in dnspython: crashes if ipaddr is unicode, wants a str!
    try:
        update(hostname, ipaddr)
        logger.info('%s - received good update -> ip: %s' % (hostname, ipaddr, ))
        return Response('good %s' % ipaddr)
    except SameIpError:
        logger.warning('%s - received no-change update, ip: %s' % (hostname, ipaddr, ))
        return Response('nochg %s' % ipaddr)
