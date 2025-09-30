# -*- coding: utf-8 -*-
"""
form definitions (which fields are available, order, autofocus, ...)
"""

import binascii
import ipaddress

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Host, RelatedHost, Domain, ServiceUpdaterHostConfig
from .dnstools import check_domain, NameServerNotAvailable


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
        fields = ['name', 'nameserver_ip', 'nameserver2_ip', 'nameserver_update_algorithm', 'comment']
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
    
    def clean_nameserver_ip(self):
        """
        Validate that nameserver_ip is a valid public IP address.
        Reject private, loopback, reserved, and link-local addresses.
        """
        nameserver_ip = self.cleaned_data.get('nameserver_ip')
        if not nameserver_ip:
            return nameserver_ip

        try:
            ip_obj = ipaddress.ip_address(nameserver_ip)
        except ValueError:
            raise forms.ValidationError(_("Enter a valid IP address."), code='invalid')
        
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_link_local:
            raise forms.ValidationError(("Enter a public IP address. Internal addresses are not allowed."), 
                code='invalid'
            )
        return nameserver_ip


    def clean(self):
        cleaned_data = super(EditDomainForm, self).clean()
        
        if self.cleaned_data['available'] and 'nameserver_ip' in cleaned_data:
            try:
                check_domain(self.instance.name, cleaned_data['nameserver_ip'])

            except (NameServerNotAvailable, ):
                raise forms.ValidationError(
                    _("Failed to add/delete host connectivity-test.%(domain)s, check your DNS server configuration. "
                      "This is a requirement for setting the available flag."),
                    code='invalid',
                    params={'domain': self.instance.name}
                )

        if cleaned_data['public'] and not cleaned_data['available']:
            raise forms.ValidationError(
                _("Domain must be available to be public"),
                code='invalid')

    class Meta(object):
        model = Domain
        fields = ['comment', 'nameserver_ip', 'nameserver2_ip', 'public', 'available',
                  'nameserver_update_algorithm', 'nameserver_update_secret']


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
