# Apollos AI

## Project Structure

All Python backend code lives under `backend/` as a proper package.
Imports use fully-qualified paths: `from backend.agents.x import y`, `from backend.db import z`.
Docker WORKDIR `/app` is the project root, not the Python package.
Frontend lives at `frontend/` — Next.js 15 (App Router), React 18, TypeScript, pnpm.
Documentation lives at `docs/` — Mintlify site (MDX pages, `docs.json` config). Preview on port 3333 to avoid frontend conflict.
Dockerfiles live with their code: `backend/Dockerfile`, `frontend/Dockerfile`, `docs/Dockerfile`. Build context for backend is root `.` (needs pyproject.toml, uv.lock, scripts/).

Backend packages: `backend/agents/`, `backend/teams/`, `backend/workflows/`, `backend/tools/`, `backend/context/`, `backend/knowledge/`, `backend/evals/`, `backend/scripts/`, `backend/registry.py` (component registry for Agent-as-Config), `backend/a2a/` (A2A protocol integration), `backend/auth/` (Entra ID JWT middleware, RBAC scope mapping, user/team sync, auth API routes), `backend/maintenance.py` (memory optimization + usage warnings), `backend/models.py` (shared `get_model()`), `backend/telemetry.py` (dual-layer tracing, opt-in), `backend/cli.py` (shared Rich CLI).
Data: `data/docs/` (knowledge docs), `data/tables/` (F1 metadata), `data/queries/` (SQL patterns), `data/business/` (rules).
Tests: `tests/` — pytest + requests.

## Commands (mise)

Task runner: `mise run <task>` (or `mise <task>` if no conflict).

- `mise run setup` - install all deps (add `--ci` for locked/frozen lockfiles)
- `mise run format` - format code (add `--check` for CI check-only mode)
- `mise run lint` - lint (ruff check)
- `mise run typecheck` - type check (mypy)
- `mise run validate` - all checks (format-check + lint + typecheck)
- `mise run dev` - docker compose watch (hot-reload)
- `mise run docker:up` - start full stack (add `--prod` for GHCR images, `--docs` to include docs service)
- `mise run docker:down` - stop stack (add `--prod` for production compose file)
- `mise run docker:logs` - tail logs (add `--prod` for production compose file)
- `mise run docker:build` - build backend, frontend, and docs images locally (add `--platform amd64` or `arm64`)
- `mise run db` - start database only
- `mise run load-docs` - load knowledge base documents
- `mise run ci` - full CI pipeline
- `mise run clean` - clean build artifacts
- `mise run release` - create GitHub release (interactive version prompt, validates, checks CI, triggers Docker builds)

Tool versions managed by mise (see `mise.toml`): Python 3.12, uv latest, Node 24, pnpm latest.

Frontend tasks:

- `mise run frontend:setup` - install frontend deps (add `--ci` for frozen lockfile)
- `mise run frontend:dev` - start frontend dev server (port 3000)
- `mise run frontend:build` - production build
- `mise run frontend:lint` / `frontend:format` / `frontend:typecheck` / `frontend:validate`

Docs tasks:

- `mise run docs:dev` - preview docs site locally (port 3333, avoids frontend port conflict)
- `mise run docs:validate` - validate docs build and check for broken links
- `mise run docs:docker` - start docs in Docker (add `--prod` for GHCR image)

Data loading tasks:

- `mise run load-sample-data` - load F1 sample data into PostgreSQL for dev/demo/evals
- `mise run load-knowledge` - load knowledge files (tables, queries, business rules) into vector DB (add `--recreate` to drop and reload)

Testing and evaluation tasks:

- `mise run test` - run integration tests (pytest, requires running backend)
- `mise run evals:run` - run eval suite (`-c` category, `-v` verbose, `-g` LLM grading, `-s` source checking, `--direct` mode; golden SQL comparison runs automatically)
- `mise run evals:reliability` - run tool-call reliability evals for all agents and research team
- `mise run maintenance:optimize-memories` - summarize and compress agent memories for all users
- `mise run agent:cli` - run agent via CLI (`-- <module> [-q question]`)

