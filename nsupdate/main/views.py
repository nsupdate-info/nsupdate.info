# -*- coding: utf-8 -*-
"""
views for the interactive web user interface
"""

from datetime import timedelta

from django.db.models import Q
from django.views.generic import View, TemplateView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now

import dnstools

from .forms import (CreateHostForm, EditHostForm, CreateDomainForm, EditDomainForm,
                    CreateUpdaterHostConfigForm, EditUpdaterHostConfigForm)
from .models import Host, Domain, ServiceUpdaterHostConfig


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


class GenerateNSSecretView(UpdateView):
    model = Domain
    template_name = "main/generate_ns_secret.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenerateNSSecretView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(GenerateNSSecretView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(GenerateNSSecretView, self).get_context_data(*args, **kwargs)
        context['nav_domain_overview'] = True
        context['shared_secret'] = self.object.generate_ns_secret()
        context['domains'] = Domain.objects.filter(created_by=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, 'Nameserver shared secret created.')
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
        return context


class StatusView(TemplateView):
    template_name = "main/status.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatusView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(
            StatusView, self).get_context_data(*args, **kwargs)
        context['nav_status'] = True
        context['domains_total'] = Domain.objects.count()
        context['domains_unavailable'] = Domain.objects.filter(available=False).count()
        context['domains_public'] = Domain.objects.filter(public=True).count()
        context['hosts_total'] = Host.objects.count()
        context['hosts_unavailable'] = Host.objects.filter(available=False).count()
        context['hosts_abuse'] = Host.objects.filter(abuse=True).count()
        context['hosts_abuse_blocked'] = Host.objects.filter(abuse_blocked=True).count()
        t_now = now()
        before_2d = t_now - timedelta(hours=48)
        before_2w = t_now - timedelta(days=14)
        before_2m = t_now - timedelta(days=61)
        before_2y = t_now - timedelta(days=730)
        context['hosts_ipv4_2d'] = Host.objects.filter(last_update_ipv4__gt=before_2d).count()
        context['hosts_ipv6_2d'] = Host.objects.filter(last_update_ipv6__gt=before_2d).count()
        context['hosts_ipv4_ssl_2d'] = Host.objects.filter(last_update_ipv4__gt=before_2d, ssl_update_ipv4=True).count()
        context['hosts_ipv6_ssl_2d'] = Host.objects.filter(last_update_ipv6__gt=before_2d, ssl_update_ipv6=True).count()
        context['hosts_ipv4_2w'] = Host.objects.filter(last_update_ipv4__gt=before_2w).count()
        context['hosts_ipv6_2w'] = Host.objects.filter(last_update_ipv6__gt=before_2w).count()
        context['hosts_ipv4_ssl_2w'] = Host.objects.filter(last_update_ipv4__gt=before_2w, ssl_update_ipv4=True).count()
        context['hosts_ipv6_ssl_2w'] = Host.objects.filter(last_update_ipv6__gt=before_2w, ssl_update_ipv6=True).count()
        context['hosts_ipv4_2m'] = Host.objects.filter(last_update_ipv4__gt=before_2m).count()
        context['hosts_ipv6_2m'] = Host.objects.filter(last_update_ipv6__gt=before_2m).count()
        context['hosts_ipv4_ssl_2m'] = Host.objects.filter(last_update_ipv4__gt=before_2m, ssl_update_ipv4=True).count()
        context['hosts_ipv6_ssl_2m'] = Host.objects.filter(last_update_ipv6__gt=before_2m, ssl_update_ipv6=True).count()
        context['hosts_ipv4_2y'] = Host.objects.filter(last_update_ipv4__gt=before_2y).count()
        context['hosts_ipv6_2y'] = Host.objects.filter(last_update_ipv6__gt=before_2y).count()
        context['hosts_ipv4_ssl_2y'] = Host.objects.filter(last_update_ipv4__gt=before_2y, ssl_update_ipv4=True).count()
        context['hosts_ipv6_ssl_2y'] = Host.objects.filter(last_update_ipv6__gt=before_2y, ssl_update_ipv6=True).count()
        user_model = get_user_model()
        context['users_total'] = user_model.objects.count()
        context['users_active'] = user_model.objects.filter(is_active=True).count()
        context['users_created_2d'] = user_model.objects.filter(date_joined__gt=before_2d).count()
        context['users_loggedin_2d'] = user_model.objects.filter(last_login__gt=before_2d).count()
        context['users_created_2w'] = user_model.objects.filter(date_joined__gt=before_2w).count()
        context['users_loggedin_2w'] = user_model.objects.filter(last_login__gt=before_2w).count()
        context['users_created_2m'] = user_model.objects.filter(date_joined__gt=before_2m).count()
        context['users_loggedin_2m'] = user_model.objects.filter(last_login__gt=before_2m).count()
        context['users_created_2y'] = user_model.objects.filter(date_joined__gt=before_2y).count()
        context['users_loggedin_2y'] = user_model.objects.filter(last_login__gt=before_2y).count()
        return context


from nsupdate.api.views import basic_challenge, basic_authenticate


