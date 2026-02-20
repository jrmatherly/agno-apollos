"""
Agent CLI
---------

Shared Rich CLI for running agents directly from the command line.
Supports single-question mode and interactive prompt loop.

Features from Agno cli_app that are also supported:
- user_id: Link sessions to specific users
- markdown: Toggle markdown rendering in output
- show_reasoning: Display agent thinking steps
- exit_on: Configurable exit commands

Usage:
    python -m backend.agents.data_agent -q "What tables exist?"
    python -m backend.agents.data_agent --user-id user123
    python -m backend.agents.data_agent --markdown --show-reasoning
    python -m backend.agents.data_agent  # interactive mode
"""

import argparse

from agno.agent import Agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Default exit commands (matches Agno cli_app defaults + our extras)
DEFAULT_EXIT_COMMANDS = ["exit", "quit", "q", "bye"]


def run_agent_cli(
    agent: Agent,
    default_question: str = "Hello",
    user: str = "User",
    emoji: str = ":sunglasses:",
    exit_on: list[str] | None = None,
) -> None:
    """Run an agent via CLI with Rich output.

    Args:
        agent: The agent instance to run.
        default_question: Example question shown in help text.
        user: Display name for the user prompt.
        emoji: Emoji shown in the user prompt.
        exit_on: Commands that exit interactive mode.
    """
    parser = argparse.ArgumentParser(description=f"Run {agent.name} directly")
    parser.add_argument(
        "--question", "-q", help=f"Single question (default: interactive mode). Example: '{default_question}'"
    )
    parser.add_argument("--stream", action="store_true", default=True, help="Stream output (default)")
    parser.add_argument("--no-stream", dest="stream", action="store_false", help="Disable streaming")
    parser.add_argument("--session-id", "-s", help="Session ID for persistence")
    parser.add_argument("--user-id", "-u", help="User ID for session linking")
    parser.add_argument("--markdown", "-m", action="store_true", help="Enable markdown rendering in output")
    parser.add_argument("--show-reasoning", action="store_true", help="Show agent reasoning/thinking steps")
    args = parser.parse_args()

    exit_commands = exit_on or DEFAULT_EXIT_COMMANDS

    console.print(Panel(f"[bold]{agent.name}[/bold] ({agent.id})", style="blue"))

    if args.question:
        _run_single(
            agent,
            args.question,
            stream=args.stream,
            session_id=args.session_id,
            user_id=args.user_id,
            markdown=args.markdown,
            show_reasoning=args.show_reasoning,
        )
    else:
        _run_interactive(
            agent,
            stream=args.stream,
            session_id=args.session_id,
            user_id=args.user_id,
            markdown=args.markdown,
            show_reasoning=args.show_reasoning,
            user=user,
            emoji=emoji,
            exit_commands=exit_commands,
        )


def _run_single(
    agent: Agent,
    question: str,
    *,
    stream: bool,
    session_id: str | None,
    user_id: str | None,
    markdown: bool,
    show_reasoning: bool,
) -> None:
    """Run a single question and exit."""
    console.print(f"\n[dim]> {question}[/dim]\n")
    if stream:
        agent.print_response(
            question,
            stream=True,
            session_id=session_id,
            user_id=user_id,
            markdown=markdown,
            show_reasoning=show_reasoning,
        )
    else:
        result = agent.run(question, session_id=session_id, user_id=user_id)
        console.print(result.content or "")


def _run_interactive(
    agent: Agent,
    *,
    stream: bool,
    session_id: str | None,
    user_id: str | None,
    markdown: bool,
    show_reasoning: bool,
    user: str,
    emoji: str,
    exit_commands: list[str],
) -> None:
    """Run an interactive prompt loop."""
    exit_hint = "/".join(exit_commands[:3])
    console.print(f"[dim]Type a question (or '{exit_hint}' to quit)[/dim]\n")
    while True:
        try:
            question = console.input(f"[bold green] {emoji} {user} [/bold green]")
        except (EOFError, KeyboardInterrupt):
            break

        question = question.strip()
        if not question:
            continue
        if question.lower() in exit_commands:
            break

        console.print()
        if stream:
            agent.print_response(
                question,
                stream=True,
                session_id=session_id,
                user_id=user_id,
                markdown=markdown,
                show_reasoning=show_reasoning,
            )
        else:
            result = agent.run(question, session_id=session_id, user_id=user_id)
            console.print(result.content or "")
        console.print()

    console.print(Text("\nGoodbye!", style="dim"))
