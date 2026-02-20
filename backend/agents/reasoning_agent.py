"""
Reasoning Agent
---------------

Standalone agent for complex analysis tasks with step-by-step reasoning.
Uses Agno's built-in reasoning capability (reasoning=True) for structured thinking.
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

from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
reasoning_learnings = create_knowledge("Reasoning Learnings", "reasoning_learnings")

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

## When to Save Learning

After finding an effective reasoning approach for a question type:
  save_learning(title="comparison tasks: use structured table", learning="When users ask to compare options, a table with pros/cons/trade-offs is more effective than prose")

After discovering that a question type needs specific depth:
  save_learning(title="math proofs need 4+ steps", learning="Mathematical proofs and formal logic benefit from at least 4 reasoning steps for clarity")

After a user indicates your reasoning was unclear:
  save_learning(title="avoid nested conditionals in explanation", learning="Flatten nested if/then reasoning into numbered steps for clarity")

DO NOT save user preferences to shared learnings — those are handled automatically by user profiles.
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
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=reasoning_learnings,
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

    run_agent_cli(reasoning_agent, default_question="Walk me through the pros and cons of microservices vs monoliths.")
