"""
System Awareness Tools
----------------------

Metadata tools for organizational context.
Helps users understand what information is available.
"""

import logging

from agno.tools import tool

logger = logging.getLogger(__name__)


@tool
def list_knowledge_sources() -> str:
    """List all available knowledge sources and their descriptions.

    Use this to understand what information is available before searching.

    Returns:
        A formatted list of knowledge sources with descriptions and last update times.
    """
    logger.info("Listing knowledge sources")
    # TODO: Implement against knowledge base metadata tables
    return "Knowledge source listing — implementation pending (Phase 3 will query KB metadata)"
