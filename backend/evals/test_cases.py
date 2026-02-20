"""
Eval Test Cases
---------------

Test cases for evaluating agent responses.
Each test case includes question, expected strings, category,
and optional golden SQL for result comparison.
"""

from dataclasses import dataclass


@dataclass
class TestCase:
    """A test case for evaluating an agent."""

    question: str
    expected_strings: list[str]
    category: str
    agent_id: str = "data-agent"
    golden_sql: str | None = None
    expected_result: str | None = None
    golden_path: str | None = None


# ---------------------------------------------------------------------------
# Data Agent Test Cases (F1 Dataset)
# ---------------------------------------------------------------------------
DATA_AGENT_CASES: list[TestCase] = [
    # Basic
    TestCase(
        question="Who won the most races in 2019?",
        expected_strings=["Hamilton", "11"],
        category="basic",
        golden_sql="""
            SELECT name, COUNT(*) as wins
            FROM race_wins
            WHERE EXTRACT(YEAR FROM TO_DATE(date, 'DD Mon YYYY')) = 2019
            GROUP BY name
            ORDER BY wins DESC
            LIMIT 1
        """,
    ),
    TestCase(
        question="Which team won the 2020 constructors championship?",
        expected_strings=["Mercedes"],
        category="basic",
        golden_sql="""
            SELECT team
            FROM constructors_championship
            WHERE year = 2020 AND position = 1
        """,
    ),
    TestCase(
        question="Who won the 2020 drivers championship?",
        expected_strings=["Hamilton"],
        category="basic",
        golden_sql="""
            SELECT name
            FROM drivers_championship
            WHERE year = 2020 AND position = '1'
        """,
    ),
    TestCase(
        question="How many races were there in 2019?",
        expected_strings=["21"],
        category="basic",
        golden_sql="""
            SELECT COUNT(DISTINCT venue) as race_count
            FROM race_wins
            WHERE EXTRACT(YEAR FROM TO_DATE(date, 'DD Mon YYYY')) = 2019
        """,
        expected_result="21",
    ),
    # Aggregation
    TestCase(
        question="Which driver has won the most world championships?",
        expected_strings=["Schumacher", "7"],
        category="aggregation",
        golden_sql="""
            SELECT name, COUNT(*) as titles
            FROM drivers_championship
            WHERE position = '1'
            GROUP BY name
            ORDER BY titles DESC
            LIMIT 1
        """,
    ),
    TestCase(
        question="Which constructor has won the most championships?",
        expected_strings=["Ferrari"],
        category="aggregation",
        golden_sql="""
            SELECT team, COUNT(*) as titles
            FROM constructors_championship
            WHERE position = 1
            GROUP BY team
            ORDER BY titles DESC
            LIMIT 1
        """,
    ),
    TestCase(
        question="How many race wins does Lewis Hamilton have in total?",
        expected_strings=["Hamilton"],
        category="aggregation",
        golden_sql="""
            SELECT COUNT(*) as wins
            FROM race_wins
            WHERE name = 'Lewis Hamilton'
        """,
    ),
    # Data quality
    TestCase(
        question="Who finished second in the 2019 drivers championship?",
        expected_strings=["Bottas"],
        category="data_quality",
        golden_sql="""
            SELECT name
            FROM drivers_championship
            WHERE year = 2019 AND position = '2'
        """,
    ),
    TestCase(
        question="How many races did Ferrari win in 2019?",
        expected_strings=["3"],
        category="data_quality",
        golden_sql="""
            SELECT COUNT(*) as wins
            FROM race_wins
            WHERE team = 'Ferrari'
              AND EXTRACT(YEAR FROM TO_DATE(date, 'DD Mon YYYY')) = 2019
        """,
        expected_result="3",
    ),
    # Complex
    TestCase(
        question="Compare Ferrari vs Mercedes championship points from 2015-2020",
        expected_strings=["Ferrari", "Mercedes"],
        category="complex",
    ),
    TestCase(
        question="Which driver won the most races for Ferrari?",
        expected_strings=["Schumacher"],
        category="complex",
        golden_sql="""
            SELECT name, COUNT(*) as wins
            FROM race_wins
            WHERE team = 'Ferrari'
            GROUP BY name
            ORDER BY wins DESC
            LIMIT 1
        """,
    ),
    # Edge cases
    TestCase(
        question="Who won the constructors championship in 1950?",
        expected_strings=["1958"],
        category="edge_case",
    ),
    TestCase(
        question="Which driver has exactly 5 world championships?",
        expected_strings=["Fangio"],
        category="edge_case",
        golden_sql="""
            SELECT name
            FROM (
                SELECT name, COUNT(*) as titles
                FROM drivers_championship
                WHERE position = '1'
                GROUP BY name
            ) t
            WHERE titles = 5
        """,
    ),
]

# ---------------------------------------------------------------------------
# Knowledge Agent Test Cases
# ---------------------------------------------------------------------------
KNOWLEDGE_AGENT_CASES: list[TestCase] = [
    TestCase(
        question="What is Agno?",
        expected_strings=["Agno", "framework", "agent"],
        category="basic",
        agent_id="knowledge-agent",
    ),
]

# ---------------------------------------------------------------------------
# Web Search Agent Test Cases
# ---------------------------------------------------------------------------
WEB_SEARCH_CASES: list[TestCase] = [
    TestCase(
        question="What is the current version of Python?",
        expected_strings=["Python", "3"],
        category="basic",
        agent_id="web-search-agent",
    ),
]

# ---------------------------------------------------------------------------
# Aggregated
# ---------------------------------------------------------------------------
ALL_CASES = DATA_AGENT_CASES + KNOWLEDGE_AGENT_CASES + WEB_SEARCH_CASES

CATEGORIES = ["basic", "aggregation", "data_quality", "complex", "edge_case"]
