from django.conf.urls import patterns, include, url
from main.views import (
    HomeView, MyIpView, OverviewView
)

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^overview/', OverviewView.as_view(), name="overview"),
    url(r'^myip/', MyIpView),
)
