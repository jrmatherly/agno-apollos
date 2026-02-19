# Apollos AI

## MANDATORY: Use td for Task Management

You must run td usage --new-session at conversation start (or after /clear) to see current work.
Use td usage -q for subsequent reads.

## Project Structure

All Python backend code lives under `backend/` as a proper package.
Imports use fully-qualified paths: `from backend.agents.x import y`, `from backend.db import z`.
Docker WORKDIR `/app` is the project root, not the Python package.
Frontend lives at `frontend/` — Next.js 15 (App Router), React 18, TypeScript, pnpm.
Documentation lives at `docs/` — Mintlify site (MDX pages, `docs.json` config). Preview on port 3333 to avoid frontend conflict.
Dockerfiles live with their code: `backend/Dockerfile`, `frontend/Dockerfile`, `docs/Dockerfile`. Build context for backend is root `.` (needs pyproject.toml, uv.lock, scripts/).
Frontend Dockerfile uses multi-stage build with `output: 'standalone'` in next.config.ts.

Backend packages:
- `backend/models.py` — Shared model factory (`get_model()`). All agents use this instead of inline `LiteLLMOpenAI`.
- `backend/agents/` — Agent definitions (knowledge, mcp, web_search, reasoning, data)
- `backend/teams/` — Multi-agent team definitions (research_team)
- `backend/workflows/` — Workflow definitions (research_workflow)
- `backend/tools/` — Custom tools (search, awareness, approved_ops)
- `backend/context/` — Context modules (semantic_model, intent_routing)
- `backend/knowledge/` — Document loaders (PDF/CSV from `data/docs/`)
- `backend/evals/` — LLM-based eval harness (grader, test cases, runner)
- `backend/telemetry.py` — OpenTelemetry trace export (opt-in)
- `tests/` — Integration tests (pytest + requests)
- `data/docs/` — Document storage for knowledge agent loaders

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

Testing and evaluation tasks:
- `mise run test` - run integration tests (pytest, requires running backend)
- `mise run evals:run` - run LLM-based evaluation suite

Auth and scheduling tasks:
- `mise run auth:generate-token` - generate dev JWT tokens for RBAC testing
- `mise run schedules:setup` - initialize scheduler tables

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

- Model provider: `LiteLLMOpenAI` from `agno.models.litellm` (proxy class, uses `base_url`). Use `backend/models.py:get_model()` — never inline model creation.
- All model/embedding config via env vars (MODEL_ID, EMBEDDING_MODEL_ID, LITELLM_BASE_URL, etc.)
- `agno.*` imports are the Agno framework library. Never rename or replace these.
- New agents go in `backend/agents/`, new teams in `backend/teams/`, new workflows in `backend/workflows/`. Register all in `backend/main.py`.
- All agents must have guardrails: `pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()]` — includes inline/ephemeral agents in workflows
- Agents with learning use `LearningMachine(learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC, knowledge=...))` from `agno.learn`
- JWT auth is opt-in: empty `JWT_SECRET_KEY` env var = auth disabled. Set a value to enable RBAC.
- Telemetry is opt-in: empty `OTEL_EXPORTER_OTLP_ENDPOINT` env var = traces not exported.
- When adding/changing env vars, update all four files: `mise.toml` (defaults), `example.env`, `docker-compose.yaml`, `docker-compose.prod.yaml`
- Keep `agnohq/python:3.12` and `agnohq/pgvector:18` base images. Frontend and docs use `node:24-alpine`.
- ruff line-length: 120
- Env var defaults live in `mise.toml` [[env]] section and `backend/db/session.py`
- `mise.toml` uses `[[env]]` array-of-tables: defaults in first block, `_.file = ".env"` in second block, so `.env` wins. Never use single `[env]` with both `_.file` and explicit values — explicit values override `_.file` regardless of position.
- Dependencies: `uv add <package>` (auto-updates uv.lock), never edit uv.lock manually
- `uv.lock` records the project version — any version bump in pyproject.toml requires `uv lock` to keep the lockfile in sync
- Frontend uses pnpm (not npm/yarn). Use `--ci` flag on setup/frontend:setup tasks for locked/frozen mode in CI.
- After changing frontend/package.json, run `mise run frontend:setup` to regenerate pnpm-lock.yaml.
- Frontend API calls are browser-side (client fetch), not server-side. API URL is configured in UI, not env vars.
- Two compose files: `docker-compose.yaml` (dev, builds locally) and `docker-compose.prod.yaml` (prod, pulls GHCR images)
- Docker compose env vars use `${VAR:-default}` substitution — never hardcode values. Defaults must match `mise.toml` and `example.env`.
- Docker compose has 3 core services: `apollos-db` (:5432), `apollos-backend` (:8000), `apollos-frontend` (:3000), plus optional `apollos-docs` (:3333, behind `docs` profile)
- CI workflows run backend and frontend validation as parallel jobs using mise tasks
- CI workflows use pinned action SHAs (not tags) for supply-chain security
- CodeQL security scanning runs on push/PR to main + weekly schedule (security-extended suite)
- Docker images publish to GHCR (`ghcr.io/<owner>/apollos-backend`, `ghcr.io/<owner>/apollos-frontend`, `ghcr.io/<owner>/apollos-docs`)
- Release flow: `mise run release` → validates → interactive version prompt → checks CI → bumps versions (pyproject.toml, package.json, uv.lock) → tags → GitHub release → Docker image builds
- `backend/Dockerfile.dockerignore` uses BuildKit naming convention (build context is root, not `backend/`)
- VS Code settings in `.vscode/` — format-on-save, ruff for Python, prettier for TS, file associations
- When updating project docs, keep in sync: CLAUDE.md, README.md, PROJECT_INDEX.md, .serena/memories/project-overview.md, frontend/README.md, docs/ (Mintlify site — especially agents/overview.mdx, teams/overview.mdx, workflows/overview.mdx, reference/architecture.mdx)
- example.env must stay in sync when env vars are added/changed across the project
- `.env` values must use Docker service names (e.g., `DB_HOST=apollos-db`) since the primary workflow is Docker-based

