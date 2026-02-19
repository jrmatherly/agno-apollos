# Session Prime

Initialize this session with project context and working conventions.

## Step 1: Assess Current State

Run these in parallel:
- `git status` (show working tree, never use `-uall`)
- `git log --oneline -5` (recent commits for context)
- `git branch --show-current` (current branch)

Report a brief summary: current branch, uncommitted changes (if any), last commit.

## Step 2: Know the Project Resources

These are available on-demand. Do NOT read them now — read when a task requires them.

| Resource | Path | Use When |
|----------|------|----------|
| Project index | `PROJECT_INDEX.md` | Need full project structure, module exports, dependencies, or architecture overview |
| Serena memory | `.serena/memories/project-overview.md` | Need quick project summary (agents, teams, workflows, env vars, dev tools) |
| Documentation site | `docs/` (Mintlify MDX) | Writing or updating user-facing docs. Use `/mintlify` skill. Key pages: `docs/docs.json` (nav), `docs/CLAUDE.md` (style guide) |
| Agno examples | `.local_docs/agno-examples/` | Need Agno cookbook patterns (agents, teams, workflows, tools, MCP) |
| Enhancement plans | `.scratchpad/agno-enhancements/` | Continuing planned enhancement work |
| Backend source | `backend/` | All Python code: agents, teams, workflows, tools, context, knowledge, evals, db |
| Frontend source | `frontend/src/` | Next.js app: components, hooks, api client, store, types |

## Step 3: Establish Session Rules

Follow these rules for the entire session:

### Skill Discipline
Before responding to ANY user request, check if an available skill applies. Even a 1% chance means invoke it. Key skills for this project:
- `/agno` — Use for ANY Agno framework question (agents, teams, workflows, tools, models, MCP). Always verify API signatures before using Agno APIs.
- `/add-agent`, `/add-team`, `/add-workflow` — Use when creating new components
- `/validate-all` — Use after making code changes
- `/new-mise-task` — Use when an operation needs a mise task
- Brainstorming, TDD, debugging, and other process skills — use when their triggers match

### Project Conventions (from CLAUDE.md)
CLAUDE.md is already loaded. Key reminders:
- Always use `mise run <task>` — never raw commands
- Always use `get_model()` — never inline model creation
- All agents need guardrails (including ephemeral workflow agents)
- Verify Agno API signatures with `python3 -c "import inspect; ..."` before using
- Keep docs in sync: CLAUDE.md, README.md, PROJECT_INDEX.md, .serena/memories/project-overview.md, docs/

### Git Worktrees
For feature work requiring isolation, use the `using-git-worktrees` skill. Worktree directory: `.worktrees/` (verify it's gitignored before use). Only set up a worktree when the task warrants isolation — not every session needs one. Pass `--worktree` or `-w` when invoking `/prime` to set one up immediately.

## Step 4: Handle Flags

If the user passed `--worktree` or `-w` with this command:
1. Invoke the `using-git-worktrees` skill
2. Follow its process to create an isolated workspace

Otherwise, skip worktree setup.

## Step 5: Ready

Confirm the session is primed with a one-line summary. Do not repeat the rules back. Just confirm readiness and ask what the user wants to work on.
