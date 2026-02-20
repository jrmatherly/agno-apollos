"""
Reliability Evals
-----------------

Verifies that agents and teams call the expected tools on canonical prompts.
Uses Agno's ReliabilityEval class to check tool-call presence in RunResponse.

Usage:
    uv run python3 -m backend.evals.reliability_evals
    # or via mise:
    mise run evals:reliability
"""

import logging

from agno.eval.reliability import ReliabilityEval

from backend.agents.data_agent import data_agent
from backend.agents.web_search_agent import web_search_agent
from backend.db.session import get_eval_db
from backend.teams.research_team import research_team

logger = logging.getLogger(__name__)


def run_data_agent_reliability() -> list[ReliabilityEval]:
    """Check that the data agent calls query tools on a simple SQL question."""
    response = data_agent.run("How many races were held in 2019?")
    evals = [
        ReliabilityEval(
            name="data-agent-run-query",
            agent_response=response,
            expected_tool_calls=["run_query"],
            db=get_eval_db(),
        ),
        ReliabilityEval(
            name="data-agent-show-tables",
            agent_response=response,
            expected_tool_calls=["show_tables"],
            db=get_eval_db(),
        ),
    ]
    for e in evals:
        e.run(print_results=True)
    return evals


def run_web_search_reliability() -> list[ReliabilityEval]:
    """Check that the web search agent calls search tools on a current-events question."""
    response = web_search_agent.run("What is the latest news about Formula 1 in 2025?")
    evals = [
        ReliabilityEval(
            name="web-search-agent-web-search",
            agent_response=response,
            expected_tool_calls=["web_search"],
            db=get_eval_db(),
        ),
    ]
    for e in evals:
        e.run(print_results=True)
    return evals


def run_research_team_reliability() -> list[ReliabilityEval]:
    """Check that the research team delegates and uses search tools."""
    response = research_team.run("Research the latest Formula 1 team standings.")
    evals = [
        ReliabilityEval(
            name="research-team-delegate",
            team_response=response,
            expected_tool_calls=["delegate_task_to_member"],
            db=get_eval_db(),
        ),
        ReliabilityEval(
            name="research-team-web-search",
            team_response=response,
            expected_tool_calls=["web_search"],
            db=get_eval_db(),
        ),
    ]
    for e in evals:
        e.run(print_results=True)
    return evals


def run_all() -> None:
    """Run all reliability evals and log results."""
    logger.info("Running data agent reliability evals...")
    run_data_agent_reliability()

    logger.info("Running web search reliability evals...")
    run_web_search_reliability()

    logger.info("Running research team reliability evals...")
    run_research_team_reliability()

    logger.info("Reliability evals complete.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all()
