# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from main.models import Host

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ['fqdn', 'comment', 'update_secret']

    def __init__(self, user, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.created_by = user

    def save(self, user, commit=True):
        instance = super(HostForm, self).save(commit=False)
        instance.created_by = user
        if commit:
            instance.save()
        return instance

    def create_host(self, user):
        self.clean()
        host = Host(fqdn=self.cleaned_data['fqdn'],
                    comment=self.cleaned_data['comment'],
                    update_secret=self.cleaned_data['update_secret'],
                    created_by=user)
        host.save()
        # TODO: Update NS with self.cleaned_data['ipv4addr']
        return host

