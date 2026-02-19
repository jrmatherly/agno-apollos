"""
Knowledge Agent
---------------

An agent that answers questions using a knowledge base.

Run:
    python -m backend.agents.knowledge_agent
"""

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode, UserMemoryConfig, UserProfileConfig

from backend.context.intent_routing import INTENT_ROUTING
from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model
from backend.tools.approved_ops import add_knowledge_source
from backend.tools.awareness import list_knowledge_sources
from backend.tools.search import search_content

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
knowledge = create_knowledge("Knowledge Agent", "knowledge_agent_docs")
knowledge_learnings = create_knowledge("Knowledge Learnings", "knowledge_learnings")

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

- Be direct and concise
- Quote relevant passages when they add value
- Provide code examples when asked
- Don't make up information - only use what's in the knowledge base

## Confidence Signaling

- When you find strong matches, answer directly with citations
- When matches are partial, say "Based on limited information in the knowledge base..."
- When no matches are found, say "I found no information on this topic" and suggest alternatives
- Never present uncertain information as definitive

{INTENT_ROUTING}

## Learning Guidelines

- Save a learning when you discover something that would help answer similar questions in the future
- Save patterns that worked well (search strategies, source combinations, answer structures)
- Save corrections when you initially gave wrong information and then corrected it
- Do NOT save user-specific preferences (those belong in user profiles, not shared learnings)
- Do NOT save trivial or obvious information
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
    tools=[search_content, list_knowledge_sources, add_knowledge_source],
    search_knowledge=True,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=knowledge_learnings,
        ),
        user_profile=UserProfileConfig(
            db=agent_db,
        ),
        user_memory=UserMemoryConfig(
            db=agent_db,
        ),
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
    load_default_documents()
