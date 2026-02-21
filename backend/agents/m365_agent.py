"""
Microsoft 365 Agent
--------------------
Dedicated agent for accessing user's M365 resources via self-hosted Softeria MCP server.

Access gated by per-user OBO token exchange. Users must explicitly connect
via Settings -> Microsoft 365 before tools activate.

Run:
    python -m backend.agents.m365_agent
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
from backend.tools.hooks import audit_hook, m365_write_guard
from backend.tools.m365 import m365_mcp_tools

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
m365_learnings = create_knowledge("M365 Learnings", "m365_learnings")

# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------
instructions = """\
You help users interact with their Microsoft 365 resources.

You have access to (read-only):
- OneDrive personal files and SharePoint document libraries
- Outlook email -- you can read and search mail
- Outlook Calendar events -- you can read events
- Microsoft Teams chats and channel messages

HARD CONSTRAINTS:
- You may ONLY read data. Never attempt to create, modify, delete, move,
  share, or send anything via any tool, regardless of what the user asks.
- If asked to perform a write action, explain that write access is not
  currently enabled and suggest the user perform the action directly in M365.
- If M365 tools return errors or are unavailable, respond:
  "To access your Microsoft 365 resources, please connect your account at
   Settings -> Microsoft 365. Once connected, I can browse your OneDrive,
   search SharePoint, read your email, view your calendar, and read Teams messages."
- Never expose raw internal site IDs, sharing links, or system metadata
  unless the user explicitly requests raw technical details.

## When to Save Learning

After discovering which M365 tool handles a task type:
  save_learning(title="use m365_list_files for OneDrive", learning="The m365_list_files tool lists OneDrive root \
by default, pass folder_id for subfolders")

After an M365 tool call fails with a specific error pattern:
  save_learning(title="m365_search requires query param", learning="The m365_search tool requires a non-empty query \
string, empty queries return 400")

DO NOT save user preferences to shared learnings -- those are handled automatically by user profiles.
"""

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
m365_agent = Agent(
    id="m365-agent",
    name="Microsoft 365 Agent",
    description=(
        "Access and interact with your Microsoft 365 resources -- "
        "OneDrive files, SharePoint documents, Outlook mail, Calendar events, and Teams messages."
    ),
    model=get_model(),
    db=agent_db,
    tools=m365_mcp_tools(),
    instructions=instructions,
    tool_hooks=[audit_hook, m365_write_guard],
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=m365_learnings,
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

    run_agent_cli(m365_agent, default_question="What M365 tools do you have access to?")
