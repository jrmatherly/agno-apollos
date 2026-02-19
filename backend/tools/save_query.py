"""
Save Validated Query Tool
-------------------------

Saves successful SQL queries to the knowledge base for reuse.
Includes safety checks to prevent saving dangerous queries.
"""

import json

from agno.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.tools import tool
from agno.utils.log import logger


def create_save_validated_query_tool(knowledge: Knowledge):
    """Create save_validated_query tool with knowledge injected."""

    @tool
    def save_validated_query(
        name: str,
        question: str,
        query: str,
        summary: str | None = None,
        tables_used: list[str] | None = None,
        data_quality_notes: str | None = None,
    ) -> str:
        """Save a validated SQL query to the knowledge base for future reuse.

        Call ONLY after a query has executed successfully and the user confirmed
        the results are correct. This builds the curated knowledge base.

        Args:
            name: Short name (e.g., "championship_wins_by_driver").
            question: The original user question this query answers.
            query: The SQL query (must be SELECT or WITH).
            summary: Brief description of what the query does.
            tables_used: List of table names used in the query.
            data_quality_notes: Any data quality issues the query handles.
        """
        if not name or not name.strip():
            return "Error: Name required."
        if not question or not question.strip():
            return "Error: Question required."
        if not query or not query.strip():
            return "Error: Query required."

        sql = " ".join(query.strip().lower().split())
        if not sql.startswith("select") and not sql.startswith("with"):
            return "Error: Only SELECT queries can be saved."

        dangerous = ["drop", "delete", "truncate", "insert", "update", "alter", "create"]
        for kw in dangerous:
            if f" {kw} " in f" {sql} ":
                return f"Error: Query contains dangerous keyword: {kw}"

        payload = {
            "type": "validated_query",
            "name": name.strip(),
            "question": question.strip(),
            "query": query.strip(),
            "summary": summary.strip() if summary else None,
            "tables_used": tables_used or [],
            "data_quality_notes": data_quality_notes.strip() if data_quality_notes else None,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            knowledge.insert(
                name=name.strip(),
                text_content=json.dumps(payload, ensure_ascii=False, indent=2),
                reader=TextReader(),
                skip_if_exists=True,
            )
            return f"Saved query '{name}' to knowledge base."
        except (AttributeError, TypeError, ValueError, OSError) as e:
            logger.error("Failed to save query: %s", e)
            return f"Error: {e}"

    return save_validated_query
