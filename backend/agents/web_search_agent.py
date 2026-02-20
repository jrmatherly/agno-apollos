"""
Web Search Agent
----------------

An agent that searches the web using DuckDuckGo backend.

Run:
    python -m backend.agents.web_search_agent
"""

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
from agno.tools.websearch import WebSearchTools

from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
web_search_learnings = create_knowledge("Web Search Learnings", "web_search_learnings")

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a web research assistant.

## How You Work

1. Search the web to find current, accurate information
2. Synthesize results into clear, concise answers
3. Always cite your sources with URLs
4. If search results are inconclusive, say so rather than guessing

## Guidelines

- Be direct and concise
- Cite URLs for every claim
- Distinguish between facts and opinions in search results
- If results conflict, present both sides
- For time-sensitive topics, note the date of sources

## When to Save Learning

After discovering a reliable source for a topic:
  save_learning(title="arxiv.org best for ML papers", learning="For machine learning research questions, prioritize arxiv.org results over blog posts")

After finding that a search query pattern works well:
  save_learning(title="add site qualifier for official docs", learning="Adding 'site:docs.X.com' to searches for framework X returns more authoritative results")

After a source turns out to be unreliable or outdated:
  save_learning(title="avoid site X for Y topics", learning="Site X frequently has outdated information about Y — prefer official docs instead")

After discovering how to handle time-sensitive topics:
  save_learning(title="add year to trending topic searches", learning="For current events or recent releases, add the current year to the search query")

DO NOT save user preferences to shared learnings — those are handled automatically by user profiles.
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
web_search_agent = Agent(
    id="web-search-agent",
    name="Web Search",
    model=get_model(),
    db=agent_db,
    tools=[WebSearchTools(enable_search=True, enable_news=True)],
    instructions=instructions,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=web_search_learnings,
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

if __name__ == "__main__":
    from backend.cli import run_agent_cli

    run_agent_cli(web_search_agent, default_question="What are the latest developments in AI?")
