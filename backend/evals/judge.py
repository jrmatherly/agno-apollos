"""
Agent-as-Judge
--------------

Opt-in quality evaluation using Agno's AgentAsJudgeEval as an agent post_hook.

Enable by setting AGENT_JUDGE_ENABLED=true in your environment.
When disabled, the returned hook function is a no-op that adds zero overhead.

The hook runs in the background (run_in_background=True) so it never blocks
the agent's response to the user.

API notes (verified against installed package):
- AgentAsJudgeEval(criteria="str", name=..., model=..., scoring_strategy="numeric",
                   run_in_background=..., threshold=..., db=...)
- AgentAsJudgeEval.run(input="question", output="response") — synchronous
- criteria is a plain string (join list with newlines if needed)

Usage:
    from backend.evals.judge import create_judge

    judge = create_judge(
        name="my-agent-judge",
        criteria=["Accurate", "Helpful", "Concise"],
    )

    agent = Agent(
        ...
        post_hooks=[judge],
    )
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from agno.eval.agent_as_judge import AgentAsJudgeEval

from backend.db.session import get_eval_db
from backend.models import get_model

logger = logging.getLogger(__name__)


def _is_judge_enabled() -> bool:
    return os.getenv("AGENT_JUDGE_ENABLED", "").lower() == "true"


def create_judge(name: str, criteria: list[str]) -> Callable[..., Any]:
    """Create an agent post_hook that runs quality evaluation via AgentAsJudgeEval.

    The hook is always returned as a callable. When AGENT_JUDGE_ENABLED is not
    set to "true", the hook is a no-op. This allows agents to always include
    the hook without any conditional wiring at the call site.

    Args:
        name: Identifier for this judge (used in eval run records).
        criteria: List of quality criteria strings. Joined into a single
            string for AgentAsJudgeEval (which takes criteria as str).

    Returns:
        A callable compatible with Agno's post_hooks list.
    """
    criteria_str = "\n".join(f"- {c}" for c in criteria)

    def judge_hook(run_response: Any, agent: Any) -> Any:
        if not _is_judge_enabled():
            return run_response

        # Extract input (user's question) and output (agent's response)
        question = ""
        if run_response.input is not None:
            question = run_response.input.input_content_string or ""

        response_text = ""
        if run_response.content is not None:
            response_text = str(run_response.content)

        try:
            eval_ = AgentAsJudgeEval(
                name=name,
                criteria=criteria_str,
                scoring_strategy="numeric",
                model=get_model(),
                run_in_background=True,
                threshold=7,
                db=get_eval_db(),
            )
            eval_.run(input=question, output=response_text)
        except Exception:
            logger.exception("Agent-as-judge eval failed for %s — skipping.", name)

        return run_response

    return judge_hook
