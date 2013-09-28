# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings

def MyIpView(request):
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")

def UpdateIpView(request):
    ip = request.META['REMOTE_ADDR']
    if ':' in ip:
        request.session['ipv6'] = request.META['REMOTE_ADDR']
    if '.' in ip:
        request.session['ipv4'] = request.META['REMOTE_ADDR']
    return HttpResponse('OK', content_type="text/plain")