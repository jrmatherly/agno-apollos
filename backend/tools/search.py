"""
Content Search Tools
--------------------

Keyword search tools for knowledge exploration.
Complements vector search with exact-match capability.
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
    """Wire the search tool to a Knowledge instance."""
    global _knowledge
    _knowledge = knowledge


@tool
def search_content(query: str, max_results: int = 5) -> str:
    """Search loaded knowledge base content using keyword matching.

    Use this when vector search is not precise enough, or when looking
    for specific terms, error messages, or exact phrases.

    Args:
        query: Search term or phrase to find in knowledge content.
        max_results: Maximum number of results to return (default 5).

    Returns:
        Matching content snippets with source references.
    """
    if _knowledge is None:
        return "Knowledge base not initialized. Load documents first with `mise run load-docs`."

    logger.info("Content search: %s (max_results=%d)", query, max_results)
    try:
        documents = _knowledge.search(query=query, max_results=max_results, search_type="keyword")
    except Exception:
        logger.exception("Keyword search failed for query: %s", query)
        return f"Search failed for '{query}'. The knowledge base may not have any documents loaded."

    if not documents:
        return f"No results found for '{query}'."

    results: list[str] = []
    for i, doc in enumerate(documents, 1):
        name: Optional[str] = getattr(doc, "name", None)
        content: str = str(getattr(doc, "content", ""))
        snippet = content[:500] + "..." if len(content) > 500 else content
        header = f"**{i}. {name}**" if name else f"**{i}.**"
        results.append(f"{header}\n{snippet}")

    return "\n\n".join(results)
