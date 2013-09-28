from django.conf.urls import patterns, include, url
from main.views import (
    HomeView, OverviewView, HostView, HostDeleteView,
)
from api.views import (
    MyIpView, UpdateIpView, NicUpdateView
)

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^host/(?P<pk>\d+)/$', HostView.as_view(), name='host_view'),
    url(r'^host/(?P<pk>\d+)/delete/$', HostDeleteView.as_view(), name='host_delete'),
    url(r'^myip$', MyIpView),
    url(r'^updateip$', UpdateIpView),
    url(r'^nic/update$', NicUpdateView),
)
