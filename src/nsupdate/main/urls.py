"""
main app url dispatching
"""

from django.conf.urls import url

from .views import (
    HomeView, OverviewView, HostView, AddHostView, DeleteHostView, AboutView, GenerateSecretView, GenerateNSSecretView,
    RobotsTxtView, DomainView, AddDomainView, DeleteDomainView, StatusView, JsUpdateView,
    UpdaterHostConfigOverviewView, UpdaterHostConfigView, DeleteUpdaterHostConfigView,
    RelatedHostOverviewView, RelatedHostView, AddRelatedHostView, DeleteRelatedHostView, CustomTemplateView)
from ..api.views import (
    myip_view, DetectIpView, AjaxGetIps, NicUpdateView, AuthorizedNicUpdateView,
    NicDeleteView, AuthorizedNicDeleteView)


urlpatterns = (
    # interactive web ui
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^custom/(?P<template>[\w.]+)$', CustomTemplateView.as_view(), name="custom"),
    url(r'^update$', JsUpdateView.as_view(), name='update'),
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^status/$', StatusView.as_view(), name='status'),
    url(r'^generate_secret/(?P<pk>\d+)/$', GenerateSecretView.as_view(), name='generate_secret_view'),
    url(r'^generate_ns_secret/(?P<pk>\d+)/$', GenerateNSSecretView.as_view(), name='generate_ns_secret_view'),
    url(r'^host/(?P<pk>\d+)/$', HostView.as_view(), name='host_view'),
    url(r'^host/add/$', AddHostView.as_view(), name='add_host'),
    url(r'^host/(?P<pk>\d+)/delete/$', DeleteHostView.as_view(), name='delete_host'),
    url(r'^host/(?P<mpk>\d+)/related/$', RelatedHostOverviewView.as_view(), name='related_host_overview'),
    url(r'^host/(?P<mpk>\d+)/related/(?P<pk>\d+)/$', RelatedHostView.as_view(), name='related_host_view'),
    url(r'^host/(?P<mpk>\d+)/related/add/$', AddRelatedHostView.as_view(), name='add_related_host'),
    url(r'^host/(?P<mpk>\d+)/related/(?P<pk>\d+)/delete/$', DeleteRelatedHostView.as_view(),
        name='delete_related_host'),
    url(r'^domain/(?P<pk>\d+)/$', DomainView.as_view(), name='domain_view'),
    url(r'^domain/add/$', AddDomainView.as_view(), name='add_domain'),
    url(r'^domain/(?P<pk>\d+)/delete/$', DeleteDomainView.as_view(), name='delete_domain'),
    url(r'^updater_hostconfig_overview/(?P<pk>\d+)/$', UpdaterHostConfigOverviewView.as_view(),
        name='updater_hostconfig_overview'),
    url(r'^updater_hostconfig/(?P<pk>\d+)/$', UpdaterHostConfigView.as_view(), name='updater_hostconfig'),
    url(r'^updater_hostconfig/(?P<pk>\d+)/delete/$', DeleteUpdaterHostConfigView.as_view(),
        name='delete_updater_hostconfig'),
    # internal use by the web ui
    url(r'^detectip/(?P<sessionid>\w+)/$', DetectIpView.as_view(), name='detectip'),
    url(r'^ajax_get_ips/$', AjaxGetIps.as_view(), name="ajax_get_ips"),
    url(r'^nic/update_authorized$', AuthorizedNicUpdateView.as_view(), name='nic_update_authorized'),
    url(r'^nic/delete_authorized$', AuthorizedNicDeleteView.as_view(), name='nic_delete_authorized'),
    # api (for update clients)
    url(r'^myip$', myip_view, name='myip'),
    url(r'^nic/update$', NicUpdateView.as_view(), name='nic_update'),
    url(r'^nic/delete$', NicDeleteView.as_view(), name='nic_delete'),  # api extension
    # for bots
    url(r'^robots.txt$', RobotsTxtView.as_view(), name='robots'),
)
