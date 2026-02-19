---
name: add-team
description: Scaffold a new Agno multi-agent team with boilerplate, register in main.py, and create docs page
disable-model-invocation: true
---

# Add Team

Create a new Agno multi-agent team and integrate it into Apollos AI.

## Steps

### 1. Gather Details

Ask the user for:
- **Team name** (human-readable, e.g., "Analysis Team")
- **Team ID** (slug, e.g., "analysis-team")
- **Mode** (`coordinate`, `collaborate`, or `route`)
- **Members** (which existing agents to include, or new ones to create)
- **Description** (one-line purpose)
- **Tools** (optional, e.g., `ReasoningTools`)

### 2. Create Team Module

Create `backend/teams/{id_with_underscores}.py` following this pattern:

```python
"""
{Team Name}
{'-' * len(team_name)}

{Description}.
"""

from agno.agent import Agent
from agno.team import Team
from agno.team.team import TeamMode
from agno.tools.reasoning import ReasoningTools

from backend.db import get_postgres_db
from backend.models import get_model

team_db = get_postgres_db()

# Team Members
member_one = Agent(
    name="{Member Name}",
    role="{role description}",
    model=get_model(),
    tools=[...],
    instructions=[...],
    markdown=True,
)

# Team
{variable_name} = Team(
    name="{Team Name}",
    id="{team-id}",
    mode=TeamMode.{mode},
    model=get_model(),
    db=team_db,
    members=[member_one, ...],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[...],
    markdown=True,
    compress_tool_results=True,
    max_iterations=5,
    store_history_messages=True,
    share_member_interactions=True,
    num_history_runs=5,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
)
```

Key conventions:
- Use `get_model()` from `backend/models.py` (never inline model creation)
- Use `id=` (not `team_id=`), `mode=TeamMode.coordinate` (not string)
- Import `TeamMode` from `agno.team.team`
- Always include `max_iterations` to prevent runaway coordination loops
- Always include `compress_tool_results=True` for cost control
- `member_timeout` and `max_interactions_to_share` do NOT exist on Team

### 3. Register in main.py

Add the import and include in the teams list:

```python
from backend.teams.{module_name} import {variable_name}

agent_os = AgentOS(
    teams=[research_team, {variable_name}],
    ...
)
```

### 4. Add Config Entry

Add a quick-prompts entry in `backend/config.yaml` for the new team.

### 5. Create Docs Page

Create `docs/teams/{id}.mdx` with frontmatter, code example, member table, and feature table.
Add the page to `docs/docs.json` navigation under the Teams group.

### 6. Update Documentation

Update these files to reflect the new team:
- `README.md` — Teams table
- `PROJECT_INDEX.md` — Teams section and core modules
- `.serena/memories/project-overview.md` — Teams list
- `docs/agents/overview.mdx` — Teams table

### 7. Confirm

Tell the user:
- File created at `backend/teams/{name}.py`
- Registered in `backend/main.py`
- Config added to `backend/config.yaml`
- Docs page created at `docs/teams/{id}.mdx`
- Restart needed: `mise run docker:up` or `docker compose restart`
