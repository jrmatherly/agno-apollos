"""
Research Workflow
-----------------

Multi-step research pipeline with a quality-gated loop.
Searches the web iteratively until findings meet a quality threshold,
then produces a structured analysis report.

Uses Agno's Loop + Condition primitives for iterative refinement.
"""

from typing import List

from agno.agent import Agent
from agno.workflow import Workflow
from agno.workflow.condition import Condition
from agno.workflow.loop import Loop
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput

from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.web_search_agent import web_search_agent
from backend.db import get_postgres_db
from backend.models import get_model

# ---------------------------------------------------------------------------
# Quality Gate: Inline Agents
# ---------------------------------------------------------------------------
quality_reviewer = Agent(
    name="Quality Reviewer",
    role="Evaluate research completeness",
    model=get_model(),
    instructions=[
        "You review research findings for completeness and quality.",
        "Evaluate whether the research is sufficient to answer the original question.",
        "If the research is comprehensive, end your response with: QUALITY_PASS",
        "If gaps remain, list the specific gaps and end with: QUALITY_FAIL",
        "Be strict - research must have multiple sources and address the core question.",
    ],
    markdown=True,
)

gap_filler = Agent(
    name="Gap Filler",
    role="Fill research gaps identified by quality review",
    model=get_model(),
    instructions=[
        "You are given feedback about gaps in research.",
        "Search the web to fill those specific gaps.",
        "Focus on the missing information identified by the reviewer.",
        "Always cite sources with URLs.",
    ],
    markdown=True,
)


# ---------------------------------------------------------------------------
# Loop End Condition
# ---------------------------------------------------------------------------
def research_quality_met(outputs: List[StepOutput]) -> bool:
    """Return True when research quality is sufficient (breaks loop)."""
    if not outputs:
        return False
    for output in outputs:
        content = str(output.content or "")
        if "QUALITY_PASS" in content:
            return True
    return False


# ---------------------------------------------------------------------------
# Complexity Evaluator
# ---------------------------------------------------------------------------
def is_complex_topic(step_input: StepInput) -> bool:
    """Return True if the input appears to be a complex multi-faceted topic."""
    text = str(step_input.previous_step_content or step_input.input or "").lower()
    complexity_signals = [
        "compare",
        "analyze",
        "evaluate",
        "trade-off",
        "pros and cons",
        "impact",
        "implications",
        "history",
        "evolution",
        "comprehensive",
        "deep dive",
        "in-depth",
        "thorough",
        "detailed",
    ]
    return any(signal in text for signal in complexity_signals)


# ---------------------------------------------------------------------------
# Research Workflow
# ---------------------------------------------------------------------------
research_workflow = Workflow(
    id="research-workflow",
    name="Research Workflow",
    description=(
        "Search the web for a topic, iteratively refine until quality threshold is met, "
        "then produce a structured analysis report."
    ),
    db=get_postgres_db(),
    add_workflow_history_to_steps=True,
    steps=[
        # Step 1: Initial broad research
        Step(
            name="Initial Research",
            description="Search the web for comprehensive information on the given topic.",
            agent=web_search_agent,
            max_retries=2,
        ),
        # Step 2: Quality-gated refinement loop (max 3 iterations)
        Loop(
            name="Quality Refinement",
            description="Review research quality and fill gaps until sufficient.",
            max_iterations=3,
            end_condition=research_quality_met,
            steps=[
                Step(
                    name="Quality Review",
                    description="Evaluate completeness of research. End with QUALITY_PASS or QUALITY_FAIL.",
                    agent=quality_reviewer,
                    add_workflow_history=True,
                ),
                Step(
                    name="Fill Gaps",
                    description="Search for information to fill gaps identified by the quality review.",
                    agent=web_search_agent,
                    add_workflow_history=True,
                    skip_on_failure=True,
                ),
            ],
        ),
        # Step 3: Conditional deep analysis for complex topics
        Condition(
            name="Complexity Check",
            description="Route to deep analysis for complex topics, or basic synthesis for simple ones.",
            evaluator=is_complex_topic,
            steps=[
                Step(
                    name="Deep Analysis",
                    description=(
                        "Produce a comprehensive analysis with multiple perspectives, "
                        "trade-offs, and structured sections. Include an executive summary."
                    ),
                    agent=reasoning_agent,
                    add_workflow_history=True,
                ),
            ],
            else_steps=[
                Step(
                    name="Basic Synthesis",
                    description="Produce a concise summary of research findings with key takeaways.",
                    agent=reasoning_agent,
                    add_workflow_history=True,
                ),
            ],
        ),
    ],
)
