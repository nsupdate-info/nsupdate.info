# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings
from main.forms import *
import dns.inet

def MyIpView(request):
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")

def UpdateIpView(request):
    ipaddr = request.META['REMOTE_ADDR']
    af = dns.inet.af_for_address(ipaddr)
    if af == dns.inet.AF_INET:
        request.session['ipv4'] = ipaddr
    else:
        request.session['ipv6'] = ipaddr
    return HttpResponse('OK', content_type="text/plain")