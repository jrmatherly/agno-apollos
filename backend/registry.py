"""
Component Registry
------------------

Central registry for non-serializable components (tools, models, functions).
Used by AgentOS for Agent-as-Config persistence — enables save/load/version
of agents, teams, and workflows to PostgreSQL.

When an agent is saved, tools and functions are serialized by name.
The Registry restores them to full callables when loading.
"""

from os import getenv

from agno.registry import Registry
from agno.tools.mcp import MCPTools
from agno.tools.postgres import PostgresTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.websearch import WebSearchTools

from backend.db import get_postgres_db
from backend.db.session import create_knowledge
from backend.db.url import db_url
from backend.models import get_model
from backend.tools.approved_ops import add_knowledge_source
from backend.tools.awareness import list_knowledge_sources
from backend.tools.introspect import create_introspect_schema_tool
from backend.tools.save_query import create_save_validated_query_tool
from backend.tools.search import search_content


def create_registry() -> Registry:
    """Build the central component registry.

    All non-serializable components (tools, models, databases, custom
    functions) must be registered here so that agents, teams, and
    workflows can be restored from saved configurations.
    """
    # Instantiate factory-created tools (need state at creation time)
    data_knowledge = create_knowledge("Data Knowledge", "data_knowledge")
    save_validated_query = create_save_validated_query_tool(data_knowledge)
    introspect_schema = create_introspect_schema_tool(db_url)

    return Registry(
        name="apollos-registry",
        description="Apollos AI component registry",
        tools=[
            # Knowledge agent tools
            WebSearchTools(enable_search=True, enable_news=True),
            # Data agent tools
            PostgresTools(
                host=getenv("DB_HOST", "apollos-db"),
                port=int(getenv("DB_PORT", "5432")),
                user=getenv("DB_USER", "ai"),
                password=getenv("DB_PASS", "ai"),
                db_name=getenv("DB_DATABASE", "ai"),
                include_tools=["show_tables", "describe_table", "summarize_table", "inspect_query"],
            ),
            # MCP agent tools
            MCPTools(url="https://docs.agno.com/mcp"),
            # Team tools
            ReasoningTools(add_instructions=True),
        ],
        functions=[
            # Knowledge agent custom tools
            search_content,  # type: ignore[list-item]  # Agno @tool wraps Callable
            list_knowledge_sources,  # type: ignore[list-item]
            add_knowledge_source,  # type: ignore[list-item]
            # Data agent custom tools
            save_validated_query,
            introspect_schema,
        ],
        models=[get_model()],
        dbs=[get_postgres_db()],
    )
