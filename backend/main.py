"""
Apollos AI
----------

The main entry point for Apollos AI.

Run:
    python -m backend.main
"""

import logging
import warnings
from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.agent.remote import RemoteAgent
from agno.os import AgentOS
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.a2a.server import create_a2a_apps
from backend.agents.data_agent import data_agent
from backend.agents.knowledge_agent import knowledge_agent
from backend.agents.mcp_agent import mcp_agent
from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.web_search_agent import web_search_agent
from backend.auth import EntraJWTMiddleware, auth_lifespan, auth_router
from backend.auth.config import auth_config
from backend.auth.jwks_cache import jwks_cache
from backend.auth.routes import limiter
from backend.auth.security_headers import SecurityHeadersMiddleware
from backend.db import get_postgres_db
from backend.registry import create_registry
from backend.teams.coordinator_team import coordinator_team
from backend.teams.research_team import research_team
from backend.telemetry import configure_telemetry
from backend.workflows.research_workflow import research_workflow

# Agno 2.5.x uses the deprecated `streamablehttp_client` alias from MCP SDK 1.26+.
# Suppress until Agno updates to `streamable_http_client`.
warnings.filterwarnings(
    "ignore",
    message=r".*streamable_http_client.*",
    category=DeprecationWarning,
    module=r"mcp\..*",
)

# ---------------------------------------------------------------------------
# Telemetry (no-ops if OTEL_EXPORTER_OTLP_ENDPOINT is not set)
# ---------------------------------------------------------------------------
configure_telemetry()

# ---------------------------------------------------------------------------
# Component Registry (enables Agent-as-Config save/load/version)
# ---------------------------------------------------------------------------
registry = create_registry()

# ---------------------------------------------------------------------------
# Base FastAPI app with Entra ID JWT middleware
# ---------------------------------------------------------------------------
# base_app is passed to AgentOS, which mounts all AgentOS routes on top.
# EntraJWTMiddleware runs for every request, sets request.state per the
# AgentOS middleware contract (authenticated, user_id, scopes, etc.).
# When auth_config.enabled is False (Azure env vars not set), middleware
# passes all requests through unauthenticated — safe local dev mode.
base_app = FastAPI()
base_app.state.limiter = limiter
base_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
# Middleware order (LIFO): SecurityHeaders first → runs after JWT on response
base_app.add_middleware(SecurityHeadersMiddleware)
base_app.add_middleware(EntraJWTMiddleware, config=auth_config, jwks_cache=jwks_cache)
base_app.include_router(auth_router)  # /auth/health, /auth/me, /auth/sync, etc.

# M365 routes (opt-in via M365_ENABLED) — no middleware needed, token resolved
# directly in MCPTools header_provider via run_context.user_id + OBOTokenService
if getenv("M365_ENABLED", "").lower() in ("true", "1", "yes"):
    from backend.auth.m365_routes import m365_router

    base_app.include_router(m365_router)

# ---------------------------------------------------------------------------
# Agent list (M365 agent opt-in via M365_ENABLED)
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)
_agents: list[Agent | RemoteAgent] = [knowledge_agent, mcp_agent, web_search_agent, data_agent, reasoning_agent]

if getenv("M365_ENABLED", "").lower() in ("true", "1", "yes"):
    from backend.agents.m365_agent import m365_agent

    _agents.append(m365_agent)
    log.info("M365 agent registered")

# ---------------------------------------------------------------------------
# Create Apollos AI
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Apollos AI",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=_agents,
    teams=[coordinator_team, research_team],
    workflows=[research_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
    enable_mcp_server=True,
    registry=registry,
    base_app=base_app,  # Custom FastAPI app with JWT middleware pre-wired
    lifespan=auth_lifespan,  # Initializes JWKS cache, auth tables, background sync
    cors_allowed_origins=[auth_config.frontend_url] if auth_config.frontend_url else None,
    # NO authorization=True — auth is fully handled by EntraJWTMiddleware on base_app
    # NO authorization_config — not applicable for RS256 Entra ID tokens
)

app = agent_os.get_app()

# ---------------------------------------------------------------------------
# A2A Protocol Endpoints (opt-in via A2A_ENABLED env var)
# ---------------------------------------------------------------------------
if getenv("A2A_ENABLED", "").lower() in ("true", "1", "yes"):
    a2a_base_url = getenv("A2A_BASE_URL", "http://localhost:8000")
    a2a_mounts = create_a2a_apps(
        agents=[knowledge_agent, mcp_agent, web_search_agent, data_agent, reasoning_agent],
        base_url=a2a_base_url,
    )
    for path, a2a_app in a2a_mounts:
        app.mount(path, a2a_app)

if __name__ == "__main__":
    agent_os.serve(
        app="backend.main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
