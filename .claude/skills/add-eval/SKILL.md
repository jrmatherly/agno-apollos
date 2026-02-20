---
name: add-eval
description: Scaffold eval test cases for an agent in backend/evals/test_cases.py, following the TestCase dataclass pattern used by DATA_AGENT_CASES, KNOWLEDGE_AGENT_CASES, and WEB_SEARCH_CASES
disable-model-invocation: true
---

Add `TestCase` entries for a new or existing agent to `backend/evals/test_cases.py`.

## Before You Start

1. Read `backend/evals/test_cases.py` — understand the `TestCase` dataclass and the existing case lists
2. Read the target agent at `backend/agents/<name>.py` — understand its `id=`, tools, knowledge sources, and expected output style
3. Read `backend/evals/run_evals.py` lines 1-30 — understand what fields are used during evaluation

## TestCase Schema

```python
@dataclass
class TestCase:
    question: str            # The user query sent to the agent
    expected_strings: list[str]  # Strings that MUST appear in the response
    category: str            # "basic" | "aggregation" | "data_quality" | "complex" | "edge_case" | "navigation"
    agent_id: str            # Must match the agent's id= field exactly (default: "data-agent")
    golden_sql: str | None   # Ground-truth SQL for data-agent cases (optional)
    expected_result: str | None  # Exact expected value for golden SQL comparison (optional)
    golden_path: str | None  # Knowledge path label for knowledge-agent cases (optional)
```

## Steps

1. **Add a named list** for the agent below the last existing `*_CASES` list:
   ```python
   # ---------------------------------------------------------------------------
   # <AgentName> Test Cases
   # ---------------------------------------------------------------------------
   <AGENT_ID_UPPER>_CASES: list[TestCase] = [
       ...
   ]
   ```

2. **Write 4–6 test cases** covering:
   - `basic` — typical, direct query the agent is designed to handle
   - `basic` — second typical query using a different tool or knowledge path
   - `complex` — multi-step or compound query
   - `edge_case` — query at the boundary of what the agent knows/can do
   - `edge_case` — query the agent should gracefully decline or redirect

3. **Set `agent_id`** to the exact string from the agent's `id=` constructor argument.

4. **Add to `ALL_CASES`** at the bottom of the file:
   ```python
   ALL_CASES = DATA_AGENT_CASES + KNOWLEDGE_AGENT_CASES + WEB_SEARCH_CASES + <AGENT_ID_UPPER>_CASES
   ```

## Rules

- `expected_strings` must be strings the agent will reliably produce — not LLM paraphrases. Use proper nouns, IDs, or keywords from the data, not generic words like "the" or "result".
- For `data-agent` cases, always include `golden_sql` when the answer is deterministic from the database. The runner uses it for exact result comparison.
- For `knowledge-agent` cases, set `golden_path` to the document section name when the answer should come from a specific loaded document.
- Do not add test cases requiring live external services (web, stock prices, real-time data) without noting that they need a running backend with appropriate tools enabled.
- `edge_case` tests for "out of scope" queries should use `expected_strings=["no"]` or a short substring the agent uses when declining — check the agent's system prompt for its exact refusal phrasing.

## Running Evals

```bash
# Run all cases for the agent
mise run evals:run -- -c basic           # filter by category
mise run evals:run                       # all cases
mise run evals:run -- -v                 # verbose (show full responses)
mise run evals:run -- -g                 # LLM grading mode
```

Requires: running backend (`mise run docker:up`) and loaded data (`mise run load-sample-data` for data-agent).
