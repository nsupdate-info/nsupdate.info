# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from .forms import UserForm, UserProfileForm
from .models import UserProfile


class UserProfileView(TemplateView):
    template_name = "accounts/user_profile.html"

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
