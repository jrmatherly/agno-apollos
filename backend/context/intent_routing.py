"""
Intent Routing
--------------

Maps question types to optimal search strategies.
Following the Scout pattern: structured rules injected into agent
instructions that guide the agent on HOW to search based on the question.
"""

INTENT_ROUTING = """\
## Intent Routing Guide

| Question Type | Best Strategy | Example |
|---------------|---------------|---------|
| Factual lookup | Search knowledge base directly | "What is the API rate limit?" |
| How-to / tutorial | Search knowledge, then check learnings for tips | "How do I configure auth?" |
| Comparison | Search multiple topics, synthesize | "Compare REST vs GraphQL for our use case" |
| Troubleshooting | Check learnings first (saved solutions), then knowledge | "Why is the API returning 403?" |
| Current events | Delegate to web search agent or team | "What's new in the latest release?" |

When confidence is LOW (no good matches found):
- Say so explicitly: "I found limited information on this topic."
- Suggest alternative queries the user might try.
- Do NOT hallucinate an answer."""
