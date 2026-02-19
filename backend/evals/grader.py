"""LLM-based response grading (Scout pattern)."""

import json
import logging

from agno.models.message import Message

from backend.models import get_model

logger = logging.getLogger(__name__)

GRADER_PROMPT = """You are evaluating an AI agent's response.

Question: {question}
Expected information: {expected}
Agent response: {response}

Evaluate on:
1. Factual correctness (does response contain expected information?)
2. Completeness (does it answer the question?)
3. No hallucinations (does it claim things not supported by facts?)

Score: 0.0 (completely wrong) to 1.0 (perfect)
Pass threshold: 0.7

Respond with JSON only:
{{"score": <float>, "pass": <bool>, "reasoning": "<brief explanation>"}}"""


def grade_response(question: str, expected: str, response: str) -> dict:
    """Grade an agent response against expected output.

    Args:
        question: The question that was asked.
        expected: Expected information the response should contain.
        response: The agent's actual response.

    Returns:
        Dict with score (float), pass (bool), and reasoning (str).
    """
    model = get_model()
    prompt = GRADER_PROMPT.format(question=question, expected=expected, response=response)
    messages = [Message(role="user", content=prompt)]

    try:
        result = model.response(messages=messages)
        content = result.content or ""
        return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Grading failed: %s", e)
        return {"score": 0.0, "pass": False, "reasoning": f"Grading error: {e}"}
