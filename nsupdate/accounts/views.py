# -*- coding: utf-8 -*-

from django.views.generic import UpdateView, TemplateView
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from .forms import UserProfileForm


class UserProfileView(UpdateView):
    template_name = "accounts/user_profile.html"
    model = get_user_model()
    fields = ['first_name', 'last_name', 'email']
    form_class = UserProfileForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        context['nav_user_profile'] = True
        return context


class DeleteUserView(TemplateView):
    template_name = "accounts/delete_user.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteUserView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteUserView, self).get_context_data(*args, **kwargs)
        context['nav_user_profile'] = True
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            # if admin set the user to inactive, the user may not delete his own account
            # this is important for abuse handling: abusers shall not be able to delete
            # their account (and all hosts/domains) and then just recreate them without
            # abuse_blocked flags set by the admin.
            user.delete()
            logout(request)
            return redirect(reverse('home'))
        else:
            return redirect(reverse('account_delete'))
