# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from main.models import * 

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['fqdn', 'comment', ]

