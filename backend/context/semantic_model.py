"""
Semantic Model
--------------

Database schema context injected into data agent instructions.
Following the Dash pattern: table descriptions, column details,
use cases, and data quality notes formatted as markdown tables.

Update this file when new tables are added or schema changes.
"""

SEMANTIC_MODEL = {
    "tables": [
        {
            "name": "agno_agent_sessions",
            "description": "Agent conversation sessions — one row per session",
            "key_columns": ["session_id", "agent_id", "user_id", "created_at", "updated_at"],
            "use_cases": ["Session analytics", "Usage patterns", "User engagement tracking"],
            "quality_notes": "Timestamps are timezone-aware UTC. session_id is UUID.",
        },
        {
            "name": "agno_agent_runs",
            "description": "Individual agent run records within sessions",
            "key_columns": ["run_id", "session_id", "agent_id", "input", "output", "created_at"],
            "use_cases": ["Run-level analytics", "Response quality tracking", "Latency analysis"],
            "quality_notes": "input/output are text. One session has many runs.",
        },
        {
            "name": "agno_memories",
            "description": "Agentic memory entries stored by agents",
            "key_columns": ["memory_id", "agent_id", "user_id", "memory", "created_at"],
            "use_cases": ["Memory usage analytics", "Memory growth tracking"],
            "quality_notes": "memory is text/JSON. Grows over time — monitor size.",
        },
        {
            "name": "agno_team_sessions",
            "description": "Team conversation sessions",
            "key_columns": ["session_id", "team_id", "user_id", "created_at"],
            "use_cases": ["Team usage analytics", "Multi-agent coordination tracking"],
            "quality_notes": "Similar schema to agent sessions.",
        },
        {
            "name": "agno_workflow_sessions",
            "description": "Workflow execution sessions with step tracking",
            "key_columns": ["session_id", "workflow_id", "user_id", "session_state", "created_at"],
            "use_cases": ["Workflow execution tracking", "Step performance analysis"],
            "quality_notes": "session_state is JSON with cross-step data.",
        },
        {
            "name": "agno_approvals",
            "description": "Human-in-the-loop approval records",
            "key_columns": ["approval_id", "agent_id", "tool_name", "status", "created_at", "resolved_at"],
            "use_cases": ["Approval workflow auditing", "Governance compliance"],
            "quality_notes": "status: pending, approved, rejected. resolved_at is NULL until acted on.",
        },
    ],
}


def _format_table(table: dict) -> str:
    cols = ", ".join(table["key_columns"])
    uses = ", ".join(table["use_cases"])
    return f"| {table['name']} | {table['description']} | {cols} | {uses} | {table.get('quality_notes', '')} |"


SEMANTIC_MODEL_STR = (
    "| Table | Description | Key Columns | Use Cases | Quality Notes |\n"
    "|-------|-------------|-------------|-----------|---------------|\n"
    + "\n".join(_format_table(t) for t in SEMANTIC_MODEL["tables"])
)
