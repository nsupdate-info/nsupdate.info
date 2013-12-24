# -*- coding: utf-8 -*-

from django.views.generic import UpdateView
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from .forms import UserProfileForm


class UserProfileView(UpdateView):
    template_name = "accounts/user_profile.html"
    model = get_user_model()
    fields = ['first_name', 'last_name', 'email']
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        context['nav_user_profile'] = True
        return context
