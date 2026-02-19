# Apollos AI - Project Overview

## Purpose
Multi-agent system using the Agno framework. Provides a FastAPI-based AgentOS with PostgreSQL/pgvector backend and a self-hosted Next.js frontend.

## Architecture
- **Framework**: Agno (agno.os.AgentOS)
- **API**: FastAPI via `backend/main.py` → `agent_os.get_app()`
- **Frontend**: Next.js 15 (App Router), React 18, TypeScript, pnpm, Tailwind CSS, shadcn/ui
- **Database**: PostgreSQL + pgvector (hybrid vector search)
- **Containerization**: Docker Compose — two files: `docker-compose.yaml` (dev) and `docker-compose.prod.yaml` (prod, GHCR images)
- **Model**: LiteLLM Proxy via `agno.models.litellm.LiteLLMOpenAI`

## Key Files
- `backend/main.py` - Apollos AI entry point, registers agents
- `backend/config.yaml` - Chat quick prompts config
- `backend/agents/knowledge_agent.py` - Agentic RAG agent with knowledge base
- `backend/agents/mcp_agent.py` - MCP tool-use agent
- `backend/db/session.py` - PostgresDb and Knowledge factory functions
- `backend/db/url.py` - Database URL builder from env vars
- `frontend/src/store.ts` - Zustand state (endpoint default: localhost:8000)
- `frontend/src/api/` - Browser-side API client (fetch, Bearer token auth)
- `frontend/Dockerfile` - Multi-stage standalone build (node:24-alpine)
- `docs/Dockerfile` - Docs container (node:24-alpine, Mintlify CLI `mint dev` on port 3333)
- `docker-compose.yaml` - Dev compose (3 core services + optional docs behind `docs` profile)
- `docker-compose.prod.yaml` - Prod compose (GHCR images, same profile structure)
- `backend/Dockerfile` - Backend, based on agnohq/python:3.12, uses uv
- `backend/Dockerfile.dockerignore` - Backend build context exclusions (BuildKit convention)

## Agents
1. **Knowledge Agent** (`knowledge-agent`): RAG with pgvector hybrid search, loads docs from agno.com
2. **MCP Agent** (`mcp-agent`): Connects to external tools via MCP protocol

## Dependencies (pyproject.toml)
agno, fastapi[standard], openai, pgvector, psycopg[binary], sqlalchemy, mcp, opentelemetry-*, litellm[proxy]

## Frontend Dependencies (package.json)
next, react, react-dom, tailwindcss, zustand, framer-motion, @radix-ui/*, react-markdown, nuqs

## Dev Tools
- mise (task runner + tool manager, see `mise.toml` and `mise-tasks/`)
- ruff (line-length=120)
- mypy (with pydantic plugin)
- uv package manager (backend, native project management with uv.lock)
- pnpm (frontend package management)
- Node.js 24 + pnpm latest (managed by mise)

## Mise Tasks
Run `mise tasks` for full list. Key tasks:
- `mise run setup` - install all deps (`--ci` for locked/frozen mode)
- `mise run format` / `lint` / `typecheck` / `validate` - backend code quality
- `mise run dev` - docker compose watch
- `mise run docker:up` / `docker:down` / `docker:logs` (all support `--prod` flag; `docker:up` also supports `--docs`)
- `mise run docker:build` - build all images locally (`--platform amd64|arm64`)
- `mise run docs:docker` - start docs in Docker (`--prod` for GHCR image)
- `mise run db` - database only
- `mise run load-docs` - load knowledge base
- `mise run ci` / `clean`
- `mise run release` - create GitHub release (interactive version prompt)
- `mise run frontend:setup` / `frontend:dev` / `frontend:build`
- `mise run frontend:lint` / `frontend:format` / `frontend:typecheck` / `frontend:validate`
- `mise run docs:dev` - preview docs site locally (port 3333)
- `mise run docs:validate` - validate docs build + check broken links

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
- `IMAGE_TAG` (Docker image tag, default: latest)
- `GHCR_OWNER` (GHCR image owner for prod compose, default: jrmatherly)
- `NEXT_PUBLIC_OS_SECURITY_KEY` (optional: pre-fill auth token in frontend)

## Documentation
- Mintlify site in `docs/` (MDX pages, `docs.json` config)
- Preview on port 3333 (`mise run docs:dev`) to avoid frontend port conflict
- Style guide at `docs/CLAUDE.md` (excluded from Mintlify build via `.mintignore`)
- Sections: Getting started, Agents, Configuration, Reference, Contributing

## Security & CI/CD
- CodeQL scanning on push/PR to main + weekly (Python, JS/TS, Actions)
- CI workflows use pinned action SHAs for supply-chain security
- CI workflows use mise tasks (not raw commands) for consistency
- Explicit `permissions` block on all workflows (least-privilege)
- Docker images publish to GHCR (ghcr.io/<owner>/apollos-backend, apollos-frontend, apollos-docs)
- Docs image builds on push to main (docs/** changes), backend/frontend images build on release
