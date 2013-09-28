# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.hashers import check_password

from main.forms import *
from main.models import Host
import dns.inet
import os

from main.dnstools import update, SameIpError


def MyIpView(request):
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")


def UpdateIpView(request):
    ipaddr = request.META['REMOTE_ADDR']
    af = dns.inet.af_for_address(ipaddr)
    key = 'ipv4' if af == dns.inet.AF_INET else 'ipv6'
    request.session[key] = ipaddr
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


def check_auth(username, password):
    """
    Check username and password against our database.

    :param username: http basic auth username (== fqdn)
    :param password: update password
    :return: True if authenticated, False otherwise.
    """
    fqdn = username
    hosts = Host.objects.filter(fqdn=fqdn)
    num_hosts = len(hosts)
    if num_hosts == 0:
        return False
    if num_hosts > 1:
        logging.error("fqdn %s has multiple entries" % fqdn)
        return False
    password_hash = hosts[0].update_secret
    return check_password(password, password_hash)


def Response(content):
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
    """
    hostname = request.GET.get('hostname')
    auth = request.META.get('HTTP_AUTHORIZATION')
    if auth is None:
        logger.warning('%s - received no auth' % (hostname, ))
        return basic_challenge("authenticate to update DNS", 'noauth')
    username, password = basic_authenticate(auth)
    if not check_auth(username, password):
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
    ipaddr = str(ipaddr)  # XXX bug in dnspython: crashes if ipaddr is unicode, wants a str!
    try:
        update(hostname, ipaddr)
        logger.info('%s - received good update -> ip: %s' % (hostname, ipaddr, ))
        return Response('good %s' % ipaddr)
    except SameIpError:
        logger.warning('%s - received no-change update, ip: %s' % (hostname, ipaddr, ))
        return Response('nochg %s' % ipaddr)
