# Project Index: Apollos AI

Generated: 2026-02-18

## Project Structure

```
apollos-ai/
├── backend/                 # All Python backend code
│   ├── __init__.py
│   ├── main.py              # Entry point — creates Apollos AI, registers agents
│   ├── config.yaml          # UI quick-prompt config for each agent
│   ├── Dockerfile           # agnohq/python:3.12, two-layer caching, uv sync --locked
│   ├── Dockerfile.dockerignore  # Build context exclusions (BuildKit convention)
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── knowledge_agent.py   # Agentic RAG agent (hybrid search over pgvector)
│   │   └── mcp_agent.py         # MCP tool-use agent (external services via MCP)
│   └── db/                  # Database layer
│       ├── __init__.py      # Re-exports: get_postgres_db, create_knowledge, db_url
│       ├── session.py       # PostgresDb factory + Knowledge factory (pgvector hybrid)
│       └── url.py           # Builds DB URL from env vars (DB_HOST, DB_PORT, etc.)
├── frontend/                # Next.js frontend (Apollos UI)
│   ├── Dockerfile           # Multi-stage standalone build (node:24-alpine)
│   ├── .dockerignore        # Excludes node_modules, .next, secrets
│   ├── package.json         # apollos-ui — deps, scripts, engines
│   ├── pnpm-lock.yaml       # pnpm lockfile (committed to git)
│   ├── next.config.ts       # output: 'standalone', devIndicators: false
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind CSS config
│   ├── postcss.config.mjs   # PostCSS config
│   ├── src/                 # App source code
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components (shadcn/ui based)
│   │   ├── api/             # API client (browser-side fetch to backend)
│   │   ├── store.ts         # Zustand state (endpoint, auth token)
│   │   └── lib/             # Utilities
│   ├── public/              # Static assets
│   ├── README.md            # Frontend-specific docs
│   └── CONTRIBUTING.md      # Frontend contribution guide
├── mise-tasks/              # File-based mise tasks
│   ├── setup                # Install all deps (backend + frontend)
│   ├── format               # ruff format + import sorting
│   ├── lint                 # ruff check
│   ├── typecheck            # mypy type-check
│   ├── validate             # All checks (backend + frontend)
│   ├── dev                  # docker compose watch (hot-reload)
│   ├── db                   # Start database only
│   ├── load-docs            # Load knowledge base documents
│   ├── ci                   # Full CI pipeline (install + validate)
│   ├── clean                # Clean build artifacts
│   ├── release              # Create GitHub release (tag + publish, triggers Docker builds)
│   ├── docker/              # Docker-specific tasks
│   │   ├── up               # Start full stack (--prod for GHCR images)
│   │   ├── down             # Stop all services (--prod for production)
│   │   ├── logs             # Tail logs (--prod for production)
│   │   └── build            # Build images locally (--platform amd64|arm64)
│   └── frontend/            # Frontend-specific tasks
│       ├── setup            # Install frontend deps (pnpm install)
│       ├── dev              # Start frontend dev server (port 3000)
│       ├── build            # Production build (next build)
│       ├── lint             # ESLint
│       ├── format           # Prettier format check
│       ├── typecheck        # TypeScript type-check
│       └── validate         # All frontend checks (lint + format + typecheck)
├── scripts/                 # Container-only scripts
│   └── entrypoint.sh        # Container entrypoint — DB wait, banner, exec command
├── .github/workflows/
│   ├── codeql.yml           # Security: CodeQL scanning (Python, JS/TS, Actions) on push/PR + weekly
│   ├── validate.yml         # CI: parallel backend + frontend validation on push/PR
│   └── docker-images.yml    # CD: build + push backend + frontend Docker images on release
├── .github/codeql/
│   └── codeql-config.yml    # CodeQL paths-ignore configuration
├── mise.toml                # Mise config — tools (Python, uv, Node, pnpm), env vars, settings
├── .python-version          # Pins Python 3.12 for uv and CI
├── docker-compose.yaml      # Dev: local builds, hot-reload, debug mode
├── docker-compose.prod.yaml # Prod: GHCR images, no reload, no debug
├── pyproject.toml           # Project metadata, deps, [dependency-groups], ruff/mypy config
├── uv.lock                  # Cross-platform lockfile (auto-managed by uv)
├── example.env              # Template for .env (LiteLLM, model, DB, runtime, frontend config)
└── README.md                # Setup guide, agent docs, common tasks
```

## Dependency Management

### Backend (Python)

Uses **uv native project management** (not pip-compatibility mode):

| Operation | Command |
|-----------|---------|
| Add a dependency | `uv add <package>` |
| Remove a dependency | `uv remove <package>` |
| Upgrade all deps | `uv lock --upgrade` |
| Sync environment | `mise run setup` |

**Lockfile**: `uv.lock` (cross-platform TOML, auto-managed, committed to git)
**Dev deps**: Defined in `[dependency-groups]` (PEP 735)

