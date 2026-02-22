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
        "mcp:tools:read",
        "mcp:tools:write",
        "mcp:tools:delete",
        "mcp:virtual-servers:read",
        "mcp:virtual-servers:write",
        "mcp:virtual-servers:delete",
        "mcp:resources:read",
        "mcp:resources:write",
        "mcp:resources:delete",
        "mcp:prompts:read",
        "mcp:prompts:write",
        "mcp:prompts:delete",
        "mcp:config:read",
        "mcp:config:write",
        "mcp:preferences:read",
        "mcp:preferences:write",
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
        "mcp:tools:read",
        "mcp:virtual-servers:read",
        "mcp:resources:read",
        "mcp:prompts:read",
        "mcp:preferences:read",
        "mcp:preferences:write",
    ],
    "Developer": [
        "agents:run",
        "agents:read",
        "sessions:read",
        "sessions:write",
        "mcp:servers:read",
        "mcp:tools:call",
        "mcp:tools:read",
        "mcp:virtual-servers:read",
        "mcp:resources:read",
        "mcp:prompts:read",
        "mcp:preferences:read",
        "mcp:preferences:write",
    ],
    "DevOps": [
        "system:read",
        "metrics:read",
        "metrics:write",
        "agents:run",
        "agents:read",
        "traces:read",
        "schedules:read",
        "mcp:tools:read",
        "mcp:virtual-servers:read",
        "mcp:resources:read",
        "mcp:prompts:read",
        "mcp:config:read",
        "mcp:preferences:read",
        "mcp:preferences:write",
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
        "mcp:tools:read",
        "mcp:virtual-servers:read",
        "mcp:resources:read",
        "mcp:prompts:read",
        "mcp:preferences:read",
        "mcp:preferences:write",
    ],
}

# Cache the default mappings once (they don't change)
_ROUTE_SCOPE_MAP: dict[str, list[str]] = get_default_scope_mappings()

# MCP Gateway route scopes (added on top of Agno defaults)
_ROUTE_SCOPE_MAP.update(
    {
        # Gateways (registered upstream MCP servers)
        "GET /mcp/servers": ["mcp:servers:read"],
        "GET /mcp/servers/*": ["mcp:servers:read"],
        "POST /mcp/servers": ["mcp:servers:write"],
        "DELETE /mcp/servers/*": ["mcp:servers:delete"],
        # Gateway mutations (HIGH-1 fix: previously missing)
        "PUT /mcp/servers/*": ["mcp:servers:write"],
        "POST /mcp/servers/*/state": ["mcp:servers:write"],
        "POST /mcp/servers/*/refresh": ["mcp:servers:write"],
        # Tools
        "GET /mcp/tools": ["mcp:tools:read"],
        "GET /mcp/tools/*": ["mcp:tools:read"],
        "POST /mcp/tools": ["mcp:tools:write"],
        "PUT /mcp/tools/*": ["mcp:tools:write"],
        "DELETE /mcp/tools/*": ["mcp:tools:delete"],
        "POST /mcp/tools/*/state": ["mcp:tools:write"],
        # Virtual servers
        "GET /mcp/virtual-servers": ["mcp:virtual-servers:read"],
        "GET /mcp/virtual-servers/*": ["mcp:virtual-servers:read"],
        "POST /mcp/virtual-servers": ["mcp:virtual-servers:write"],
        "PUT /mcp/virtual-servers/*": ["mcp:virtual-servers:write"],
        "DELETE /mcp/virtual-servers/*": ["mcp:virtual-servers:delete"],
        "POST /mcp/virtual-servers/*/state": ["mcp:virtual-servers:write"],
        # Virtual server sub-resources (HIGH-1 fix: previously missing)
        "GET /mcp/virtual-servers/*/tools": ["mcp:virtual-servers:read"],
        "GET /mcp/virtual-servers/*/resources": ["mcp:virtual-servers:read"],
        "GET /mcp/virtual-servers/*/prompts": ["mcp:virtual-servers:read"],
        # Resources
        "GET /mcp/resources": ["mcp:resources:read"],
        "GET /mcp/resources/*": ["mcp:resources:read"],
        "POST /mcp/resources": ["mcp:resources:write"],
        "PUT /mcp/resources/*": ["mcp:resources:write"],
        "DELETE /mcp/resources/*": ["mcp:resources:delete"],
        "POST /mcp/resources/*/state": ["mcp:resources:write"],
        # Resource sub-routes (HIGH-1 fix: previously missing)
        "GET /mcp/resources/*/info": ["mcp:resources:read"],
        "GET /mcp/resources/templates": ["mcp:resources:read"],
        # Prompts
        "GET /mcp/prompts": ["mcp:prompts:read"],
        "GET /mcp/prompts/*": ["mcp:prompts:read"],
        "POST /mcp/prompts": ["mcp:prompts:write"],
        "PUT /mcp/prompts/*": ["mcp:prompts:write"],
        "DELETE /mcp/prompts/*": ["mcp:prompts:delete"],
        "POST /mcp/prompts/*/state": ["mcp:prompts:write"],
        # Tags — any authenticated user (MEDIUM-5 fix)
        "GET /mcp/tags": [],
        "GET /mcp/tags/*": [],
        # Import/Export
        "GET /mcp/export": ["mcp:config:read"],
        "POST /mcp/import": ["mcp:config:write"],
        "GET /mcp/import/status": ["mcp:config:read"],
        "GET /mcp/import/status/*": ["mcp:config:read"],
        # Health (no auth required)
        "GET /mcp/health": [],
        "GET /mcp/version": [],
        # Preferences
        "GET /mcp/preferences": ["mcp:preferences:read"],
        "PUT /mcp/preferences": ["mcp:preferences:write"],
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
