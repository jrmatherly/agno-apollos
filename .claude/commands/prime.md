# Session Prime

Initialize this session with superpowers, project context, and working conventions.

## Step 1: Establish Superpowers

Invoke the `superpowers:using-superpowers` skill using the Skill tool. This is mandatory — do not skip.

This consciously establishes the skill discipline for the session: **check for an applicable skill before ANY response or action, even a 1% chance requires invocation.**

## Step 2: Activate Project Context

Run all of these in parallel:

- Call `mcp__plugin_serena_serena__activate_project` with the current working directory to establish Serena's semantic code intelligence for this session
- `git status` (show working tree, never use `-uall`)
- `git log --oneline -5` (recent commits for context)
- `git branch --show-current` (current branch)

Report: current branch, uncommitted changes (if any), last commit. Confirm Serena project is active.

## Step 3: Know Your Memory & Knowledge Resources

Do NOT read these now. Retrieve on-demand when a task requires them.

### claude-mem — Auto-Captured Session History (Already Active)

claude-mem automatically injects compressed context from the last 10 sessions at session start — the `[agentos-docker] recent context` block visible in your system prompt is this injection. **No action needed at session start.**

For targeted searches of past work, use the **`claude-mem:mem-search` skill** which follows the mandatory 3-layer workflow:

| Layer | MCP Tool | Purpose | Cost |
|-------|----------|---------|------|
| 1. Search | `mcp__plugin_claude-mem_mcp-search__search` | Get index table with IDs (~50-100 tokens/result) | Low |
| 2. Timeline | `mcp__plugin_claude-mem_mcp-search__timeline` | Get surrounding context for interesting results | Low |
| 3. Fetch | `mcp__plugin_claude-mem_mcp-search__get_observations` | Full details ONLY for filtered IDs (~500-1000 tokens each) | High |

**Always filter before fetching — 10x token savings.** Never call `get_observations` without first searching.

**Save important discoveries:** `mcp__plugin_claude-mem_mcp-search__save_memory` with `project="agentos-docker"`

**Observation types:** 🔴 bugfix, 🟣 feature, 🔄 refactor, ✅ change, 🔵 discovery, ⚖️ decision

**When to use:** "Did we fix this before?", "How did we implement X?", "What did we decide about Y?", "What changed last week?"

### Serena Memories — Curated Project Knowledge

Serena memories contain stable, hand-maintained project knowledge (architecture, conventions, design decisions). Located in `.serena/memories/`.

| Action | MCP Tool | When to Use |
|--------|----------|-------------|
| List available memories | `mcp__plugin_serena_serena__list_memories` | Need to know what curated context exists |
| Read a memory | `mcp__plugin_serena_serena__read_memory` with `memory_name` | Architecture questions, "how does this project do X" |
| Write a new memory | `mcp__plugin_serena_serena__write_memory` | After establishing something worth persisting as project knowledge |
| Edit a memory | `mcp__plugin_serena_serena__edit_memory` | Updating stale or incorrect project knowledge |

**Current memories:** `project-overview.md` — agents, teams, workflows, architecture, env vars, dev tools.

**When to use:** architectural questions, agent design patterns, understanding established conventions. Use the MCP tools — not the Read/Write file tools — for Serena memories.

### Memory System Quick Reference

| "I need to know..." | Use |
|---------------------|-----|
| What bugs/features happened in past sessions | claude-mem search |
| How this project's architecture/agents/conventions work | Serena `read_memory` |
| What was said in a past conversation | `episodic-memory:search-conversations` skill |
| What files/code exist right now | Serena symbolic tools (`find_symbol`, `get_symbols_overview`) |

### Agno Framework — Primary Project Stack

This project IS an Agno application. Agents, teams, workflows, tools, the FastAPI AgentOS, and the LearningMachine stack are all Agno. The `agno:agno` skill is the authoritative API reference for all of it.

**Rule: Invoke `agno:agno` before writing, debugging, or modifying ANY Agno code.** Do not guess at parameter names or signatures — they change without warning.

