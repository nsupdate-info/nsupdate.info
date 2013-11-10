"""
Tests for dnstools module.
"""

import pytest

pytestmark = pytest.mark.django_db

from dns.resolver import NXDOMAIN, NoAnswer

from ..dnstools import add, delete, update, query_ns, parse_name, update_ns, SameIpError, DnsUpdateError

# see also conftest.py
BASEDOMAIN = 'nsupdate.info'
TEST_HOST = 'test.' + BASEDOMAIN  # you can ONLY update THIS host in unit tests
INVALID_HOST = 'test999.' + BASEDOMAIN  # therefore, this can't get updated


def remove_records(host, records=('A', 'AAAA', )):
    # make sure the records are not there
    for record in records:
        try:
            update_ns(host, record, action='del')
        except (NXDOMAIN, NoAnswer):
            # it is ok if it was never there
            pass


class TestIntelligentUpdater(object):
    def test_double_update(self):
        host, ip = TEST_HOST, '1.2.3.4'
        remove_records(host)
        # first update with this IP, should work without issue:
        update(host, ip)
        assert query_ns(host, 'A') == ip
        with pytest.raises(SameIpError):
            # trying to update again with same IP should raise
            update(host, ip)


class TestIntelligentAdder(object):
    def test_double_add_same(self):
        host, ip = TEST_HOST, '1.2.3.4'
        remove_records(host)
        # first add with this IP, should work without issue:
        add(host, ip)
        assert query_ns(host, 'A') == ip
        with pytest.raises(SameIpError):
            # trying to add again with same IP should raise
            add(host, ip)

    def test_double_add_different(self):
        host, ip = TEST_HOST, '1.2.3.4'
        remove_records(host)
        # first add with this IP, should work without issue:
        add(host, ip)
        assert query_ns(host, 'A') == ip
        different_ip = '4.3.2.1'
        # trying to add again with same IP should raise
        add(host, different_ip)  # internally triggers an update
        assert query_ns(host, 'A') == different_ip


class TestIntelligentDeleter(object):
    def test_delete(self):
        host, ip = TEST_HOST, '1.2.3.4'
        # make sure the host is there
        update_ns(host, 'A', ip, action='add')
        delete(host)
        # make sure it is gone
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'A')

    def test_double_delete(self):
        host = TEST_HOST
        remove_records(host)
        delete(host)  # hmm, this doesn't raise NXDOMAIN!?


class TestQuery(object):
    def test_queries_ok(self):
        host, ipv4, ipv6 = TEST_HOST, '42.42.42.42', '::23'
        remove_records(host)
        with pytest.raises(NXDOMAIN):
            query_ns(TEST_HOST, 'A')
        with pytest.raises(NXDOMAIN):
            query_ns(TEST_HOST, 'AAAA')
        add(host, ipv4)
        assert query_ns(TEST_HOST, 'A') == ipv4
        with pytest.raises(NoAnswer):
            query_ns(TEST_HOST, 'AAAA')
        add(host, ipv6)
        assert query_ns(TEST_HOST, 'AAAA') == ipv6


class TestUpdate(object):
    def test_parse1(self):
        host, domain = 'test', BASEDOMAIN
        origin, relname = parse_name(host + '.' + domain)
        assert str(origin) == domain + '.'
        assert str(relname) == host

    def test_parse2(self):
        host, domain = 'prefix.test', BASEDOMAIN
        origin, relname = parse_name(host + '.' + domain)
        assert str(origin) == domain + '.'
        assert str(relname) == 'prefix.test'

    def test_parse_with_origin(self):
        origin, relname = parse_name('foo.bar.baz.org', 'bar.baz.org')
        assert str(origin) == 'bar.baz.org' + '.'
        assert str(relname) == 'foo'

    def test_add_del_v4(self):
        host, ip = TEST_HOST, '1.1.1.1'
        remove_records(host)
        response = update_ns(host, 'A', ip, action='add', ttl=60)
        print response
        assert query_ns(host, 'A') == ip
        response = update_ns(host, 'A', action='del')
        print response
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'A') == ip

    def test_update_v4(self):
        host, ip = TEST_HOST, '2.2.2.2'
        response = update_ns(host, 'A', ip, action='upd', ttl=60)
        print response
        assert query_ns(host, 'A') == ip

        host, ip = TEST_HOST, '3.3.3.3'
        response = update_ns(host, 'A', ip, action='upd', ttl=60)
        print response
        assert query_ns(host, 'A') == ip

    def test_add_del_v6(self):
        host, ip = TEST_HOST, '::1'
        remove_records(host)
        response = update_ns(host, 'AAAA', ip, action='add', ttl=60)
        print response
        assert query_ns(host, 'AAAA') == ip
        response = update_ns(host, 'AAAA', action='del')
        print response
        with pytest.raises(NXDOMAIN):
            query_ns(host, 'AAAA') == ip

    def test_update_v6(self):
        host, ip = TEST_HOST, '::2'
        response = update_ns(host, 'AAAA', ip, action='upd', ttl=60)
        print response
        assert query_ns(host, 'AAAA') == ip

        host, ip = TEST_HOST, '::3'
        response = update_ns(host, 'AAAA', ip, action='upd', ttl=60)
        print response
        assert query_ns(host, 'AAAA') == ip

    def test_update_mixed(self):
        host4, ip4 = TEST_HOST, '4.4.4.4'
        response = update_ns(host4, 'A', ip4, action='upd', ttl=60)
        print response
        assert query_ns(host4, 'A') == ip4

        host6, ip6 = TEST_HOST, '::4'
        response = update_ns(host6, 'AAAA', ip6, action='upd', ttl=60)
        print response
        assert query_ns(host6, 'AAAA') == ip6

        # make sure the v4 is unchanged
        assert query_ns(host4, 'A') == ip4

        host4, ip4 = TEST_HOST, '5.5.5.5'
        response = update_ns(host4, 'A', ip4, action='upd', ttl=60)
        print response
        assert query_ns(host4, 'A') == ip4

        # make sure the v6 is unchanged
        assert query_ns(host6, 'AAAA') == ip6

    def test_bad_update(self):
        # test whether we ONLY can update the TEST_HOST
        with pytest.raises(DnsUpdateError):
            response = update_ns(INVALID_HOST, 'A', '6.6.6.6', action='upd', ttl=60)
            print response
