# Project Index: Apollos AI

Generated: 2026-02-18

## Project Structure

```
apollos-ai/
├── agents/                  # AI agent implementations
│   ├── __init__.py
│   ├── knowledge_agent.py   # Agentic RAG agent (hybrid search over pgvector)
│   └── mcp_agent.py         # MCP tool-use agent (external services via MCP)
├── app/                     # FastAPI application
│   ├── __init__.py
│   ├── config.yaml          # UI quick-prompt config for each agent
│   └── main.py              # Entry point — creates Apollos AI, registers agents
├── db/                      # Database layer
│   ├── __init__.py          # Re-exports: get_postgres_db, create_knowledge, db_url
│   ├── session.py           # PostgresDb factory + Knowledge factory (pgvector hybrid)
│   └── url.py               # Builds DB URL from env vars (DB_HOST, DB_PORT, etc.)
├── scripts/                 # Developer toolchain
│   ├── build_image.sh       # Multi-arch Docker build (amd64 + arm64) with Buildx
│   ├── entrypoint.sh        # Container entrypoint — DB wait, banner, exec command
│   ├── format.sh            # ruff format + import sorting
│   ├── validate.sh          # ruff check + mypy type-check
│   └── venv_setup.sh        # uv sync --dev (creates .venv, installs everything)
├── .github/workflows/
│   ├── validate.yml         # CI: format, lint, type-check on push/PR
│   └── docker-images.yml    # CD: build + push Docker image on release
├── .python-version          # Pins Python 3.12 for uv and CI
├── Dockerfile               # agnohq/python:3.12, two-layer caching, uv sync --locked
├── compose.yaml             # apollos-api (FastAPI) + apollos-db (pgvector:18) + watch mode
├── pyproject.toml           # Project metadata, deps, [dependency-groups], ruff/mypy config
├── uv.lock                  # Cross-platform lockfile (auto-managed by uv)
├── example.env              # Template for .env (OPENAI_API_KEY, DB creds)
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
| API Server | `app/main.py` | `uv run python -m app.main` | Starts Apollos AI FastAPI server on :8000 |
| Knowledge Loader | `agents/knowledge_agent.py` | `uv run python -m agents.knowledge_agent` | Loads default docs into vector DB |
| MCP Agent CLI | `agents/mcp_agent.py` | `uv run python -m agents.mcp_agent` | Runs MCP agent interactively |
| Docker Compose | `compose.yaml` | `docker compose up -d --build` | Full stack (API + pgvector DB) |
| Docker Watch | `compose.yaml` | `docker compose watch` | Auto-sync code + rebuild on dep changes |

## Core Modules

### agents/knowledge_agent.py
- **Exports**: `knowledge_agent` (Agent instance)
- **Purpose**: RAG agent using pgvector hybrid search over ingested documents
- **Model**: `OpenAIResponses("gpt-5.2")`
- **Features**: Agentic memory, history context, knowledge search, markdown output
- **Knowledge source**: Loads from `docs.agno.com` (introduction + first-agent)

### agents/mcp_agent.py
- **Exports**: `mcp_agent` (Agent instance)
- **Purpose**: Tool-use agent connecting to external services via MCP protocol
- **Model**: `OpenAIResponses("gpt-5.2")`
- **MCP endpoint**: `https://docs.agno.com/mcp`
- **Features**: Agentic memory, history context, markdown output

### app/main.py
- **Exports**: `agent_os` (AgentOS), `app` (FastAPI app)
- **Purpose**: Creates and configures Apollos AI with both agents, tracing, scheduler
- **Config**: Reads `app/config.yaml` for UI quick-prompts
- **Dev mode**: Auto-reload when `RUNTIME_ENV=dev`

### db/session.py
- **Exports**: `get_postgres_db()`, `create_knowledge()`
- **Purpose**: Factory functions for PostgresDb and Knowledge (pgvector hybrid search)
- **Embedder**: `OpenAIEmbedder("text-embedding-3-small")`
- **Search type**: Hybrid (vector + keyword)

### db/url.py
- **Exports**: `db_url` (connection string)
- **Purpose**: Builds `postgresql+psycopg://` URL from env vars with URL-encoded password

## Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, [dependency-groups], ruff/mypy config |
| `uv.lock` | Cross-platform lockfile (auto-managed, committed to git) |
| `.python-version` | Pins Python 3.12 for uv, pyenv, and CI |
| `compose.yaml` | Docker services + watch mode: `apollos-api` (:8000) + `apollos-db` (:5432) |
| `app/config.yaml` | Agent quick-prompts for the Agno web UI |
| `example.env` | Template: `OPENAI_API_KEY`, `OPENAI_API_BASE`, DB credentials |
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
| `openai` | OpenAI API client (GPT models) |
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
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `OPENAI_API_BASE` | No | `https://api.openai.com/v1` | OpenAI base URL |
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
cp example.env .env  # Add your OPENAI_API_KEY

# 2. Start the stack
docker compose up -d --build

# 3. Load knowledge base documents
docker exec -it apollos-api python -m agents.knowledge_agent

# 4. Open API docs
open http://localhost:8000/docs

# 5. Connect web UI: os.agno.com → Add OS → Local → http://localhost:8000
```

## Test Coverage

- **Unit tests**: 0 files (no test directory present)
- **Integration tests**: 0 files
- **CI validation**: Format, lint, type-check only (no test runner in CI)

## Architecture Notes

- **Framework**: Apollos AI (built on Agno AgentOS) — orchestrates multiple agents behind a single FastAPI app
- **Storage**: pgvector (PostgreSQL 18 with vector extension) for both agent state and RAG embeddings
- **Agent pattern**: Each agent is a standalone module exporting an `Agent` instance, registered in `app/main.py`
- **Deployment**: Docker Compose with watch mode for dev, multi-arch images for production
- **Tooling**: `uv` (native project management with lockfile), `ruff` for formatting/linting, `mypy` for type-checking