## Agno Framework API Notes

Always verify Agno API signatures with `python3 -c "import inspect; from agno.X import Y; print(inspect.signature(Y))"` before using. Docs and examples frequently have wrong signatures.

Known gotchas:
- `@tool` must be outer decorator, `@approval` inner (otherwise mypy error on Function type)
- `@approval(type="audit")` requires explicit HITL flag on `@tool()` (e.g., `@tool(requires_confirmation=True)`). Plain `@approval` auto-sets this.
- Team: use `id=` (not `team_id=`), `mode=TeamMode.coordinate` (not string). Import `from agno.team.team import TeamMode`.
- `member_timeout` and `max_interactions_to_share` do not exist on Team in current version
- Workflow Step: takes `agent=` or `executor=` (no `instructions` or `timeout_seconds` params)
- Condition: takes `evaluator` + `steps` + `else_steps` (not `on_true`/`on_false`)
- Loop `end_condition`: receives `List[StepOutput]`, returns `True` to break. Condition `evaluator`: receives `StepInput`, returns `True` for primary path. Check `step_input.input` for user query (not `previous_step_content` which has accumulated output).
- Knowledge readers: `agno.knowledge.reader.pdf_reader.PDFReader` (not `agno.document.reader`)
- `include_tools`/`exclude_tools`: On base `Toolkit` class, passed via `**kwargs` to PostgresTools etc.
- Model API for direct calls: `model.response(messages=[Message(role="user", content=...)])` (not `model.invoke(str)`)
- `enable_session_summaries` is on Agent (not AgentOS); `enable_mcp_server` is on AgentOS
- `show_tool_calls` is NOT a valid Agent parameter

## Agno Docs Style

When writing documentation, follow `docs/CLAUDE.md`:
- No em dashes, no "learn how to", no contrastive negation
- Code first, explain after. Tables over prose for comparisons.

## Documentation Site (Mintlify)

- Docs site lives at `docs/` — Mintlify MDX pages with `docs.json` config
- Preview: `mise run docs:dev` (port 3333, avoids frontend :3000 conflict)
- Validate: `mise run docs:validate` (runs `mint validate` + `mint broken-links`)
- Navigation structure defined in `docs/docs.json` — add new pages there or they won't appear in sidebar
- `docs/CLAUDE.md` is the docs style guide (excluded from build via `.mintignore`)
- `.mintignore` auto-excludes README.md, LICENSE.md, CHANGELOG.md, CONTRIBUTING.md — manually exclude other non-doc files
- Every MDX page needs `title` and `description` in frontmatter
- Internal links use root-relative paths without extensions: `/agents/overview` not `./agents/overview.mdx`
- Logo assets in `docs/logo/`, images in `docs/images/`