### Frontend (Node.js)

Uses **pnpm** for package management:

| Operation | Command |
|-----------|---------|
| Install deps | `mise run frontend:setup` |
| Add a dependency | `cd frontend && pnpm add <package>` |
| Remove a dependency | `cd frontend && pnpm remove <package>` |
| Build for production | `mise run frontend:build` |

**Lockfile**: `frontend/pnpm-lock.yaml` (committed to git)
**Dev deps**: Defined in `devDependencies` in `frontend/package.json`

## Entry Points

| Entry Point | Path | Command | Description |
|-------------|------|---------|-------------|
| API Server | `backend/main.py` | `mise run docker:up` | Starts Apollos AI FastAPI server on :8000 |
| Frontend UI | `frontend/` | `mise run frontend:dev` | Starts Next.js dev server on :3000 |
| Knowledge Loader | `backend/agents/knowledge_agent.py` | `mise run load-docs` | Loads default docs into vector DB |
| Full Stack | `docker-compose.yaml` | `mise run docker:up` | All 3 services (DB + backend + frontend) |
| Watch Mode | `docker-compose.yaml` | `mise run dev` | Auto-sync code + rebuild on dep changes |

## Core Modules

### backend/agents/knowledge_agent.py
- **Exports**: `knowledge_agent` (Agent instance)
- **Purpose**: RAG agent using pgvector hybrid search over ingested documents
- **Model**: `LiteLLMOpenAI` via LiteLLM Proxy (configurable via `MODEL_ID` env var)
- **Features**: Agentic memory, history context, knowledge search, markdown output
- **Knowledge source**: Loads from `docs.agno.com` (introduction + first-agent)

### backend/agents/mcp_agent.py
- **Exports**: `mcp_agent` (Agent instance)
- **Purpose**: Tool-use agent connecting to external services via MCP protocol
- **Model**: `LiteLLMOpenAI` via LiteLLM Proxy (configurable via `MODEL_ID` env var)
- **MCP endpoint**: `https://docs.agno.com/mcp`
- **Features**: Agentic memory, history context, markdown output

### backend/main.py
- **Exports**: `agent_os` (AgentOS), `app` (FastAPI app)
- **Purpose**: Creates and configures Apollos AI with both agents, tracing, scheduler
- **Config**: Reads `backend/config.yaml` for UI quick-prompts
- **Dev mode**: Auto-reload when `RUNTIME_ENV=dev`

### backend/db/session.py
- **Exports**: `get_postgres_db()`, `create_knowledge()`
- **Purpose**: Factory functions for PostgresDb and Knowledge (pgvector hybrid search)
- **Embedder**: `OpenAIEmbedder` routed through LiteLLM Proxy (configurable via env vars)
- **Search type**: Hybrid (vector + keyword)

### backend/db/url.py
- **Exports**: `db_url` (connection string)
- **Purpose**: Builds `postgresql+psycopg://` URL from env vars with URL-encoded password

### frontend/src/store.ts
- **Exports**: Zustand store (endpoint, auth token, agent selection)
- **Purpose**: Client-side state management for API connection settings
- **Default endpoint**: `http://localhost:8000`

### frontend/src/api/
- **Purpose**: Browser-side API client for AgentOS
- **Pattern**: All API calls use dynamic `agentOSUrl` from Zustand store, no hardcoded URLs
- **Auth**: Bearer token from store, included in all requests

## Configuration

| File | Purpose |
|------|---------|
| `mise.toml` | Mise config: tools (Python 3.12, uv, Node 24, pnpm), env vars, settings |
| `mise-tasks/` | File-based mise tasks (22 dev workflow commands) |
| `pyproject.toml` | Backend metadata, dependencies, [dependency-groups], ruff/mypy config |
| `uv.lock` | Backend lockfile (auto-managed, committed to git) |
| `frontend/package.json` | Frontend metadata, dependencies, scripts |
| `frontend/pnpm-lock.yaml` | Frontend lockfile (committed to git) |
| `.python-version` | Pins Python 3.12 for uv, pyenv, and CI |
| `docker-compose.yaml` | Dev: 3 services + watch mode (local builds, hot-reload, debug) |
| `docker-compose.prod.yaml` | Prod: 3 services (GHCR images, no reload, no debug) |
| `backend/config.yaml` | Agent quick-prompts for the Agno web UI |
| `example.env` | Template: LiteLLM, model, DB, runtime, Docker, frontend config |
| `backend/Dockerfile` | Backend: two-layer cached build, `uv sync --locked` |
| `frontend/Dockerfile` | Frontend: multi-stage standalone build, node:24-alpine |

