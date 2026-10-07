from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkStatus:
    addresses: tuple[str, ...]
    configured: tuple[str, ...]
    trusted: bool


def local_ipv4_addresses() -> list[str]:
    """Return non-loopback IPv4 addresses without contacting an external service.

    AuraAgenda deliberately does not query a public-IP web service. Public IPs can
    change and are not suitable as a primary authentication factor. These values
    are only used by the optional trusted-local-network guard.
    """
    found: set[str] = set()
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_DGRAM):
            addr = info[4][0]
            ip = ipaddress.ip_address(addr)
            if not ip.is_loopback and not ip.is_unspecified:
                found.add(str(ip))
    except OSError:
        pass

    # This normally resolves the interface Windows would use for outbound traffic.
    # UDP connect() does not establish a session or transmit application data.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("10.255.255.255", 1))
            addr = sock.getsockname()[0]
            ip = ipaddress.ip_address(addr)
            if not ip.is_loopback and not ip.is_unspecified:
                found.add(str(ip))
        finally:
            sock.close()
    except OSError:
        pass

    return sorted(found, key=lambda value: (not ipaddress.ip_address(value).is_private, value))


def primary_local_ipv4() -> str:
    addresses = local_ipv4_addresses()
    return addresses[0] if addresses else ""


def parse_trusted_networks(value: str) -> list[ipaddress.IPv4Network]:
    networks: list[ipaddress.IPv4Network] = []
    for raw in (value or "").replace(";", ",").split(","):
        item = raw.strip()
        if not item:
            continue
        try:
            if "/" not in item:
                item = f"{item}/32"
            network = ipaddress.ip_network(item, strict=False)
        except ValueError as exc:
            raise ValueError(f"Invalid trusted network: {raw.strip()}") from exc
        if not isinstance(network, ipaddress.IPv4Network):
            raise ValueError("Only IPv4 trusted networks are supported in this version")
        networks.append(network)
    return networks


def canonical_trusted_networks(value: str) -> str:
    return ", ".join(str(network) for network in parse_trusted_networks(value))


def suggested_local_network() -> str:
    ip_text = primary_local_ipv4()
    if not ip_text:
        return ""
    ip = ipaddress.ip_address(ip_text)
    if not isinstance(ip, ipaddress.IPv4Address):
        return ""
    # /24 is intentionally only a convenience suggestion. The owner can use an
    # exact /32 or a different CIDR if their network is configured differently.
    return str(ipaddress.ip_network(f"{ip}/24", strict=False))


def network_status(configured: str) -> NetworkStatus:
    addresses = tuple(local_ipv4_addresses())
    networks = tuple(str(network) for network in parse_trusted_networks(configured))
    if not networks:
        return NetworkStatus(addresses, networks, True)
    parsed = [ipaddress.ip_network(value, strict=False) for value in networks]
    trusted = any(ipaddress.ip_address(address) in network for address in addresses for network in parsed)
    return NetworkStatus(addresses, networks, trusted)
