"""
Eval Runner
-----------

Runs evaluation suite against live agents with Rich CLI output.
Supports string matching, golden SQL comparison, and LLM grading.

Golden SQL comparison runs automatically for test cases that define golden_sql.
It checks the agent's response against ground truth DB values with lenient
matching (number words, partial names). String matching is the fallback for
test cases without golden SQL.

Usage:
    python -m backend.evals.run_evals                    # All tests via API
    python -m backend.evals.run_evals -c basic           # Category filter
    python -m backend.evals.run_evals -v                 # Verbose (show responses)
    python -m backend.evals.run_evals -g                 # LLM grading
    python -m backend.evals.run_evals --direct           # Direct agent invocation
    python -m backend.evals.run_evals -g -v              # LLM grading + verbose
"""

import argparse
import os
import sys
import time
from typing import TypedDict

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text
from sqlalchemy import create_engine, text

from backend.evals.grader import GradeResult, grade_response
from backend.evals.test_cases import ALL_CASES, CATEGORIES, TestCase

console = Console()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class EvalResult(TypedDict, total=False):
    status: str
    question: str
    category: str
    agent_id: str
    missing: list[str] | None
    duration: float
    response: str | None
    error: str
    llm_grade: float | None
    llm_reasoning: str | None
    result_match: bool | None
    result_explanation: str | None


