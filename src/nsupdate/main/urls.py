"""
Main application URL routing.
"""

from django.urls import re_path

from .views import (
    HomeView, OverviewView, HostView, AddHostView, DeleteHostView, AboutView, GenerateSecretView, GenerateNSSecretView,
    RobotsTxtView, DomainView, AddDomainView, DeleteDomainView, StatusView, JsUpdateView,
    UpdaterHostConfigOverviewView, UpdaterHostConfigView, DeleteUpdaterHostConfigView,
    RelatedHostOverviewView, RelatedHostView, AddRelatedHostView, DeleteRelatedHostView, CustomTemplateView)
from ..api.views import (
    myip_view, DetectIpView, AjaxGetIps, NicUpdateView, AuthorizedNicUpdateView,
    NicDeleteView, AuthorizedNicDeleteView)


urlpatterns = (
    # Interactive web UI
    re_path(r'^$', HomeView.as_view(), name="home"),
    re_path(r'^about/$', AboutView.as_view(), name="about"),
    re_path(r'^custom/(?P<template>[\w.]+)$', CustomTemplateView.as_view(), name="custom"),
    re_path(r'^update$', JsUpdateView.as_view(), name='update'),
    re_path(r'^overview/$', OverviewView.as_view(), name='overview'),
    re_path(r'^status/$', StatusView.as_view(), name='status'),
    re_path(r'^generate_secret/(?P<pk>\d+)/$', GenerateSecretView.as_view(), name='generate_secret_view'),
    re_path(r'^generate_ns_secret/(?P<pk>\d+)/$', GenerateNSSecretView.as_view(), name='generate_ns_secret_view'),
    re_path(r'^host/(?P<pk>\d+)/$', HostView.as_view(), name='host_view'),
    re_path(r'^host/add/$', AddHostView.as_view(), name='add_host'),
    re_path(r'^host/(?P<pk>\d+)/delete/$', DeleteHostView.as_view(), name='delete_host'),
    re_path(r'^host/(?P<mpk>\d+)/related/$', RelatedHostOverviewView.as_view(), name='related_host_overview'),
    re_path(r'^host/(?P<mpk>\d+)/related/(?P<pk>\d+)/$', RelatedHostView.as_view(), name='related_host_view'),
    re_path(r'^host/(?P<mpk>\d+)/related/add/$', AddRelatedHostView.as_view(), name='add_related_host'),
    re_path(r'^host/(?P<mpk>\d+)/related/(?P<pk>\d+)/delete/$', DeleteRelatedHostView.as_view(),
            name='delete_related_host'),
    re_path(r'^domain/(?P<pk>\d+)/$', DomainView.as_view(), name='domain_view'),
    re_path(r'^domain/add/$', AddDomainView.as_view(), name='add_domain'),
    re_path(r'^domain/(?P<pk>\d+)/delete/$', DeleteDomainView.as_view(), name='delete_domain'),
    re_path(r'^updater_hostconfig_overview/(?P<pk>\d+)/$', UpdaterHostConfigOverviewView.as_view(),
            name='updater_hostconfig_overview'),
    re_path(r'^updater_hostconfig/(?P<pk>\d+)/$', UpdaterHostConfigView.as_view(), name='updater_hostconfig'),
    re_path(r'^updater_hostconfig/(?P<pk>\d+)/delete/$', DeleteUpdaterHostConfigView.as_view(),
            name='delete_updater_hostconfig'),
    # Internal use by the web UI
    re_path(r'^detectip/(?P<sessionid>\w+)/$', DetectIpView.as_view(), name='detectip'),
    re_path(r'^ajax_get_ips/$', AjaxGetIps.as_view(), name="ajax_get_ips"),
    re_path(r'^nic/update_authorized$', AuthorizedNicUpdateView.as_view(), name='nic_update_authorized'),
    re_path(r'^nic/delete_authorized$', AuthorizedNicDeleteView.as_view(), name='nic_delete_authorized'),
    # API (for update clients)
    re_path(r'^myip$', myip_view, name='myip'),
    re_path(r'^nic/update$', NicUpdateView.as_view(), name='nic_update'),
    re_path(r'^nic/delete$', NicDeleteView.as_view(), name='nic_delete'),  # API extension
    # For bots
    re_path(r'^robots.txt$', RobotsTxtView.as_view(), name='robots'),
)
