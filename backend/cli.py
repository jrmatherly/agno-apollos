"""
Agent CLI
---------

Shared Rich CLI for running agents directly from the command line.
Supports single-question mode and interactive prompt loop.

Usage:
    python -m backend.agents.data_agent -q "What tables exist?"
    python -m backend.agents.data_agent  # interactive mode
"""

import argparse

from agno.agent import Agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def run_agent_cli(agent: Agent, default_question: str = "Hello") -> None:
    """Run an agent via CLI with Rich output.

    Args:
        agent: The agent instance to run.
        default_question: Example question shown in help text.
    """
    parser = argparse.ArgumentParser(description=f"Run {agent.name} directly")
    parser.add_argument(
        "--question", "-q", help=f"Single question (default: interactive mode). Example: '{default_question}'"
    )
    parser.add_argument("--stream", action="store_true", default=True, help="Stream output (default)")
    parser.add_argument("--no-stream", dest="stream", action="store_false", help="Disable streaming")
    parser.add_argument("--session-id", "-s", help="Session ID for persistence")
    args = parser.parse_args()

    console.print(Panel(f"[bold]{agent.name}[/bold] ({agent.id})", style="blue"))

    if args.question:
        _run_single(agent, args.question, stream=args.stream, session_id=args.session_id)
    else:
        _run_interactive(agent, stream=args.stream, session_id=args.session_id)


def _run_single(agent: Agent, question: str, *, stream: bool, session_id: str | None) -> None:
    """Run a single question and exit."""
    console.print(f"\n[dim]> {question}[/dim]\n")
    if stream:
        agent.print_response(question, stream=True, session_id=session_id)
    else:
        result = agent.run(question, session_id=session_id)
        console.print(result.content or "")


def _run_interactive(agent: Agent, *, stream: bool, session_id: str | None) -> None:
    """Run an interactive prompt loop."""
    console.print("[dim]Type a question (or 'exit' to quit)[/dim]\n")
    while True:
        try:
            question = console.input("[bold green]> [/bold green]")
        except (EOFError, KeyboardInterrupt):
            break

        question = question.strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            break

        console.print()
        if stream:
            agent.print_response(question, stream=True, session_id=session_id)
        else:
            result = agent.run(question, session_id=session_id)
            console.print(result.content or "")
        console.print()

    console.print(Text("\nGoodbye!", style="dim"))
