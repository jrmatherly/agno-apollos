"""
Semantic Model
--------------

Database schema context injected into data agent instructions.
Following the Dash pattern: table descriptions, column details,
use cases, and data quality notes formatted as markdown tables.
"""

SEMANTIC_MODEL = {
    "tables": [
        {
            "name": "agno_agent_sessions",
            "description": "Agent conversation sessions",
            "key_columns": ["session_id", "agent_id", "user_id", "created_at"],
            "use_cases": ["Session analytics", "Usage patterns", "User engagement"],
            "quality_notes": "created_at is timezone-aware UTC",
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
