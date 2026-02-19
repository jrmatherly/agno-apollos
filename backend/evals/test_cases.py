"""Eval test cases — question + expected answer pairs."""

KNOWLEDGE_AGENT_CASES = [
    {
        "question": "What is Agno?",
        "expected": "Agno is a framework for building AI agents",
        "agent_id": "knowledge-agent",
    },
]

WEB_SEARCH_CASES = [
    {
        "question": "What is the current version of Python?",
        "expected": "Python 3",
        "agent_id": "web-search-agent",
    },
]

ALL_CASES = KNOWLEDGE_AGENT_CASES + WEB_SEARCH_CASES
