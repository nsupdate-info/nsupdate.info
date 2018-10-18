# -*- coding: utf-8 -*-
"""
views for the interactive web user interface
"""

import socket
from datetime import timedelta

import dns.name

from django.db.models import Q
from django.views.generic import View, TemplateView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import Http404
from django import template
from django.utils.timezone import now

from . import dnstools
from .iptools import normalize_ip

from .forms import (CreateHostForm, EditHostForm, CreateRelatedHostForm, EditRelatedHostForm,
                    CreateDomainForm, EditDomainForm, CreateUpdaterHostConfigForm, EditUpdaterHostConfigForm)
from .models import Host, RelatedHost, Domain, ServiceUpdaterHostConfig


class GenerateSecretView(UpdateView):
    model = Host
    fields = "__all__"
    template_name = "main/generate_secret.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenerateSecretView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(GenerateSecretView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(GenerateSecretView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        # generate secret, store it hashed and return the plain secret for the context
        context['update_secret'] = self.object.generate_secret()
        messages.add_message(self.request, messages.SUCCESS, 'Host secret created.')
        return context


class GenerateNSSecretView(UpdateView):
    model = Domain
    fields = "__all__"
    template_name = "main/generate_ns_secret.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenerateNSSecretView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(GenerateNSSecretView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(GenerateNSSecretView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        context['shared_secret'] = self.object.generate_ns_secret()
        messages.add_message(self.request, messages.SUCCESS, 'Nameserver shared secret created.')
        return context


class AboutView(TemplateView):
    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['nav_about'] = True
        return context


class CustomTemplateView(TemplateView):
    # template_name is set in dispatch method

    def dispatch(self, *args, **kwargs):
        self.template_name = 'main/custom/%s' % kwargs.get('template')
        try:
            template.loader.select_template([self.template_name, ])
            return super(CustomTemplateView, self).dispatch(*args, **kwargs)
        except template.TemplateDoesNotExist:
            raise Http404


class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['nav_home'] = True
        return context


class StatusView(TemplateView):
    template_name = "main/status.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatusView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            StatusView, self).get_context_data(**kwargs)
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
        context['hosts_ipv4_tls_2d'] = Host.objects.filter(last_update_ipv4__gt=before_2d, tls_update_ipv4=True).count()
        context['hosts_ipv6_tls_2d'] = Host.objects.filter(last_update_ipv6__gt=before_2d, tls_update_ipv6=True).count()
        context['hosts_ipv4_2w'] = Host.objects.filter(last_update_ipv4__gt=before_2w).count()
        context['hosts_ipv6_2w'] = Host.objects.filter(last_update_ipv6__gt=before_2w).count()
        context['hosts_ipv4_tls_2w'] = Host.objects.filter(last_update_ipv4__gt=before_2w, tls_update_ipv4=True).count()
        context['hosts_ipv6_tls_2w'] = Host.objects.filter(last_update_ipv6__gt=before_2w, tls_update_ipv6=True).count()
        context['hosts_ipv4_2m'] = Host.objects.filter(last_update_ipv4__gt=before_2m).count()
        context['hosts_ipv6_2m'] = Host.objects.filter(last_update_ipv6__gt=before_2m).count()
        context['hosts_ipv4_tls_2m'] = Host.objects.filter(last_update_ipv4__gt=before_2m, tls_update_ipv4=True).count()
        context['hosts_ipv6_tls_2m'] = Host.objects.filter(last_update_ipv6__gt=before_2m, tls_update_ipv6=True).count()
        context['hosts_ipv4_2y'] = Host.objects.filter(last_update_ipv4__gt=before_2y).count()
        context['hosts_ipv6_2y'] = Host.objects.filter(last_update_ipv6__gt=before_2y).count()
        context['hosts_ipv4_tls_2y'] = Host.objects.filter(last_update_ipv4__gt=before_2y, tls_update_ipv4=True).count()
        context['hosts_ipv6_tls_2y'] = Host.objects.filter(last_update_ipv6__gt=before_2y, tls_update_ipv6=True).count()
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

    def get_context_data(self, **kwargs):
        context = super(JsUpdateView, self).get_context_data(**kwargs)
        context['hostname'] = self.hostname
        context['secret'] = self.secret
        return context


