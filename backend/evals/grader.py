"""
LLM-based Eval Grader
---------------------

Grades agent responses using an LLM and compares SQL results
against golden SQL output.
"""

import json
import logging
from dataclasses import dataclass

from agno.models.message import Message

from backend.models import get_model

logger = logging.getLogger(__name__)


@dataclass
class GradeResult:
    """Result of LLM grading."""

    passed: bool
    reasoning: str
    score: float


GRADER_PROMPT = """You are evaluating an AI agent's response.

Question: {question}
Expected information: {expected}
Agent response: {response}

Evaluate on:
1. Factual correctness (does response contain expected information?)
2. Completeness (does it answer the question?)
3. No hallucinations (does it claim things not supported by facts?)

Be lenient about:
- Extra context or insights (the agent may provide more than asked)
- Different phrasing or formatting
- Minor variations in names (e.g., "Lewis Hamilton" vs "Hamilton")

Score: 0.0 (completely wrong) to 1.0 (perfect)
Pass threshold: 0.7

Respond with JSON only:
{{"score": <float>, "pass": <bool>, "reasoning": "<brief explanation>"}}"""


def grade_response(question: str, expected: str, response: str) -> GradeResult:
    """Grade an agent response against expected output.

    Args:
        question: The question that was asked.
        expected: Expected information the response should contain.
        response: The agent's actual response.

    Returns:
        GradeResult with score, passed, and reasoning.
    """
    model = get_model()
    prompt = GRADER_PROMPT.format(question=question, expected=expected, response=response)
    messages = [Message(role="user", content=prompt)]

    try:
        result = model.response(messages=messages)
        content = result.content or ""
        data = json.loads(content)
        return GradeResult(
            score=float(data.get("score", 0.0)),
            passed=bool(data.get("pass", False)),
            reasoning=str(data.get("reasoning", "No reasoning")),
        )
    except Exception as e:
        logger.error("Grading failed: %s", e)
        return GradeResult(score=0.0, passed=False, reasoning=f"Grading error: {e}")


def compare_results(
    expected: list[dict],
    actual: list[dict],
    key_columns: list[str] | None = None,
) -> tuple[bool, str]:
    """Compare expected vs actual query results.

    Args:
        expected: Expected results from golden SQL.
        actual: Actual results from agent's query.
        key_columns: Columns to compare (if None, compare all).

    Returns:
        Tuple of (matches, explanation).
    """
    if not expected and not actual:
        return True, "Both results are empty"

    if not expected:
        return False, "Expected results are empty but actual has data"

    if not actual:
        return False, "Actual results are empty but expected has data"

    def normalize_row(row: dict) -> dict:
        return {k.lower().strip(): str(v).strip() for k, v in row.items()}

    expected_normalized = [normalize_row(r) for r in expected]
    actual_normalized = [normalize_row(r) for r in actual]

    if key_columns:
        key_cols = [k.lower().strip() for k in key_columns]
        expected_normalized = [{k: v for k, v in r.items() if k in key_cols} for r in expected_normalized]
        actual_normalized = [{k: v for k, v in r.items() if k in key_cols} for r in actual_normalized]

    expected_first = expected_normalized[0] if expected_normalized else {}
    actual_first = actual_normalized[0] if actual_normalized else {}

    if len(expected_normalized) == 1:
        for key, expected_val in expected_first.items():
            if key in actual_first:
                if expected_val.lower() != actual_first[key].lower():
                    return False, f"Mismatch in '{key}': expected '{expected_val}', got '{actual_first[key]}'"
            else:
                found = any(expected_val.lower() in str(v).lower() for r in actual_normalized for v in r.values())
                if not found:
                    return False, f"Expected value '{expected_val}' not found in actual results"
        return True, "Key values match"

    expected_values = {str(v).lower() for r in expected_normalized for v in r.values()}
    actual_values = {str(v).lower() for r in actual_normalized for v in r.values()}
    missing = expected_values - actual_values
    if missing:
        return False, f"Missing expected values: {missing}"

    return True, "All expected values found in actual results"
