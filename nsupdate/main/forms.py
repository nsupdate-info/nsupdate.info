# -*- coding: utf-8 -*-
"""
form definitions (which fields are available, order, autofocus, ...)
"""

from django import forms

from .models import Host, Domain, ServiceUpdaterHostConfig


class CreateHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['subdomain', 'domain', 'comment']
        widgets = {
            'subdomain': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['comment', 'available', 'abuse']


class CreateDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        fields = ['domain', 'nameserver_ip', 'nameserver_update_algorithm',
                  'public', 'available', 'comment']
        widgets = {
            'domain': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        fields = ['comment', 'nameserver_ip', 'public', 'available',
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
