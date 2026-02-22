"""URL validation for BYOMCP (Bring Your Own MCP) server registration.

Security controls for user-registered MCP servers:
- HTTPS required for external servers
- Private/internal IP ranges blocked
- Cloud metadata endpoints blocked (169.254.169.254)

ContextForge RC1 has built-in SSRF protection (SSRF_PROTECTION_ENABLED=true),
but we add application-level validation as defense-in-depth.
"""

from __future__ import annotations

import ipaddress
import logging
from urllib.parse import urlparse

log = logging.getLogger(__name__)

# Internal Docker service URLs are allowed (they use HTTP internally)
_INTERNAL_HOSTS = frozenset(
    {
        "apollos-m365-mcp",
        "apollos-mcp-gateway",
        "apollos-backend",
        "apollos-db",
        "apollos-frontend",
        "apollos-docs",
    }
)


class URLValidationError(Exception):
    """Raised when a BYOMCP URL fails validation."""


def validate_mcp_server_url(url: str, *, allow_internal: bool = False) -> str:
    """Validate a URL for MCP server registration.

    Args:
        url: The URL to validate.
        allow_internal: If True, allow HTTP for internal Docker service URLs.
            Set to True for admin-registered servers, False for user BYOMCP.

    Returns:
        The validated URL (stripped of trailing slashes).

    Raises:
        URLValidationError: If the URL fails validation.
    """
    parsed = urlparse(url)

    if not parsed.scheme:
        raise URLValidationError("URL must include a scheme (https://)")

    if not parsed.hostname:
        raise URLValidationError("URL must include a hostname")

    hostname = parsed.hostname.lower()

    # Allow internal Docker service names with HTTP
    if hostname in _INTERNAL_HOSTS:
        if not allow_internal:
            raise URLValidationError("Internal service URLs are not allowed for user-registered servers")
        return url.rstrip("/")

    # External URLs must use HTTPS
    if parsed.scheme != "https":
        raise URLValidationError("External MCP servers must use HTTPS")

    # Block localhost variants
    if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):  # noqa: S104
        raise URLValidationError("Localhost URLs are not allowed")

    # Block private/reserved IP ranges
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_reserved or ip.is_loopback or ip.is_link_local:
            raise URLValidationError(f"Private/reserved IP addresses are not allowed: {hostname}")
    except ValueError:
        pass  # Not an IP address — hostname is fine

    # Block cloud metadata endpoints
    if hostname in ("169.254.169.254", "metadata.google.internal"):
        raise URLValidationError("Cloud metadata endpoints are not allowed")

    return url.rstrip("/")
