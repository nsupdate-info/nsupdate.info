# -*- coding: utf-8 -*-
from django import forms
from main.models import Host


class CreateHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['subdomain', 'domain', 'comment']


class EditHostForm(forms.ModelForm):
    class Meta(object):
        model = Host
        fields = ['comment']
