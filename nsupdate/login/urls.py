# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = (
    # login and logout url
    url(r'^login/$', LoginView.as_view(template_name='login.html'), name='login'),
    # or use logout with template 'logout.html'
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    # password reset urls
    url(r'^password_reset/$',
        PasswordResetView.as_view(template_name='password_reset.html'),
        name='password_reset'),
    url(r'^password_reset_done/$',
        PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^password_reset_complete/$',
        PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
)
