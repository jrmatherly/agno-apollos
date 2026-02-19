# Project Index: Apollos AI

Generated: 2026-02-19

## Project Structure

```
apollos-ai/
├── backend/                 # All Python backend code
│   ├── __init__.py
│   ├── main.py              # Entry point — creates Apollos AI, registers agents
│   ├── config.yaml          # UI quick-prompt config for each agent
│   ├── Dockerfile           # agnohq/python:3.12, two-layer caching, uv sync --locked
│   ├── Dockerfile.dockerignore  # Build context exclusions (BuildKit convention)
│   ├── models.py              # Shared model factory (get_model())
│   ├── telemetry.py           # OpenTelemetry trace export (opt-in via env var)
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── knowledge_agent.py   # Agentic RAG agent (hybrid search, learning, user profiles)
│   │   ├── mcp_agent.py         # MCP tool-use agent (external services via MCP)
│   │   ├── web_search_agent.py  # Web research agent (DuckDuckGo)
│   │   ├── reasoning_agent.py   # Chain-of-thought reasoning agent
│   │   └── data_agent.py        # Data analyst agent (read-only PostgreSQL)
│   ├── teams/               # Multi-agent team definitions
│   │   ├── __init__.py
│   │   └── research_team.py     # Coordinate-mode research team
│   ├── workflows/           # Workflow definitions
│   │   ├── __init__.py
│   │   └── research_workflow.py # Quality-gated research pipeline (Loop + Condition)
│   ├── tools/               # Custom tool factory
│   │   ├── __init__.py
│   │   ├── search.py            # Content search tool
│   │   ├── awareness.py         # Knowledge source listing tool
│   │   ├── approved_ops.py      # Approval-gated tools (@tool + @approval)
│   │   ├── introspect.py        # Runtime schema introspection (SQLAlchemy inspect)
│   │   └── save_query.py        # Save validated SQL queries to knowledge base
│   ├── context/             # Context modules for agents
│   │   ├── __init__.py
│   │   ├── semantic_model.py    # 11-table semantic model (Agno + F1) for data agent
│   │   ├── business_rules.py    # Business rules, metrics, gotchas from JSON
│   │   └── intent_routing.py    # Intent routing guide for knowledge agent
│   ├── knowledge/           # Document loaders
│   │   ├── __init__.py
│   │   └── loaders.py           # PDF/CSV loaders from data/docs/
│   ├── evals/               # LLM-based evaluation harness
│   │   ├── __init__.py
│   │   ├── grader.py            # LLM grader (GradeResult) + golden SQL result comparison
│   │   ├── test_cases.py        # TestCase dataclass with golden SQL, 15 F1 + agent cases
│   │   └── run_evals.py         # Rich CLI runner (string match, LLM grade, SQL compare, API/direct)
│   ├── scripts/             # Data loading scripts
│   │   ├── __init__.py
│   │   ├── load_sample_data.py  # Download and load F1 data (1950-2020) into PostgreSQL
│   │   └── load_knowledge.py    # Load table/query/business knowledge into vector DB
│   └── db/                  # Database layer
│       ├── __init__.py      # Re-exports: get_postgres_db, create_knowledge, db_url
│       ├── session.py       # PostgresDb factory + Knowledge factory (pgvector hybrid)
│       └── url.py           # Builds DB URL from env vars (DB_HOST, DB_PORT, etc.)
├── frontend/                # Next.js frontend (Apollos UI)
│   ├── Dockerfile           # Multi-stage standalone build (node:24-alpine)
│   ├── .dockerignore        # Excludes node_modules, .next, secrets
│   ├── package.json         # apollos-ui v1.0.7 — deps, scripts, engines
│   ├── pnpm-lock.yaml       # pnpm lockfile (committed to git)
│   ├── next.config.ts       # output: 'standalone', devIndicators: false
│   ├── components.json      # shadcn/ui component registry config
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind CSS config
│   ├── postcss.config.mjs   # PostCSS config
│   ├── src/                 # App source code
│   │   ├── app/             # Next.js App Router pages (layout.tsx, page.tsx)
│   │   ├── components/      # React components
│   │   │   ├── chat/        # Chat UI (ChatArea, Sidebar, Messages, Multimedia)
│   │   │   └── ui/          # shadcn/ui primitives (button, dialog, select, etc.)
│   │   ├── api/             # API client (browser-side fetch to backend)
│   │   │   ├── os.ts        # AgentOS API functions (agents, teams, sessions, runs)
│   │   │   └── routes.ts    # Route constants
│   │   ├── hooks/           # React hooks
│   │   │   ├── useAIResponseStream.tsx  # SSE stream handler
│   │   │   ├── useAIStreamHandler.tsx   # Stream event processing
│   │   │   ├── useChatActions.ts        # Chat actions (send, clear, endpoint)
│   │   │   └── useSessionLoader.tsx     # Session history loader
│   │   ├── types/           # TypeScript type definitions
│   │   │   └── os.ts        # AgentOS types (RunEvent, ChatMessage, Agent, Team)
│   │   ├── store.ts         # Zustand state (endpoint, auth token, agents, teams)
│   │   └── lib/             # Utilities (audio, endpoint URL, model provider)
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
│   ├── test                 # Run integration tests (pytest)
│   ├── auth/                # Auth tasks
│   │   └── generate-token   # Generate dev JWT tokens for RBAC testing
│   ├── load-sample-data     # Load F1 sample data into PostgreSQL
│   ├── load-knowledge       # Load knowledge files into vector DB
│   ├── evals/               # Evaluation tasks
│   │   └── run              # Run eval suite (Rich CLI, LLM grading, golden SQL)
│   ├── schedules/           # Scheduler tasks
│   │   └── setup            # Initialize scheduler tables
│   ├── docker/              # Docker-specific tasks
│   │   ├── up               # Start full stack (--prod for GHCR images)
│   │   ├── down             # Stop all services (--prod for production)
│   │   ├── logs             # Tail logs (--prod for production)
│   │   └── build            # Build all images locally (--platform amd64|arm64)
│   ├── frontend/            # Frontend-specific tasks
│   │   ├── setup            # Install frontend deps (pnpm install)
│   │   ├── dev              # Start frontend dev server (port 3000)
│   │   ├── build            # Production build (next build)
│   │   ├── lint             # ESLint
│   │   ├── format           # Prettier format check
│   │   ├── typecheck        # TypeScript type-check
│   │   └── validate         # All frontend checks (lint + format + typecheck)
│   └── docs/                # Documentation tasks
│       ├── dev              # Preview docs site locally (port 3333)
│       ├── validate         # Validate docs build + check broken links
│       └── docker           # Start docs in Docker (--prod for GHCR image)
├── scripts/                 # Container-only scripts
│   └── entrypoint.sh        # Container entrypoint — DB wait, banner, exec command
├── .vscode/                 # VS Code settings
│   ├── settings.json        # Format-on-save, ruff for Python, prettier for TS
│   └── extensions.json      # Recommended extensions for contributors
├── .github/workflows/
│   ├── codeql.yml           # Security: CodeQL scanning (Python, JS/TS, Actions) on push/PR + weekly
│   ├── validate.yml         # CI: parallel backend + frontend validation on push/PR
│   ├── docker-images.yml    # CD: build + push backend + frontend Docker images on release
│   └── docs-image.yml       # CD: build + push docs Docker image on docs/** push to main
├── .github/codeql/
│   └── codeql-config.yml    # CodeQL paths-ignore configuration
├── mise.toml                # Mise config — tools (Python, uv, Node, pnpm), env vars, settings
├── .python-version          # Pins Python 3.12 for uv and CI
├── docker-compose.yaml      # Dev: local builds, hot-reload, debug mode
├── docker-compose.prod.yaml # Prod: GHCR images, no reload, no debug
├── pyproject.toml           # Project metadata, deps, [dependency-groups], ruff/mypy config
├── uv.lock                  # Cross-platform lockfile (auto-managed by uv)
├── docs/                    # Mintlify documentation site
│   ├── docs.json            # Site config (navigation, theme, branding)
│   ├── Dockerfile           # Docs container (node:24-alpine, mint dev)
│   ├── .dockerignore        # Docs build context exclusions
│   ├── index.mdx            # Introduction page
│   ├── quickstart.mdx       # Getting started guide
│   ├── development.mdx      # Development workflow
│   ├── contributing.mdx     # Contributing guide
│   ├── agents/              # Agent documentation (overview + per-agent pages + creating guide)
│   ├── teams/               # Team documentation (overview)
│   ├── workflows/           # Workflow documentation (overview)
│   ├── configuration/       # Environment, security, telemetry, Docker config
│   ├── reference/           # Architecture and mise-tasks reference
│   ├── logo/                # Apollos AI logo assets
│   ├── images/              # Documentation images
│   └── CLAUDE.md            # Docs style guide (excluded from build via .mintignore)
├── data/                    # Data storage
│   ├── docs/                # Document files for knowledge agent (PDF, CSV)
│   │   └── .gitkeep
│   ├── tables/              # F1 table metadata JSON (5 files: drivers, constructors, etc.)
│   ├── queries/             # Common SQL query patterns (common_queries.sql)
│   └── business/            # Business rules and metrics (agno_tables.json)
├── tests/                   # Integration tests
│   ├── conftest.py          # Test fixtures (backend health wait)
│   ├── test_health.py       # Health and agent list tests
│   ├── test_agents.py       # Agent run request tests
│   ├── test_teams.py        # Team list and run tests
│   └── test_schedules.py    # Scheduler endpoint tests
├── example.env              # Template for .env (LiteLLM, model, DB, auth, telemetry, frontend config)
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
| Full Stack | `docker-compose.yaml` | `mise run docker:up` | Core services (DB + backend + frontend) |
| Docs Site | `docs/Dockerfile` | `mise run docs:docker` | Documentation on :3333 |
| Watch Mode | `docker-compose.yaml` | `mise run dev` | Auto-sync code + rebuild on dep changes |

## Core Modules

### backend/models.py
- **Exports**: `get_model()` factory function
- **Purpose**: Shared model factory — all agents use this instead of inline `LiteLLMOpenAI`
- **Config**: `MODEL_ID`, `LITELLM_BASE_URL`, `LITELLM_API_KEY` env vars

### backend/agents/knowledge_agent.py
- **Exports**: `knowledge_agent` (Agent instance), `load_default_documents()` function
- **Purpose**: RAG agent using pgvector hybrid search over ingested documents
- **Features**: Agentic memory, intent routing, confidence signaling, learning system (LearningMachine), user profiles (UserProfileConfig, UserMemoryConfig), guardrails, session summaries, custom tools (search_content, list_knowledge_sources, add_knowledge_source)
- **Knowledge source**: Loads from `docs.agno.com` + PDF/CSV files from `data/docs/`

### backend/agents/mcp_agent.py
- **Exports**: `mcp_agent` (Agent instance)
- **Purpose**: Tool-use agent connecting to external services via MCP protocol
- **MCP endpoint**: `https://docs.agno.com/mcp`
- **Features**: Agentic memory, guardrails, session summaries