# ---------------------------------------------------------------------------
# Execution modes
# ---------------------------------------------------------------------------
def run_agent_api(agent_id: str, question: str) -> str:
    """Send a question to an agent via HTTP API."""
    import requests

    r = requests.post(
        f"{BACKEND_URL}/agents/{agent_id}/runs",
        data={"message": question, "stream": "false"},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("content", str(data))


def run_agent_direct(agent_id: str, question: str) -> str:
    """Run an agent directly via Python import."""
    from backend.agents.data_agent import data_agent
    from backend.agents.knowledge_agent import knowledge_agent
    from backend.agents.web_search_agent import web_search_agent

    agents = {
        "data-agent": data_agent,
        "knowledge-agent": knowledge_agent,
        "web-search-agent": web_search_agent,
    }
    agent = agents.get(agent_id)
    if agent is None:
        return f"Error: Unknown agent '{agent_id}'"

    result = agent.run(question)
    return result.content or ""


def execute_golden_sql(sql: str) -> list[dict]:
    """Execute a golden SQL query and return results."""
    from backend.db import db_url as _db_url

    engine = create_engine(_db_url)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def check_strings(response: str, expected: list[str]) -> list[str]:
    """Return missing expected strings from response."""
    response_lower = response.lower()
    return [v for v in expected if v.lower() not in response_lower]


# Number words for lenient numeric matching (0-20)
_NUMBER_WORDS: dict[str, str] = {
    str(i): w
    for i, w in enumerate(
        "zero one two three four five six seven eight nine ten "
        "eleven twelve thirteen fourteen fifteen sixteen seventeen "
        "eighteen nineteen twenty".split()
    )
}


def _value_in_response(value: str, response_lower: str) -> bool:
    """Check if a golden SQL value appears in the agent response.

    Lenient matching handles common LLM output variations:
    - Numbers 0-20 match their word form ("11" matches "eleven")
    - Multi-word values match if any significant word appears ("Michael Schumacher" matches "Schumacher")
    """
    val = str(value).strip().lower()
    if not val:
        return True

    # Direct substring match
    if val in response_lower:
        return True

    # Numeric: also check word form (0-20)
    if val in _NUMBER_WORDS and _NUMBER_WORDS[val] in response_lower:
        return True

    # Multi-word (e.g. full names): check if any word >2 chars appears
    words = val.split()
    if len(words) > 1 and any(w in response_lower for w in words if len(w) > 2):
        return True

    return False


def evaluate_response(
    test_case: TestCase,
    response: str,
    llm_grader: bool = False,
) -> dict:
    """Evaluate an agent response using configured methods.

    Evaluation priority: LLM grading > golden SQL > string matching.
    Golden SQL runs automatically when the test case defines it.
    """
    result: dict = {}

    # String matching (always runs as baseline)
    missing = check_strings(response, test_case.expected_strings)
    result["missing"] = missing if missing else None
    string_pass = len(missing) == 0

    # Golden SQL comparison (auto-runs when golden_sql is defined)
    # Checks agent response against ground truth DB values
    result_pass: bool | None = None
    if test_case.golden_sql:
        try:
            golden_result = execute_golden_sql(test_case.golden_sql)
            response_lower = response.lower()

            if test_case.expected_result is not None:
                # Focused: validate expected_result exists in DB AND in response
                golden_values = [str(v) for row in golden_result for v in row.values()]
                sql_valid = any(test_case.expected_result.lower() in gv.lower() for gv in golden_values)
                if not sql_valid:
                    result_pass = False
                    result["result_explanation"] = f"Golden SQL missing expected '{test_case.expected_result}'"
                else:
                    in_response = _value_in_response(test_case.expected_result, response_lower)
                    result_pass = in_response
                    result["result_explanation"] = (
                        f"'{test_case.expected_result}'"
                        + (" — found" if in_response else " — missing")
                        + " in response"
                    )
            elif golden_result:
                # Value check: verify golden SQL values appear in agent response
                first_row = golden_result[0]
                missing_cols = []
                for col, val in first_row.items():
                    if not _value_in_response(str(val), response_lower):
                        missing_cols.append(f"{col}={val}")
                result_pass = len(missing_cols) == 0
                result["result_explanation"] = (
                    "All golden SQL values found in response"
                    if result_pass
                    else f"Response missing: {', '.join(missing_cols)}"
                )
            result["result_match"] = result_pass
        except Exception as e:
            result["result_match"] = None
            result["result_explanation"] = f"Error executing golden SQL: {e}"

    # LLM grading
    llm_pass: bool | None = None
    if llm_grader:
        try:
            grade: GradeResult = grade_response(
                question=test_case.question,
                expected=", ".join(test_case.expected_strings),
                response=response,
            )
            result["llm_grade"] = grade.score
            result["llm_reasoning"] = grade.reasoning
            llm_pass = grade.passed
        except Exception as e:
            result["llm_grade"] = None
            result["llm_reasoning"] = f"Error: {e}"

    # Final status (priority: LLM > golden SQL > string matching)
    if llm_grader and llm_pass is not None:
        result["status"] = "PASS" if llm_pass else "FAIL"
    elif result_pass is not None:
        result["status"] = "PASS" if result_pass else "FAIL"
    else:
        result["status"] = "PASS" if string_pass else "FAIL"

    return result


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display_results(results: list[EvalResult], verbose: bool, llm_grader: bool) -> None:
    """Display results table."""
    table = Table(title="Results", show_lines=True)
    table.add_column("Status", style="bold", width=6)
    table.add_column("Agent", style="dim", width=16)
    table.add_column("Category", style="dim", width=12)
    table.add_column("Question", width=42)
    table.add_column("Time", justify="right", width=6)
    table.add_column("Notes", width=32)

    for r in results:
        if r["status"] == "PASS":
            status = Text("PASS", style="green")
            notes = ""
            if llm_grader and r.get("llm_grade") is not None:
                notes = f"LLM: {r['llm_grade']:.1f}"
        elif r["status"] == "FAIL":
            status = Text("FAIL", style="red")
            if llm_grader and r.get("llm_reasoning"):
                notes = (r.get("llm_reasoning") or "")[:32]
            elif r.get("result_explanation"):
                notes = (r.get("result_explanation") or "")[:32]
            elif r.get("missing"):
                notes = f"Missing: {', '.join((r.get('missing') or [])[:2])}"
            else:
                notes = ""
        else:
            status = Text("ERR", style="yellow")
            notes = (r.get("error") or "")[:32]

        q = r["question"]
        table.add_row(
            status,
            r.get("agent_id", ""),
            r["category"],
            q[:40] + "..." if len(q) > 40 else q,
            f"{r['duration']:.1f}s",
            notes,
        )

    console.print(table)

    if verbose:
        failures = [r for r in results if r["status"] == "FAIL" and r.get("response")]
        for r in failures:
            resp = r["response"] or ""
            content = resp[:500] + "..." if len(resp) > 500 else resp
            if r.get("llm_reasoning"):
                content += f"\n\n[dim]LLM: {r['llm_reasoning']}[/dim]"
            if r.get("result_explanation"):
                content += f"\n[dim]SQL: {r['result_explanation']}[/dim]"
            console.print(Panel(content, title=f"[red]{r['question'][:60]}[/red]", border_style="red"))


def display_summary(results: list[EvalResult], total_duration: float, category: str | None) -> None:
    """Display summary statistics."""
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    total = len(results)
    rate = (passed / total * 100) if total else 0

    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column()
    summary.add_row("Total:", f"{total} tests in {total_duration:.1f}s")
    summary.add_row("Passed:", Text(f"{passed} ({rate:.0f}%)", style="green"))
    summary.add_row("Failed:", Text(str(failed), style="red" if failed else "dim"))
    summary.add_row("Errors:", Text(str(errors), style="yellow" if errors else "dim"))
    summary.add_row("Avg time:", f"{total_duration / total:.1f}s per test" if total else "N/A")

    llm_grades = [
        r["llm_grade"] for r in results if r.get("llm_grade") is not None and isinstance(r["llm_grade"], (int, float))
    ]
    if llm_grades:
        summary.add_row("Avg LLM Score:", f"{sum(llm_grades) / len(llm_grades):.2f}")

    console.print(Panel(summary, title="[bold]Summary[/bold]", border_style="green" if rate == 100 else "yellow"))

    if not category and len(CATEGORIES) > 1:
        cat_table = Table(title="By Category", show_header=True)
        cat_table.add_column("Category")
        cat_table.add_column("Passed", justify="right")
        cat_table.add_column("Total", justify="right")
        cat_table.add_column("Rate", justify="right")

        for cat in CATEGORIES:
            cat_results = [r for r in results if r["category"] == cat]
            if not cat_results:
                continue
            cat_passed = sum(1 for cr in cat_results if cr["status"] == "PASS")
            cat_total = len(cat_results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total else 0
            rate_style = "green" if cat_rate == 100 else "yellow" if cat_rate >= 50 else "red"
            cat_table.add_row(cat, str(cat_passed), str(cat_total), Text(f"{cat_rate:.0f}%", style=rate_style))

        console.print(cat_table)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_evals(
    category: str | None = None,
    verbose: bool = False,
    llm_grader: bool = False,
    direct: bool = False,
    agent_id: str | None = None,
) -> None:
    """Run evaluation suite."""
    run_fn = run_agent_direct if direct else run_agent_api

    tests = ALL_CASES
    if category:
        tests = [tc for tc in tests if tc.category == category]
    if agent_id:
        tests = [tc for tc in tests if tc.agent_id == agent_id]

    if not tests:
        console.print(f"[red]No tests found for filters: category={category}, agent={agent_id}[/red]")
        return

    mode_info = []
    if llm_grader:
        mode_info.append("LLM grading")
    golden_count = sum(1 for tc in tests if tc.golden_sql)
    if golden_count:
        mode_info.append(f"Golden SQL ({golden_count} tests)")
    mode_info.append("String matching")
    mode_info.append("direct" if direct else "API")

    console.print(Panel(f"[bold]Running {len(tests)} tests[/bold]\nMode: {', '.join(mode_info)}", style="blue"))

    results: list[EvalResult] = []
    start = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Evaluating...", total=len(tests))

        for tc in tests:
            progress.update(task, description=f"[cyan]{tc.question[:40]}...[/cyan]")
            test_start = time.time()

            try:
                response = run_fn(tc.agent_id, tc.question)
                duration = time.time() - test_start

                eval_result = evaluate_response(
                    test_case=tc,
                    response=response,
                    llm_grader=llm_grader,
                )

                results.append(
                    {
                        "status": eval_result["status"],
                        "question": tc.question,
                        "category": tc.category,
                        "agent_id": tc.agent_id,
                        "missing": eval_result.get("missing"),
                        "duration": duration,
                        "response": response if verbose else None,
                        "llm_grade": eval_result.get("llm_grade"),
                        "llm_reasoning": eval_result.get("llm_reasoning"),
                        "result_match": eval_result.get("result_match"),
                        "result_explanation": eval_result.get("result_explanation"),
                    }
                )
            except Exception as e:
                duration = time.time() - test_start
                results.append(
                    {
                        "status": "ERROR",
                        "question": tc.question,
                        "category": tc.category,
                        "agent_id": tc.agent_id,
                        "missing": None,
                        "duration": duration,
                        "error": str(e),
                        "response": None,
                    }
                )

            progress.advance(task)

    total_duration = time.time() - start
    display_results(results, verbose, llm_grader)
    display_summary(results, total_duration, category)

    failed = sum(1 for r in results if r["status"] != "PASS")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run agent evaluations")
    parser.add_argument("--category", "-c", choices=CATEGORIES, help="Filter by category")
    parser.add_argument("--agent", "-a", help="Filter by agent ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full responses on failure")
    parser.add_argument("--llm-grader", "-g", action="store_true", help="Use LLM to grade responses")
    parser.add_argument("--direct", action="store_true", help="Run agents directly (no API server needed)")
    args = parser.parse_args()

    run_evals(
        category=args.category,
        verbose=args.verbose,
        llm_grader=args.llm_grader,
        direct=args.direct,
        agent_id=args.agent,
    )
