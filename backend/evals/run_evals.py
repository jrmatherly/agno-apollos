"""Eval runner — executes test cases against live agents and grades responses."""

import json
import logging
import os
import sys

import requests

from backend.evals.grader import grade_response
from backend.evals.test_cases import ALL_CASES

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def run_agent(agent_id: str, question: str) -> str:
    """Send a question to an agent and return the response text."""
    r = requests.post(
        f"{BACKEND_URL}/v1/agents/{agent_id}/runs",
        json={"message": question, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("content", str(data))


def run_evals() -> list[dict]:
    """Run all eval cases and return results."""
    results = []

    for case in ALL_CASES:
        agent_id = case["agent_id"]
        question = case["question"]
        expected = case["expected"]

        logger.info("Evaluating %s: %s", agent_id, question)

        try:
            response = run_agent(agent_id, question)
            grade = grade_response(question, expected, response)
        except Exception as e:
            logger.error("Agent call failed: %s", e)
            grade = {"score": 0.0, "pass": False, "reasoning": f"Agent error: {e}"}
            response = ""

        result = {
            "agent_id": agent_id,
            "question": question,
            "expected": expected,
            "response": response[:200],
            **grade,
        }
        results.append(result)

        status = "PASS" if result["pass"] else "FAIL"
        logger.info("  %s (%.2f) — %s", status, result["score"], result["reasoning"])

    return results


def main():
    """Run evals and report summary."""
    results = run_evals()

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    print(f"\n{'=' * 60}")
    print(f"Eval Results: {passed}/{total} passed")
    print(f"{'=' * 60}")

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  [{status}] {r['agent_id']}: {r['question']}")
        print(f"         Score: {r['score']:.2f} — {r['reasoning']}")

    print(f"\n{json.dumps(results, indent=2)}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
