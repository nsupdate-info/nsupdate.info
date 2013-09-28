from django.conf.urls import patterns, include, url
from main.views import (
    HomeView, MyIpView, OverviewView, UserProfileView
)
from django.contrib.auth.views import password_change

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^overview/', OverviewView.as_view(), name="overview"),
    url(r'^myip/', MyIpView),
    url(r'^account/profile/', UserProfileView.as_view(), name="account_profile"),
    url(r'^account/change_pw/', password_change, {
            'template_name': 'registration/password_change.html',
            'post_change_redirect': '/account/profile/',
        },
        name="password_change"),
)
