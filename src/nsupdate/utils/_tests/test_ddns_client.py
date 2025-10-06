"""
Tests for the ddns_client module.
"""

import pytest

from ..ddns_client import dyndns2_update, Timeout, ConnectionError

# See also conftest.py.
BASEDOMAIN = 'nsupdate.info'
HOSTNAME = 'nsupdate-ddns-client-unittest.' + BASEDOMAIN
INVALID_HOSTNAME = 'nsupdate-ddns-client-nohost.' + BASEDOMAIN
USER, PASSWORD = HOSTNAME, 'yUTvxjRwNu'  # No problem; used only for this unit test.
SERVER = 'ipv4.' + BASEDOMAIN
SECURE = False  # Do not use TLS for these tests.


class TestDynDns2Client(object):
    def test_timeout(self):
        with pytest.raises(Timeout):
            # Assume the service can't respond in 1 µs and thus times out.
            dyndns2_update('wrong', 'wrong', SERVER,
                           hostname='wrong', myip='1.2.3.4', secure=SECURE,
                           timeout=0.000001)

    def test_connrefused(self):
        with pytest.raises(ConnectionError):
            # Assume there is no service running on 127.0.0.42.
            dyndns2_update('wrong', 'wrong', '127.0.0.42',
                           hostname='wrong', myip='1.2.3.4', secure=SECURE,
                           timeout=2.0)

    def test_notfqdn(self):
        status, text = dyndns2_update('wrongdomainnotfqdn', 'wrongpassword', SERVER,
                                      hostname=HOSTNAME, myip='1.2.3.4', secure=SECURE)
        assert status == 200
        assert text == 'notfqdn'

    def test_badauth(self):
        status, text = dyndns2_update(USER, 'wrongpassword', SERVER,
                                      hostname=HOSTNAME, myip='1.2.3.4', secure=SECURE)
        assert status == 401

    def test_nohost(self):
        status, text = dyndns2_update(USER, PASSWORD, SERVER,
                                      hostname=INVALID_HOSTNAME, myip='1.2.3.4', secure=SECURE)
        assert status == 200
        assert text == 'nohost'

    def test_success(self):
        ip = '1.2.3.4'
        status, text = dyndns2_update(USER, PASSWORD, SERVER,
                                      hostname=HOSTNAME, myip=ip, secure=SECURE)
        assert status == 200
        assert text in ["good %s" % ip, "nochg %s" % ip]
