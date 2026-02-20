"""
MCP Agent
---------

An agent that uses MCP tools to answer questions.

Run:
    python -m backend.agents.mcp_agent
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
from agno.tools.mcp import MCPTools

from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
mcp_learnings = create_knowledge("MCP Learnings", "mcp_learnings")

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a helpful assistant with access to external tools via MCP (Model Context Protocol).

## How You Work

1. Understand what the user needs
2. Use your tools to find information or take action
3. Provide clear answers based on tool results
4. If a tool can't help, say so and suggest alternatives

## Guidelines

- Be direct and concise
- Explain what you're doing when using tools
- Provide code examples when asked
- If you're unsure which tool to use, ask for clarification

## When to Save Learning

After discovering which tool handles a task type:
  save_learning(title="use search_docs for API questions", learning="The search_docs tool returns better results for API-specific questions than general search")

After an MCP tool call fails with a specific error pattern:
  save_learning(title="tool X requires param Y format", learning="Tool X expects dates in ISO 8601 format, not natural language")

After finding an effective tool combination:
  save_learning(title="search then fetch for deep answers", learning="Search first to find the right page, then fetch the full content for detailed answers")

DO NOT save user preferences to shared learnings — those are handled automatically by user profiles.
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
mcp_agent = Agent(
    id="mcp-agent",
    name="MCP Agent",
    model=get_model(),
    db=agent_db,
    tools=[MCPTools(url="https://docs.agno.com/mcp")],
    instructions=instructions,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=mcp_learnings,
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

    run_agent_cli(mcp_agent, default_question="What tools do you have access to?")
