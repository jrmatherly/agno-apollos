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
- `backend/main.py` - Entry point: registers agents, teams, workflows, auth, telemetry, MCP server
- `backend/models.py` - Shared model factory (`get_model()`)
- `backend/config.yaml` - Chat quick prompts config
- `backend/telemetry.py` - OpenTelemetry trace export (opt-in)
- `backend/agents/` - Agent definitions (knowledge, mcp, web_search, reasoning, data)
- `backend/teams/research_team.py` - Multi-agent research team (coordinate mode)
- `backend/workflows/research_workflow.py` - Quality-gated research pipeline (Loop + Condition)
- `backend/tools/` - Custom tools (search, awareness, approved_ops with @approval, introspect schema, save validated query)
- `backend/context/` - Context modules (11-table semantic_model, intent_routing, business_rules)
- `backend/knowledge/loaders.py` - PDF/CSV document loaders from `data/docs/`
- `backend/evals/` - LLM-based eval harness (Rich CLI, TestCase/GradeResult dataclasses, string matching + LLM grading + golden SQL comparison)
- `backend/scripts/` - Data loading scripts (load_sample_data, load_knowledge)
- `backend/db/session.py` - PostgresDb and Knowledge factory functions
- `backend/db/url.py` - Database URL builder from env vars
- `tests/` - Integration tests (health, agents, teams, schedules)
- `frontend/src/store.ts` - Zustand state (endpoint default: localhost:8000)
- `frontend/src/api/` - Browser-side API client (fetch, Bearer token auth)
- `docker-compose.yaml` - Dev compose (3 core services + optional docs behind `docs` profile)
- `docker-compose.prod.yaml` - Prod compose (GHCR images, same profile structure)

## Agents
1. **Knowledge Agent** (`knowledge-agent`): RAG with pgvector hybrid search, learning system, user profiles, intent routing, custom tools
2. **MCP Agent** (`mcp-agent`): Connects to external tools via MCP protocol
3. **Web Search Agent** (`web-search-agent`): Web research via DuckDuckGo with source citations
4. **Reasoning Agent** (`reasoning-agent`): Chain-of-thought reasoning (2-6 steps)
5. **Data Analyst** (`data-agent`): Read-only PostgreSQL queries (Dash pattern) with dual knowledge system (curated `data_knowledge` + dynamic `data_learnings`), runtime schema introspection, validated query saving, F1 dataset support, and insight-focused instructions

## Teams
1. **Research Team** (`research-team`): Coordinate-mode multi-agent research (web_researcher + analyst), safety parameters (max_iterations=5, num_history_runs=5, add_datetime_to_context)

## Workflows
1. **Research Workflow** (`research-workflow`): Quality-gated research pipeline (Search → Loop refinement → Conditional analysis)

## Dependencies (pyproject.toml)
agno, fastapi[standard], openai, pgvector, psycopg[binary], sqlalchemy, mcp, opentelemetry-*, opentelemetry-exporter-otlp-proto-http, litellm, ddgs, fastmcp, pypdf, aiofiles, pandas, httpx, rich
Dev: mypy, ruff, pytest, requests, pandas-stubs

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
- `mise run test` - integration tests (pytest, requires running backend)
- `mise run evals:run` - LLM-based evaluation suite (`-v` verbose, `-g` LLM grading, `-r` golden SQL, `--direct` no API)
- `mise run load-sample-data` - load F1 sample data into PostgreSQL
- `mise run load-knowledge` - populate vector DB with curated knowledge (`--recreate` to rebuild)
- `mise run auth:generate-token` - generate dev JWT tokens
- `mise run schedules:setup` - initialize scheduler tables
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
- `JWT_SECRET_KEY` (empty = auth disabled; set to enable JWT RBAC)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (empty = traces not exported; set for OTel)
- `NEXT_PUBLIC_DEFAULT_ENDPOINT` (default endpoint shown in frontend UI, default: http://localhost:8000)
- `NEXT_PUBLIC_OS_SECURITY_KEY` (optional: pre-fill auth token in frontend)

## Documentation
- Mintlify site in `docs/` (MDX pages, `docs.json` config)
- Preview on port 3333 (`mise run docs:dev`) to avoid frontend port conflict
- Style guide at `docs/CLAUDE.md` (excluded from Mintlify build via `.mintignore`)
- Sections: Getting started, Agents, Teams, Workflows, Configuration, Reference, Contributing

## Security & CI/CD
- CodeQL scanning on push/PR to main + weekly (Python, JS/TS, Actions)
- CI workflows use pinned action SHAs for supply-chain security
- CI workflows use mise tasks (not raw commands) for consistency
- Explicit `permissions` block on all workflows (least-privilege)
- Docker images publish to GHCR (ghcr.io/<owner>/apollos-backend, apollos-frontend, apollos-docs)
- Docs image builds on push to main (docs/** changes), backend/frontend images build on release
