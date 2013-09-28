# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings
import json


class HomeView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['nav_home'] = True
        return context


class OverviewView(TemplateView):
    template_name = "main/overview.html"

    def get_context_data(self, *args, **kwargs):
        context = super(OverviewView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        context['ipv4'] = settings.WWW_IPV4_HOST
        context['ipv6'] = settings.WWW_IPV6_HOST
        return context


def MyIpView(request):
    return HttpResponse(
        json.dumps({'ip': request.META['REMOTE_ADDR']}),
        content_type="application/json")


class UserProfileView(TemplateView):
    template_name = "main/user_profile.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        context['nav_user_profile'] = True
        return context


class PasswordChangeView(TemplateView):
    template_name = "registration/password_change.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(*args, **kwargs)
        context['nav_change_password'] = True
        return context
