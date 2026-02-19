"""
Web Search Agent
----------------

An agent that searches the web using DuckDuckGo backend.

Run:
    python -m backend.agents.web_search_agent
"""

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.tools.websearch import WebSearchTools

from backend.db import get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

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
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    web_search_agent.print_response("What are the latest developments in AI?", stream=True)
