# -*- coding: utf-8 -*-
from django.urls import re_path
from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = (
    # login and logout URLs
    re_path(r'^login/$', LoginView.as_view(template_name='login.html'), name='login'),
    # Alternatively, use the logout view with the 'logout.html' template
    re_path(r'^logout/$', LogoutView.as_view(), name='logout'),

    # Password reset URLs
    re_path(r'^password_reset/$',
            PasswordResetView.as_view(template_name='password_reset.html'),
            name='password_reset'),
    re_path(r'^password_reset_done/$',
            PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
            name='password_reset_done'),
    re_path(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
            PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
            name='password_reset_confirm'),
    re_path(r'^password_reset_complete/$',
            PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
            name='password_reset_complete'),
)
