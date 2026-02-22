"""Pydantic schemas for MCP Gateway proxy routes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Constrained types for MCP entity visibility and workspace tabs
MCPVisibility = Literal["public", "private", "team"]
MCPTab = Literal["servers", "tools", "virtual-servers", "resources", "prompts", "config"]

# ── Existing Gateway Schemas ──────────────────────────────────────────


class MCPServerInfo(BaseModel):
    """Summary of a registered MCP server from the gateway."""

    id: str
    name: str
    url: str
    status: str | None = None


class MCPServerRegister(BaseModel):
    """Request body for registering an upstream MCP server."""

    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    url: str = Field(..., min_length=1)


class MCPServerResponse(BaseModel):
    """Response after registering a server."""

    id: str
    name: str
    url: str


class MCPServerUpdate(BaseModel):
    """Request body for updating a registered MCP server (gateway)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


# ── State Toggle ──────────────────────────────────────────────────────


class MCPStateToggle(BaseModel):
    """Request body for enabling/disabling an entity.
    Proxy route converts this to ?activate=bool query param for ContextForge.
    """

    activate: bool


# ── Tools ─────────────────────────────────────────────────────────────


class MCPToolInfo(BaseModel):
    """Tool from the gateway. Fields match ContextForge ToolRead."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    gateway_id: str | None = None
    tags: list[str] = []
    is_active: bool = True
    input_schema: dict | None = None
    annotations: dict | None = None
    visibility: MCPVisibility | None = None
    team_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class MCPToolCreate(BaseModel):
    """Request body for creating a tool."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    gateway_id: str | None = None
    tags: list[str] = []
    team_id: str | None = None
    visibility: MCPVisibility = "public"


class MCPToolUpdate(BaseModel):
    """Request body for updating a tool."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    tags: list[str] | None = None


# ── Virtual Servers ───────────────────────────────────────────────────


class MCPVirtualServerInfo(BaseModel):
    """Virtual server (ContextForge 'server'). Fields match ContextForge ServerRead."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    is_active: bool = True
    tags: list[str] = []
    visibility: MCPVisibility | None = None
    team_id: str | None = None


class MCPVirtualServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    team_id: str | None = None
    visibility: MCPVisibility = "public"


class MCPVirtualServerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


# ── Resources ─────────────────────────────────────────────────────────


class MCPResourceInfo(BaseModel):
    """Resource from the gateway. Fields match ContextForge ResourceRead."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    uri: str | None = None
    description: str | None = None
    mime_type: str | None = None
    is_active: bool = True
    annotations: dict | None = None
    visibility: MCPVisibility | None = None
    team_id: str | None = None


class MCPResourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    uri: str | None = None
    description: str | None = None
    mime_type: str | None = None
    team_id: str | None = None
    visibility: MCPVisibility = "public"


class MCPResourceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


# ── Prompts ───────────────────────────────────────────────────────────


class MCPPromptArgument(BaseModel):
    """A prompt argument definition."""

    model_config = ConfigDict(extra="ignore")

    name: str
    description: str | None = None
    required: bool = False


class MCPPromptInfo(BaseModel):
    """Prompt from the gateway. Fields match ContextForge PromptRead."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    is_active: bool = True
    arguments: list[MCPPromptArgument] = []
    visibility: MCPVisibility | None = None
    team_id: str | None = None


class MCPPromptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    team_id: str | None = None
    visibility: MCPVisibility = "public"


class MCPPromptUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


# ── Tags ──────────────────────────────────────────────────────────────
# CORRECTION: ContextForge TagInfo returns nested stats, not flat count.


class MCPTagStats(BaseModel):
    """Per-entity-type usage counts for a tag."""

    tools: int = 0
    resources: int = 0
    prompts: int = 0
    servers: int = 0
    gateways: int = 0
    total: int = 0


class MCPTagInfo(BaseModel):
    """A tag with usage statistics. Matches ContextForge TagInfo response."""

    model_config = ConfigDict(extra="ignore")

    name: str
    stats: MCPTagStats = Field(default_factory=MCPTagStats)
    entities: list[dict] = []


class MCPTagEntities(BaseModel):
    """Entities associated with a tag."""

    tag: str
    entities: list[dict] = []


# ── Import/Export ─────────────────────────────────────────────────────


class MCPExportResponse(BaseModel):
    """Response from config export."""

    data: dict


class MCPImportRequest(BaseModel):
    """Request body for config import."""

    data: dict
    conflict_strategy: str = Field("update", pattern=r"^(skip|update|rename|fail)$")
    dry_run: bool = False


class MCPImportResponse(BaseModel):
    """Response from config import."""

    import_id: str | None = None
    status: str
    summary: dict = {}


# ── Health ────────────────────────────────────────────────────────────


class MCPHealthResponse(BaseModel):
    """Gateway health check response."""

    status: str
    version: str | None = None


# ── Preferences ───────────────────────────────────────────────────────


class MCPUserPreferences(BaseModel):
    """Per-user MCP workspace preferences."""

    hidden_tools: list[str] = []
    hidden_servers: list[str] = []
    default_tab: MCPTab = "servers"
    compact_view: bool = False
