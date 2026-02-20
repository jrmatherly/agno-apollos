---
name: doc-sync
description: Verify all project documentation reflects current codebase state after feature changes
disable-model-invocation: true
---

# Documentation Sync

Systematically verify all documentation files reflect the current codebase after feature changes.

## When to Use

After any feature PR, enhancement batch, or structural change to agents, teams, workflows, tools, context modules, or evals.

## Steps

### 1. Identify What Changed

Run `git diff --stat` (or `git diff --stat HEAD~N` for recent commits) to get the list of changed backend/frontend files. Categorize changes:

- **New files**: tools, context modules, knowledge assets, agents
- **Modified agents/teams/workflows**: instruction changes, new tools wired, new features
- **New env vars**: added to mise.toml, example.env, compose files
- **New eval features**: grader additions, test cases, runner flags
- **CLI changes**: new flags, new modes

### 2. Check Each Documentation File

Verify each file against the changes identified in Step 1. Read the actual file content, do not rely on memory.

| File                                   | What to Check                                                                                                         |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`                            | Backend packages list, commands section (task descriptions), conventions section (env vars, patterns), Agno API notes |
| `README.md`                            | Agents table, Development Tasks table (task flags), env vars table, CLI section                                       |
| `PROJECT_INDEX.md`                     | Project structure tree, core modules section, env vars table, architecture notes                                      |
| `.serena/memories/project-overview.md` | Agents list, tools list, context list, evals description, mise tasks list, env vars                                   |
| `docs/agents/*.mdx`                    | Per-agent pages: code example, features table, tools list, example queries                                            |
| `docs/reference/architecture.mdx`      | Backend directory table, project structure tree, evals description                                                    |
| `docs/reference/code-map.mdx`          | Agent wiring diagram, agent wiring table, context module table, eval harness diagram/table, tool patterns             |
| `docs/configuration/environment.mdx`   | All env var sections, new variable categories                                                                         |
| `frontend/README.md`                   | Only if frontend changes were made                                                                                    |
| `backend/README.md`                    | Only if backend changes were made                                                                                     |

### 3. Report Gaps

Present findings as a checklist:

```
Documentation Sync Results:

PASS:
- [x] CLAUDE.md — all changes reflected
- [x] PROJECT_INDEX.md — all changes reflected

GAPS FOUND:
- [ ] README.md — missing `-s` flag in evals:run task (line N)
- [ ] docs/agents/knowledge-agent.mdx — code example outdated (missing FileTools)
```

### 4. Fix Gaps

For each gap found, make the edit. After all edits:

1. Run `mise run docs:validate` to verify Mintlify build + broken links
2. Run `mise run validate` to verify backend + frontend code quality
3. Report both validation results with actual output

### 5. Confirm

Only claim completion after both validations pass with fresh output evidence.
