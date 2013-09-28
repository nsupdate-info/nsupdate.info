"""
Misc. DNS related code: query, dynamic update, etc.
"""

SERVER = '85.10.192.104'  # ns1.thinkmo.de (master / dynamic upd server for nsupdate.info)
BASEDOMAIN = 'nsupdate.info'

NONEXISTING_HOST = 'nonexisting.' + BASEDOMAIN
WWW_HOST = 'www.' + BASEDOMAIN
WWW_IPV4_HOST = 'www.ipv4.' + BASEDOMAIN
WWW_IPV6_HOST = 'www.ipv6.' + BASEDOMAIN
WWW_IPV4_IP = '178.32.221.14'
WWW_IPV6_IP = '2001:41d0:8:e00e::1'

import dns.name
import dns.resolver

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
