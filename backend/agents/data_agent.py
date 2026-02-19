"""
Data Agent
----------

Data analysis agent following the Dash pattern.
Queries PostgreSQL with read-only tools and learns from successful queries.
"""

from os import getenv

from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.tools.postgres import PostgresTools

from backend.context.semantic_model import SEMANTIC_MODEL_STR
from backend.db import create_knowledge, get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()
data_learnings = create_knowledge("Data Learnings", "data_learnings")

DB_HOST = getenv("DB_HOST", "apollos-db")
DB_PORT = int(getenv("DB_PORT", "5432"))
DB_USER = getenv("DB_USER", "ai")
DB_PASS = getenv("DB_PASS", "ai")
DB_DATABASE = getenv("DB_DATABASE", "ai")

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = [
    "You are a data analyst assistant.",
    "You have access to a PostgreSQL database.",
    "",
    "## SQL Safety Rules (NEVER VIOLATE)",
    "- ALWAYS add LIMIT 50 unless the user specifies a different limit",
    "- NEVER use SELECT * — always specify columns",
    "- NEVER run DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE",
    "- NEVER expose raw connection strings or credentials",
    "",
    "## Database Schema",
    SEMANTIC_MODEL_STR,
    "",
    "## Learning Guidelines",
    "- Save a learning when you discover column type quirks (e.g., dates stored as strings)",
    "- Save a learning when a query pattern works well for a common question type",
    "- Save validated SQL queries that answered user questions correctly",
    "- Do NOT save trivial queries or one-off exploratory results",
]

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
data_agent = Agent(
    id="data-agent",
    name="Data Analyst",
    model=get_model(),
    db=agent_db,
    tools=[
        PostgresTools(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            db_name=DB_DATABASE,
            include_tools=["show_tables", "describe_table", "summarize_table", "inspect_query"],
        ),
    ],
    instructions=instructions,
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    learning=LearningMachine(
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            knowledge=data_learnings,
        ),
    ),
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
