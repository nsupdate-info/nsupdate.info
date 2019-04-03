"""
Misc. DNS related code: query, dynamic update, etc.

Usually, higher level code wants to call the add/update/delete functions.
"""

import os

# time to wait for dns name resolving [s]
RESOLVER_TIMEOUT = float(os.environ.get('DNS_RESOLVER_TIMEOUT', '10.0'))

# time to wait for dns name updating [s]
UPDATE_TIMEOUT = float(os.environ.get('DNS_UPDATE_TIMEOUT', '20.0'))

# time after we retry to reach a previously unreachable ns [s]
UNAVAILABLE_RETRY = 120.0


import binascii
import time
from datetime import timedelta
from collections import namedtuple

import logging
logger = logging.getLogger(__name__)

import socket
import random
import struct

import dns.inet
import dns.message
import dns.name
import dns.resolver
import dns.query
import dns.update
import dns.tsig
import dns.tsigkeyring
import dns.exception

from django.utils.timezone import now


class FQDN(namedtuple('FQDN', ['host', 'domain'])):
    """
    named tuple to represent a fully qualified domain name:

    * a host in a zone/domain
    * just a zone/domain (give host=None when creating)

    use this instead of str so that the information is not lost
    what the host part is vs. what the domain part is.

    e.g. foo.bar.example.org could be a host foo in domain bar.example.org
    or a host foo.bar in domain example.org.
    """
    def __str__(self):
        """
        when transforming this into a str, just give the fqdn
        """
        if self.host:
            return self.host + '.' + self.domain
        else:
            return self.domain


Timeout = dns.resolver.Timeout
NoNameservers = dns.resolver.NoNameservers
DNSException = dns.exception.DNSException


class SameIpError(ValueError):
    """
    raised if an IP address is already present in DNS and and update was
    requested, but is not needed.
    """


class DnsUpdateError(ValueError):
    """
    raised if DNS update return code is not NOERROR
    """


class NameServerNotAvailable(Exception):
    """
    raised if some nameserver was flagged as not available,
    but we tried using it.
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


def check_domain(domain):
    fqdn = FQDN(host="connectivity-test", domain=domain)

    from .models import Domain
    d = Domain.objects.get(name=domain)
    # temporarily set domain to available to allow add/update/deletes
    domain_available_state = d.available
    d.available = True
    d.save()

    try:
        # add host connectivity-test.<domain> with a random IP. See add()
        add(fqdn, socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

    except (dns.exception.DNSException, DnsUpdateError) as e:
        raise NameServerNotAvailable(str(e))

    finally:
        # reset domain available
        d.available = domain_available_state
        d.save()


def add(fqdn, ipaddr, ttl=60):
    """
    intelligent dns adder - first does a lookup on the master server to find
    the current ip and only sends an 'add' if there is no such entry.
    otherwise send an 'upd' if the if we have a different ip.

    :param fqdn: fully qualified domain name (FQDN)
    :param ipaddr: new ip address
    :param ttl: time to live, default 60s (int)
    :raises: SameIpError if new and old IP is the same
    :raises: ValueError if ipaddr is no valid ip address string
    """
    assert isinstance(fqdn, FQDN)
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
    intelligent dns deleter - first does a lookup on the master server to find
    out whether there is a dns entry and only send a 'del' if there is an entry.

    :param fqdn: fully qualified domain name (FQDN)
    :param rdtype: 'A', 'AAAA' or None (deletes 'A' and 'AAAA')
    """
    assert isinstance(fqdn, FQDN)
    if rdtype is not None:
        assert rdtype in ['A', 'AAAA', ]
        rdtypes = [rdtype, ]
    else:
        rdtypes = ['A', 'AAAA']
    for rdtype in rdtypes:
        try:
            # check if we have a DNS entry
            query_ns(fqdn, rdtype)
            # there is a dns entry
            ok = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # no dns entry, it is already deleted
            ok = False
        except (dns.resolver.Timeout, dns.resolver.NoNameservers) as e:  # socket.error also?
            # maybe could be caused by secondary DNS Timeout and master still ok?
            # assume the delete is OK...
            ok = True
        if ok:
            # send a del
            update_ns(fqdn, rdtype, action='del')


