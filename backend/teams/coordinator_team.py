"""
Coordinator Team
-----------------

Intelligent router that delegates queries to specialist agents.
Users interact with this team by default — specialist selection
is automatic based on query intent, with optional hints from the UI.
"""

from os import getenv

from agno.team import Team
from agno.team.team import TeamMode
from agno.tools.reasoning import ReasoningTools

from backend.agents.data_agent import data_agent
from backend.agents.knowledge_agent import knowledge_agent
from backend.agents.mcp_agent import mcp_agent
from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.web_search_agent import web_search_agent
from backend.db import get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
team_db = get_postgres_db()


# ---------------------------------------------------------------------------
# Members — callable factory defers MCPTools resolution to per-run
# ---------------------------------------------------------------------------
def _get_members():
    members = [knowledge_agent, mcp_agent, data_agent, web_search_agent, reasoning_agent]
    if getenv("M365_ENABLED", "").lower() in ("true", "1", "yes"):
        from backend.agents.m365_agent import m365_agent

        members.append(m365_agent)
    return members


# ---------------------------------------------------------------------------
# Coordinator Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are the Apollos AI coordinator. Analyze each user query and delegate
to the single best specialist.

## Routing Rules

- **Knowledge Agent**: Questions about documents, policies, internal knowledge base,
  file browsing, or anything requiring the curated knowledge base.
- **MCP Agent**: Questions about connected tools and integrations, API documentation,
  or tasks requiring external MCP-connected services.
- **Data Agent**: SQL queries, data analysis, table lookups, charts, metrics,
  or questions about structured data.
- **Web Search Agent**: Current events, external information, web lookups,
  or anything requiring live internet data.
- **Reasoning Agent**: Complex multi-step reasoning, analysis, comparisons,
  or tasks requiring structured thinking.
- **Microsoft 365 Agent** (when available): Email, calendar, OneDrive,
  SharePoint, Teams — anything involving the user's M365 resources.

## Specialist Hints

If the user message starts with `[hints: ...]`, prefer routing to those
specialists. Hints are suggestions, not hard constraints — if the query
clearly belongs to a different specialist, route there instead.
Strip the `[hints: ...]` prefix before passing the query to the specialist.

## Default Behavior

When no hints are provided, analyze the query and route to the single best
specialist. If uncertain, prefer the Knowledge Agent.
Always provide a final, consolidated answer to the user.
"""

# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------
coordinator_team = Team(
    name="Apollos Coordinator",
    id="apollos-coordinator",
    mode=TeamMode.coordinate,
    model=get_model(),
    db=team_db,
    members=_get_members,
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[instructions],
    markdown=True,
    compress_tool_results=True,
    max_iterations=5,
    store_history_messages=True,
    share_member_interactions=True,
    num_history_runs=5,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    enable_session_summaries=True,
)
