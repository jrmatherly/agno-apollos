# Apollos AI

## Project Structure

All Python backend code lives under `backend/` as a proper package.
Imports use fully-qualified paths: `from backend.agents.x import y`, `from backend.db import z`.
Docker WORKDIR `/app` is the project root, not the Python package.

## Commands (mise)

Task runner: `mise run <task>` (or `mise <task>` if no conflict).

- `mise run setup` - install all deps (uv sync --dev)
- `mise run format` - format code (ruff format + import sort)
- `mise run lint` - lint (ruff check)
- `mise run typecheck` - type check (mypy)
- `mise run validate` - all checks (format-check + lint + typecheck)
- `mise run dev` - docker compose watch (hot-reload)
- `mise run docker:up` - start full stack
- `mise run docker:down` - stop stack
- `mise run docker:logs` - tail logs
- `mise run docker:build` - multi-arch image build
- `mise run db` - start database only
- `mise run load-docs` - load knowledge base documents
- `mise run ci` - full CI pipeline
- `mise run clean` - clean build artifacts

Tool versions managed by mise (see `mise.toml`): Python 3.12, uv latest.

## Mise Tasks

- Tasks are file-based scripts in `mise-tasks/` (not inline in `mise.toml`)
- Use `#MISE` comment headers for metadata: `description`, `depends`, `alias`
- Tasks must be executable (`chmod +x`)
- Subdirectories create namespaced tasks: `mise-tasks/docker/up` → `mise run docker:up`
- `scripts/` is container-only (just `entrypoint.sh`). Dev tasks go in `mise-tasks/`.
- `mise.local.toml` is gitignored — use for local developer overrides

## Conventions

- Model provider: `LiteLLMOpenAI` from `agno.models.litellm` (proxy class, uses `base_url`)
- All model/embedding config via env vars (MODEL_ID, EMBEDDING_MODEL_ID, LITELLM_BASE_URL, etc.)
- `agno.*` imports are the Agno framework library. Never rename or replace these.
- New agents go in `backend/agents/`, register in `backend/main.py`
- Keep `agnohq/python:3.12` and `agnohq/pgvector:18` base images
- ruff line-length: 120
- Env var defaults live in `mise.toml` [env] section and `backend/db/session.py`
- Dependencies: `uv add <package>` (auto-updates uv.lock), never edit uv.lock manually

## Agno Docs Style

When writing documentation, follow `docs/CLAUDE.md`:
- No em dashes, no "learn how to", no contrastive negation
- Code first, explain after. Tables over prose for comparisons.
