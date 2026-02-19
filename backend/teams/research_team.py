"""
Research Team
-------------

Multi-agent team with web search and reasoning capabilities.
Coordinates a Web Researcher and an Analyst to produce comprehensive research.
"""

from agno.agent import Agent
from agno.team import Team
from agno.team.team import TeamMode
from agno.tools.reasoning import ReasoningTools
from agno.tools.websearch import WebSearchTools

from backend.db import get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
team_db = get_postgres_db()

# ---------------------------------------------------------------------------
# Team Members
# ---------------------------------------------------------------------------
web_researcher = Agent(
    name="Web Researcher",
    role="Search the web for current information",
    model=get_model(),
    tools=[WebSearchTools(enable_search=True, enable_news=True)],
    instructions=[
        "Search the web to find relevant, current information.",
        "Always cite sources with URLs.",
        "Provide concise, factual summaries.",
    ],
    markdown=True,
)

analyst = Agent(
    name="Analyst",
    role="Analyze information and synthesize findings",
    model=get_model(),
    instructions=[
        "Analyze the information provided by team members.",
        "Identify patterns, contradictions, and gaps.",
        "Provide structured analysis with clear conclusions.",
        "Use the think tool for complex multi-step reasoning.",
    ],
    markdown=True,
)

# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------
research_team = Team(
    name="Research Team",
    id="research-team",
    mode=TeamMode.coordinate,
    model=get_model(),
    db=team_db,
    members=[web_researcher, analyst],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "You lead a research team with a web researcher and an analyst.",
        "For factual questions, delegate to the Web Researcher.",
        "For analysis and synthesis, delegate to the Analyst.",
        "For complex questions, have the Researcher gather data, then the Analyst synthesize.",
        "Always provide a final, consolidated answer.",
    ],
    markdown=True,
    compress_tool_results=True,
    max_iterations=5,
    store_history_messages=True,
    share_member_interactions=True,
    num_history_runs=5,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
)