class OverviewView(TemplateView):
    template_name = "main/overview.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OverviewView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        context['hosts'] = Host.objects.filter(created_by=self.request.user).select_related("domain")\
            .only("name", "comment", "available", "client_faults", "server_faults", "abuse_blocked", "abuse",
                  "last_update_ipv4", "tls_update_ipv4", "last_update_ipv6", "tls_update_ipv6", "domain__name")
        context['your_domains'] = Domain.objects.filter(
            created_by=self.request.user).select_related("created_by__profile")\
            .only("name", "public", "available", "comment", "created_by__username")
        context['public_domains'] = Domain.objects.filter(
            public=True).exclude(created_by=self.request.user).select_related("created_by")\
            .only("name", "public", "available", "comment", "created_by__username")
        return context


class AddHostView(CreateView):
    template_name = "main/host_add.html"
    model = Host
    form_class = CreateHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddHostView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('generate_secret_view', args=(self.object.pk,))

    def get_form(self, form_class=None):
        form = super(AddHostView, self).get_form(form_class)
        form.fields['domain'].queryset = Domain.objects.filter(
            Q(created_by=self.request.user) | Q(public=True))
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            dnstools.add(self.object.get_fqdn(), normalize_ip(self.request.META['REMOTE_ADDR']))
        except dnstools.Timeout:
            success, level, msg = False, messages.ERROR, 'Timeout - communicating to name server failed.'
        except dnstools.NameServerNotAvailable:
            success, level, msg = False, messages.ERROR, 'Name server unavailable.'
        except dnstools.NoNameservers:
            success, level, msg = False, messages.ERROR, 'Resolving failed: No name servers.'
        except dnstools.DnsUpdateError as e:
            success, level, msg = False, messages.ERROR, 'DNS update error [%s].' % str(e)
        except Domain.DoesNotExist:
            # should not happen: POST data had invalid (base)domain
            success, level, msg = False, messages.ERROR, 'Base domain does not exist.'
        except dnstools.SameIpError:
            success, level, msg = False, messages.ERROR, 'Host already exists in DNS.'
        except dnstools.DNSException as e:
            success, level, msg = False, messages.ERROR, 'DNSException [%s]' % str(e)
        except socket.error as err:
            success, level, msg = False, messages.ERROR, 'Communication to name server failed [%s]' % str(err)
        else:
            self.object.created_by = self.request.user
            dt_now = now()
            self.object.last_update_ipv4 = dt_now
            self.object.last_update_ipv6 = dt_now
            self.object.save()
            success, level, msg = True, messages.SUCCESS, 'Host added.'
        messages.add_message(self.request, level, msg)
        url = self.get_success_url() if success else reverse('overview')
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        context = super(AddHostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
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
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(HostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        context['remote_addr'] = normalize_ip(self.request.META['REMOTE_ADDR'])
        return context


class DeleteHostView(DeleteView):
    model = Host
    template_name = "main/delete_object.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteHostView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteHostView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user or obj.abuse_blocked:
            # disallow deletion if abuse_blocked is set, otherwise the
            # abuser can just delete and recreate the host
            raise Http404
        return obj

    def get_success_url(self):
        return reverse('overview')

    def get_context_data(self, **kwargs):
        context = super(DeleteHostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class RelatedHostOverviewView(TemplateView):
    template_name = "main/related_host_overview.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.__main_host = Host.objects.get(pk=kwargs.pop('mpk', None), created_by=self.request.user)
        except Host.DoesNotExist:
            raise Http404
        return super(RelatedHostOverviewView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RelatedHostOverviewView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        context['main_host'] = self.__main_host
        context['related_hosts'] = RelatedHost.objects.filter(main_host=self.__main_host)
        return context


class AddRelatedHostView(CreateView):
    template_name = "main/related_host_add.html"
    model = RelatedHost
    form_class = CreateRelatedHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.__main_host = Host.objects.get(pk=kwargs.pop('mpk', None), created_by=self.request.user)
        except Host.DoesNotExist:
            raise Http404
        return super(AddRelatedHostView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('related_host_overview', args=(self.object.main_host.pk, ))

    def get_form(self, form_class=None):
        form = super(AddRelatedHostView, self).get_form(form_class)
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.main_host = self.__main_host
        self.object.save()
        success, level, msg = True, messages.SUCCESS, 'Related host added.'
        messages.add_message(self.request, level, msg)
        url = self.get_success_url()
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        context = super(AddRelatedHostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class RelatedHostView(UpdateView):
    model = RelatedHost
    template_name = "main/related_host.html"
    form_class = EditRelatedHostForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.__main_host = Host.objects.get(pk=kwargs.pop('mpk', None), created_by=self.request.user)
        except Host.DoesNotExist:
            raise Http404
        return super(RelatedHostView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('related_host_overview', args=(self.object.main_host.pk, ))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Related host updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        obj = super(RelatedHostView, self).get_object(*args, **kwargs)
        if obj.main_host.created_by != self.request.user or obj.main_host != self.__main_host:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(RelatedHostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class DeleteRelatedHostView(DeleteView):
    model = RelatedHost
    template_name = "main/delete_object.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.__main_host = Host.objects.get(pk=kwargs.pop('mpk', None), created_by=self.request.user)
        except Host.DoesNotExist:
            raise Http404
        return super(DeleteRelatedHostView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super(DeleteRelatedHostView, self).get_object(*args, **kwargs)
        if obj.main_host.created_by != self.request.user or obj.main_host != self.__main_host:
            raise Http404
        return obj

    def get_success_url(self):
        return reverse('related_host_overview', args=(self.object.main_host.pk, ))

    def get_context_data(self, **kwargs):
        context = super(DeleteRelatedHostView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class AddDomainView(CreateView):
    template_name = "main/domain_add.html"
    model = Domain
    form_class = CreateDomainForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddDomainView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('generate_ns_secret_view', args=(self.object.pk,))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            dns.name.from_text(self.object.name, None)
        except dns.name.EmptyLabel as err:
            success, level, msg = False, messages.ERROR, 'Invalid domain name [%s]' % str(err)
        else:
            self.object.created_by = self.request.user
            self.object.save()
            success, level, msg = True, messages.SUCCESS, 'Domain added.'
        messages.add_message(self.request, level, msg)
        url = self.get_success_url() if success else reverse('overview')
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        context = super(AddDomainView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class DomainView(UpdateView):
    model = Domain
    template_name = "main/domain.html"
    form_class = EditDomainForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DomainView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('overview')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Domain updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        obj = super(DomainView, self).get_object(*args, **kwargs)
        if obj.created_by != self.request.user:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(DomainView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
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
            raise Http404
        return obj

    def get_success_url(self):
        return reverse('overview')

    def get_context_data(self, **kwargs):
        context = super(DeleteDomainView, self).get_context_data(**kwargs)
        context['nav_overview'] = True
        return context


class UpdaterHostConfigOverviewView(CreateView):
    model = ServiceUpdaterHostConfig
    template_name = "main/updater_hostconfig_overview.html"
    form_class = CreateUpdaterHostConfigForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            self.__host = Host.objects.get(pk=kwargs.pop('pk', None), created_by=self.request.user)
        except Host.DoesNotExist:
            raise Http404
        return super(UpdaterHostConfigOverviewView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('updater_hostconfig_overview', args=(self.__host.pk, ))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.host = self.__host
        self.object.created_by = self.request.user
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, 'Service Updater Host Configuration added.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(
            UpdaterHostConfigOverviewView, self).get_context_data(**kwargs)
        context['updater_configs'] = ServiceUpdaterHostConfig.objects.filter(host=self.__host)
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
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(UpdaterHostConfigView, self).get_context_data(**kwargs)
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
            raise Http404
        return obj

    def get_success_url(self):
        host_pk = self.object.host.pk
        return reverse('updater_hostconfig_overview', args=(host_pk,))

    def get_context_data(self, **kwargs):
        context = super(DeleteUpdaterHostConfigView, self).get_context_data(**kwargs)
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
