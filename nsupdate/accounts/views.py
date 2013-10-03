# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .forms import UserProfileForm


class UserProfileView(UpdateView):
    template_name = "accounts/user_profile.html"
    model = User
    fields = ['first_name', 'last_name']
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        context['nav_user_profile'] = True
        return context


class PasswordChangeView(TemplateView):
    template_name = "registration/password_change.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(*args, **kwargs)
        context['nav_change_password'] = True
        return context
