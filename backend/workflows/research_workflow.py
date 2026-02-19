"""
Research Workflow
-----------------

A multi-step workflow that searches the web, analyzes findings,
and produces a structured research report.

Uses Agno's Workflow + Step primitives to chain agents together.
"""

from agno.workflow import Workflow
from agno.workflow.step import Step

from backend.agents.reasoning_agent import reasoning_agent
from backend.agents.web_search_agent import web_search_agent

# ---------------------------------------------------------------------------
# Research Workflow
# ---------------------------------------------------------------------------
research_workflow = Workflow(
    id="research-workflow",
    name="Research Workflow",
    description="Search the web for a topic, then analyze and synthesize findings into a structured report.",
    steps=[
        Step(
            name="Web Research",
            description="Search the web for information on the given topic.",
            agent=web_search_agent,
        ),
        Step(
            name="Analysis & Synthesis",
            description="Analyze the research findings and produce a structured report with key insights.",
            agent=reasoning_agent,
        ),
    ],
)
