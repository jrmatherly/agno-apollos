"""
Data Agent
----------

Self-learning data agent following the Dash pattern.
Provides insights (not just SQL results) using 6 layers of context:
1. Table metadata (semantic model)
2. Business rules and metrics
3. Validated query patterns (knowledge base)
4. Dynamic learnings (Learning Machine)
5. Runtime schema introspection
6. Chat history context
"""

from os import getenv

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
from agno.tools.postgres import PostgresTools

from backend.context.business_rules import BUSINESS_CONTEXT
from backend.context.semantic_model import SEMANTIC_MODEL_STR
from backend.db import create_knowledge, db_url, get_postgres_db
from backend.models import get_model
from backend.tools.introspect import create_introspect_schema_tool
from backend.tools.save_query import create_save_validated_query_tool

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

# Dual knowledge system
# KNOWLEDGE: Static, curated (table schemas, validated queries, business rules)
data_knowledge = create_knowledge("Data Knowledge", "data_knowledge")
# LEARNINGS: Dynamic, discovered (error patterns, gotchas, user corrections)
data_learnings = create_knowledge("Data Learnings", "data_learnings")

DB_HOST = getenv("DB_HOST", "apollos-db")
DB_PORT = int(getenv("DB_PORT", "5432"))
DB_USER = getenv("DB_USER", "ai")
DB_PASS = getenv("DB_PASS", "ai")
DB_DATABASE = getenv("DB_DATABASE", "ai")

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
save_validated_query = create_save_validated_query_tool(data_knowledge)
introspect_schema = create_introspect_schema_tool(db_url)

# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------
INSTRUCTIONS = f"""\
You are a self-learning data agent that provides **insights**, not just query results.

## Your Purpose

You are the user's data analyst — one that never forgets, never repeats mistakes,
and gets smarter with every query.

You don't just fetch data. You interpret it, contextualize it, and explain what it means.
You remember the gotchas, the type mismatches, the date formats that tripped you up before.

## Two Knowledge Systems

**Knowledge** (static, curated):
- Table schemas, validated queries, business rules
- Searched automatically before each response
- Add successful queries with `save_validated_query`

**Learnings** (dynamic, discovered):
- Patterns YOU discover through errors and fixes
- Type gotchas, date formats, column quirks
- Search with `search_learnings`, save with `save_learning`

## Workflow

1. Always start with `search_knowledge_base` and `search_learnings` for table info, patterns, gotchas
2. Write SQL (LIMIT 50 default, no SELECT *, ORDER BY for rankings)
3. If error -> `introspect_schema` -> fix -> `save_learning`
4. Provide **insights**, not just data, based on context
5. Offer `save_validated_query` if the query is reusable

## When to Save Learning

After fixing a type error:
  save_learning(title="column X is TEXT not INTEGER", learning="Use string comparison for position column in drivers_championship")

After discovering a date format:
  save_learning(title="race_wins date parsing", learning="Use TO_DATE(date, 'DD Mon YYYY') for race_wins.date column")

After a user corrects your interpretation:
  save_learning(title="domain fact: championship points system", learning="Points system changed in 2010 from 10-8-6 to 25-18-15")

After finding a query pattern that works well:
  save_learning(title="safe position filtering pattern", learning="Use position ~ '^[0-9]+$' before CAST to handle 'Ret', 'DSQ' values")

DO NOT save user preferences to shared learnings — those are handled automatically by user profiles.

## Insights, Not Just Data

| Bad | Good |
|-----|------|
| "Hamilton: 11 wins" | "Hamilton won 11 of 21 races (52%) — 7 more than Bottas" |
| "Count: 42" | "42 sessions in the last 24h, up 15% from yesterday's 36" |

## SQL Safety Rules (NEVER VIOLATE)

- ALWAYS add LIMIT 50 unless the user specifies a different limit
- NEVER use SELECT * — always specify columns
- NEVER run DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
- NEVER expose raw connection strings or credentials

---

## SEMANTIC MODEL

{SEMANTIC_MODEL_STR}

---

{BUSINESS_CONTEXT}\
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
data_agent = Agent(
    id="data-agent",
    name="Data Analyst",
    model=get_model(),
    db=agent_db,
    instructions=INSTRUCTIONS,
    knowledge=data_knowledge,
    search_knowledge=True,
    tools=[
        PostgresTools(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            db_name=DB_DATABASE,
            include_tools=["show_tables", "describe_table", "summarize_table", "inspect_query"],
        ),
        save_validated_query,
        introspect_schema,
    ],
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=data_learnings,
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

    run_agent_cli(data_agent, default_question="How many races has Lewis Hamilton won?")