> **Project override:** CLAUDE.md "Agno Framework API Notes" section documents known gotchas and project-specific corrections that take precedence over the generic skill patterns.

Available inside the skill on-demand (invoke via Skill tool, never read files directly):

| Reference | Content |
|-----------|---------|
| `agno:agno` SKILL.md | 10 working examples, key patterns, important rules |
| `references/agents.md` | Agent params, tools, memory, knowledge, guardrails |
| `references/teams.md` | Team modes (route/broadcast/tasks/coordinate), coordination |
| `references/workflows.md` | Step, Parallel, Condition, Loop, Router |
| `references/mcp.md` | MCPTools, MultiMCPTools, transports (stdio/SSE/HTTP) |
| `references/tools.md` | 120+ built-in tools, custom `@tool` creation, tool hooks |
| `references/learning.md` | LearningMachine (profiles, memory, session, knowledge, entity) |
| `references/models.md` | 40+ model providers and configuration |

**Local cookbook:** `.local_docs/agno-examples/` — cookbook patterns adapted for this project.
**Signature verification:** `python3 -c "import inspect; from agno.X import Y; print(inspect.signature(Y))"`

### Project Resources — Read on Demand

| Resource | Path | Use When |
|----------|------|----------|
| Project index | `PROJECT_INDEX.md` | Full project structure, module exports, dependencies, architecture overview |
| Documentation site | `docs/` (Mintlify MDX) | Writing or updating user-facing docs. Key: `docs/docs.json` (nav), `docs/CLAUDE.md` (style guide). Use `/mintlify` skill. |
| Enhancement plans | `.scratchpad/agno-enhancements/` | Continuing planned enhancement work |
| Backend source | `backend/` | All Python code: agents, teams, workflows, tools, context, knowledge, evals, db |
| Frontend source | `frontend/src/` | Next.js app: components, hooks, api client, store, types |

## Step 4: Establish Session Rules

Follow these rules for the entire session:

### Skill Discipline

Before responding to ANY user request, check if an available skill applies. Even a 1% chance means invoke it. Key skills for this project:

- **`agno:agno` (invoke first for all Agno work)** — Agents, teams, workflows, tools, MCP, LearningMachine, AgentOS. This is an Agno project — this skill applies to the majority of work. Always verify API signatures.
- `/add-agent`, `/add-team`, `/add-workflow` — Use when creating new components
- `/validate-all` — Use after making code changes
- `/new-mise-task` — Use when an operation needs a mise task
- `/doc-sync` — Use after changes that should be reflected in documentation
- `claude-mem:mem-search` — Use when looking for past decisions or implementations
- Brainstorming, TDD, debugging, and other process skills — use when their triggers match

### Project Conventions (from CLAUDE.md)

CLAUDE.md is already loaded. Key reminders:

- Always use `mise run <task>` — never raw commands
- Always use `get_model()` — never inline model creation
- All agents need guardrails (including ephemeral workflow agents)
- Verify Agno API signatures with `python3 -c "import inspect; ..."` before using
- Keep docs in sync: CLAUDE.md, README.md, PROJECT_INDEX.md, .serena/memories/project-overview.md, docs/
- Serena memories: use `write_memory`/`edit_memory` MCP tools, not Write/Edit file tools
- claude-mem saves: use `save_memory` MCP tool with `project="agentos-docker"`

### Git Worktrees

For feature work requiring isolation, invoke the `superpowers:using-git-worktrees` skill. Worktree directory: `.worktrees/` (verify it's gitignored before use). Only set up a worktree when the task warrants isolation. Pass `--worktree` or `-w` when invoking `/prime` to set one up immediately.

## Step 5: Handle Flags

If the user passed `--worktree` or `-w` with this command:

1. Invoke the `superpowers:using-git-worktrees` skill
2. Follow its process to create an isolated workspace

Otherwise, skip worktree setup.

## Step 6: Ready

Confirm the session is primed with a one-line summary. Do not repeat the rules back. Just confirm readiness and ask what the user wants to work on.
