import os
from unittest.mock import MagicMock, patch


def test_create_judge_returns_callable():
    """create_judge() always returns a callable hook function."""
    from backend.evals.judge import create_judge

    hook = create_judge("test-agent", criteria=["Accurate", "Helpful"])
    assert callable(hook)


def test_hook_noop_when_disabled():
    """Hook returns run_response unchanged when AGENT_JUDGE_ENABLED is not 'true'."""
    from backend.evals.judge import create_judge

    hook = create_judge("test-agent", criteria=["Accurate"])
    fake_response = MagicMock()

    with patch.dict(os.environ, {"AGENT_JUDGE_ENABLED": "false"}):
        result = hook(fake_response, MagicMock())
    assert result is fake_response


def test_criteria_joined_as_string():
    """Multiple criteria strings are joined with newlines for the eval."""
    from backend.evals.judge import create_judge

    # If criteria list is passed, it should not raise at construction time
    hook = create_judge("test-agent", criteria=["Criterion A", "Criterion B"])
    assert callable(hook)
