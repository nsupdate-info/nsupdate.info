# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete

urlpatterns = (
    # login and logout url
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    # or use logout with template 'logout.html'
    url(r'^logout/$', logout, name='logout'),

    # password reset urls
    url(r'^password_reset/$', password_reset, {'template_name': 'password_reset.html'},
        name='password_reset'),
    url(r'^password_reset_done/$', password_reset_done,
        {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm, {'template_name': 'password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^password_reset_complete/$', password_reset_complete,
        {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),
)
