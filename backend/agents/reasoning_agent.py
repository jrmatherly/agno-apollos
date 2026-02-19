"""
Reasoning Agent
---------------

Standalone agent for complex analysis tasks with step-by-step reasoning.
Uses Agno's built-in reasoning capability (reasoning=True) for structured thinking.
"""

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

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
You are a reasoning and analysis assistant.

## How You Work

1. Break down complex problems step by step
2. Consider multiple perspectives before concluding
3. Show your reasoning process clearly
4. If a problem has multiple valid answers, present them all with trade-offs

## Guidelines

- Be thorough but concise
- Identify assumptions and state them explicitly
- When comparing options, use structured tables
- If you need more information to give a good answer, ask
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
reasoning_agent = Agent(
    id="reasoning-agent",
    name="Reasoning Agent",
    model=get_model(),
    db=agent_db,
    instructions=instructions,
    reasoning=True,
    reasoning_min_steps=2,
    reasoning_max_steps=6,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
