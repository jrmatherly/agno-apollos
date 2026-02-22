from agno.os.scopes import get_accessible_resource_ids, get_default_scope_mappings, has_required_scopes

# Entra App Role → list of Agno scope strings
# Scope format verified: resource:action or resource:<id>:action
ROLE_SCOPE_MAP: dict[str, list[str]] = {
    "GlobalAdmin": ["agent_os:admin"],
    "Admin": [
        "agents:read",
        "agents:write",
        "agents:delete",
        "agents:run",
        "teams:read",
        "teams:write",
        "teams:delete",
        "teams:run",
        "workflows:read",
        "workflows:write",
        "workflows:delete",
        "workflows:run",
        "sessions:read",
        "sessions:write",
        "sessions:delete",
        "knowledge:read",
        "knowledge:write",
        "knowledge:delete",
        "memories:read",
        "memories:write",
        "memories:delete",
        "metrics:read",
        "metrics:write",
        "evals:read",
        "evals:write",
        "evals:delete",
        "traces:read",
        "schedules:read",
        "schedules:write",
        "schedules:delete",
        "approvals:read",
        "approvals:write",
        "approvals:delete",
        "mcp:servers:read",
        "mcp:servers:write",
        "mcp:servers:delete",
        "mcp:tools:call",
    ],
    "TeamLead": [
        "agents:run",
        "agents:read",
        "sessions:read",
        "sessions:write",
        "sessions:delete",
        "knowledge:read",
        "memories:read",
        "memories:write",
        "memories:delete",
        "mcp:servers:read",
        "mcp:tools:call",
    ],
    "Developer": [
        "agents:run",
        "agents:read",
        "sessions:read",
        "sessions:write",
        "mcp:servers:read",
        "mcp:tools:call",
    ],
    "DevOps": [
        "system:read",
        "metrics:read",
        "metrics:write",
        "agents:run",
        "agents:read",
        "traces:read",
        "schedules:read",
    ],
    "InfoSec": [
        "system:read",
        "agents:read",
        "teams:read",
        "workflows:read",
        "sessions:read",
        "knowledge:read",
        "memories:read",
        "metrics:read",
        "evals:read",
        "traces:read",
        "approvals:read",
    ],
    "User": [
        "agents:read",
        "sessions:read",
        "sessions:write",
        "mcp:servers:read",
        "mcp:tools:call",
    ],
}

# Cache the default mappings once (they don't change)
_ROUTE_SCOPE_MAP: dict[str, list[str]] = get_default_scope_mappings()

# MCP Gateway route scopes (added on top of Agno defaults)
_ROUTE_SCOPE_MAP.update(
    {
        "GET /mcp/servers": ["mcp:servers:read"],
        "GET /mcp/servers/*": ["mcp:servers:read"],
        "POST /mcp/servers": ["mcp:servers:write"],
        "DELETE /mcp/servers/*": ["mcp:servers:delete"],
    }
)


def roles_to_scopes(roles: list[str]) -> list[str]:
    """Map Entra App Role names to deduplicated Agno scope strings."""
    scopes: set[str] = set()
    for role in roles:
        scopes.update(ROLE_SCOPE_MAP.get(role, []))
    return sorted(scopes)


def get_required_scopes(method: str, path: str) -> list[str] | None:
    """
    Get required scopes for a route.
    Returns None for excluded routes (no auth needed).
    Returns [] for routes not in the map (access allowed for any authenticated user).
    """
    # Try exact match first, then wildcard patterns
    key = f"{method.upper()} {path}"
    if key in _ROUTE_SCOPE_MAP:
        return _ROUTE_SCOPE_MAP[key]

    # Try wildcard matching (/* patterns)
    parts = path.split("/")
    for pattern, required in _ROUTE_SCOPE_MAP.items():
        p_method, p_path = pattern.split(" ", 1)
        if p_method != method.upper():
            continue
        p_parts = p_path.split("/")
        if len(p_parts) != len(parts):
            continue
        if all(pp == rp or pp == "*" for pp, rp in zip(p_parts, parts)):
            return required

    return ["agent_os:admin"]  # Unknown route — default-deny, require admin


# Re-export agno scope functions for use in middleware
__all__ = [
    "ROLE_SCOPE_MAP",
    "roles_to_scopes",
    "get_required_scopes",
    "has_required_scopes",
    "get_accessible_resource_ids",
]
