"""
Tests for api package.
"""

import pytest

from django.core.urlresolvers import reverse


TEST_HOST = "test.nsupdate.info"
TEST_SECRET = "secret"

USERNAME = 'test'
PASSWORD = 'pass'


def test_myip(client):
    response = client.get(reverse('myip'))
    assert response.status_code == 200
    assert response.content in ['127.0.0.1', '::1']


def test_nic_update_noauth(client):
    response = client.get(reverse('nic_update'))
    assert response.status_code == 401
    assert response.content == "badauth"


def make_basic_auth_header(username, password):
    import base64
    return "Basic " + base64.b64encode("%s:%s" % (username, password))


def test_nic_update_badauth(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, "wrong"))
    assert response.status_code == 401
    assert response.content == "badauth"


def test_nic_update_authorized(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be one of them:
    assert response.content.startswith('good ') or response.content.startswith('nochg ')


def test_nic_update_session_nosession(client):
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 302  # redirects to login view


def test_nic_update_session(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 200
    assert response.content == "nohost"  # we did not tell which host
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '1.2.3.4'))
    assert response.status_code == 200
    assert response.content.startswith('good ') or response.content.startswith('nochg ')


def test_detect_ip(client):
    response = client.get(reverse('detectip', args=('invalid_session_id', )))
    assert response.status_code == 204


def test_ajax_get_ips(client):
    response = client.get(reverse('ajax_get_ips'))
    assert response.status_code == 200
