"""
Source Registry
---------------

Loads structured source metadata from JSON and formats it for
injection into agent instructions. Following the Scout pattern:
rich metadata about what sources exist, their capabilities,
and how to search them effectively.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCES_DIR = Path(__file__).parent.parent / "knowledge" / "sources"


def load_source_metadata(sources_dir: Path | None = None) -> list[dict[str, Any]]:
    """Load source metadata from JSON files."""
    if sources_dir is None:
        sources_dir = SOURCES_DIR

    sources: list[dict[str, Any]] = []
    if not sources_dir.exists():
        return sources

    for filepath in sorted(sources_dir.glob("*.json")):
        try:
            with open(filepath) as f:
                source = json.load(f)
            sources.append(source)
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.error("Failed to load %s: %s", filepath, e)

    return sources


def format_source_registry(sources_dir: Path | None = None) -> str:
    """Format source registry for system prompt injection."""
    sources = load_source_metadata(sources_dir)
    if not sources:
        return ""

    lines: list[str] = ["## Source Registry\n"]

    for source in sources:
        lines.append(f"### {source.get('source_name', 'Unknown')} (`{source.get('source_type', 'unknown')}`)")
        if source.get("description"):
            lines.append(source["description"])
        lines.append("")

        if source.get("capabilities"):
            lines.append("**Capabilities:** " + ", ".join(source["capabilities"][:5]))
            lines.append("")

        if source.get("search_tips"):
            lines.append("**Search tips:**")
            for tip in source["search_tips"][:4]:
                lines.append(f"- {tip}")
            lines.append("")

        if source.get("common_locations"):
            lines.append("**Known locations:**")
            for key, value in source["common_locations"].items():
                lines.append(f"- {key}: `{value}`")
            lines.append("")

        if source.get("limitations"):
            lines.append("**Limitations:** " + "; ".join(source["limitations"][:3]))
            lines.append("")

    return "\n".join(lines)


SOURCE_REGISTRY = format_source_registry()
