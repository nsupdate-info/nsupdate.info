# -*- coding: utf-8 -*-
from django import forms
from main.models import Host


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['subdomain', 'domain', 'comment', 'update_secret']
