"""
Tests for api package.
"""

from django.core.urlresolvers import reverse

from nsupdate.main.dnstools import query_ns
from nsupdate.main.models import Domain


TEST_HOST = "test.nsupdate.info"
TEST_HOST2 = "test2.nsupdate.info"
TEST_SECRET = "secret"

USERNAME = 'test'
PASSWORD = 'pass'

BASEDOMAIN = "nsupdate.info"
HOSTNAME = 'nsupdate-ddns-client-unittest.' + BASEDOMAIN


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


def test_nic_update_authorized_nonexistent_host(client):
    response = client.get(reverse('nic_update') + '?hostname=nonexistent.nsupdate.info',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we must not get this updated, it doesn't exist in the database:
    assert response.content == 'nohost'


def test_nic_update_authorized_foreign_host(client):
    response = client.get(reverse('nic_update') + '?hostname=%s' % TEST_HOST2,
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we must not get this updated, this is a host of some other user!
    assert response.content == 'nohost'


def test_nic_update_authorized_not_fqdn_hostname(client):
    response = client.get(reverse('nic_update') + '?hostname=test',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == 'notfqdn'


def test_nic_update_authorized_not_fqdn_username(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header('test', TEST_SECRET))
    assert response.status_code == 200
    assert response.content == 'notfqdn'


def test_nic_update_authorized(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be one of them:
    assert response.content.startswith('good ') or response.content.startswith('nochg ')


def test_nic_update_authorized_ns_unavailable(client):
    d = Domain.objects.get(domain=TEST_HOST)
    d.available = False  # simulate DNS unavailability
    d.save()
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == 'dnserr'


def test_nic_update_authorized_myip(client):
    response = client.get(reverse('nic_update') + '?myip=4.3.2.1',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be the ip from myip=...:
    assert response.content in ['good 4.3.2.1', 'nochg 4.3.2.1']
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == 'good 1.2.3.4'
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be nochg (was same IP)
    assert response.content == 'nochg 1.2.3.4'


def test_nic_update_authorized_update_other_services(client):
    response = client.get(reverse('nic_update') + '?myip=4.3.2.1',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be the ip from myip=...:
    assert response.content in ['good 4.3.2.1', 'nochg 4.3.2.1']
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == 'good 1.2.3.4'
    # now check if it updated the other service also:
    assert query_ns(HOSTNAME, 'A') == '1.2.3.4'
    response = client.get(reverse('nic_update') + '?myip=2.3.4.5',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == 'good 2.3.4.5'
    # now check if it updated the other service also:
    assert query_ns(HOSTNAME, 'A') == '2.3.4.5'


def test_nic_update_authorized_badagent(client, settings):
    settings.BAD_AGENTS = ['foo', 'bad_agent', 'bar', ]
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET),
                          HTTP_USER_AGENT='bad_agent')
    assert response.status_code == 200
    assert response.content == 'badagent'


def test_nic_update_session_nosession(client):
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 302  # redirects to login view


def test_nic_update_session_no_hostname(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 200
    assert response.content == "nohost"  # we did not tell which host


def test_nic_update_session(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s' % (TEST_HOST, ))
    assert response.status_code == 200
    assert response.content.startswith('good ') or response.content.startswith('nochg ')


def test_nic_update_session_myip(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '1.2.3.4'))
    assert response.status_code == 200
    assert response.content.startswith('good 1.2.3.4') or response.content.startswith('nochg 1.2.3.4')


def test_nic_update_session_foreign_host(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s' % TEST_HOST2)
    assert response.status_code == 200
    # we must not get this updated, this is a host of some other user!
    assert response.content == "nohost"


def test_detect_ip_invalid_session(client):
    response = client.get(reverse('detectip', args=('invalid_session_id', )))
    assert response.status_code == 204


def test_ajax_get_ips(client):
    response = client.get(reverse('ajax_get_ips'))
    assert response.status_code == 200
