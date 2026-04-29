# DoT tests to verify that the DNS server is working correctly.

import pytest
import ssl
import dns.message
import dns.query
import dns.name
import dns.update
import dns.tsigkeyring
import dns.tsig


def get_ssl_context():
    # For a self-signed cert, we create a context that doesn't verify.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def test_dot_query():
    # BIND is configured to listen on 127.0.0.1 port 853 with DoT
    # We use the self-signed certificate generated in install-bind.sh
    # Since it's self-signed and for "localhost", we can skip verification for this test
    # or just use a context that doesn't verify.

    server = '127.0.0.1'
    port = 853
    qname = dns.name.from_text('nsupdate.info')
    query = dns.message.make_query(qname, dns.rdatatype.SOA)

    ctx = get_ssl_context()

    try:
        response = dns.query.tls(query, server, port=port, ssl_context=ctx, timeout=5)
        assert response.rcode() == dns.rcode.NOERROR
        assert len(response.answer) > 0
        print("DoT query successful")
    except Exception as e:
        pytest.fail(f"DoT query failed: {e}")


def test_dot_update():
    server = '127.0.0.1'
    port = 853
    origin = 'nsupdate.info'
    keyname = 'nsupdate.info.'
    secret = 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=='
    algo = dns.tsig.HMAC_SHA512

    keyring = dns.tsigkeyring.from_text({keyname: secret})
    ctx = get_ssl_context()

    # 1. Add a record
    upd = dns.update.Update(origin, keyring=keyring, keyalgorithm=algo)
    upd.add('connectivity-test', 60, 'A', '127.0.0.2')

    try:
        response = dns.query.tls(upd, server, port=port, ssl_context=ctx, timeout=5)
        assert response.rcode() == dns.rcode.NOERROR
        print("DoT update (add) successful")
    except Exception as e:
        pytest.fail(f"DoT update (add) failed: {e}")

    # 2. Verify it's there
    qname = dns.name.from_text('connectivity-test.nsupdate.info')
    query = dns.message.make_query(qname, 'A')
    try:
        response = dns.query.tls(query, server, port=port, ssl_context=ctx, timeout=5)
        assert response.rcode() == dns.rcode.NOERROR
        assert any(rr.address == '127.0.0.2' for rrset in response.answer for rr in rrset)
        print("DoT query (verification) successful")
    except Exception as e:
        pytest.fail(f"DoT query (verification) failed: {e}")

    # 3. Delete the record
    upd = dns.update.Update(origin, keyring=keyring, keyalgorithm=algo)
    upd.delete('connectivity-test', 'A')

    try:
        response = dns.query.tls(upd, server, port=port, ssl_context=ctx, timeout=5)
        assert response.rcode() == dns.rcode.NOERROR
        print("DoT update (delete) successful")
    except Exception as e:
        pytest.fail(f"DoT update (delete) failed: {e}")


if __name__ == "__main__":
    # Allow running this script directly for manual verification
    test_dot_query()
    test_dot_update()