def update(fqdn, ipaddr, ttl=60):
    """
    intelligent dns updater - first does a lookup on the master server to find
    the current ip and only sends a dynamic update if we have a different ip.

    :param fqdn: fully qualified domain name (FQDN)
    :param ipaddr: new ip address
    :param ttl: time to live, default 60s (int)
    :raises: SameIpError if new and old IP is the same
    :raises: ValueError if ipaddr is no valid ip address string
    """
    assert isinstance(fqdn, FQDN)
    rdtype = check_ip(ipaddr, keys=('A', 'AAAA'))
    try:
        current_ipaddr = query_ns(fqdn, rdtype)
        # check if ip really changed
        ok = ipaddr != current_ipaddr
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        # no dns entry yet, ok
        ok = True
    except (dns.resolver.Timeout, dns.resolver.NoNameservers) as e:  # socket.error also?
        # maybe could be caused by secondary DNS Timeout and master still ok?
        # assume the update is OK...
        ok = True
    except dns.message.UnknownTSIGKey:
        raise DnsUpdateError("UnknownTSIGKey")
    if ok:
        # only send an update if the ip really changed as the update
        # causes write I/O on the nameserver and also traffic to the
        # dns slaves (they get a notify if we update the zone).
        update_ns(fqdn, rdtype, ipaddr, action='upd', ttl=ttl)
    else:
        raise SameIpError


def query_ns(fqdn, rdtype, prefer_primary=False):
    """
    query a dns name from our DNS server(s)

    :param fqdn: fqdn to query the name server for
    :type fqdn: dnstools.FQDN
    :param rdtype: the query type
    :type rdtype: int or str
    :param prefer_primary: whether we rather want to query the primary first
    :return: IP (as str)
    :raises: see dns.resolver.Resolver.query
    """
    assert isinstance(fqdn, FQDN)
    nameserver, nameserver2, origin = get_ns_info(fqdn)[0:3]
    resolver = dns.resolver.Resolver(configure=False)
    # we do not configure it from resolv.conf, but patch in the values we
    # want into the documented attributes:
    resolver.nameservers = [nameserver, ]
    if nameserver2:
        pos = 1 if prefer_primary else 0
        resolver.nameservers.insert(pos, nameserver2)
    # we must put the root zone into the search list, so that if a fqdn without "."
    # at the end comes in, it will append "." (and not the service server's domain).
    resolver.search = [dns.name.root, ]
    resolver.lifetime = RESOLVER_TIMEOUT
    # as we query directly the (authoritative) master dns, we do not desire
    # recursion. But: RD (recursion desired) is the internal default for flags
    # (used if flags = None is given). Thus, we explicitly give flags (all off):
    resolver.flags = 0
    try:
        answer = resolver.query(str(fqdn), rdtype)
        ip = str(list(answer)[0])
        logger.debug("query: %s answer: %s" % (fqdn, ip))
        return ip
    except (dns.resolver.Timeout, dns.resolver.NoNameservers, dns.message.UnknownTSIGKey) as e:  # socket.error also?
        logger.warning("error when querying for name '%s' in zone '%s' with rdtype '%s' [%s]." % (
                       fqdn.host, origin, rdtype, str(e)))
        set_ns_availability(origin, False)
        raise


def rev_lookup(ipaddr):
    """
    do a normal reverse DNS lookup, IP to name

    note: this call may be slow, especially if there is no reverse dns entry

    :param ipaddr: ip address (str)
    :return: hostname (or empty string if lookup failed)
    """
    name = ''
    if ipaddr:
        try:
            name = socket.gethostbyaddr(ipaddr)[0]
        except socket.error:
            pass
    return name


def get_ns_info(fqdn):
    """
    Get the master nameserver for fqdn, the key secret needed to update the zone and the key algorithm used.

    :param fqdn: the fully qualified hostname we are dealing with (str)
    :return: master nameserver, origin, domain, update keyname, update secret, update algo
    :raises: NameServerNotAvailable if ns was flagged unavailable in the db
    """
    assert isinstance(fqdn, FQDN)
    from .models import Domain
    try:
        # first we check if we have an entry for the fqdn
        # single-host update secret use case
        # XXX we need 2 DB accesses for the usual case just to support this rare case
        domain = str(fqdn)
        d = Domain.objects.get(name=domain)
    except Domain.DoesNotExist:
        # now check the base zone, the usual case
        # zone update secret use case
        domain = fqdn.domain
        d = Domain.objects.get(name=domain)
    if not d.available:
        if d.last_update + timedelta(seconds=UNAVAILABLE_RETRY) > now():
            # if there are troubles with a nameserver, we set available=False
            # and stop trying working with that nameserver for a while
            raise NameServerNotAvailable("nameserver for domain %s at IP %s was flagged unavailable" % (
                                         domain, d.nameserver_ip, ))
        else:
            # retry timeout is over, set it available again
            set_ns_availability(domain, True)
    algorithm = getattr(dns.tsig, d.nameserver_update_algorithm)
    return (d.nameserver_ip, d.nameserver2_ip, fqdn.domain, domain, fqdn.host, domain,
            d.nameserver_update_secret, algorithm)


