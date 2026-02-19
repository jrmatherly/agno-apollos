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

from backend.agents.knowledge_agent import knowledge_agent
from backend.agents.mcp_agent import mcp_agent
from backend.agents.web_search_agent import web_search_agent
from backend.db import get_postgres_db
from backend.teams.research_team import research_team

# ---------------------------------------------------------------------------
# Create Apollos AI
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Apollos AI",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[knowledge_agent, mcp_agent, web_search_agent],
    teams=[research_team],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="backend.main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
