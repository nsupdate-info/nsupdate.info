import base64
from http import HTTPStatus
from random import randint

import dns
import pytest
from django.urls import reverse

from nsupdate.conftest import TEST_HOST, RELATED_HOST_NAME, TEST_HOST_RELATED, USERNAME, PASSWORD
from nsupdate.main.dnstools import query_ns, FQDN
from nsupdate.main.models import Host, RelatedHost


def make_basic_auth_header(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {token}"


def test_add_related_host_updates_dns(client):
    # first set an ip for the main host
    v4 = '1.2.3.4'
    v6 = '2001:cafe::1'
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + f'?hostname={TEST_HOST}&myip={v4},{v6}')
    assert response.status_code == HTTPStatus.OK

    # then add a related host
    related_host_name = 'related%da' % randint(1, 1000000)
    related_host_fqdn = FQDN(related_host_name + '.' + TEST_HOST.host, TEST_HOST.domain)
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    response = client.post(reverse('add_related_host', args=[main_host.id]), data={
        'name': related_host_name,
        'available': 1,
        'interface_id_ipv4': '0.0.0.1',
        'interface_id_ipv6': '::1',
    })
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['location'] == f'/host/{main_host.id}/related/'

    # expect the related host to have an appropriate ip
    assert query_ns(related_host_fqdn, 'A') == '1.2.3.1'  # 1.2.3.4/29 + 0.0.0.1
    assert query_ns(related_host_fqdn, 'AAAA') == '2001:cafe::1'  # 2001:cafe::1/64 + ::1


def test_delete_related_host_updates_dns(client):
    # main host and related host are already set up by fixtures
    # now set an ip for the main host
    v4 = '1.2.3.4'
    v6 = '2001:cafe::1'
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + f'?hostname={TEST_HOST}&myip={v4},{v6}')
    assert response.status_code == HTTPStatus.OK

    # expect the related host to have an appropriate ip
    assert query_ns(TEST_HOST_RELATED, 'A') == '1.2.3.1'  # 1.2.3.4/29 + 0.0.0.1
    assert query_ns(TEST_HOST_RELATED, 'AAAA') == '2001:cafe::1'  # 2001:cafe::1/64 + ::1

    # delete the related host
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    response = client.post(reverse('delete_related_host', args=[main_host.id, related_host.id]))
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers['location'] == f'/host/{main_host.id}/related/'

    # expect the related host to not exist anymore
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'A') is None
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'AAAA') is None


def test_update_related_host_interface_id_when_main_host_has_ip_updates_dns(client):
    # main host and related host are already set up by fixtures
    # now set an ip for the main host
    v4 = '1.2.3.4'
    v6 = '2001:cafe::1'
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + f'?hostname={TEST_HOST}&myip={v4},{v6}')
    assert response.status_code == HTTPStatus.OK

    # expect the related host to have an appropriate ip
    assert query_ns(TEST_HOST_RELATED, 'A') == '1.2.3.1'  # 1.2.3.4/29 + 0.0.0.1
    assert query_ns(TEST_HOST_RELATED, 'AAAA') == '2001:cafe::1'  # 2001:cafe::1/64 + ::1

    # now update the related host's interface ids
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'name': RELATED_HOST_NAME,
        'available': 1,
        'interface_id_ipv4': '0.0.0.2',
        'interface_id_ipv6': '::2',
    })
    assert response.status_code == HTTPStatus.FOUND

    # expect the related host to have an appropriate ip
    assert query_ns(TEST_HOST_RELATED, 'A') == '1.2.3.2'  # 1.2.3.4/29 + 0.0.0.2
    assert query_ns(TEST_HOST_RELATED, 'AAAA') == '2001:cafe::2'  # 2001:cafe::1/64 + ::2


def test_update_related_host_interface_id_when_main_host_has_no_ip_succeeds(client):
    # main host and related host are already set up by fixtures

    # delete ip from main-host
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_delete_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '0.0.0.0'))
    assert response.status_code == 200
    response = client.get(reverse('nic_delete_authorized') + '?hostname=%s&myip=%s' % (TEST_HOST, '::'))
    assert response.status_code == 200

    # expect the related host to not exist
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'A') is None
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'AAAA') is None

    # update the related host's interface id
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'name': RELATED_HOST_NAME,
        'available': 1,
        'interface_id_ipv4': '0.0.0.2',
        'interface_id_ipv6': '::2',
    })

    # expect to succeed anyway
    assert response.status_code == HTTPStatus.FOUND

    # expect the related host to still not exist
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'A') is None
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'AAAA') is None