Test conventions:

- Tests use fixtures from `tests/conftest.py`: `backend_url` (waits for healthy backend), `session` (requests with retries), `url_for` (builds API URLs, rejects `/v1/` prefix)

Auth and scheduling tasks:

- `mise run auth:generate-token` - generate dev JWT tokens for RBAC testing
- `mise run schedules:setup` - initialize scheduler tables
- `mise run hooks:install` - install git pre-commit hook (auto-formats + validates before each commit)

## Mise Tasks

- Tasks are file-based scripts in `mise-tasks/` (not inline in `mise.toml`)
- Use `#MISE` comment headers for metadata: `description`, `depends`, `alias`
- Tasks must be executable (`chmod +x`)
- Subdirectories create namespaced tasks: `mise-tasks/docker/up` → `mise run docker:up`
- `scripts/` is container-only (just `entrypoint.sh`). Dev tasks go in `mise-tasks/`.
- `mise.local.toml` is gitignored — use for local developer overrides
- Interactive tasks (prompts/input) must use `read < /dev/tty` and `echo > /dev/tty` — mise does not forward stdin/stderr

## Development Workflow

- **Always use `mise run <task>` for project operations** — never run raw commands (pnpm, uv, ruff, mypy, docker compose) directly
- mise tasks are the single source of truth for how operations are performed
- If a task doesn't exist for an operation, create one in `mise-tasks/` rather than running ad-hoc commands
- For frontend dev, prefer `mise run frontend:dev` over `mise run dev` — compose watch rebuilds the entire container on source changes since standalone Next.js can't hot-reload synced files

## Conventions

### API & Backend

- **API routes have NO `/v1/` prefix.** AgentOS registers at `/agents/...`, `/teams/...`, `/workflows/...`, `/schedules/...`. Agno upstream docs use `/v1/` paths — do NOT copy that pattern. In tests, use the `url_for` helper from conftest.py.
- **Agent/team run endpoints use form data, not JSON.** `POST /agents/{id}/runs` uses `Form(...)` params. Send `data={"message": ..., "stream": "false"}` (not `json=`). Boolean form fields must be strings (`"false"`, not `False`).
- Model provider: use `get_model()` from `backend/models.py` — never inline `LiteLLMOpenAI` creation.
- All model/embedding config via env vars (MODEL_ID, EMBEDDING_MODEL_ID, LITELLM_BASE_URL, etc.)
- `agno.*` imports are the Agno framework library. Never rename or replace these.
- New agents in `backend/agents/`, teams in `backend/teams/`, workflows in `backend/workflows/`. Register all in `backend/main.py`.
- Auth is opt-in: empty `AZURE_TENANT_ID`/`AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_AUDIENCE` = auth disabled (passthrough mode for local dev). Set all 4 to enable Entra ID RBAC.
- **Azure audience**: `AZURE_AUDIENCE` is set as `api://clientId` but middleware accepts both `api://clientId` and bare GUID — Azure issues the bare GUID when SPA client and API resource share one app registration (single-app setup), even with `accessTokenAcceptedVersion: 2`.
- `JWT_SECRET_KEY` is retained for backward compat but superseded by Entra ID when Azure vars are set.
- Auth architecture: `EntraJWTMiddleware` on `base_app` (FastAPI), passed to `AgentOS(base_app=base_app)`. No `authorization=True` on AgentOS.
- `backend/auth/` package: config, middleware, jwks_cache, scope_mapper, models, database, graph, sync_service, dependencies, routes, security_headers, m365_token_service, m365_routes, m365_middleware, __init__
- New auth API routes: `GET /auth/health`, `GET /auth/me`, `POST /auth/sync`, `GET /auth/teams`, `GET /auth/users`
- M365 integration is opt-in: `M365_ENABLED=true` registers the M365 agent and mounts `/m365/` API routes. Requires Entra ID auth (Azure vars must be set). OBO token exchange in `backend/auth/m365_token_service.py`. MCP tools in `backend/tools/m365.py`. Frontend settings at `frontend/src/app/settings/m365/page.tsx`. Docker service `apollos-m365-mcp` uses `profiles: [m365]`.
- Telemetry is opt-in: `TRACING_ENABLED=true` stores traces in PostgreSQL (Layer 1). `OTLP_ENDPOINTS` exports to Langfuse/Phoenix/etc (Layer 2). Legacy `OTEL_EXPORTER_OTLP_ENDPOINT` supported as fallback.
- A2A Protocol: `A2A_ENABLED=true` exposes each agent at `/a2a/agents/{id}` via the Agent-to-Agent protocol (a2a-sdk v0.3.x). Set `A2A_BASE_URL` for production AgentCard URLs.
- Agent-as-Config: Central Registry in `backend/registry.py` maps tools/functions by name for save/load persistence via Agno Registry.
- `DOCUMENTS_DIR` env var controls the knowledge agent file browsing directory (default: `data/docs`).
- ruff line-length: 120

