"""
Maintenance
-----------

Scheduled maintenance operations for Apollos AI.

- optimize_all_memories(): Summarize and compress agent memories for all users.
- warn_excessive_memories(): Log a warning when any user has too many memories.

Usage:
    uv run python3 -m backend.maintenance
    # or via mise:
    mise run maintenance:optimize-memories
"""

import logging

from agno.memory import MemoryManager
from agno.memory.strategies.types import MemoryOptimizationStrategyType

from backend.db.session import get_postgres_db
from backend.models import get_model

logger = logging.getLogger(__name__)

# Warn when a user accumulates more than this many memories
MEMORY_WARN_THRESHOLD = 500


def optimize_all_memories() -> None:
    """Summarize and compress memories for all users.

    Uses MemoryManager with the summarize strategy. Passing user_id=None
    runs the optimization across every user stored in the database.
    Requires apply=True to persist changes (without it, changes are simulated).

    MemoryManager.optimize_memories() is synchronous — no await needed.
    """
    logger.info("Starting memory optimization for all users...")
    manager = MemoryManager(
        model=get_model(),
        db=get_postgres_db(),
    )
    manager.optimize_memories(
        user_id=None,
        strategy=MemoryOptimizationStrategyType.SUMMARIZE,
        apply=True,
    )
    logger.info("Memory optimization complete.")


def warn_excessive_memories() -> None:
    """Log a warning for users with more than MEMORY_WARN_THRESHOLD memories.

    Fetches per-user memory stats from PostgresDb and warns when any user
    exceeds the threshold. Run before optimize_all_memories() to surface
    high-memory users in logs before compression.

    get_user_memory_stats() signature: (limit=None, page=None, user_id=None)
    Returns: Tuple[List[Dict[str, Any]], int]  — (rows, total_count)
    """
    db = get_postgres_db()
    rows, _total = db.get_user_memory_stats()
    for row in rows:
        count = row.get("count", 0)
        user_id = row.get("user_id", "unknown")
        if count > MEMORY_WARN_THRESHOLD:
            logger.warning(
                "User %s has %d memories (threshold: %d). Optimization recommended.",
                user_id,
                count,
                MEMORY_WARN_THRESHOLD,
            )


def run_maintenance() -> None:
    """Run full maintenance cycle: warn then optimize."""
    warn_excessive_memories()
    optimize_all_memories()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_maintenance()
