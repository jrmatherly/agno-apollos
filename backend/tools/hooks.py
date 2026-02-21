"""
Agent-Level Tool Hooks
-----------------------
Composable hooks for audit logging and authorization.
Wire into agents via Agent(tool_hooks=[...]).
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

log = logging.getLogger("apollos.audit")


def audit_hook(
    function_name: str,
    function_call: Callable[..., Any],
    arguments: dict[str, Any],
    run_context: Any,
) -> Any:
    """Log all tool calls with user, timing, and argument keys."""
    user_id = getattr(run_context, "user_id", "anonymous")
    start = time.monotonic()
    result = function_call(**arguments)
    elapsed = time.monotonic() - start
    log.info(
        "tool_call user=%s tool=%s args=%s duration=%.3fs",
        user_id,
        function_name,
        list(arguments.keys()),
        elapsed,
    )
    return result


def m365_write_guard(
    function_name: str,
    function_call: Callable[..., Any],
    arguments: dict[str, Any],
    run_context: Any,
) -> Any:
    """
    Defense-in-depth: block write operations even if the MCP server's
    --read-only flag is somehow bypassed.
    """
    from agno.exceptions import StopAgentRun

    _WRITE_PREFIXES = ("m365_send", "m365_create", "m365_update", "m365_delete", "m365_upload", "m365_move")
    if any(function_name.startswith(p) for p in _WRITE_PREFIXES):
        raise StopAgentRun(
            f"Write operation '{function_name}' is not permitted. "
            "M365 access is read-only. Suggest the user perform this action directly in Microsoft 365."
        )
    return function_call(**arguments)
