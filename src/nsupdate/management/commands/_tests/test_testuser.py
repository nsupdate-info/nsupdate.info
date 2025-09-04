"""
Tests for the testuser command.
"""

from django.conf import settings
from django.core import management
from django.contrib.auth import get_user_model


def test_testuser():
    user_model = get_user_model()
    # The test user is already there, created by conftest.py.
    # Change its email address so we can notice whether the command worked.
    u = user_model.objects.get(username='test')
    u.email = "invalid-for-testcase@example.org"
    u.save()
    # Now re-initialize the test user via management command:
    management.call_command('testuser')
    # Check whether the test user is there with the default email.
    u = user_model.objects.get(username='test')
    assert u.email == settings.DEFAULT_FROM_EMAIL
