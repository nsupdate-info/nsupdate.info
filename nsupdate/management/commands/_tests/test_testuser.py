"""
Tests for testuser command.
"""

from django.conf import settings
from django.core import management
from django.contrib.auth import get_user_model


def test_testuser():
    user_model = get_user_model()
    # the test user is already there, created by conftest.py
    # change its email address, so we can notice whether the command worked
    u = user_model.objects.get(username='test')
    u.email = "invalid-for-testcase@example.org"
    u.save()
    # now re-initialize the test user via managment command:
    management.call_command('testuser')
    # check if the test user is there, with default email
    u = user_model.objects.get(username='test')
    assert u.email == settings.DEFAULT_FROM_EMAIL