### Environment & Config

- When adding/changing env vars, update all four files: `mise.toml` (defaults), `example.env`, `docker-compose.yaml`, `docker-compose.prod.yaml`
- For Azure auth env vars, update all five: `mise.toml`, `example.env`, `docker-compose.yaml` (backend `environment:` + frontend `build.args:`), `docker-compose.prod.yaml`
- `NEXT_PUBLIC_AZURE_*` vars are baked at Next.js build time — must be set as `build.args` in docker-compose and declared as `ARG`/`ENV` in `frontend/Dockerfile`
- `mise.toml` uses `[[env]]` array-of-tables: defaults in first block, `_.file = ".env"` in second block, so `.env` wins. Never use single `[env]` with both `_.file` and explicit values — explicit values override `_.file` regardless of position.
- `.env` values must use Docker service names (e.g., `DB_HOST=apollos-db`) since the primary workflow is Docker-based
- Dependencies: `uv add <package>` (auto-updates uv.lock). Never edit uv.lock manually.
- `uv.lock` records the project version — any version bump in pyproject.toml requires `uv lock` to keep the lockfile in sync.

### Docker & Infrastructure

- Two compose files: `docker-compose.yaml` (dev, builds locally) and `docker-compose.prod.yaml` (prod, pulls GHCR images)
- Docker compose env vars use `${VAR:-default}` substitution — never hardcode values. Defaults must match `mise.toml` and `example.env`.
- Core services: `apollos-db` (:5432), `apollos-backend` (:8000), `apollos-frontend` (:3000), optional `apollos-docs` (:3333, behind `docs` profile)
- Base images: `agnohq/python:3.12` and `agnohq/pgvector:18`. Frontend and docs use `node:24-alpine`.
- `backend/Dockerfile.dockerignore` uses BuildKit naming convention (build context is root `.`, not `backend/`)
- Docker images publish to GHCR (`ghcr.io/<owner>/apollos-backend`, `ghcr.io/<owner>/apollos-frontend`, `ghcr.io/<owner>/apollos-docs`)

### CI/CD

- CI workflows use pinned action SHAs (not tags) for supply-chain security
- CI workflows use mise tasks (not raw commands) for consistency
- CodeQL security scanning runs on push/PR to main + weekly schedule (security-extended suite)
- Release flow: `mise run release` → validates → interactive version prompt → checks CI → bumps versions (pyproject.toml, package.json, uv.lock) → tags → GitHub release → Docker builds

### Documentation

- When updating project docs, keep in sync: CLAUDE.md, README.md, PROJECT_INDEX.md, .serena/memories/project-overview.md, frontend/README.md, mise.toml (task listing comment block), docs/ (especially agents/*.mdx, reference/architecture.mdx, reference/code-map.mdx, configuration/environment.mdx)
- example.env must stay in sync when env vars are added/changed across the project
- VS Code settings in `.vscode/` — format-on-save, ruff for Python, prettier for TS, file associations
- Docs style guide: follow `docs/CLAUDE.md` when writing or editing any Mintlify MDX pages
