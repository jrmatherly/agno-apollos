"""
System Awareness Tools
----------------------

Metadata tools for organizational context.
Helps users understand what information is available.
"""

import logging
from typing import TYPE_CHECKING, Optional

from agno.tools import tool

if TYPE_CHECKING:
    from agno.knowledge import Knowledge

logger = logging.getLogger(__name__)

# Lazy reference to the knowledge base (set by knowledge agent at init time)
_knowledge: Optional["Knowledge"] = None


def set_knowledge(knowledge: "Knowledge") -> None:
    """Wire the awareness tool to a Knowledge instance."""
    global _knowledge
    _knowledge = knowledge


@tool
def list_knowledge_sources() -> str:
    """List all available knowledge sources and their descriptions.

    Use this to understand what information is available before searching.

    Returns:
        A formatted list of knowledge sources with descriptions and last update times.
    """
    if _knowledge is None:
        return "Knowledge base not initialized. Load documents first with `mise run load-docs`."

    logger.info("Listing knowledge sources")
    try:
        contents, total = _knowledge.get_content(limit=100)
    except Exception:
        logger.exception("Failed to list knowledge sources")
        return "Could not retrieve knowledge sources. The knowledge base may not be initialized."

    if not contents:
        return "No knowledge sources loaded. Run `mise run load-docs` to populate the knowledge base."

    lines: list[str] = [f"**{total} knowledge source(s) loaded:**\n"]
    for content in contents:
        name = getattr(content, "name", "Untitled") or "Untitled"
        url = getattr(content, "url", None)
        status = getattr(content, "status", None)
        source = f" ({url})" if url else ""
        status_str = f" [{status.value}]" if status else ""
        lines.append(f"- {name}{source}{status_str}")

    return "\n".join(lines)
