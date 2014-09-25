# -*- coding: utf-8 -*-
"""
form definitions (which fields are available, order, autofocus, ...)
"""

from django import forms

from .models import Host, RelatedHost, Domain, ServiceUpdaterHostConfig


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
        fields = ['comment', 'available', 'abuse']


class CreateRelatedHostForm(forms.ModelForm):
    class Meta(object):
        model = RelatedHost
        fields = ['name', 'available', 'interface_id_ipv4', 'interface_id_ipv6']
        widgets = {
            'name': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditRelatedHostForm(forms.ModelForm):
    class Meta(object):
        model = RelatedHost
        fields = ['name', 'available', 'interface_id_ipv4', 'interface_id_ipv6']


class CreateDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        fields = ['name', 'nameserver_ip', 'nameserver_update_algorithm',
                  'public', 'available', 'comment']
        widgets = {
            'name': forms.widgets.TextInput(attrs=dict(autofocus=None)),
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
