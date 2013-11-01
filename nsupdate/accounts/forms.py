# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
    class Meta(object):
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.widgets.TextInput(attrs=dict(autofocus=None)),
        }