class JsUpdateView(TemplateView):
    template_name = "main/update.html"

    def get(self, request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION')
        if auth is None:
            return basic_challenge("authenticate to update DNS", 'badauth')
        username, password = basic_authenticate(auth)
        self.hostname = username
        self.secret = password
        return super(JsUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(JsUpdateView, self).get_context_data(*args, **kwargs)
        context['hostname'] = self.hostname
        context['secret'] = self.secret
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

    def get_form(self, form_class):
        form = super(OverviewView, self).get_form(form_class)
        form.fields['domain'].queryset = Domain.objects.filter(
            Q(created_by=self.request.user) | Q(public=True))
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            dnstools.add(self.object.get_fqdn(), self.request.META['REMOTE_ADDR'], origin=self.object.domain.domain)
        except dnstools.Timeout:
            success, level, msg = False, messages.ERROR, 'Timeout - communicating to name server failed.'
        except dnstools.NameServerNotAvailable:
            success, level, msg = False, messages.ERROR, 'Name server unavailable.'
        else:
            self.object.created_by = self.request.user
            self.object.save()
            success, level, msg = True, messages.SUCCESS, 'Host added.'
        messages.add_message(self.request, level, msg)
        url = self.get_success_url() if success else reverse('overview')
        return HttpResponseRedirect(url)

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
    template_name = "main/delete_object.html"

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


class DomainOverviewView(CreateView):
    model = Domain
    template_name = "main/domain_overview.html"
    form_class = CreateDomainForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainOverviewView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('generate_ns_secret_view', args=(self.object.pk,))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Domain added.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(
            DomainOverviewView, self).get_context_data(*args, **kwargs)
        context['nav_domain_overview'] = True
        context['your_domains'] = Domain.objects.filter(
            created_by=self.request.user)
        context['public_domains'] = Domain.objects.filter(
            public=True).exclude(created_by=self.request.user)
        return context


class DomainView(UpdateView):
    model = Domain
    template_name = "main/domain.html"
    form_class = EditDomainForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('domain_overview')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Domain updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        obj = super(DomainView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(DomainView, self).get_context_data(*args, **kwargs)
        context['nav_domain_overview'] = True
        context['domains'] = Domain.objects.filter(created_by=self.request.user)
        return context


class DeleteDomainView(DeleteView):
    model = Domain
    template_name = "main/delete_object.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteDomainView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteDomainView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_success_url(self):
        return reverse('domain_overview')

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteDomainView, self).get_context_data(*args, **kwargs)
        context['nav_domain_overview'] = True
        context['domains'] = Domain.objects.filter(created_by=self.request.user)
        return context


class UpdaterHostConfigOverviewView(CreateView):
    model = ServiceUpdaterHostConfig
    template_name = "main/updater_hostconfig_overview.html"
    form_class = CreateUpdaterHostConfigForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.__host_pk = kwargs.pop('pk', None)
        return super(UpdaterHostConfigOverviewView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('updater_hostconfig_overview', args=(self.__host_pk,))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.host = Host(pk=self.__host_pk)
        self.object.created_by = self.request.user
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Service Updater Host Configuration added.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(
            UpdaterHostConfigOverviewView, self).get_context_data(*args, **kwargs)
        context['updater_configs'] = ServiceUpdaterHostConfig.objects.filter(
            host=self.__host_pk)
        return context


class UpdaterHostConfigView(UpdateView):
    model = ServiceUpdaterHostConfig
    template_name = "main/updater_hostconfig.html"
    form_class = EditUpdaterHostConfigForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdaterHostConfigView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        host_pk = self.object.host.pk
        return reverse('updater_hostconfig_overview', args=(host_pk,))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Service Updater Host Configuration updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        obj = super(UpdaterHostConfigView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(UpdaterHostConfigView, self).get_context_data(*args, **kwargs)
        return context


class DeleteUpdaterHostConfigView(DeleteView):
    model = ServiceUpdaterHostConfig
    template_name = "main/delete_object.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteUpdaterHostConfigView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteUpdaterHostConfigView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise PermissionDenied()  # or Http404
        return obj

    def get_success_url(self):
        host_pk = self.object.host.pk
        return reverse('updater_hostconfig_overview', args=(host_pk,))

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteUpdaterHostConfigView, self).get_context_data(*args, **kwargs)
        return context


class RobotsTxtView(View):
    """
    Dynamically serve robots.txt content.
    If you like, you can optimize this by statically serving this by your web server.
    """
    def get(self, request):
        content = """\
User-agent: *
Crawl-delay: 10
Disallow: /account/
Disallow: /accounts/
Disallow: /login/
Disallow: /admin/
Disallow: /status/
Disallow: /myip/
Disallow: /detect_ip/
Disallow: /ajax_get_ips/
Disallow: /nic/update/
Disallow: /nic/update_authorized/
Disallow: /update/
Disallow: /host/
Disallow: /overview/
Disallow: /domain/
Disallow: /domain_overview/
Disallow: /updater_hostconfig/
Disallow: /updater_hostconfig_overview/
"""
        return HttpResponse(content, content_type="text/plain")


def csrf_failure_view(request, reason):  # pragma: no cover (hard to test)
    """
    Django's CSRF middleware's builtin view doesn't tell the user that he needs to have cookies enabled.

    :param request: django request object
    :param reason: why the csrf check failed
    :return: HttpResponse object
    """
    if reason == "CSRF cookie not set.":
        content = """\
This site needs cookies (for CSRF protection, for keeping your session after login).

Please enable cookies in your browser (or otherwise make sure the CSRF cookie can be set).
""" % dict(reason=reason)
        status = 200
    else:
        content = """\
%(reason)s

CSRF verification failure.

Either you are trying to access this site in 'unusual' ways (then please stop doing that), or
you found an issue in the code (then please file an issue for this and tell how you got here).
""" % dict(reason=reason)
        status = 403
    return HttpResponse(content, status=status, content_type="text/plain")
