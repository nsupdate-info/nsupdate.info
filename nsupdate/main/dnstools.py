"""
Misc. DNS related code: query, dynamic update, etc.

Usually, higher level code wants to call the add/update/delete functions.
"""

import dns.inet
import dns.name
import dns.resolver
import dns.query
import dns.update
import dns.tsig
import dns.tsigkeyring

from django.conf import settings


class SameIpError(ValueError):
    """
    raised if an IP address is already present in DNS and and update was
    requested, but is not needed.
    """


def check_ip(ipaddr, keys=('ipv4', 'ipv6')):
    """
    Check if a string is a valid ip address and also
    determine the kind of the address (address family).
    Return first key for v4, second key for v6.

    :param ipaddr: ip address, v4 or v6, str
    :param keys: 2-tuple (v4key, v6key)
    :return: v4key or v6key
    :raises: ValueError if the ip is invalid
    """
    af = dns.inet.af_for_address(ipaddr)
    return keys[af == dns.inet.AF_INET6]


def add(fqdn, ipaddr, ttl=60):
    """
    intelligent dns adder - first does a lookup on the master server to find
    the current ip and only sends an 'add' if there is no such entry.
    otherwise send an 'upd' if the if we have a different ip.

    :param fqdn: fully qualified domain name (str)
    :param ipaddr: new ip address
    :param ttl: time to live, default 60s (int)
    :raises: SameIpError if new and old IP is the same
    """
    rdtype = check_ip(ipaddr, keys=('A', 'AAAA'))
    try:
        current_ipaddr = query_ns(fqdn, rdtype)
        # check if ip really changed
        ok = ipaddr != current_ipaddr
        action = 'upd'
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        # no dns entry yet, ok
        ok = True
        action = 'add'
    if ok:
        # only send an add/update if the ip really changed as the update
        # causes write I/O on the nameserver and also traffic to the
        # dns slaves (they get a notify if we update the zone).
        update_ns(fqdn, rdtype, ipaddr, action=action, ttl=ttl)
    else:
        raise SameIpError


def delete(fqdn, rdtype=None):
    """
    dns deleter

    :param fqdn: fully qualified domain name (str)
    :param rdtype: 'A', 'AAAA' or None (deletes 'A' and 'AAAA')
    """
    if rdtype is not None:
        assert rdtype in ['A', 'AAAA', ]
        rdtypes = [rdtype, ]
    else:
        rdtypes = ['A', 'AAAA']
    for rdtype in rdtypes:
        update_ns(fqdn, rdtype, action='del')


def update(fqdn, ipaddr, ttl=60):
    """
    intelligent dns updater - first does a lookup on the master server to find
    the current ip and only sends a dynamic update if we have a different ip.

    :param fqdn: fully qualified domain name (str)
    :param ipaddr: new ip address
    :param ttl: time to live, default 60s (int)
    :raises: SameIpError if new and old IP is the same
    """
    rdtype = check_ip(ipaddr, keys=('A', 'AAAA'))
    try:
        current_ipaddr = query_ns(fqdn, rdtype)
        # check if ip really changed
        ok = ipaddr != current_ipaddr
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        # no dns entry yet, ok
        ok = True
    if ok:
        # only send an update if the ip really changed as the update
        # causes write I/O on the nameserver and also traffic to the
        # dns slaves (they get a notify if we update the zone).
        update_ns(fqdn, rdtype, ipaddr, action='upd', ttl=ttl)
    else:
        raise SameIpError


def query_ns(qname, rdtype, origin=None):
    """
    query a dns name from our master server

    :param qname: the query name
    :type qname: dns.name.Name object or str
    :param rdtype: the query type
    :type rdtype: int or str
    :param origin: origin zone
    :type origin: str or None
    :return: IP (as str)
    """
    origin, name = parse_name(qname, origin)
    origin_str = str(origin)
    nameserver = get_ns_info(origin_str)[0]
    resolver = dns.resolver.Resolver(configure=False)
    # we do not configure it from resolv.conf, but patch in the values we
    # want into the documented attributes:
    resolver.nameservers = [nameserver, ]
    resolver.search = [dns.name.from_text(settings.BASEDOMAIN), ]
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


def get_ns_info(origin):
    """
    Get the master nameserver for the <origin> zone, the key needed
    to update the zone and the key algorithm used.

    :param origin: zone we are dealing with, must be with trailing dot
    :return: master nameserver, update key
    """
    # later look this up from Domain model: domain+'.': nameserver_ip, nameserver_update_key
    ns_info = {
        settings.BASEDOMAIN + '.': (settings.SERVER, settings.UPDATE_KEY, settings.UPDATE_ALGO),
    }
    return ns_info[origin]


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
    origin_str = str(origin)
    nameserver, key, algo = get_ns_info(origin_str)
    upd = dns.update.Update(origin,
                            keyring=dns.tsigkeyring.from_text({origin_str: key}),
                            keyalgorithm=algo)
    if action == 'add':
        assert ipaddr is not None
        upd.add(name, ttl, rdtype, ipaddr)
    elif action == 'del':
        upd.delete(name, rdtype)
    elif action == 'upd':
        assert ipaddr is not None
        upd.replace(name, ttl, rdtype, ipaddr)
    response = dns.query.tcp(upd, nameserver)
    return response
