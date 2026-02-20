"""
Knowledge Agent
---------------

An agent that answers questions using a knowledge base.

Run:
    python -m backend.agents.knowledge_agent
"""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    SessionContextConfig,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.tools.file import FileTools

from backend.context.intent_routing import INTENT_ROUTING
from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model
from backend.tools import approved_ops, awareness, save_discovery, search
from backend.tools.approved_ops import add_knowledge_source
from backend.tools.awareness import list_knowledge_sources
from backend.tools.save_discovery import save_intent_discovery
from backend.tools.search import search_content

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
knowledge = create_knowledge("Knowledge Agent", "knowledge_agent_docs")
knowledge_learnings = create_knowledge("Knowledge Learnings", "knowledge_learnings")

# ---------------------------------------------------------------------------
# Documents directory for file browsing
# ---------------------------------------------------------------------------
DOCUMENTS_DIR = Path(getenv("DOCUMENTS_DIR", str(Path(__file__).parent.parent.parent / "data" / "docs")))

# Wire tools to the knowledge base instance
search.set_knowledge(knowledge)
awareness.set_knowledge(knowledge)
approved_ops.set_knowledge(knowledge)
save_discovery.set_knowledge(knowledge_learnings)

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = f"""\
You are a knowledge assistant. You answer questions by searching your knowledge base.

## How You Work

1. Search the knowledge base for relevant information
2. Answer based on what you find
3. Cite your sources
4. If the information isn't in the knowledge base, say so clearly

## Guidelines

- Provide **answers**, not just file paths or source names
- Read full documents when available — never answer from snippets alone
- Include source paths and section references in every answer
- Include specifics from the source: numbers, dates, names, code examples
- Don't hallucinate content that doesn't exist in the sources

## Confidence Signaling

- **High confidence**: Direct quote from an authoritative source with full path and section reference
- **Medium confidence**: Information found but in an unexpected location or from an older document
- **Low confidence**: Inferred from related documents, not explicitly stated

## Citation Pattern

Every answer MUST include:
1. The source path or name (e.g., `Agno Introduction` or `data/docs/guide.pdf`)
2. The specific section or heading when available
3. Key details from the source: numbers, dates, names

| Bad | Good |
|-----|------|
| "I found 3 results for 'auth'" | "JWT authentication uses HS256 by default. Source: `Agno First Agent`, Authentication section" |
| "See the API docs" | "Rate limit is 100 req/min per user. Source: `agno-docs/introduction.md`, Rate Limits heading" |

## When Information Is NOT Found

Be explicit, not evasive. List what you searched and suggest next steps.

| Bad | Good |
|-----|------|
| "I couldn't find that" | "I searched the knowledge base for 'webhook' and 'callback' but found no matches. This topic may not be documented yet." |
| "Try asking someone" | "No docs for custom middleware. Try searching web for 'Agno middleware' or ask the web search agent." |

{INTENT_ROUTING}

## When to Save Learning

After discovering a useful search strategy:
  save_learning(title="multi-term search for API docs", learning="Searching for 'create agent' + 'tools' gives better results than broad 'agent' search")

After a user correction:
  save_learning(title="correction: AgentOS requires FastAPI", learning="AgentOS.get_app() returns a FastAPI app, not a standalone server")

After finding that a source combination works well:
  save_learning(title="combine intro + first-agent for onboarding questions", learning="New user questions about getting started are best answered by combining these two sources")

DO NOT save user preferences to shared learnings — those are handled automatically by user profiles.
DO NOT save trivial or obvious information.

## When to Save Intent Discovery

After finding information in an unexpected location:
  save_intent_discovery(
      name="auth_config_in_agent_docs",
      intent="Find authentication configuration",
      location="agno-docs/first-agent.md",
      summary="Auth config examples are in the first-agent guide, not a dedicated auth page",
      search_terms=["authentication", "auth config", "jwt"],
  )

After a user asks a question you can now answer quickly:
  save_intent_discovery(
      name="rate_limits_location",
      intent="Find API rate limits",
      location="agno-docs/introduction.md",
      summary="Rate limits are documented in the introduction overview section",
      search_terms=["rate limit", "throttle", "api limits"],
  )

Use save_intent_discovery for LOCATION mappings (intent -> where to find it).
Use save_learning for STRATEGY insights (what search approach worked).
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
knowledge_agent = Agent(
    id="knowledge-agent",
    name="Knowledge Agent",
    model=get_model(),
    db=agent_db,
    knowledge=knowledge,
    instructions=instructions,
    tools=[
        FileTools(
            base_dir=DOCUMENTS_DIR,
            enable_read_file=True,
            enable_list_files=True,
            enable_search_files=True,
            enable_read_file_chunk=True,
            enable_save_file=False,
            enable_replace_file_chunk=False,
            enable_delete_file=False,
        ),
        search_content,
        list_knowledge_sources,
        add_knowledge_source,
        save_intent_discovery,
    ],
    search_knowledge=True,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=knowledge_learnings,
        ),
        user_profile=UserProfileConfig(db=agent_db),
        user_memory=UserMemoryConfig(db=agent_db),
        session_context=SessionContextConfig(db=agent_db),
    ),
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
    enable_session_summaries=True,
)


def load_default_documents() -> None:
    """Load default documents into the knowledge base.

    Loads URL-based documents and any PDF/CSV files from data/docs/.
    """
    from backend.knowledge.loaders import load_csv_documents, load_pdf_documents

    knowledge.insert(
        name="Agno Introduction",
        url="https://docs.agno.com/introduction.md",
        skip_if_exists=True,
    )
    knowledge.insert(
        name="Agno First Agent",
        url="https://docs.agno.com/first-agent.md",
        skip_if_exists=True,
    )

    load_pdf_documents(knowledge)
    load_csv_documents(knowledge)


if __name__ == "__main__":
    import sys

    if "--load-docs" in sys.argv:
        load_default_documents()
    else:
        from backend.cli import run_agent_cli

        run_agent_cli(knowledge_agent, default_question="What is Agno?")
