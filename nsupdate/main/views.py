# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, CreateView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse

from main.forms import HostForm
from main.models import Host

def create_context(request):
    context = {}
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    context['session'] = request.session
    return context


class HomeView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context.update(create_context(self.request))
        context['nav_home'] = True
        return context


class OverviewView(CreateView):
    model = Host
    template_name = "main/overview.html"
    form_class = HostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OverviewView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('overview')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Host added.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(OverviewView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        context['hosts'] = Host.objects.filter(created_by=self.request.user)
        return context


@login_required
def HostView(request,pk=None):
    context = create_context(request)
    context['nav_overview'] = True
    context['HostForm'] = HostForm(request.user,instance=get_object_or_404(Host, pk=pk, created_by=request.user))
    if request.method == "POST":
        print "POST"
        form = HostForm(request.user, request.POST,)
        print form
        if form.is_valid():
            print "valid"
            host = form.save(request.user)
        context['HostForm'] = form
    return render(request, "main/host.html", context)