### backend/agents/web_search_agent.py
- **Exports**: `web_search_agent` (Agent instance)
- **Purpose**: Web research agent using DuckDuckGo search + news
- **Features**: Agentic memory, guardrails, session summaries, source citations

### backend/agents/reasoning_agent.py
- **Exports**: `reasoning_agent` (Agent instance)
- **Purpose**: Chain-of-thought reasoning with configurable step depth (2-6 steps)
- **Features**: Agentic memory, guardrails, session summaries, `reasoning=True`

### backend/agents/data_agent.py
- **Exports**: `data_agent` (Agent instance), `data_knowledge` (Knowledge), `data_learnings` (Knowledge)
- **Purpose**: Self-learning data analyst with dual knowledge system (Dash pattern)
- **Features**: Agentic memory, guardrails, session summaries, dual knowledge (curated + learnings), business rules context, insight-focused instructions
- **Tools**: PostgresTools (show_tables, describe_table, summarize_table, inspect_query), `introspect_schema`, `save_validated_query`

### backend/context/semantic_model.py
- **Exports**: `SEMANTIC_MODEL` (dict), `SEMANTIC_MODEL_STR` (formatted markdown)
- **Purpose**: 11-table database schema context injected into data agent instructions (Dash pattern)
- **Tables**: 6 Agno tables (`agno_agent_sessions`, `agno_agent_runs`, `agno_memories`, `agno_team_sessions`, `agno_workflow_sessions`, `agno_approvals`) + 5 F1 tables (`drivers_championship`, `constructors_championship`, `race_wins`, `race_results`, `fastest_laps`)

