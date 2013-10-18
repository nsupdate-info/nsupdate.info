# -*- coding: utf-8 -*-
from django import forms

from .models import Host, Domain


class CreateHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['subdomain', 'domain', 'comment']


class EditHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['comment']


class CreateDomainForm(forms.ModelForm):
    class Meta(object):
        model = Domain
        exclude = ['created_by']
