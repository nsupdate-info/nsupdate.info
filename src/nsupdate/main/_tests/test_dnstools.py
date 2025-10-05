"""
Tests for the dnstools module.
"""

from __future__ import print_function

import pytest

pytestmark = pytest.mark.django_db

from dns.resolver import NXDOMAIN, NoAnswer

from ..dnstools import (add, delete, update, query_ns, rev_lookup, update_ns,
                        SameIpError, DnsUpdateError, FQDN)

# See also conftest.py
BASEDOMAIN = 'nsupdate.info'
INVALID_HOST = FQDN('test999', BASEDOMAIN)  # This can't get updated.


class TestFQDN(object):
    def test_create(self):
        fqdn = FQDN('test', 'example.org')
        assert fqdn.host == 'test'
        assert fqdn.domain == 'example.org'
        assert str(fqdn) == 'test.example.org'


def remove_records(host, records=('A', 'AAAA', )):
    # Make sure the records are not present.
    for record in records:
        try:
            update_ns(host, record, action='del')
        except (NXDOMAIN, NoAnswer):
            # It is OK if it was never there.
            pass


class TestIntelligentUpdater(object):
    def test_double_update(self, ddns_fqdn):
        host, ip = ddns_fqdn, '1.2.3.4'
        remove_records(host)
        # First update with this IP should work without issue.
        update(host, ip)
        assert query_ns(host, 'A') == ip
        with pytest.raises(SameIpError):
            # Trying to update again with the same IP should raise.
            update(host, ip)


class TestIntelligentAdder(object):
    def test_double_add_same(self, ddns_fqdn):
        host, ip = ddns_fqdn, '1.2.3.4'
        remove_records(host)
        # First add with this IP should work without issue.
        add(host, ip)
        assert query_ns(host, 'A') == ip
        with pytest.raises(SameIpError):
            # Trying to add again with the same IP should raise.
            add(host, ip)

    def test_double_add_different(self, ddns_fqdn):
        host, ip = ddns_fqdn, '1.2.3.4'
        remove_records(host)
        # First add with this IP should work without issue.
        add(host, ip)
        assert query_ns(host, 'A') == ip
        different_ip = '4.3.2.1'
        # Adding again with a different IP should update the record:
        add(host, different_ip)  # Internally triggers an update.
        assert query_ns(host, 'A') == different_ip


class TestIntelligentDeleter(object):
    def test_delete(self, ddns_fqdn):
        host, ip = ddns_fqdn, '1.2.3.4'
        # Make sure the host exists.
        update_ns(host, 'A', ip, action='add')
        delete(host)
        # Ensure it is gone.
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'A')

    def test_double_delete(self, ddns_fqdn):
        host = ddns_fqdn
        remove_records(host)
        delete(host)  # Note: this does not raise NXDOMAIN.

    def test_delete_typed(self, ddns_fqdn):
        host, ip4, ip6 = ddns_fqdn, '1.2.3.4', '::42'
        # Make sure the host exists.
        update_ns(host, 'A', ip4, action='add')
        update_ns(host, 'AAAA', ip6, action='add')
        delete(host, 'A')
        # Ensure it is gone.
        with pytest.raises(NoAnswer):
            query_ns(host, 'A')
        delete(host, 'AAAA')
        # Ensure it is gone.
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'AAAA')


class TestQuery(object):
    def test_queries_ok(self, ddns_fqdn):
        host, ipv4, ipv6 = ddns_fqdn, '42.42.42.42', '::23'
        remove_records(host)
        with pytest.raises(NXDOMAIN):
            query_ns(ddns_fqdn, 'A')
        with pytest.raises(NXDOMAIN):
            query_ns(ddns_fqdn, 'AAAA')
        add(host, ipv4)
        assert query_ns(ddns_fqdn, 'A') == ipv4
        with pytest.raises(NoAnswer):
            query_ns(ddns_fqdn, 'AAAA')
        add(host, ipv6)
        assert query_ns(ddns_fqdn, 'AAAA') == ipv6


class TestReverseLookup(object):
    def test_rev_lookup_v4(self):
        name, ip = 'one.one.one.one', '1.1.1.1'
        assert rev_lookup(ip) == name

    def test_rev_lookup_v6(self):
        name, ip = 'one.one.one.one', '2606:4700:4700::1111'
        assert rev_lookup(ip) == name


class TestUpdate(object):
    def test_add_del_v4(self, ddns_fqdn):
        host, ip = ddns_fqdn, '1.1.1.1'
        remove_records(host)
        response = update_ns(host, 'A', ip, action='add', ttl=60)
        print(response)
        assert query_ns(host, 'A') == ip
        response = update_ns(host, 'A', action='del')
        print(response)
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'A') == ip

    def test_update_v4(self, ddns_fqdn):
        host, ip = ddns_fqdn, '2.2.2.2'
        response = update_ns(host, 'A', ip, action='upd', ttl=60)
        print(response)
        assert query_ns(host, 'A') == ip

        host, ip = ddns_fqdn, '3.3.3.3'
        response = update_ns(host, 'A', ip, action='upd', ttl=60)
        print(response)
        assert query_ns(host, 'A') == ip

    def test_add_del_v6(self, ddns_fqdn):
        host, ip = ddns_fqdn, '::1'
        remove_records(host)
        response = update_ns(host, 'AAAA', ip, action='add', ttl=60)
        print(response)
        assert query_ns(host, 'AAAA') == ip
        response = update_ns(host, 'AAAA', action='del')
        print(response)
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'AAAA') == ip

    def test_update_v6(self, ddns_fqdn):
        host, ip = ddns_fqdn, '::2'
        response = update_ns(host, 'AAAA', ip, action='upd', ttl=60)
        print(response)
        assert query_ns(host, 'AAAA') == ip

        host, ip = ddns_fqdn, '::3'
        response = update_ns(host, 'AAAA', ip, action='upd', ttl=60)
        print(response)
        assert query_ns(host, 'AAAA') == ip

    def test_update_mixed(self, ddns_fqdn):
        host4, ip4 = ddns_fqdn, '4.4.4.4'
        response = update_ns(host4, 'A', ip4, action='upd', ttl=60)
        print(response)
        assert query_ns(host4, 'A') == ip4

        host6, ip6 = ddns_fqdn, '::4'
        response = update_ns(host6, 'AAAA', ip6, action='upd', ttl=60)
        print(response)
        assert query_ns(host6, 'AAAA') == ip6

        # Make sure the IPv4 record remains unchanged.
        assert query_ns(host4, 'A') == ip4

        host4, ip4 = ddns_fqdn, '5.5.5.5'
        response = update_ns(host4, 'A', ip4, action='upd', ttl=60)
        print(response)
        assert query_ns(host4, 'A') == ip4

        # Make sure the IPv6 record remains unchanged.
        assert query_ns(host6, 'AAAA') == ip6

    def test_bad_update(self):
        # Test whether we can update ONLY the TESTDOMAIN.
        with pytest.raises(DnsUpdateError):
            response = update_ns(INVALID_HOST, 'A', '6.6.6.6', action='upd', ttl=60)
            print(response)
