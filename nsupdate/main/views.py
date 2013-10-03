# -*- coding: utf-8 -*-

import dns.inet

from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

import dnstools

from main.forms import CreateHostForm, EditHostForm
from main.models import Host


class GenerateSecretView(UpdateView):
    model = Host
    template_name = "main/generate_secret.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenerateSecretView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(GenerateSecretView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(GenerateSecretView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        # generate secret, store it hashed and return the plain secret for the context
        context['update_secret'] = self.object.generate_secret()
        context['hosts'] = Host.objects.filter(created_by=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, 'Host secret created.')
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AboutView, self).get_context_data(*args, **kwargs)
        context['nav_about'] = True
        return context


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['nav_home'] = True

        s = self.request.session
        ipaddr = self.request.META['REMOTE_ADDR']
        af = dns.inet.af_for_address(ipaddr)
        key = 'ipv4' if af == dns.inet.AF_INET else 'ipv6'
        s[key] = ipaddr
        s.save()

        return context


class HelpView(TemplateView):
    template_name = "main/help.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HelpView, self).get_context_data(*args, **kwargs)
        context['nav_help'] = True
        return context


class OverviewView(CreateView):
    model = Host
    template_name = "main/overview.html"
    form_class = CreateHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OverviewView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('generate_secret_view', args=(self.object.pk,))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        dnstools.add(self.object.get_fqdn(), self.request.META['REMOTE_ADDR'])
        messages.add_message(self.request, messages.SUCCESS, 'Host added.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(OverviewView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        context['hosts'] = Host.objects.filter(created_by=self.request.user)
        return context


class HostView(UpdateView):
    model = Host
    template_name = "main/host.html"
    form_class = EditHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HostView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('overview')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Host updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        obj = super(HostView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(HostView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        context['remote_addr'] = self.request.META['REMOTE_ADDR']
        context['hosts'] = Host.objects.filter(created_by=self.request.user)
        return context


class DeleteHostView(DeleteView):
    model = Host
    template_name = "main/delete_host.html"
    form_class = EditHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteHostView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteHostView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_success_url(self):
        return reverse('overview')

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteHostView, self).get_context_data(*args, **kwargs)
        context['nav_overview'] = True
        context['hosts'] = Host.objects.filter(created_by=self.request.user)
        return context


def RobotsTxtView(request):
    """
    Dynamically serve robots.txt content.
    If you like, you can optimize this by statically serving this by your web server.

    :param request: django request object
    :return: HttpResponse object
    """
    content = """\
User-agent: *
Crawl-delay: 10
Disallow: /accounts/
Disallow: /myip/
Disallow: /nic/update/
"""
    return HttpResponse(content, content_type="text/plain")
