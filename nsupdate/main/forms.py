# -*- coding: utf-8 -*-
from django import forms

from .models import Host, Domain


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
        fields = ['comment']


class CreateDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        exclude = ['created_by']
        widgets = {
            'domain': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }


class EditDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        fields = ['comment', 'nameserver_ip', 'public', 'available',
                  'nameserver_update_algorithm', 'nameserver_update_key']
