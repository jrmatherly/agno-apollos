# Apollos AI - Project Overview

## Purpose
Multi-agent system using the Agno framework. Provides a FastAPI-based AgentOS with PostgreSQL/pgvector backend.

## Architecture
- **Framework**: Agno (agno.os.AgentOS)
- **API**: FastAPI via `app/main.py` → `agent_os.get_app()`
- **Database**: PostgreSQL + pgvector (hybrid vector search)
- **Containerization**: Docker Compose (api + db services)
- **Model**: OpenAI GPT-5.2 via `agno.models.openai.OpenAIResponses`

## Key Files
- `app/main.py` - Apollos AI entry point, registers agents
- `app/config.yaml` - Chat quick prompts config
- `agents/knowledge_agent.py` - Agentic RAG agent with knowledge base
- `agents/mcp_agent.py` - MCP tool-use agent
- `db/session.py` - PostgresDb and Knowledge factory functions
- `db/url.py` - Database URL builder from env vars
- `compose.yaml` - Docker Compose (apollos-db, apollos-api)
- `Dockerfile` - Based on agnohq/python:3.12, uses uv

## Agents
1. **Knowledge Agent** (`knowledge-agent`): RAG with pgvector hybrid search, loads docs from agno.com
2. **MCP Agent** (`mcp-agent`): Connects to external tools via MCP protocol

## Dependencies (pyproject.toml)
agno, fastapi[standard], openai, pgvector, psycopg[binary], sqlalchemy, mcp, opentelemetry-*, litellm[proxy]

## Dev Tools
- ruff (line-length=120)
- mypy (with pydantic plugin)
- uv package manager (native project management with uv.lock)

## Adding an Agent
1. Create `agents/my_agent.py` with Agent definition
2. Import and register in `app/main.py` agents list
3. Restart containers

## Environment Variables
- `OPENAI_API_KEY` (required)
- `DB_HOST/PORT/USER/PASS/DATABASE` (defaults: localhost:5432, ai/ai/ai)
- `RUNTIME_ENV` (dev enables auto-reload)
