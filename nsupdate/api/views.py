# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.conf import settings

def MyIpView(request):
    return HttpResponse(request.META['REMOTE_ADDR'], content_type="text/plain")