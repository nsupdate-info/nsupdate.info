"""
Tests for accounts views module.
"""

from __future__ import print_function

import pytest

from django.core.urlresolvers import reverse


USERNAME = 'test'
PASSWORD = 'pass'


def test_views_anon(client):
    for view, kwargs, status_code in [
        # stuff that requires being logged-in redirects to the login view:
        ('account_profile', dict(), 302),
        ('account_delete', dict(), 302),
    ]:
        print("%s, %s, %s" % (view, kwargs, status_code))
        response = client.get(reverse(view, kwargs=kwargs))
        assert response.status_code == status_code


def test_views_logged_in(client):
    client.login(username=USERNAME, password=PASSWORD)
    for view, kwargs, status_code in [
        ('account_profile', dict(), 200),
        ('account_delete', dict(), 200),
    ]:
        print("%s, %s, %s" % (view, kwargs, status_code))
        response = client.get(reverse(view, kwargs=kwargs))
        assert response.status_code == status_code
