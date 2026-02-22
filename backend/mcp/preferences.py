"""Per-user MCP workspace preferences.

Stores preferences as JSON files. Designed for easy migration to database
storage if needed.
"""

from __future__ import annotations

import logging
from os import getenv
from pathlib import Path

from backend.mcp.schemas import MCPUserPreferences

log = logging.getLogger(__name__)

# Use env var instead of /tmp (volatile in Docker containers)
_PREFS_DIR = Path(getenv("MCP_PREFERENCES_DIR", "/app/data/mcp-preferences"))

_DEFAULT_PREFS = MCPUserPreferences()

_MAX_ID_LENGTH = 200  # Prevent excessively long filenames


def _prefs_path(user_id: str) -> Path:
    """Get the preferences file path for a user (safe filename)."""
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id[:_MAX_ID_LENGTH])
    return _PREFS_DIR / f"{safe_id}.json"


def get_preferences(user_id: str) -> MCPUserPreferences:
    """Load preferences for a user, returning defaults if none exist."""
    path = _prefs_path(user_id)
    if not path.exists():
        return _DEFAULT_PREFS
    try:
        return MCPUserPreferences.model_validate_json(path.read_text())
    except Exception:
        log.warning("Failed to read preferences for %s, returning defaults", user_id)
        return _DEFAULT_PREFS


def save_preferences(user_id: str, prefs: MCPUserPreferences) -> None:
    """Save preferences for a user."""
    _PREFS_DIR.mkdir(parents=True, exist_ok=True)
    path = _prefs_path(user_id)
    path.write_text(prefs.model_dump_json(indent=2))
