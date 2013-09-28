"""
Misc. DNS related code: query, dynamic update, etc.
"""

import dns.name
import dns.resolver
import dns.query
import dns.update
import dns.tsig
import dns.tsigkeyring


SERVER = '85.10.192.104'  # ns1.thinkmo.de (master / dynamic upd server for nsupdate.info)
BASEDOMAIN = 'nsupdate.info'

NONEXISTING_HOST = 'nonexisting.' + BASEDOMAIN
WWW_HOST = 'www.' + BASEDOMAIN
WWW_IPV4_HOST = 'www.ipv4.' + BASEDOMAIN
WWW_IPV6_HOST = 'www.ipv6.' + BASEDOMAIN
WWW_IPV4_IP = '178.32.221.14'
WWW_IPV6_IP = '2001:41d0:8:e00e::1'

UPDATE_ALGO = dns.tsig.HMAC_SHA512
UPDATE_KEY = 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=='


def query_ns(qname, rdtype):
    """
    query a dns name from our master server

    :param qname: the query name
    :type qname: dns.name.Name object or str
    :param rdtype: the query type
    :type rdtype: int or str
    :return: IP (as str)
    """
    resolver = dns.resolver.Resolver(configure=False)
    # we do not configure it from resolv.conf, but patch in the values we
    # want into the documented attributes:
    resolver.nameservers = [SERVER, ]
    resolver.search = [dns.name.from_text(BASEDOMAIN), ]
    answer = resolver.query(qname, rdtype)
    return str(list(answer)[0])


def parse_name(fqdn, origin=None):
    """
    Parse a fully qualified domain name into a relative name
    and a origin zone. Please note that the origin return value will
    have a trailing dot.

    :param fqdn: fully qualified domain name (str)
    :param origin: origin zone (optional, str)
    :return: origin, relative name (both dns.name.Name)
    """
    fqdn = dns.name.from_text(fqdn)
    if origin is None:
        origin = dns.resolver.zone_for_name(fqdn)
        rel_name = fqdn.relativize(origin)
    else:
        origin = dns.name.from_text(origin)
        rel_name = fqdn - origin
    return origin, rel_name


def update_ns(fqdn, rdtype='A', ipaddr=None, origin=None, action='upd', ttl=60):
    """
    update our master server

    :param fqdn: the fully qualified domain name to update (str)
    :param rdtype: the record type (default: 'A') (str)
    :param ipaddr: ip address (v4 or v6), if needed (str)
    :param origin: the origin zone to update (default; autodetect) (str)
    :param action: 'add', 'del' or 'upd'
    :param ttl: time to live for the added/updated resource, default 60s (int)
    :return: dns response
    """
    assert action in ['add', 'del', 'upd', ]
    origin, name = parse_name(fqdn, origin)
    upd = dns.update.Update(origin,
                            keyring=dns.tsigkeyring.from_text({BASEDOMAIN+'.': UPDATE_KEY}),
                            keyalgorithm=UPDATE_ALGO)
    if action == 'add':
        assert ipaddr is not None
        upd.add(name, ttl, rdtype, ipaddr)
    elif action == 'del':
        upd.delete(name, rdtype)
    elif action == 'upd':
        assert ipaddr is not None
        upd.replace(name, ttl, rdtype, ipaddr)
    response = dns.query.tcp(upd, SERVER)
    return response
