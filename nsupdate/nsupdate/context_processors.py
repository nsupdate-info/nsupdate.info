# -*- coding: utf-8 -*-
from django.conf import settings


def add_settings(request):
    context = {}
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    try:
        context['ENABLE_PIWIK_PRODUCTION'] = settings.ENABLE_PIWIK_PRODUCTION
    except:
        pass
    return context
