---
name: add-agent
description: Scaffold a new Agno agent with boilerplate, register in main.py, and add config.yaml entry
disable-model-invocation: true
---

# Add Agent

Create a new Agno agent and integrate it into Apollos AI.

## Steps

### 1. Gather Details

Ask the user for:
- **Agent name** (human-readable, e.g., "Research Agent")
- **Agent ID** (slug, e.g., "research-agent")
- **Description** (one-line purpose)
- **Tools** (optional, any Agno tool integrations needed)

### 2. Create Agent Module

Create `backend/agents/{id_with_underscores}.py` following this pattern:

```python
from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

from backend.db import get_postgres_db
from backend.models import get_model

{variable_name} = Agent(
    id="{agent-id}",
    name="{Agent Name}",
    model=get_model(),
    db=get_postgres_db(),
    instructions=["{description}"],
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    enable_agentic_memory=True,
    enable_session_summaries=True,
    add_datetime_to_context=True,
    num_history_runs=5,
    markdown=True,
)
```

Key conventions:
- Use `get_model()` from `backend/models.py` (never inline `LiteLLMOpenAI`)
- Always pass `db=get_postgres_db()` for persistent state
- Always include guardrails (`pre_hooks`) — this is mandatory for all agents
- Enable agentic memory and session summaries by default

### 3. Register in main.py

Add the import and include in the agents list:

```python
from backend.agents.{module_name} import {variable_name}

agent_os = AgentOS(
    agents=[knowledge_agent, mcp_agent, {variable_name}],
    ...
)
```

### 4. Add Config Entry

Add a quick-prompts entry in `backend/config.yaml` for the new agent.

### 5. Add Dependencies

If the agent uses tools that require new packages, add them:
```
uv add <package>
```

### 6. Create Docs Page

Create `docs/agents/{id}.mdx` with frontmatter, code example, features, and example queries.
Add the page to `docs/docs.json` navigation under the Agents group.

### 7. Update Documentation

Update these files to reflect the new agent:
- `README.md` — Agents table
- `PROJECT_INDEX.md` — Agents section and core modules
- `.serena/memories/project-overview.md` — Agents list
- `docs/agents/overview.mdx` — Agents table and card group

### 8. Confirm

Tell the user:
- File created at `backend/agents/{name}.py`
- Registered in `backend/main.py`
- Config added to `backend/config.yaml`
- Docs page created at `docs/agents/{id}.mdx`
- Restart needed: `mise run docker:up` or `docker compose restart`
