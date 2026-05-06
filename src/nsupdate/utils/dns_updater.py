from django.conf import settings
from netaddr import IPNetwork, AddrFormatError, IPAddress

from nsupdate.main.dnstools import check_ip, delete, update, SameIpError, DnsUpdateError, NameServerNotAvailable, FQDN
from nsupdate.utils import ddns_client


def strip_ip(ipaddr):
    """strip away spaces and trailing /xx prefix length / netmask"""
    ipaddr = str(ipaddr).strip()
    if '/' in ipaddr:
        # there is a trailing /xx prefix length / netmask - get rid of it.
        # by doing this we support myip=<ip6lanprefix> of FritzBox.
        ipaddr = ipaddr.rsplit('/')[0]
    return ipaddr


def update_or_delete(host, ipaddr, secure=False, logger=None, _delete=False):
    """
    common code shared by the 2 update/delete views

    :param host: host object
    :param ipaddr: ip addr (v4 or v6)
    :param secure: True if we use TLS/https
    :param logger: a logger object
    :param _delete: True for delete, False for update
    :return: dyndns2 response string
    """
    mode = ('update', 'delete')[_delete]  # only use this for logging
    # we are doing abuse / available checks rather late, so the client might
    # get more specific responses (like 'badagent' or 'notfqdn') by earlier
    # checks. it also avoids some code duplication if done here:
    fqdn = host.get_fqdn()
    if host.abuse or host.abuse_blocked:
        msg = '%s - received %s for host with abuse / abuse_blocked flag set' % (fqdn, mode,)
        logger.warning(msg)
        host.register_client_result(msg, fault=False)
        return 'abuse'
    if not host.available:
        # not available is like it doesn't exist
        msg = '%s - received %s for unavailable host' % (fqdn, mode,)
        logger.warning(msg)
        host.register_client_result(msg, fault=False)
        return 'nohost'
    try:
        ipaddr = strip_ip(ipaddr)
        kind = check_ip(ipaddr, ('ipv4', 'ipv6'))
        rdtype = 'A' if kind == 'ipv4' else 'AAAA'
        IPNetwork(ipaddr)  # raise AddrFormatError here if there is an issue with ipaddr, see #394
    except (ValueError, UnicodeError, AddrFormatError):
        # invalid ip address string
        # some people manage to even give a non-ascii string instead of an ip addr
        msg = '%s - received bad ip address: %r' % (fqdn, ipaddr)
        logger.warning(msg)
        host.register_client_result(msg, fault=True)
        return 'dnserr'  # there should be a better response code for this

    # If we receive an update request with an address that has only the network prefix,
    # but the interface id is all-zero, we will NOT update DNS with a useless A or AAAA record,
    # but rather delete any A or AAAA record we already might have, see issue #648.
    if not _delete:
        if kind == 'ipv4':
            netmask = host.netmask_ipv4
            single_ip = netmask == 32  # the usual case for home routers
        elif kind == 'ipv6':
            netmask = host.netmask_ipv6
            single_ip = netmask == 128  # rather theoretical case, but who knows...
        else:
            raise ValueError('unknown ip address kind: %s' % kind)
        # we do not want to update A/AAAA records with network addresses:
        is_network = not single_ip and IPNetwork("%s/%d" % (ipaddr, netmask)).network == IPAddress(ipaddr)
        if is_network:
            logger.info('%s - received %s for host %s, but address has only network prefix, deleting instead' % (fqdn, mode, ipaddr,))
    else:
        is_network = False

    if not _delete and IPAddress(ipaddr) in settings.BAD_IPS_HOST:
        msg = '%s - received %s to blacklisted ip address: %r' % (fqdn, mode, ipaddr)
        logger.warning(msg)
        host.abuse = True
        host.abuse_blocked = True
        host.register_client_result(msg, fault=True)
        return 'abuse'
    host.poke(kind, secure)
    try:
        if _delete or is_network:
            delete(fqdn, rdtype)
        else:
            update(fqdn, ipaddr)
    except SameIpError:
        msg = '%s - received no-change update, ip: %s tls: %r' % (fqdn, ipaddr, secure)
        logger.warning(msg)
        host.register_client_result(msg, fault=True)
        return 'nochg %s' % ipaddr
    except (DnsUpdateError, NameServerNotAvailable) as e:
        msg = str(e)
        msg = '%s - received %s that resulted in a dns error [%s], ip: %s tls: %r' % (
            fqdn, mode, msg, ipaddr, secure)
        logger.error(msg)
        host.register_server_result(msg, fault=True)
        return 'dnserr'
    else:
        if _delete:
            msg = '%s - received delete for record %s, tls: %r' % (fqdn, rdtype, secure)
        else:
            msg = '%s - received good update -> ip: %s tls: %r' % (fqdn, ipaddr, secure)
        logger.info(msg)
        host.register_client_result(msg, fault=False)
        _update_related_hosts(host, kind, ipaddr, secure, logger)
        if _delete:
            return 'deleted %s' % rdtype
        else:  # update
            return 'good %s' % ipaddr


