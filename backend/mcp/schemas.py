"""Pydantic schemas for MCP Gateway proxy routes."""

from __future__ import annotations

from pydantic import BaseModel, Field


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