def test_delete_related_host_interface_id_updates_dns(client):
    # main host and related host are already set up by fixtures
    # now set an ip for the main host
    v4 = '1.2.3.4'
    v6 = '2001:cafe::1'
    client.login(username=USERNAME, password=PASSWORD)
    response = client.get(reverse('nic_update_authorized') + f'?hostname={TEST_HOST}&myip={v4},{v6}')
    assert response.status_code == HTTPStatus.OK

    # expect the related host to have an appropriate ip
    assert query_ns(TEST_HOST_RELATED, 'A') == '1.2.3.1'  # 1.2.3.4/29 + 0.0.0.1
    assert query_ns(TEST_HOST_RELATED, 'AAAA') == '2001:cafe::1'  # 2001:cafe::1/64 + ::1

    # remove related host v4 interface id
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'name': RELATED_HOST_NAME,
        'available': 1,
        'interface_id_ipv4': '',
        'interface_id_ipv6': '::1',
    })
    assert response.status_code == HTTPStatus.FOUND

    # expect the related host to have no v4 address anymore
    with pytest.raises(dns.resolver.NoAnswer):
        assert query_ns(TEST_HOST_RELATED, 'A') is None
    assert query_ns(TEST_HOST_RELATED, 'AAAA') == '2001:cafe::1'

    # remove the v6 interface id, set ipv4
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'name': RELATED_HOST_NAME,
        'available': 1,
        'interface_id_ipv4': '0.0.0.1',
        'interface_id_ipv6': '',

    })
    assert response.status_code == HTTPStatus.FOUND

    # expect the related host to have no v6 address anymore
    assert query_ns(TEST_HOST_RELATED, 'A') == '1.2.3.1'
    with pytest.raises(dns.resolver.NoAnswer):
        assert query_ns(TEST_HOST_RELATED, 'AAAA') is None

    # remove both interface ids
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'name': RELATED_HOST_NAME,
        'available': 1,
        'interface_id_ipv4': '',
        'interface_id_ipv6': '',

    })
    assert response.status_code == HTTPStatus.FOUND

    # expect the domain to be gone
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'A') is None
    with pytest.raises(dns.resolver.NXDOMAIN):
        assert query_ns(TEST_HOST_RELATED, 'AAAA') is None


invalid_interface_ids_ipv4 = [
    ('1'),
    ('1.1'),
    ('1.1.1'),
    # 1.1.1.1 is ok
    ('1.1.1.1.1'),
    ('foo'),
    ('1.1.1.1/32'),
    ('::1'),
]

invalid_interface_ids_ipv6 = [
    ('1'),
    ('1.1.1.1'),
    ('1::1::1'),
    ('foo'),
    ('::1/64'),
]


@pytest.mark.parametrize("interface_id_ipv4", invalid_interface_ids_ipv4)
def test_update_related_host_invalid_interface_id_v4_fails(client, interface_id_ipv4):
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    client.login(username=USERNAME, password=PASSWORD)
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'interface_id_ipv4': interface_id_ipv4,
    })
    assert response.status_code == HTTPStatus.OK
    assert 'is not a valid interface-id for IPv4' in response.text


@pytest.mark.parametrize("interface_id_ipv6", invalid_interface_ids_ipv6)
def test_update_related_host_invalid_interface_id_v6_fails(client, interface_id_ipv6):
    main_host = Host.objects.filter(name=TEST_HOST.host)[0]
    related_host = RelatedHost.objects.filter(main_host=main_host, name=RELATED_HOST_NAME)[0]
    client.login(username=USERNAME, password=PASSWORD)
    response = client.post(reverse('related_host_view', args=[main_host.id, related_host.id]), data={
        'interface_id_ipv6': interface_id_ipv6,
    })
    assert response.status_code == HTTPStatus.OK
    assert 'is not a valid interface-id for IPv6' in response.text