### backend/teams/research_team.py
- **Exports**: `research_team` (Team instance)
- **Purpose**: Multi-agent research team (coordinate mode) with web_researcher + analyst members
- **Features**: Shared history, agentic memory, ReasoningTools, safety parameters (max_iterations=5, num_history_runs=5, add_datetime_to_context)

### backend/workflows/research_workflow.py
- **Exports**: `research_workflow` (Workflow instance)
- **Purpose**: Quality-gated research pipeline with iterative refinement and conditional analysis
- **Steps**: Initial Research (web_search_agent) → Quality Refinement Loop (quality_reviewer + gap filling, max 3 iterations) → Complexity-based Condition (deep analysis vs basic synthesis via reasoning_agent)
- **Primitives**: Uses Agno `Loop` (with `end_condition` callback) and `Condition` (with `evaluator` function)

### backend/main.py
- **Exports**: `agent_os` (AgentOS), `app` (FastAPI app)
- **Purpose**: Creates and configures Apollos AI with all agents, teams, workflows, tracing, scheduler
- **Config**: Reads `backend/config.yaml` for UI quick-prompts
- **Features**: JWT RBAC auth (opt-in), MCP server endpoint, telemetry export
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
| `mise-tasks/` | File-based mise tasks (25 dev workflow commands) |
| `pyproject.toml` | Backend metadata, dependencies, [dependency-groups], ruff/mypy config |
| `uv.lock` | Backend lockfile (auto-managed, committed to git) |
| `frontend/package.json` | Frontend metadata, dependencies, scripts |
| `frontend/pnpm-lock.yaml` | Frontend lockfile (committed to git) |
| `.python-version` | Pins Python 3.12 for uv, pyenv, and CI |
| `docker-compose.yaml` | Dev: 3 core services + optional docs (local builds, hot-reload, debug) |
| `docker-compose.prod.yaml` | Prod: 3 core services + optional docs (GHCR images, no reload, no debug) |
| `backend/config.yaml` | Agent quick-prompts for the Agno web UI |
| `example.env` | Template: LiteLLM, model, DB, runtime, Docker, frontend config |
| `backend/Dockerfile` | Backend: two-layer cached build, `uv sync --locked` |
| `frontend/Dockerfile` | Frontend: multi-stage standalone build, node:24-alpine |
| `docs/Dockerfile` | Docs: node:24-alpine, Mintlify CLI (`mint dev`) |

