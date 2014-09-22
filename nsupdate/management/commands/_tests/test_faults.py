"""
Tests for faults command.
"""

from conftest import TEST_HOST

from django.core import management
from nsupdate.main.models import Host


def test_faults_reset():
    # trigger execution of all code for coverage, test resetting
    # set flags and counters
    hostname = TEST_HOST.host
    h = Host.objects.get(name=hostname)
    h.client_faults = 1
    h.server_faults = 1
    h.available = False
    h.abuse = True
    h.abuse_blocked = True
    h.save()
    # reset counters / flags
    management.call_command('faults',
                            show_server=True, show_client=True,
                            reset_server=True, reset_client=True,
                            reset_abuse=True, reset_abuse_blocked=True,
                            reset_available=True)
    # check if the resetting worked
    h = Host.objects.get(name=hostname)
    assert h.client_faults == 0
    assert h.server_faults == 0
    assert h.available is True
    assert h.abuse is False
    assert h.abuse_blocked is False


def test_faults_no_abuse():
    hostname = TEST_HOST.host
    h = Host.objects.get(name=hostname)
    h.client_faults = 10  # below threshold
    h.abuse = False
    h.save()
    # flag abusive hosts
    management.call_command('faults', flag_abuse=23)
    # check if it did not get flagged
    h = Host.objects.get(name=hostname)
    assert h.client_faults == 10
    assert h.abuse is False


def test_faults_abuse():
    hostname = TEST_HOST.host
    h = Host.objects.get(name=hostname)
    h.client_faults = 42  # above threshold
    h.abuse = False
    h.save()
    # flag abusive hosts
    management.call_command('faults', flag_abuse=23)
    # check if it did get flagged
    h = Host.objects.get(name=hostname)
    assert h.client_faults == 0
    assert h.abuse is True
