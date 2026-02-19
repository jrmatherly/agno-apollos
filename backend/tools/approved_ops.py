"""
Approval-Gated Operations
-------------------------

Tools that require human approval before execution.
Uses Agno's @approval decorator for human-in-the-loop governance.
"""

import json
import logging
from typing import TYPE_CHECKING, Optional

from agno.approval import approval
from agno.db.base import SessionType
from agno.tools import tool

if TYPE_CHECKING:
    from agno.knowledge import Knowledge

logger = logging.getLogger(__name__)

# Lazy reference to the knowledge base (set by knowledge agent at init time)
_knowledge: Optional["Knowledge"] = None


def set_knowledge(knowledge: "Knowledge") -> None:
    """Wire the approval tools to a Knowledge instance."""
    global _knowledge
    _knowledge = knowledge


@tool
@approval
def add_knowledge_source(url: str, name: str) -> str:
    """Add an external URL to the knowledge base.

    This operation requires human approval because it introduces
    external content that will be used for answering questions.

    Args:
        url: The URL to add as a knowledge source.
        name: A descriptive name for the knowledge source.

    Returns:
        Confirmation message after approval and loading.
    """
    if _knowledge is None:
        return "Knowledge base not initialized. Cannot add sources."

    logger.info("Approved: adding knowledge source '%s' from %s", name, url)
    try:
        _knowledge.insert(name=name, url=url, skip_if_exists=True)
        return f"Knowledge source '{name}' from {url} added successfully."
    except Exception:
        logger.exception("Failed to add knowledge source '%s' from %s", name, url)
        return f"Failed to add knowledge source '{name}' from {url}. Check the URL and try again."


@tool(requires_confirmation=True)
@approval(type="audit")
def export_session_data(session_id: str, format: str = "json") -> str:
    """Export conversation session data for analysis.

    This operation is audit-logged because it accesses conversation history
    which may contain sensitive information.

    Args:
        session_id: The session ID to export.
        format: Export format (json or csv).

    Returns:
        Export status message with session data.
    """
    from backend.db import get_postgres_db

    logger.info("Audit: exporting session %s as %s", session_id, format)
    try:
        db = get_postgres_db()
        session = db.get_session(session_id=session_id, session_type=SessionType.AGENT)

        if session is None:
            return f"Session '{session_id}' not found."

        if format == "json":
            data = session.model_dump() if hasattr(session, "model_dump") else str(session)
            return json.dumps(data, indent=2, default=str)
        else:
            return f"Format '{format}' is not supported. Use 'json'."
    except Exception:
        logger.exception("Failed to export session %s", session_id)
        return f"Failed to export session '{session_id}'. Check the session ID and try again."
