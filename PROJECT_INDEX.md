# Project Index: Apollos AI

Generated: 2026-02-18

## Project Structure

```
apollos-ai/
├── backend/                 # All Python backend code
│   ├── __init__.py
│   ├── main.py              # Entry point — creates Apollos AI, registers agents
│   ├── config.yaml          # UI quick-prompt config for each agent
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── knowledge_agent.py   # Agentic RAG agent (hybrid search over pgvector)
│   │   └── mcp_agent.py         # MCP tool-use agent (external services via MCP)
│   └── db/                  # Database layer
│       ├── __init__.py      # Re-exports: get_postgres_db, create_knowledge, db_url
│       ├── session.py       # PostgresDb factory + Knowledge factory (pgvector hybrid)
│       └── url.py           # Builds DB URL from env vars (DB_HOST, DB_PORT, etc.)
├── mise-tasks/              # File-based mise tasks (replaces scripts/*.sh)
│   ├── setup                # Install deps (uv sync --dev)
│   ├── format               # ruff format + import sorting
│   ├── lint                 # ruff check
│   ├── typecheck            # mypy type-check
│   ├── validate             # All checks (format-check + lint + typecheck)
│   ├── dev                  # docker compose watch (hot-reload)
│   ├── db                   # Start database only
│   ├── load-docs            # Load knowledge base documents
│   ├── ci                   # Full CI pipeline (install + validate)
│   ├── clean                # Clean build artifacts
│   └── docker/              # Docker-specific tasks
│       ├── up               # Start full stack (build + detach)
│       ├── down             # Stop all services
│       ├── logs             # Tail logs
│       └── build            # Multi-arch image build (amd64 + arm64)
├── scripts/                 # Container-only scripts
│   └── entrypoint.sh        # Container entrypoint — DB wait, banner, exec command
├── .github/workflows/
│   ├── validate.yml         # CI: format, lint, type-check on push/PR
│   └── docker-images.yml    # CD: build + push Docker image on release
├── mise.toml                # Mise config — tools (Python, uv), env vars, settings
├── .python-version          # Pins Python 3.12 for uv and CI
├── Dockerfile               # agnohq/python:3.12, two-layer caching, uv sync --locked
├── docker-compose.yaml             # apollos-api (FastAPI) + apollos-db (pgvector:18) + watch mode
├── pyproject.toml           # Project metadata, deps, [dependency-groups], ruff/mypy config
├── uv.lock                  # Cross-platform lockfile (auto-managed by uv)
├── example.env              # Template for .env (LiteLLM, model, DB credentials)
└── README.md                # Setup guide, agent docs, common tasks
```

## Dependency Management

Uses **uv native project management** (not pip-compatibility mode):

| Operation | Command |
|-----------|---------|
| Add a dependency | `uv add <package>` |
| Remove a dependency | `uv remove <package>` |
| Upgrade all deps | `uv lock --upgrade` |
| Sync environment | `uv sync --dev` |
| Run a command | `uv run <command>` |

**Lockfile**: `uv.lock` (cross-platform TOML, auto-managed, committed to git)
**Dev deps**: Defined in `[dependency-groups]` (PEP 735)

## Entry Points

| Entry Point | Path | Command | Description |
|-------------|------|---------|-------------|
| API Server | `backend/main.py` | `uv run python -m backend.main` | Starts Apollos AI FastAPI server on :8000 |
| Knowledge Loader | `backend/agents/knowledge_agent.py` | `uv run python -m backend.agents.knowledge_agent` | Loads default docs into vector DB |
| MCP Agent CLI | `backend/agents/mcp_agent.py` | `uv run python -m backend.agents.mcp_agent` | Runs MCP agent interactively |
| Docker Compose | `docker-compose.yaml` | `docker compose up -d --build` | Full stack (API + pgvector DB) |
| Docker Watch | `docker-compose.yaml` | `docker compose watch` | Auto-sync code + rebuild on dep changes |

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

## Configuration

| File | Purpose |
|------|---------|
| `mise.toml` | Mise config: tools (Python 3.12, uv), env vars, settings |
| `mise-tasks/` | File-based mise tasks (dev workflow commands) |
| `pyproject.toml` | Project metadata, dependencies, [dependency-groups], ruff/mypy config |
| `uv.lock` | Cross-platform lockfile (auto-managed, committed to git) |
| `.python-version` | Pins Python 3.12 for uv, pyenv, and CI |
| `docker-compose.yaml` | Docker services + watch mode: `apollos-api` (:8000) + `apollos-db` (:5432) |
| `backend/config.yaml` | Agent quick-prompts for the Agno web UI |
| `example.env` | Template: LiteLLM config, model config, DB credentials |
| `Dockerfile` | Two-layer cached build: deps layer + project layer, `uv sync --locked` |

## CI/CD

| Workflow | Trigger | Steps |
|----------|---------|-------|
| `validate.yml` | Push, PR to main | `uv sync --locked --dev`, format (ruff), lint (ruff), type-check (mypy) |
| `docker-images.yml` | Release published | Build multi-arch image (amd64+arm64), push to DockerHub |

## Key Dependencies

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
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |
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

# 5. Open API docs
open http://localhost:8000/docs

# 6. Connect web UI: os.agno.com → Add OS → Local → http://localhost:8000
```

## Test Coverage

- **Unit tests**: 0 files (no test directory present)
- **Integration tests**: 0 files
- **CI validation**: Format, lint, type-check only (no test runner in CI)

## Architecture Notes

- **Framework**: Apollos AI (built on Agno AgentOS) — orchestrates multiple agents behind a single FastAPI app
- **Storage**: pgvector (PostgreSQL 18 with vector extension) for both agent state and RAG embeddings
- **Agent pattern**: Each agent is a standalone module exporting an `Agent` instance, registered in `backend/main.py`
- **LLM Provider**: LiteLLM Proxy (all LLM and embedding traffic routes through self-hosted proxy)
- **Deployment**: Docker Compose with watch mode for dev, multi-arch images for production
- **Tooling**: `mise` (task runner + tool manager), `uv` (native project management with lockfile), `ruff` for formatting/linting, `mypy` for type-checking
