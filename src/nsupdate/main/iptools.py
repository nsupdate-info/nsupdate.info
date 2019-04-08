"""
Misc. IP tools: normalize, handle mapped addresses
"""

from netaddr import IPAddress


def normalize_mapped_address(ipaddr):
    """
    Converts a IPv4-mapped IPv6 address into a IPv4 address. Handles both the
    ::ffff:192.0.2.128 format as well as the deprecated ::192.0.2.128 format.

    :param ipaddr: IP address [str]
    :return: normalized IP address [str]
    """
    ipaddr = IPAddress(ipaddr)
    if ipaddr.is_ipv4_compat() or ipaddr.is_ipv4_mapped():
        ipaddr = ipaddr.ipv4()
    return str(ipaddr)


# currently, normalize_ip does no more than normalize_mapped_address:
normalize_ip = normalize_mapped_address