def _update_related_hosts(host, kind, ipaddr, secure, logger):
    """after updating the host in dns, do related other updates"""
    # update related hosts
    for rh in host.relatedhosts.all():
        update_related_host(rh, kind, ipaddr, logger, secure)

    # now check if there are other services we shall relay updates to:
    for hc in host.serviceupdaterhostconfigs.all():
        _update_service_updater_host(hc, kind, ipaddr, logger)


def _update_service_updater_host(host_config, kind, ipaddr, logger):
    if (kind == 'ipv4' and host_config.give_ipv4 and host_config.service.accept_ipv4
        or
        kind == 'ipv6' and host_config.give_ipv6 and host_config.service.accept_ipv6):
        kwargs = dict(
            name=host_config.name, password=host_config.password,
            hostname=host_config.hostname, myip=ipaddr,
            server=host_config.service.server, path=host_config.service.path, secure=host_config.service.secure,
        )
        try:
            ddns_client.dyndns2_update(**kwargs)
        except Exception:
            # we never want to crash here
            kwargs.pop('password')
            logger.exception("the dyndns2 updater raised an exception [%r]" % kwargs)


def update_related_host(related_host, kind, ipaddr, logger, secure):
    host = related_host.main_host
    fqdn = host.get_fqdn()
    rdtype = 'A' if kind == 'ipv4' else 'AAAA'
    if related_host.available:
        if kind == 'ipv4':
            ifid = related_host.interface_id_ipv4
            netmask = host.netmask_ipv4
            _delete = (ipaddr == '0.0.0.0')
        else:  # kind == 'ipv6':
            ifid = related_host.interface_id_ipv6
            netmask = host.netmask_ipv6
            _delete = (ipaddr == '::')
        ifid = ifid.strip() if ifid else ifid
        if not ifid:
            # leave ifid empty if you don't want this rh record
            _delete = True
        try:
            rh_fqdn = FQDN(related_host.name + '.' + fqdn.host, fqdn.domain)
            if not _delete:
                ifid = IPAddress(ifid)
                network = IPNetwork("%s/%d" % (ipaddr, netmask))
                rh_ipaddr = str(IPAddress(network.network) + int(ifid))
        except (IndexError, AddrFormatError, ValueError) as e:
            logger.warning("trouble computing address of related host %s [%s]" % (related_host, e))
        else:
            if not _delete:
                logger.info("updating related host %s -> %s" % (rh_fqdn, rh_ipaddr))
            else:
                logger.info("deleting related host %s" % (rh_fqdn,))
            try:
                if not _delete:
                    update(rh_fqdn, rh_ipaddr)
                else:
                    delete(rh_fqdn, rdtype)
            except SameIpError:
                msg = '%s - related hosts no-change update, ip: %s tls: %r' % (rh_fqdn, rh_ipaddr, secure)
                logger.warning(msg)
                host.register_client_result(msg, fault=True)
            except (DnsUpdateError, NameServerNotAvailable) as e:
                msg = str(e)
                if not _delete:
                    msg = '%s - related hosts update that resulted in a dns error [%s], ip: %s tls: %r' % (
                        rh_fqdn, msg, rh_ipaddr, secure)
                else:
                    msg = '%s - related hosts deletion that resulted in a dns error [%s], tls: %r' % (
                        rh_fqdn, msg, secure)
                logger.error(msg)
                host.register_server_result(msg, fault=True)
