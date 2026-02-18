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
from os import getenv

from agno.agent import Agent
from agno.models.litellm import LiteLLMOpenAI
from backend.db import get_postgres_db

{variable_name} = Agent(
    id="{agent-id}",
    name="{Agent Name}",
    model=LiteLLMOpenAI(
        id=getenv("MODEL_ID", "gpt-5-mini"),
        base_url=getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
    ),
    db=get_postgres_db(),
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    instructions="{description}",
)
```

Key conventions:
- Import `getenv` from `os`, not `os.getenv`
- Use `LiteLLMOpenAI` (never direct OpenAI or Anthropic classes)
- Always pass `db=get_postgres_db()` for persistent state
- Use env vars for MODEL_ID and LITELLM_BASE_URL (never hardcode)

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

### 6. Confirm

Tell the user:
- File created at `backend/agents/{name}.py`
- Registered in `backend/main.py`
- Config added to `backend/config.yaml`
- Restart needed: `mise run docker:up` or `docker compose restart`
