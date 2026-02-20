"""
A2A Server
----------

Sets up A2A protocol endpoints for all registered agents.
Each agent gets an AgentCard for discovery and a handler for messages.

Discovery: GET /.well-known/agent.json (A2A convention)
Messages:  POST /a2a/agents/{agent-id} (send/stream)
"""

import logging
from os import getenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agno.agent import Agent
from starlette.types import ASGIApp

from backend.a2a.executor import AgnoAgentExecutor

logger = logging.getLogger(__name__)

# Agent metadata for AgentCards (descriptions and skills)
AGENT_METADATA: dict[str, dict] = {
    "knowledge-agent": {
        "description": "Answer questions from loaded documents and a curated knowledge base with source citations",
        "skills": [
            {
                "id": "knowledge-qa",
                "name": "Knowledge Q&A",
                "description": "Answer questions from loaded documents and knowledge base",
            },
        ],
    },
    "data-agent": {
        "description": "Query PostgreSQL databases, analyze data with SQL, and explain results in natural language",
        "skills": [
            {"id": "data-query", "name": "Data Query", "description": "Query databases and analyze data with SQL"},
        ],
    },
    "web-search-agent": {
        "description": "Search the web for current information, news, and real-time data",
        "skills": [
            {
                "id": "web-search",
                "name": "Web Search",
                "description": "Search the web for current information and news",
            },
        ],
    },
    "reasoning-agent": {
        "description": "Analyze complex topics with structured multi-step reasoning and produce comprehensive reports",
        "skills": [
            {
                "id": "reasoning",
                "name": "Multi-Step Reasoning",
                "description": "Analyze complex topics with structured reasoning",
            },
        ],
    },
    "mcp-agent": {
        "description": "Execute tools and access services via Model Context Protocol servers",
        "skills": [
            {
                "id": "mcp-tools",
                "name": "MCP Tool Execution",
                "description": "Execute tools via Model Context Protocol",
            },
        ],
    },
}


def create_agent_card(agent: Agent, base_url: str) -> AgentCard:
    """Create an A2A AgentCard for an Agno agent."""
    metadata = AGENT_METADATA.get(agent.id or "", {})
    skills = metadata.get("skills", [])
    # Use metadata description (preferred), then agent attrs, then generic fallback
    description = metadata.get("description") or str(agent.description or agent.role or f"{agent.name} agent")
    return AgentCard(
        name=agent.name or agent.id or "Unknown",
        description=description,
        url=f"{base_url}/a2a/agents/{agent.id}",
        version=getenv("APP_VERSION", "1.0.0"),
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[AgentSkill(**skill) for skill in skills],
    )


def create_a2a_apps(agents: list[Agent], base_url: str) -> list[tuple[str, ASGIApp]]:
    """Create A2A Starlette apps for all agents.

    Returns a list of (mount_path, asgi_app) tuples for mounting on the FastAPI app.
    Use app.mount(path, asgi_app) for each pair — this is the standard FastAPI
    pattern for sub-applications and avoids fragile app.routes.append().
    """
    mounts: list[tuple[str, ASGIApp]] = []

    for agent in agents:
        if not agent.id:
            logger.warning("Skipping agent without ID for A2A: %s", agent.name)
            continue

        card = create_agent_card(agent, base_url)
        executor = AgnoAgentExecutor(agent)
        handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        a2a_app = A2AStarletteApplication(
            agent_card=card,
            http_handler=handler,
        )

        path = f"/a2a/agents/{agent.id}"
        mounts.append((path, a2a_app.build()))
        logger.info("A2A endpoint registered: %s", path)

    logger.info("A2A server configured with %d agent(s)", len(mounts))
    return mounts