## CI/CD

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `codeql.yml` | Push to main, PR, weekly Mon 6am UTC | CodeQL security scanning: Python, JavaScript/TypeScript, Actions (security-extended suite) |
| `validate.yml` | Push to main, PR | Parallel jobs: backend (format, lint, typecheck via mise) + frontend (validate via mise) |
| `docker-images.yml` | Release published | Parallel jobs: build + push apollos-backend and apollos-frontend images to GHCR |
| `docs-image.yml` | Push to main (docs/**) | Build + push apollos-docs image to GHCR |

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
| `opentelemetry-exporter-otlp-proto-http` | OTLP HTTP trace exporter |
| `openinference-instrumentation-agno` | Agno-specific OTel instrumentation |
| `litellm` | Multi-provider LLM routing (external proxy, no [proxy] extra) |
| `ddgs` | Web search backend for web_search_agent |
| `fastmcp` | MCP server for AgentOS |
| `pypdf` | PDF document reader for knowledge loaders |
| `aiofiles` | Async file I/O for document loading |
| `pandas` | DataFrame loading for F1 sample data scripts |
| `rich` | Rich CLI output for eval runner |

**Dev deps** (`[dependency-groups]`): `mypy`, `pandas-stubs`, `ruff`, `pytest`, `requests`

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
| `JWT_SECRET_KEY` | No | — | Enable JWT RBAC auth (empty = auth disabled) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | — | OTel trace export endpoint (empty = traces not exported) |
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

- **Integration tests**: `tests/` — 5 files (health, agents, teams, schedules). Run via `mise run test` (requires running backend).
- **Eval harness**: `backend/evals/` — LLM-based grading of agent responses. Run via `mise run evals:run`.
- **CI validation**: Format, lint, type-check (backend + frontend). No test runner in CI yet (tests require live backend).

## Architecture Notes

- **Framework**: Apollos AI (built on Agno AgentOS). Orchestrates agents, teams, and workflows behind a single FastAPI app.
- **Storage**: pgvector (PostgreSQL 18 with vector extension) for agent state, RAG embeddings, learnings, and user profiles.
- **Agent pattern**: Each agent is a standalone module exporting an `Agent` instance, registered in `backend/main.py`. All agents use `get_model()` from `backend/models.py`, guardrails (PII + prompt injection), agentic memory, and session summaries.
- **Teams**: Multi-agent teams in `backend/teams/`, using Agno's `Team` class with coordinate mode.
- **Workflows**: Multi-step pipelines in `backend/workflows/`, using Agno's `Workflow`, `Step`, `Loop`, and `Condition` classes for iterative refinement and conditional routing.
- **Security**: JWT RBAC auth (opt-in via `JWT_SECRET_KEY`), human-in-the-loop approval workflows (`@approval` decorator on tools).
- **Observability**: OpenTelemetry trace export (opt-in via `OTEL_EXPORTER_OTLP_ENDPOINT`), Agno native tracing, MCP server endpoint.
- **Learning**: Agents use `LearningMachine` for agentic learning. Knowledge agent has user profiles and memory.
- **LLM Provider**: LiteLLM Proxy (all LLM and embedding traffic routes through self-hosted proxy).
- **Frontend**: Next.js 15 with standalone output. Connects to backend via browser-side fetch (not server-side). Default endpoint configurable via `NEXT_PUBLIC_DEFAULT_ENDPOINT` env var (defaults to `http://localhost:8000`).
- **Deployment**: Two compose files: `docker-compose.yaml` (dev, local builds) and `docker-compose.prod.yaml` (prod, GHCR images). Multi-arch images for production.
- **Tooling**: `mise` (task runner + tool manager), `uv` (backend package management), `pnpm` (frontend package management), `ruff` for formatting/linting, `mypy` for type-checking.
