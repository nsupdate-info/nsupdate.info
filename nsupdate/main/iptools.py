"""
Misc. IP tools: normalize, handle mapped addresses
"""

from netaddr import IPAddress

def normalize_ip(ipaddr):
    ipaddr = normalize_mapped_address(ipaddr)
    return ipaddr

def normalize_mapped_address(ipaddr):
    ipaddr = IPAddress(ipaddr)

    if ipaddr.is_ipv4_compat() or ipaddr.is_ipv4_mapped():
        ipaddr = ipaddr.ipv4()

    return str(ipaddr)
