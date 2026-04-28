"""
Utility functions / classes do dnspython. Might be offered to dnspython for an inclusion.
"""

import dns.nameserver


class UdpNameServer(dns.nameserver.AddressAndPortNameserver):
    def __init__(self, address: str, port: int = 53):
        super().__init__(address, port)

    def kind(self):
        return "udp"

    def query(
        self,
        request: dns.message.QueryMessage,
        timeout: float,
        source: str | None = None,
        source_port: int = 0,
        one_rr_per_rrset: bool = False,
        ignore_trailing: bool = False,
        max_size: int | None = None
    ) -> dns.message.Message:
        response = dns.query.udp(
            request,
            self.address,
            timeout=timeout,
            port=self.port,
            source=source,
            source_port=source_port,
            raise_on_truncation=True,
            one_rr_per_rrset=one_rr_per_rrset,
            ignore_trailing=ignore_trailing,
            ignore_errors=True,
            ignore_unexpected=True,
        )
        return response

    async def async_query(
        self,
        request: dns.message.QueryMessage,
        timeout: float,
        source: str | None = None,
        source_port: int = 0,
        backend: dns.asyncbackend.Backend | None = None,
        one_rr_per_rrset: bool = False,
        ignore_trailing: bool = False,
        max_size: int | None = None
    ) -> dns.message.Message:
        response = await dns.asyncquery.udp(
            request,
            self.address,
            timeout=timeout,
            port=self.port,
            source=source,
            source_port=source_port,
            raise_on_truncation=True,
            backend=backend,
            one_rr_per_rrset=one_rr_per_rrset,
            ignore_trailing=ignore_trailing,
            ignore_errors=True,
            ignore_unexpected=True,
        )
        return response


class TcpNameServer(dns.nameserver.AddressAndPortNameserver):
    def __init__(self, address: str, port: int = 53):
        super().__init__(address, port)

    def kind(self):
        return "tcp"

    def query(
        self,
        request: dns.message.QueryMessage,
        timeout: float,
        source: str | None = None,
        source_port: int = 0,
        one_rr_per_rrset: bool = False,
        ignore_trailing: bool = False,
        max_size: int | None = None
    ) -> dns.message.Message:
        response = dns.query.tcp(
            request,
            self.address,
            timeout=timeout,
            port=self.port,
            source=source,
            source_port=source_port,
            one_rr_per_rrset=one_rr_per_rrset,
            ignore_trailing=ignore_trailing,
        )
        return response

    async def async_query(
        self,
        request: dns.message.QueryMessage,
        timeout: float,
        source: str | None,
        source_port: int,
        backend: dns.asyncbackend.Backend | None = None,
        one_rr_per_rrset: bool = False,
        ignore_trailing: bool = False,
        max_size: int | None = None
    ) -> dns.message.Message:
        response = await dns.asyncquery.tcp(
            request,
            self.address,
            timeout=timeout,
            port=self.port,
            source=source,
            source_port=source_port,
            backend=backend,
            one_rr_per_rrset=one_rr_per_rrset,
            ignore_trailing=ignore_trailing,
        )
        return response


def make_nameserver(ip, port, protocol):
    match protocol.lower():
      case "udp":
        return UdpNameServer(ip, port)
      case "tcp":
        return TcpNameServer(ip, port)
      case "dot":
        return dns.nameserver.DoTNameServer(ip, port)
      case "doh":
        return dns.nameserver.DoHNameServer(ip, port)
      case "doq":
        return dns.nameserver.DoQNameServer(ip, port)
      case _:
        raise dns.nameserver.SyntaxError(f"invalid protocol {protocol}")
