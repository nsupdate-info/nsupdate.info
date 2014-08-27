"""
Tests for api package.
"""

from django.core.urlresolvers import reverse

from nsupdate.main.dnstools import query_ns
from nsupdate.main.models import Domain

from conftest import TESTDOMAIN, TEST_HOST, TEST_HOST2, TEST_SECRET, TEST_SECRET2

USERNAME = 'test'
PASSWORD = 'pass'

BASEDOMAIN = "nsupdate.info"
HOSTNAME = 'nsupdate-ddns-client-unittest.' + BASEDOMAIN


def test_myip(client):
    response = client.get(reverse('myip'))
    assert response.status_code == 200
    assert response.content in [b'127.0.0.1', b'::1']


def test_nic_update_noauth(client):
    response = client.get(reverse('nic_update'))
    assert response.status_code == 401
    assert response.content == b'badauth'


def make_basic_auth_header(username, password):
    import base64
    return b'Basic ' + base64.b64encode((username + ':' + password).encode('utf-8'))


def test_nic_update_badauth(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, "wrong"))
    assert response.status_code == 401
    assert response.content == b'badauth'


def test_nic_update_authorized_nonexistent_host(client):
    response = client.get(reverse('nic_update') + '?hostname=nonexistent.nsupdate.info',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we must not get this updated, it doesn't exist in the database:
    assert response.content == b'nohost'


def test_nic_update_authorized_foreign_host(client):
    response = client.get(reverse('nic_update') + '?hostname=%s' % TEST_HOST2,
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we must not get this updated, this is a host of some other user!
    assert response.content == b'nohost'


def test_nic_update_authorized_not_fqdn_hostname(client):
    response = client.get(reverse('nic_update') + '?hostname=test',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == b'notfqdn'


def test_nic_update_authorized_not_fqdn_username(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header('test', TEST_SECRET))
    assert response.status_code == 200
    assert response.content == b'notfqdn'


def test_nic_update_authorized(client):
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be one of them:
    content = response.content.decode('utf-8')
    assert content.startswith('good ') or content.startswith('nochg ')


def test_nic_update_authorized_ns_unavailable(client):
    d = Domain.objects.get(domain=TESTDOMAIN)
    d.available = False  # simulate DNS unavailability
    d.save()
    # prepare: we must make sure the real test is not a nochg update
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # now do the real test: ip changed, but we can't update DNS as it is unavailable
    response = client.get(reverse('nic_update') + '?myip=4.3.2.1',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == b'dnserr'


def test_nic_update_authorized_myip(client):
    response = client.get(reverse('nic_update') + '?myip=4.3.2.1',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be the ip from myip=...:
    assert response.content in [b'good 4.3.2.1', b'nochg 4.3.2.1']
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == b'good 1.2.3.4'
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be nochg (was same IP)
    assert response.content == b'nochg 1.2.3.4'


def test_nic_update_authorized_update_other_services(client):
    response = client.get(reverse('nic_update') + '?myip=4.3.2.1',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # we don't care whether it is nochg or good, but should be the ip from myip=...:
    assert response.content in [b'good 4.3.2.1', b'nochg 4.3.2.1']
    response = client.get(reverse('nic_update') + '?myip=1.2.3.4',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == b'good 1.2.3.4'
    # now check if it updated the other service also:
    assert query_ns(HOSTNAME, 'A') == '1.2.3.4'
    response = client.get(reverse('nic_update') + '?myip=2.3.4.5',
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    # must be good (was different IP)
    assert response.content == b'good 2.3.4.5'
    # now check if it updated the other service also:
    assert query_ns(HOSTNAME, 'A') == '2.3.4.5'


def test_nic_update_authorized_badagent(client, settings):
    settings.BAD_AGENTS = ['foo', 'bad_agent', 'bar', ]
    response = client.get(reverse('nic_update'),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET),
                          HTTP_USER_AGENT='bad_agent')
    assert response.status_code == 200
    assert response.content == b'badagent'


def test_nic_update_session_nosession(client):
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 302  # redirects to login view


def test_nic_update_session_no_hostname(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized'))
    assert response.status_code == 200
    assert response.content == b'nohost'  # we did not tell which host


def test_nic_update_session(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s' % (TEST_HOST, ))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert content.startswith('good ') or content.startswith('nochg ')


def test_nic_update_session_myip(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '1.2.3.4'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert content.startswith('good 1.2.3.4') or content.startswith('nochg 1.2.3.4')


def test_nic_update_session_foreign_host(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s' % TEST_HOST2)
    assert response.status_code == 200
    # we must not get this updated, this is a host of some other user!
    assert response.content == b'nohost'


def test_nic_delete_authorized(client):
    response = client.get(reverse('nic_update') + '?myip=%s' % ('1.2.3.4', ),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    response = client.get(reverse('nic_update') + '?myip=%s' % ('::1', ),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    response = client.get(reverse('nic_delete') + '?myip=%s' % ('0.0.0.0', ),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == b'deleted A'
    response = client.get(reverse('nic_delete') + '?myip=%s' % ('::', ),
                          HTTP_AUTHORIZATION=make_basic_auth_header(TEST_HOST, TEST_SECRET))
    assert response.status_code == 200
    assert response.content == b'deleted AAAA'


def test_nic_delete_session(client):
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '1.2.3.4'))
    assert response.status_code == 200
    response = client.get(reverse('nic_update_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '::1'))
    assert response.status_code == 200
    response = client.get(reverse('nic_delete_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '0.0.0.0'))
    assert response.status_code == 200
    assert response.content == b'deleted A'
    response = client.get(reverse('nic_delete_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '::'))
    assert response.status_code == 200
    assert response.content == b'deleted AAAA'


def test_detect_ip_invalid_session(client):
    response = client.get(reverse('detectip', args=('invalid_session_id', )))
    assert response.status_code == 204


def test_ajax_get_ips(client):
    response = client.get(reverse('ajax_get_ips'))
    assert response.status_code == 200
