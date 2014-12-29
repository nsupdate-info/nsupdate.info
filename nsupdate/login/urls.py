# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    # login and logout url
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    # or use 'django.contrib.auth.views.logout' with template 'logout.html
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    # password reset urls
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset',
        {'template_name': 'password_reset.html'}, name='password_reset'),
    url(r'^password_reset_done/$', 'django.contrib.auth.views.password_reset_done',
        {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),
)
