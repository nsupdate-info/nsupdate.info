"""
Tests for dnstools module.
"""

import pytest

from nsupdate.main.dnstools import (query_ns, NONEXISTING_HOST, WWW_HOST, WWW_IPV4_HOST, WWW_IPV4_IP,
                                    WWW_IPV6_HOST, WWW_IPV6_IP, )

from dns.resolver import NXDOMAIN


class Tests(object):
    def test_queries_ok(self):
        """
        check some simple dns lookups
        """
        assert query_ns(WWW_IPV4_HOST, 'A') == WWW_IPV4_IP  # v4 ONLY
        assert query_ns(WWW_IPV6_HOST, 'AAAA') == WWW_IPV6_IP  # v6 ONLY
        assert query_ns(WWW_HOST, 'A') == WWW_IPV4_IP  # v4 and v6, query v4
        assert query_ns(WWW_HOST, 'AAAA') == WWW_IPV6_IP  # v4 and v6, query v6

    def test_queries_failing(self):
        with pytest.raises(NXDOMAIN):
            query_ns(NONEXISTING_HOST, 'A')
        with pytest.raises(NXDOMAIN):
            query_ns(NONEXISTING_HOST, 'AAAA')
