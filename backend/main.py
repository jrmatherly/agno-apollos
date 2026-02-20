"""
Apollos AI
----------

The main entry point for Apollos AI.

Run:
    python -m backend.main
"""

from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.os.config import AuthorizationConfig

from backend.agents.data_agent import data_agent
from backend.agents.knowledge_agent import knowledge_agent
from backend.agents.mcp_agent import mcp_agent
from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.web_search_agent import web_search_agent
from backend.db import get_postgres_db
from backend.registry import create_registry
from backend.teams.research_team import research_team
from backend.telemetry import configure_telemetry
from backend.workflows.research_workflow import research_workflow

# ---------------------------------------------------------------------------
# Telemetry (no-ops if OTEL_EXPORTER_OTLP_ENDPOINT is not set)
# ---------------------------------------------------------------------------
configure_telemetry()

# ---------------------------------------------------------------------------
# Component Registry (enables Agent-as-Config save/load/version)
# ---------------------------------------------------------------------------
registry = create_registry()

# ---------------------------------------------------------------------------
# Create Apollos AI
# ---------------------------------------------------------------------------
jwt_secret = getenv("JWT_SECRET_KEY", "")

agent_os = AgentOS(
    name="Apollos AI",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[knowledge_agent, mcp_agent, web_search_agent, data_agent, reasoning_agent],
    teams=[research_team],
    workflows=[research_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
    enable_mcp_server=True,
    registry=registry,
    authorization=bool(jwt_secret),
    authorization_config=AuthorizationConfig(
        verification_keys=[jwt_secret] if jwt_secret else None,
        algorithm="HS256",
    )
    if jwt_secret
    else None,
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="backend.main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
