from django.conf.urls import patterns, include, url
from main.views import HomeView, OverviewView, HostView, DeleteHostView
from api.views import MyIpView, DetectIpView, NicUpdateView, AuthorizedNicUpdateView


urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^host/(?P<pk>\d+)/$', HostView.as_view(), name='host_view'),
    url(r'^host/(?P<pk>\d+)/delete/$', DeleteHostView.as_view(), name='delete_host'),
    url(r'^myip$', MyIpView),
    url(r'^detectip/$', DetectIpView),
    url(r'^nic/update$', NicUpdateView),
    url(r'^nic/update_authorized$', AuthorizedNicUpdateView, name='nic_update_authorized'),
)
