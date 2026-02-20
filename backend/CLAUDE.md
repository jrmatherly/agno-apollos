# Backend — Agent & Agno Conventions

Agent-specific patterns and Agno framework gotchas for `backend/`. See root `CLAUDE.md` for project-wide conventions.

## Agent Conventions

- All agents must have guardrails: `pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()]` — includes inline/ephemeral agents in workflows
- All agents use full LearningMachine stack: `learned_knowledge` (AGENTIC, shared), `user_profile`, `user_memory`, `session_context`
- Agent CLI for direct testing: `python -m backend.agents.<name>` (shared Rich CLI module at `backend/cli.py`)
- Data agent uses dual knowledge system: static `data_knowledge` (curated) + dynamic `data_learnings` (discovered via LearningMachine)

## Agno Framework API Notes

Always verify signatures before using: `python3 -c "import inspect; from agno.X import Y; print(inspect.signature(Y))"`

Docs and examples frequently have wrong parameter names — never assume, always verify.

Known gotchas:

- `@tool` must be outer decorator, `@approval` inner (otherwise mypy error on Function type)
- `@approval(type="audit")` requires explicit HITL flag on `@tool()` (e.g., `@tool(requires_confirmation=True)`). Plain `@approval` auto-sets this.
- Team: use `id=` (not `team_id=`), `mode=TeamMode.coordinate` (not string). Import `from agno.team.team import TeamMode`.
- `member_timeout` and `max_interactions_to_share` do not exist on Team in current version
- Workflow Step: takes `agent=` or `executor=` (no `instructions` or `timeout_seconds` params)
- Condition: takes `evaluator` + `steps` + `else_steps` (not `on_true`/`on_false`)
- Loop `end_condition`: receives `List[StepOutput]`, returns `True` to break. Condition `evaluator`: receives `StepInput`, returns `True` for primary path. Check `step_input.input` for user query (not `previous_step_content` which has accumulated output).
- Knowledge readers: `agno.knowledge.reader.pdf_reader.PDFReader` (not `agno.document.reader`)
- `include_tools`/`exclude_tools`: On base `Toolkit` class, passed via `**kwargs` to PostgresTools etc.
- Model API for direct calls: `model.response(messages=[Message(role="user", content=...)])` (not `model.invoke(str)`)
- `enable_session_summaries` is on Agent (not AgentOS); `enable_mcp_server` is on AgentOS
- `show_tool_calls` is NOT a valid Agent parameter