## CI/CD

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `codeql.yml` | Push to main, PR, weekly Mon 6am UTC | CodeQL security scanning: Python, JavaScript/TypeScript, Actions (security-extended suite) |
| `validate.yml` | Push to main, PR | Parallel jobs: backend (format, lint, typecheck via mise) + frontend (validate via mise) |
| `docker-images.yml` | Release published | Parallel jobs: build + push apollos-backend and apollos-frontend images to GHCR |

## Key Dependencies

### Backend

| Package | Purpose |
|---------|---------|
| `agno` | Core agent framework (Agent, AgentOS, Knowledge, tools) |
| `fastapi[standard]` | HTTP API framework with uvicorn |
| `openai` | OpenAI API client (used by embedder via LiteLLM Proxy) |
| `pgvector` | Vector similarity search extension for PostgreSQL |
| `psycopg[binary]` | PostgreSQL adapter (async-capable) |
| `sqlalchemy` | ORM / database toolkit |
| `mcp` | Model Context Protocol client |
| `opentelemetry-api/sdk` | Distributed tracing |
| `openinference-instrumentation-agno` | Agno-specific OTel instrumentation |
| `litellm[proxy]` | Multi-provider LLM proxy / routing |

**Dev deps** (`[dependency-groups]`): `mypy`, `ruff`

### Frontend

| Package | Purpose |
|---------|---------|
| `next` (15.5.10) | React framework (App Router) |
| `react` / `react-dom` (18) | UI library |
| `tailwindcss` | Utility-first CSS |
| `zustand` | State management |
| `framer-motion` | Animations |
| `@radix-ui/*` | Accessible UI primitives (shadcn/ui base) |
| `react-markdown` | Markdown rendering |
| `nuqs` | URL query state sync |

**Dev deps**: `typescript`, `eslint`, `prettier`, `@types/node`, `@types/react`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_API_KEY` | Yes | — | LiteLLM Proxy API key |
| `LITELLM_BASE_URL` | No | `http://localhost:4000/v1` | LiteLLM Proxy URL |
| `MODEL_ID` | No | `gpt-5-mini` | LLM model ID |
| `EMBEDDING_MODEL_ID` | No | `text-embedding-3-small` | Embedding model ID |
| `EMBEDDING_DIMENSIONS` | No | `1536` | Embedding vector dimensions |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | `ai` | PostgreSQL user |
| `DB_PASS` | No | `ai` | PostgreSQL password |
| `DB_DATABASE` | No | `ai` | PostgreSQL database name |
| `DB_DRIVER` | No | `postgresql+psycopg` | SQLAlchemy DB driver |
| `RUNTIME_ENV` | No | `dev` | Set to `dev` for auto-reload |
| `IMAGE_TAG` | No | `latest` | Docker image tag for backend and frontend |
| `GHCR_OWNER` | No | `jrmatherly` | GHCR image owner (used by docker-compose.prod.yaml) |
| `NEXT_PUBLIC_DEFAULT_ENDPOINT` | No | `http://localhost:8000` | Default AgentOS endpoint shown in the UI |
| `NEXT_PUBLIC_OS_SECURITY_KEY` | No | — | Pre-fill auth token in the frontend UI |
| `WAIT_FOR_DB` | No | — | Container waits for DB readiness |
| `PRINT_ENV_ON_LOAD` | No | — | Print env vars on container start |

## Quick Start

```sh
# 1. Clone and configure
cp example.env .env  # Add your LITELLM_API_KEY and LITELLM_BASE_URL

# 2. Install tools and dependencies
mise install && mise run setup

# 3. Start the stack
mise run docker:up

# 4. Load knowledge base documents
mise run load-docs

# 5. Open the frontend UI
open http://localhost:3000

# 6. Open API docs
open http://localhost:8000/docs
```

## Test Coverage

- **Unit tests**: 0 files (no test directory present)
- **Integration tests**: 0 files
- **CI validation**: Format, lint, type-check only (no test runner in CI)

## Architecture Notes

- **Framework**: Apollos AI (built on Agno AgentOS). Orchestrates multiple agents behind a single FastAPI app.
- **Storage**: pgvector (PostgreSQL 18 with vector extension) for both agent state and RAG embeddings.
- **Agent pattern**: Each agent is a standalone module exporting an `Agent` instance, registered in `backend/main.py`.
- **LLM Provider**: LiteLLM Proxy (all LLM and embedding traffic routes through self-hosted proxy).
- **Frontend**: Next.js 15 with standalone output. Connects to backend via browser-side fetch (not server-side). Default endpoint configurable via `NEXT_PUBLIC_DEFAULT_ENDPOINT` env var (defaults to `http://localhost:8000`).
- **Deployment**: Two compose files: `docker-compose.yaml` (dev, local builds) and `docker-compose.prod.yaml` (prod, GHCR images). Multi-arch images for production.
- **Tooling**: `mise` (task runner + tool manager), `uv` (backend package management), `pnpm` (frontend package management), `ruff` for formatting/linting, `mypy` for type-checking.
