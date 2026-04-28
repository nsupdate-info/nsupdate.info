# -*- coding: utf-8 -*-
"""
Form definitions (available fields, order, auto-focus, ...).
"""

import binascii

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Host, RelatedHost, Domain, ServiceUpdaterHostConfig
from .dnstools import check_domain, NameServerNotAvailable

import logging
logger = logging.getLogger(__name__)


class CreateHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['name', 'domain', 'comment']
        widgets = {
            'name': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['comment', 'available', 'abuse', 'netmask_ipv4', 'netmask_ipv6']

    netmask_ipv4 = forms.IntegerField(min_value=0, max_value=32)
    netmask_ipv6 = forms.IntegerField(min_value=0, max_value=64)


class CreateRelatedHostForm(forms.ModelForm):
    class Meta(object):
        model = RelatedHost
        fields = ['name', 'comment', 'available', 'interface_id_ipv4', 'interface_id_ipv6']
        widgets = {
            'name': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditRelatedHostForm(forms.ModelForm):
    class Meta(object):
        model = RelatedHost
        fields = ['name', 'comment', 'available', 'interface_id_ipv4', 'interface_id_ipv6']


class CreateDomainForm(forms.ModelForm):
    def clean_nameserver_update_secret(self):
        secret = self.cleaned_data['nameserver_update_secret']
        try:
            binascii.a2b_base64(secret.encode(encoding="ascii", errors="strict"))
        except (binascii.Error, UnicodeEncodeError):
            raise forms.ValidationError(_("Enter a valid secret in base64 format."), code='invalid')
        return secret

    class Meta(object):
        model = Domain
        fields = ['name',
                  'public', 'available',
                  'nameserver_ip', 'nameserver_port', 'nameserver_protocol',
                  'nameserver2_ip', 'nameserver2_port', 'nameserver2_protocol',
                  'nameserver_update_key_name', 'nameserver_update_algorithm', 'nameserver_update_secret',
                  'comment']
        widgets = {
            'name': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditDomainForm(forms.ModelForm):
    def clean_nameserver_update_secret(self):
        secret = self.cleaned_data['nameserver_update_secret']
        try:
            binascii.a2b_base64(secret.encode(encoding="ascii", errors="strict"))
        except (binascii.Error, UnicodeEncodeError):
            raise forms.ValidationError(_("Enter a valid secret in base64 format."), code='invalid')
        return secret

    def clean(self):
        cleaned_data = super(EditDomainForm, self).clean()
        logger.debug("cleaned_data: " + str(cleaned_data))

        if self.cleaned_data['available']:
            try:
                check_domain(self.instance.name, cleaned_data)

            except NameServerNotAvailable as e:
                raise forms.ValidationError(
                    _("Failed to add/delete host connectivity-test.%(domain)s, check your DNS server configuration.") +
                    " " +
                    _("This is a requirement for setting the available flag.") +
                    " (%(error_detail)s)",
                    code='invalid',
                    params={
                        'domain': self.instance.name,
                        'error_detail': str(e)
                    }
                )

        if cleaned_data['public'] and not cleaned_data['available']:
            raise forms.ValidationError(
                _("Domain must be available to be public."),
                code='invalid')

    class Meta(object):
        model = Domain
        fields = ['name',
                  'public', 'available',
                  'nameserver_ip', 'nameserver_port', 'nameserver_protocol',
                  'nameserver2_ip', 'nameserver2_port', 'nameserver2_protocol',
                  'nameserver_update_key_name', 'nameserver_update_algorithm', 'nameserver_update_secret',
                  'comment'
        ]


class CreateUpdaterHostConfigForm(forms.ModelForm):
    class Meta(object):
        model = ServiceUpdaterHostConfig
        fields = ['service', 'hostname', 'name', 'password',
                  'give_ipv4', 'give_ipv6', 'comment']
        widgets = {
            'hostname': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditUpdaterHostConfigForm(forms.ModelForm):
    class Meta(object):
        model = ServiceUpdaterHostConfig
        fields = ['hostname', 'comment', 'name', 'password',
                  'give_ipv4', 'give_ipv6']
