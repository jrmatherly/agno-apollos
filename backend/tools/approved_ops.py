"""
Approval-Gated Operations
-------------------------

Tools that require human approval before execution.
Uses Agno's @approval decorator for human-in-the-loop governance.
"""

import logging

from agno.approval import approval
from agno.tools import tool

logger = logging.getLogger(__name__)


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
    logger.info("Approved: adding knowledge source '%s' from %s", name, url)
    # TODO: Wire to knowledge.insert() in Phase 5
    return f"Knowledge source '{name}' from {url} — queued for loading (implementation pending)"


@tool
@approval(type="audit")
def export_session_data(session_id: str, format: str = "json") -> str:
    """Export conversation session data for analysis.

    This operation is audit-logged because it accesses conversation history
    which may contain sensitive information.

    Args:
        session_id: The session ID to export.
        format: Export format (json or csv).

    Returns:
        Export status message.
    """
    logger.info("Audit: exporting session %s as %s", session_id, format)
    # TODO: Implement session export in Phase 5
    return f"Session {session_id} export as {format} — implementation pending"
