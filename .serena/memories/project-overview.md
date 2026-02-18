# Apollos AI - Project Overview

## Purpose
Multi-agent system using the Agno framework. Provides a FastAPI-based AgentOS with PostgreSQL/pgvector backend.

## Architecture
- **Framework**: Agno (agno.os.AgentOS)
- **API**: FastAPI via `backend/main.py` → `agent_os.get_app()`
- **Database**: PostgreSQL + pgvector (hybrid vector search)
- **Containerization**: Docker Compose (api + db services)
- **Model**: LiteLLM Proxy via `agno.models.litellm.LiteLLMOpenAI`

## Key Files
- `backend/main.py` - Apollos AI entry point, registers agents
- `backend/config.yaml` - Chat quick prompts config
- `backend/agents/knowledge_agent.py` - Agentic RAG agent with knowledge base
- `backend/agents/mcp_agent.py` - MCP tool-use agent
- `backend/db/session.py` - PostgresDb and Knowledge factory functions
- `backend/db/url.py` - Database URL builder from env vars
- `docker-compose.yaml` - Docker Compose (apollos-db, apollos-backend)
- `Dockerfile` - Based on agnohq/python:3.12, uses uv

## Agents
1. **Knowledge Agent** (`knowledge-agent`): RAG with pgvector hybrid search, loads docs from agno.com
2. **MCP Agent** (`mcp-agent`): Connects to external tools via MCP protocol

## Dependencies (pyproject.toml)
agno, fastapi[standard], openai, pgvector, psycopg[binary], sqlalchemy, mcp, opentelemetry-*, litellm[proxy]

## Dev Tools
- mise (task runner + tool manager, see `mise.toml` and `mise-tasks/`)
- ruff (line-length=120)
- mypy (with pydantic plugin)
- uv package manager (native project management with uv.lock)

## Mise Tasks
Run `mise tasks` for full list. Key tasks:
- `mise run setup` - install deps
- `mise run format` / `lint` / `typecheck` / `validate` - code quality
- `mise run dev` - docker compose watch
- `mise run docker:up` / `docker:down` / `docker:logs` / `docker:build`
- `mise run db` - database only
- `mise run load-docs` - load knowledge base
- `mise run ci` / `clean`

## Adding an Agent
1. Create `backend/agents/my_agent.py` with Agent definition
2. Import and register in `backend/main.py` agents list
3. Restart containers

## Environment Variables
- `LITELLM_API_KEY` (required)
- `LITELLM_BASE_URL` (default: http://localhost:4000/v1)
- `MODEL_ID` (default: gpt-5-mini)
- `EMBEDDING_MODEL_ID` (default: text-embedding-3-small)
- `EMBEDDING_DIMENSIONS` (default: 1536)
- `DB_HOST/PORT/USER/PASS/DATABASE` (defaults: localhost:5432, ai/ai/ai)
- `RUNTIME_ENV` (dev enables auto-reload)
