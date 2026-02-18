# Apollos AI

## Project Structure

All Python backend code lives under `backend/` as a proper package.
Imports use fully-qualified paths: `from backend.agents.x import y`, `from backend.db import z`.
Docker WORKDIR `/app` is the project root, not the Python package.
Frontend lives at `frontend/` — Next.js 15 (App Router), React 18, TypeScript, pnpm.
Dockerfiles live with their code: `backend/Dockerfile`, `frontend/Dockerfile`. Build context for backend is root `.` (needs pyproject.toml, uv.lock, scripts/).
Frontend Dockerfile uses multi-stage build with `output: 'standalone'` in next.config.ts.

## Commands (mise)

Task runner: `mise run <task>` (or `mise <task>` if no conflict).

- `mise run setup` - install all deps (backend: uv sync --dev, frontend: pnpm install)
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

Tool versions managed by mise (see `mise.toml`): Python 3.12, uv latest, Node 24, pnpm latest.

Frontend tasks:
- `mise run frontend:setup` - install frontend deps (pnpm install)
- `mise run frontend:dev` - start frontend dev server (port 3000)
- `mise run frontend:build` - production build
- `mise run frontend:lint` / `frontend:format` / `frontend:typecheck` / `frontend:validate`

## Mise Tasks

- Tasks are file-based scripts in `mise-tasks/` (not inline in `mise.toml`)
- Use `#MISE` comment headers for metadata: `description`, `depends`, `alias`
- Tasks must be executable (`chmod +x`)
- Subdirectories create namespaced tasks: `mise-tasks/docker/up` → `mise run docker:up`
- `scripts/` is container-only (just `entrypoint.sh`). Dev tasks go in `mise-tasks/`.
- `mise.local.toml` is gitignored — use for local developer overrides

## Development Workflow

- **Always use `mise run <task>` for project operations** — never run raw commands (pnpm, uv, ruff, mypy, docker compose) directly
- mise tasks are the single source of truth for how operations are performed
- If a task doesn't exist for an operation, create one in `mise-tasks/` rather than running ad-hoc commands
- For frontend dev, prefer `mise run frontend:dev` over `mise run dev` — compose watch rebuilds the entire container on source changes since standalone Next.js can't hot-reload synced files

## Conventions

- Model provider: `LiteLLMOpenAI` from `agno.models.litellm` (proxy class, uses `base_url`)
- All model/embedding config via env vars (MODEL_ID, EMBEDDING_MODEL_ID, LITELLM_BASE_URL, etc.)
- `agno.*` imports are the Agno framework library. Never rename or replace these.
- New agents go in `backend/agents/`, register in `backend/main.py`
- Keep `agnohq/python:3.12` and `agnohq/pgvector:18` base images. Frontend uses `node:24-alpine`.
- ruff line-length: 120
- Env var defaults live in `mise.toml` [env] section and `backend/db/session.py`
- Dependencies: `uv add <package>` (auto-updates uv.lock), never edit uv.lock manually
- Frontend uses pnpm (not npm/yarn). Local setup uses `pnpm install`; CI uses `--frozen-lockfile`.
- After changing frontend/package.json, run `mise run frontend:setup` to regenerate pnpm-lock.yaml.
- Frontend API calls are browser-side (client fetch), not server-side. API URL is configured in UI, not env vars.
- Docker compose has 3 services: `apollos-db` (:5432), `apollos-backend` (:8000), `apollos-frontend` (:3000)
- CI workflows run backend and frontend validation as parallel jobs
- `backend/Dockerfile.dockerignore` uses BuildKit naming convention (build context is root, not `backend/`)
- VS Code settings in `.vscode/` — format-on-save, ruff for Python, prettier for TS, file associations
- When updating project docs, keep in sync: CLAUDE.md, README.md, PROJECT_INDEX.md, .serena/memories/project-overview.md, frontend/README.md
- example.env must stay in sync when env vars are added/changed across the project

## Agno Docs Style

When writing documentation, follow `docs/CLAUDE.md`:
- No em dashes, no "learn how to", no contrastive negation
- Code first, explain after. Tables over prose for comparisons.
