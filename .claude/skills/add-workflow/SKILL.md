---
name: add-workflow
description: Scaffold a new Agno workflow with Steps, Loops, and Conditions, register in main.py, and create docs page
disable-model-invocation: true
---

# Add Workflow

Create a new Agno workflow and integrate it into Apollos AI.

## Steps

### 1. Gather Details

Ask the user for:
- **Workflow name** (human-readable, e.g., "Investment Analysis Workflow")
- **Workflow ID** (slug, e.g., "investment-workflow")
- **Description** (one-line purpose)
- **Steps** (which agents handle each stage)
- **Quality gates** (optional, iterative refinement loops)
- **Conditions** (optional, branching logic)

### 2. Create Workflow Module

Create `backend/workflows/{id_with_underscores}.py` following this pattern:

```python
"""
{Workflow Name}
{'-' * len(name)}

{Description}.

Uses Agno's Loop + Condition primitives for iterative refinement.
"""

from typing import List

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.workflow import Workflow
from agno.workflow.condition import Condition
from agno.workflow.loop import Loop
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput

from backend.agents.{agent_module} import {agent_name}
from backend.db import get_postgres_db
from backend.models import get_model


# Inline Agents (ephemeral, no DB persistence needed)
# Guardrails included per project convention.
inline_agent = Agent(
    name="{Inline Agent}",
    role="{role}",
    model=get_model(),
    instructions=[...],
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    markdown=True,
)


# Loop End Condition
def quality_met(outputs: List[StepOutput]) -> bool:
    """Return True to break the loop when quality is sufficient."""
    if not outputs:
        return False
    for output in outputs:
        content = str(output.content or "")
        if "QUALITY_PASS" in content:
            return True
    return False


# Condition Evaluator
def should_branch(step_input: StepInput) -> bool:
    """Check the original user input (not accumulated content) for routing."""
    text = str(step_input.input or "").lower()
    return any(signal in text for signal in ["compare", "analyze", "evaluate"])


# Workflow
{variable_name} = Workflow(
    id="{workflow-id}",
    name="{Workflow Name}",
    description="{description}",
    db=get_postgres_db(),
    add_workflow_history_to_steps=True,
    steps=[
        Step(
            name="Step 1",
            description="...",
            agent={agent_name},
            max_retries=2,
        ),
        Loop(
            name="Refinement Loop",
            description="Iterate until quality threshold met.",
            max_iterations=3,
            end_condition=quality_met,
            steps=[
                Step(name="Review", agent=inline_agent, add_workflow_history=True),
                Step(name="Refine", agent={agent_name}, add_workflow_history=True, skip_on_failure=True),
            ],
        ),
        Condition(
            name="Routing",
            description="Branch based on input complexity.",
            evaluator=should_branch,
            steps=[Step(name="Branch A", agent={agent_name}, add_workflow_history=True)],
            else_steps=[Step(name="Branch B", agent={agent_name}, add_workflow_history=True)],
        ),
    ],
)
```

Key conventions:
- All inline agents MUST have guardrails (`pre_hooks`)
- Inline agents are ephemeral (no DB, memory, or session summaries). Add a comment explaining this.
- Loop `end_condition` receives `List[StepOutput]`, returns `True` to break
- Condition `evaluator` receives `StepInput`, returns `True` for primary path
- Evaluators should check `step_input.input` (user query), NOT `previous_step_content` (accumulated output causes false positives)
- Always set `add_workflow_history_to_steps=True` on the Workflow
- Step params: `agent`, `max_retries`, `skip_on_failure`, `add_workflow_history` (no `instructions` or `timeout_seconds`)

### 3. Register in main.py

Add the import and include in the workflows list:

```python
from backend.workflows.{module_name} import {variable_name}

agent_os = AgentOS(
    workflows=[research_workflow, {variable_name}],
    ...
)
```

### 4. Add Config Entry

Add a quick-prompts entry in `backend/config.yaml` for the new workflow.

### 5. Create Docs Page

Create `docs/workflows/{id}.mdx` with frontmatter, code example, step table, and primitives reference.
Add the page to `docs/docs.json` navigation under the Workflows group.

### 6. Update Documentation

Update these files to reflect the new workflow:
- `README.md` — Workflows table
- `PROJECT_INDEX.md` — Workflows section and core modules
- `.serena/memories/project-overview.md` — Workflows list
- `docs/agents/overview.mdx` — Workflows table

### 7. Confirm

Tell the user:
- File created at `backend/workflows/{name}.py`
- Registered in `backend/main.py`
- Config added to `backend/config.yaml`
- Docs page created at `docs/workflows/{id}.mdx`
- Restart needed: `mise run docker:up` or `docker compose restart`
