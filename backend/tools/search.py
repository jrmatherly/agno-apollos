"""
Content Search Tools
--------------------

Keyword search tools for knowledge exploration.
Complements vector search with exact-match capability.
"""

import logging

from agno.tools import tool

logger = logging.getLogger(__name__)


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
    logger.info("Content search: %s (max_results=%d)", query, max_results)
    # TODO: Implement against pgvector keyword search or direct DB query
    return f"Search for '{query}' — implementation pending (Phase 3 will wire to knowledge DB)"
