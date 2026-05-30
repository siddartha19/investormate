"""
Network safety helpers for InvestorMate.

Guards against Server-Side Request Forgery (SSRF) when the library fetches
user-supplied URLs (e.g. ``Investor.analyze_document``). We refuse non-HTTP(S)
schemes and any host that resolves to a private, loopback, link-local, reserved,
or otherwise non-public address (including the cloud metadata endpoint
``169.254.169.254``).
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from .exceptions import DocumentProcessingError
from .logging import get_logger

logger = get_logger(__name__)

ALLOWED_SCHEMES = {"http", "https"}


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def is_safe_public_url(url: str, *, allow_private: bool = False) -> bool:
    """
    Return True if ``url`` is an HTTP(S) URL whose host resolves only to public
    IP addresses.

    Args:
        url: The URL to validate.
        allow_private: If True, skip the IP-range check (escape hatch for trusted
            internal use). Scheme validation still applies.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False

    host = parsed.hostname
    if not host:
        return False

    if allow_private:
        return True

    default_port = 443 if parsed.scheme.lower() == "https" else 80
    try:
        infos = socket.getaddrinfo(
            host, parsed.port or default_port, proto=socket.IPPROTO_TCP
        )
    except (socket.gaierror, UnicodeError, ValueError):
        return False

    if not infos:
        return False

    # Every resolved address must be public to defend against DNS rebinding
    # that mixes public and private records.
    for info in infos:
        ip_str = str(info[4][0])
        if not _is_public_ip(ip_str):
            return False
    return True


def assert_safe_url(url: str, *, allow_private: bool = False) -> str:
    """
    Validate ``url`` is safe to fetch, raising on failure.

    Returns:
        The original URL when safe.

    Raises:
        DocumentProcessingError: If the URL scheme is unsupported or the host
            resolves to a non-public address.
    """
    if not is_safe_public_url(url, allow_private=allow_private):
        logger.warning("Refusing to fetch unsafe or non-public URL: %s", url)
        raise DocumentProcessingError(
            f"Refusing to fetch unsafe or non-public URL: {url!r}"
        )
    return url