def update_ns(fqdn, rdtype='A', ipaddr=None, action='upd', ttl=60):
    """
    update the master server

    :param fqdn: the fully qualified domain name to update (FQDN)
    :param rdtype: the record type (default: 'A') (str)
    :param ipaddr: ip address (v4 or v6), if needed (str)
    :param action: 'add', 'del' or 'upd'
    :param ttl: time to live for the added/updated resource, default 60s (int)
    :return: dns response
    :raises: DnsUpdateError, Timeout
    """
    assert isinstance(fqdn, FQDN)
    assert action in ['add', 'del', 'upd', ]
    nameserver, nameserver2, origin, domain, name, keyname, key, algo = get_ns_info(fqdn)
    try:
        keyring = dns.tsigkeyring.from_text({keyname: key})
    except (UnicodeError, binascii.Error) as e:
        msg = "Exception when building keyring for %s: [%s]" % (keyname, str(e))
        logger.error(msg)
        raise DnsUpdateError(msg)
    upd = dns.update.Update(origin, keyring=keyring, keyalgorithm=algo)
    if action == 'add':
        assert ipaddr is not None
        upd.add(name, ttl, rdtype, ipaddr)
    elif action == 'del':
        upd.delete(name, rdtype)
    elif action == 'upd':
        assert ipaddr is not None
        upd.replace(name, ttl, rdtype, ipaddr)
    logger.debug("performing %s for name %s and origin %s with rdtype %s and ipaddr %s" % (
                 action, name, origin, rdtype, ipaddr))
    try:
        response = dns.query.tcp(upd, nameserver, timeout=UPDATE_TIMEOUT)
        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            rcode_text = dns.rcode.to_text(rcode)
            logger.warning("DNS error [%s] performing %s for name %s and origin %s with rdtype %s and ipaddr %s" % (
                           rcode_text, action, name, origin, rdtype, ipaddr))
            raise DnsUpdateError(rcode_text)
        return response
    # TODO simplify exception handling when https://github.com/rthalley/dnspython/pull/85 is merged/released
    except socket.error as e:
        logger.error("socket.error [%s] - zone: %s" % (str(e), origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("SocketError %d" % e.errno)
    except EOFError as e:
        logger.error("EOFError [%s] - zone: %s" % (str(e), origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("EOFError")
    except dns.exception.Timeout:
        logger.warning("timeout when performing %s for name %s and origin %s with rdtype %s and ipaddr %s" % (
                       action, name, origin, rdtype, ipaddr))
        set_ns_availability(domain, False)
        raise DnsUpdateError("Timeout")
    except dns.tsig.PeerBadSignature:
        logger.error("PeerBadSignature - shared secret mismatch? zone: %s" % (origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("PeerBadSignature")
    except dns.tsig.PeerBadKey:
        logger.error("PeerBadKey - shared secret mismatch? zone: %s" % (origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("PeerBadKey")
    except dns.tsig.PeerBadTime:
        logger.error("PeerBadTime - DNS server did not like the time we sent. zone: %s" % (origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("PeerBadTime")
    except dns.message.UnknownTSIGKey as e:
        logger.error("UnknownTSIGKey [%s] - zone: %s" % (str(e), origin, ))
        set_ns_availability(domain, False)
        raise DnsUpdateError("UnknownTSIGKey")


def set_ns_availability(domain, available):
    """
    Set availability of the master nameserver for <domain>.

    As each Timeout takes quite a while, we want to avoid it.

    :param domain: domain object or string, may end with "."
    :param available: True/False for availability of ns
    """
    from .models import Domain
    domain = str(domain).rstrip('.')
    d = Domain.objects.get(name=domain)
    d.available = available
    d.save()
    if available:
        logger.info("set zone '%s' to available" % domain)
    else:
        logger.warning("set zone '%s' to unavailable" % domain)


def put_ip_into_session(session, ipaddr, kind=None, max_age=0,
                        save=False):
    """
    put an IP address into the session, including a timestamp,
    so we know how fresh it is.

    :param session: the session object
    :param ipaddr: ip address (can be v4 or v6, str)
    :param kind: 'ipv4' or 'ipv6' or None to autodetect
    :param max_age: maximum age of info, if older we refresh the timestamp
    :param save: save the session immediately, if it was changed
    """
    if kind is None:
        kind = check_ip(ipaddr)
    # we try to avoid modifying the session if not necessary...
    if session.get(kind) != ipaddr:
        # we have a new ip, remember it, with timestamp
        session[kind + '_timestamp'] = int(time.time())
        session[kind] = ipaddr
        session[kind + '_rdns'] = rev_lookup(ipaddr)  # may be slow
    else:
        old_timestamp = session.get(kind + '_timestamp')
        if not max_age or old_timestamp is None or old_timestamp + max_age < int(time.time()):
            # keep it fresh (to avoid that it gets killed and triggers detection)
            session[kind + '_timestamp'] = int(time.time())
    if save and session.modified:
        session.save()
