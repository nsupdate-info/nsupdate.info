# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.forms import *

class HomeView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['nav_home'] = True
        return context

@login_required
def OverviewView(request):
    context = {}
    context['nav_overview'] = True
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    context['session'] = request.session
    context['HostForm'] = HostForm(request.user)
    context['Hosts'] = Host.objects.filter(created_by=request.user)
    if request.method == "POST":
        print "POST"
        form = HostForm(request.user,request.POST)
        print form
        if form.is_valid():
            print "valid"
            host = form.create_host(request.user)
            host.save()

        context['HostForm'] = form
    return render(request, "main/overview.html", context)