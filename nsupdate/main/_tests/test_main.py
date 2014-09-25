"""
Tests for main views module.
"""

from __future__ import print_function

import pytest

from django.core.urlresolvers import reverse


USERNAME = 'test'
PASSWORD = 'pass'


def test_views_anon(client):
    for view, kwargs, status_code in [
        ('home', dict(), 200),
        ('about', dict(), 200),
        ('robots', dict(), 200),
        # stuff that requires being logged-in redirects to the login view:
        ('status', dict(), 302),
        ('overview', dict(), 302),
        ('generate_secret_view', dict(pk=1), 302),
        ('generate_ns_secret_view', dict(pk=1), 302),
        ('host_view', dict(pk=1), 302),
        ('add_host', dict(), 302),
        ('delete_host', dict(pk=1), 302),
        ('related_host_view', dict(mpk=1, pk=1), 302),
        ('add_related_host', dict(mpk=1), 302),
        ('delete_related_host', dict(mpk=1, pk=1), 302),
        ('domain_view', dict(pk=1), 302),
        ('add_domain', dict(), 302),
        ('delete_domain', dict(pk=1), 302),
        ('updater_hostconfig_overview', dict(pk=1), 302),
        ('updater_hostconfig', dict(pk=1), 302),
        ('delete_updater_hostconfig', dict(pk=1), 302),
        # interactive updater shows http basic auth popup
        ('update', dict(), 401),
    ]:
        print("%s, %s, %s" % (view, kwargs, status_code))
        response = client.get(reverse(view, kwargs=kwargs))
        assert response.status_code == status_code


def test_views_logged_in(client):
    client.login(username=USERNAME, password=PASSWORD)
    for view, kwargs, status_code in [
        ('home', dict(), 200),
        ('about', dict(), 200),
        ('robots', dict(), 200),
        ('status', dict(), 200),
        ('overview', dict(), 200),
        ('generate_secret_view', dict(pk=1), 200),
        ('generate_ns_secret_view', dict(pk=1), 200),
        ('host_view', dict(pk=1), 200),
        ('add_host', dict(), 200),
        ('delete_host', dict(pk=1), 200),
        ('related_host_view', dict(mpk=1, pk=1), 200),
        ('add_related_host', dict(mpk=1), 200),
        ('delete_related_host', dict(mpk=1, pk=1), 200),
        ('domain_view', dict(pk=1), 200),
        ('add_domain', dict(), 200),
        ('delete_domain', dict(pk=1), 200),
        ('updater_hostconfig_overview', dict(pk=1), 200),
        ('updater_hostconfig', dict(pk=1), 200),
        ('delete_updater_hostconfig', dict(pk=1), 200),
        ('update', dict(), 401),
    ]:
        print("%s, %s, %s" % (view, kwargs, status_code))
        response = client.get(reverse(view, kwargs=kwargs))
        assert response.status_code == status_code
