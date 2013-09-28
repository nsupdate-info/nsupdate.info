from django.conf.urls import patterns, include, url
from main.views import (
    HomeView, OverviewView, HostView,
)
from api.views import (
    MyIpView, UpdateIpView, NicUpdateView
)

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^overview/$', OverviewView, name='overview'),
    url(r'^host/(?P<pk>\w+)$', HostView, name='host-view'),
    url(r'^myip$', MyIpView),
    url(r'^updateip$', UpdateIpView),
    url(r'^nic/update$', NicUpdateView),
)
