# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from main.models import * 

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['fqdn', 'comment', ]

    def __init__(self, user, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.created_by = user

    def create_host(self, user):
        self.clean()
        host = Host(fqdn=self.cleaned_data['fqdn'],
                    comment=self.cleaned_data['comment'],
                    created_by=user)
        host.save()
        # TODO: Update NS with self.cleaned_data['ipv4addr']
        return host

