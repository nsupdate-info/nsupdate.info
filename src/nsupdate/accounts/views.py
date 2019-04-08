# -*- coding: utf-8 -*-

from django.views.generic import TemplateView, FormView
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import update_session_auth_hash

from .forms import UserForm, UserProfileForm
from .models import UserProfile


class UserProfileView(TemplateView):
    template_name = "accounts/user_settings_profile.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        profileform = UserProfileForm(instance=profile)
        userform = UserForm(instance=request.user)
        context = dict(userform=userform, profileform=profileform)
        context['nav_user_profile'] = True
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        profileform = UserProfileForm(data=request.POST, instance=profile)
        userform = UserForm(data=request.POST, instance=request.user)
        if userform.is_valid() and profileform.is_valid():
            u = userform.save()
            p = profileform.save(commit=False)
            p.user = u
            p.save()
            return redirect(reverse('account_profile'))
        else:
            context = dict(userform=userform, profileform=profileform)
            context['nav_user_profile'] = True
            return self.render_to_response(context)


class UserChangePasswordView(FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('account_settings')
    template_name = 'accounts/user_settings_account.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserChangePasswordView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserChangePasswordView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one if
        # django.contrib.auth.middleware.SessionAuthenticationMiddleware
        # is enabled.
        update_session_auth_hash(self.request, form.user)
        messages.add_message(self.request, messages.SUCCESS, _('Your password was changed!'))
        return super(UserChangePasswordView, self).form_valid(form)


class DeleteUserView(TemplateView):
    template_name = "accounts/delete_user.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteUserView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteUserView, self).get_context_data(**kwargs)
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
