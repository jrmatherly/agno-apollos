"""
A2A Agent Executor
------------------

Wraps Agno agents for A2A protocol message handling.
Supports both synchronous and streaming (SSE) responses.
"""

import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TextPart
from a2a.utils import new_agent_text_message
from agno.agent import Agent, Message

logger = logging.getLogger(__name__)


class AgnoAgentExecutor(AgentExecutor):
    """Wraps an Agno Agent for A2A protocol execution."""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle an incoming A2A message by routing to the Agno agent."""
        # Extract text from A2A message parts
        parts = context.message.parts if context.message and context.message.parts else []
        text_parts = [part.root.text for part in parts if isinstance(part.root, TextPart)]
        text = " ".join(text_parts).strip()

        if not text:
            event_queue.enqueue_event(new_agent_text_message("No message content received."))
            return

        logger.info("A2A request for %s: %s", self.agent.name, text[:100])

        try:
            result = await self.agent.arun(Message(role="user", content=text))
            content = result.content if result else "No response generated."
            event_queue.enqueue_event(new_agent_text_message(content or ""))
        except Exception:
            logger.exception("A2A execution failed for %s", self.agent.name)
            event_queue.enqueue_event(new_agent_text_message("An error occurred processing your request."))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle cancellation request."""
        logger.info("A2A cancellation requested for %s", self.agent.name)
        raise NotImplementedError("Cancellation not yet supported")
