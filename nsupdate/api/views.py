# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.conf import settings
from main.forms import *
import dns.inet

from main.dnstools import update, SameIpError


def MyIpView(request):
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")


def UpdateIpView(request):
    ipaddr = request.META['REMOTE_ADDR']
    af = dns.inet.af_for_address(ipaddr)
    key = 'ipv4' if af == dns.inet.AF_INET else 'ipv6'
    request.session[key] = ipaddr
    return HttpResponse('OK', content_type="text/plain")


def basic_challenge(realm):
    response = HttpResponse('Authorization Required', content_type="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm, )
    response.status_code = 401
    return response


def basic_authenticate(auth):
    authmeth, auth = auth.split(' ', 1)
    if authmeth.lower() != 'basic':
        return
    auth = auth.strip().decode('base64')
    username, password = auth.split(':', 1)
    return username, password


def check_auth(username, password):
    return password == 'pass'  # FIXME


def Response(content):
    return HttpResponse(content, content_type='text/plain')


def NicUpdateView(request):
    hostname = request.GET.get('hostname')
    auth = request.META.get('HTTP_AUTHORIZATION')
    if auth is None:
        logger.warning('%s - received no auth' % (hostname, ))
        return basic_challenge("authenticate to update DNS")
    username, password = basic_authenticate(auth)
    if not check_auth(username, password):
        logger.info('%s - received bad credentials, username: %s' % (hostname, username, ))
        return Response('badauth')
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
