"""
Save Intent Discovery
---------------------

Saves structured intent-to-location mappings into the knowledge base.
Following the Scout pattern: the agent learns where information lives
and gets faster at finding it over time.
"""

import json
import logging
from typing import TYPE_CHECKING, Optional

from agno.knowledge.reader.text_reader import TextReader
from agno.tools import tool

if TYPE_CHECKING:
    from agno.knowledge import Knowledge

logger = logging.getLogger(__name__)

_knowledge: Optional["Knowledge"] = None


def set_knowledge(knowledge: "Knowledge") -> None:
    """Wire the save_discovery tool to a Knowledge instance."""
    global _knowledge
    _knowledge = knowledge


@tool
def save_intent_discovery(
    name: str,
    intent: str,
    location: str,
    summary: str | None = None,
    search_terms: list[str] | None = None,
) -> str:
    """Save a successful discovery to knowledge base for future reference.

    Call this after finding information that might be useful for similar
    future queries. This helps learn where information is typically found.

    Args:
        name: Short name for this discovery (e.g., "api_rate_limits_location").
        intent: What the user was looking for (e.g., "Find API rate limits").
        location: Where the information was found (e.g., "agno-docs/introduction.md").
        summary: Brief description of what was found.
        search_terms: Search terms that worked to find this.
    """
    if _knowledge is None:
        return "Knowledge base not initialized. Cannot save discovery."

    if not name or not name.strip():
        return "Error: name is required."
    if not intent or not intent.strip():
        return "Error: intent is required."
    if not location or not location.strip():
        return "Error: location is required."

    payload = {
        "type": "intent_discovery",
        "name": name.strip(),
        "intent": intent.strip(),
        "location": location.strip(),
        "summary": summary.strip() if summary else None,
        "search_terms": search_terms or [],
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        _knowledge.insert(
            name=name.strip(),
            text_content=json.dumps(payload, ensure_ascii=False, indent=2),
            reader=TextReader(),
            skip_if_exists=True,
        )
        return f"Saved discovery '{name}' to knowledge base."
    except (AttributeError, TypeError, ValueError, OSError) as e:
        logger.exception("Failed to save discovery: %s", e)
        return f"Error saving discovery: {e}"
