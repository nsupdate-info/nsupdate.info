# -*- coding: utf-8 -*-
from django.views.generic import TemplateView


class UserProfileView(TemplateView):
    template_name = "accounts/user_profile.html"

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

