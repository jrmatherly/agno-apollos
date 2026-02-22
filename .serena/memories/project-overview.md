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

- `backend/main.py` - Entry point: registers agents, teams, workflows, auth, dual-layer telemetry, registry, MCP server, A2A endpoints (opt-in)
- `backend/models.py` - Shared model factory (`get_model()`)
- `backend/config.yaml` - Chat quick prompts config
- `backend/cli.py` - Shared Rich CLI module for direct agent testing
- `backend/telemetry.py` - Dual-layer observability: trace-to-DB (Agno, `TRACING_ENABLED`) + OTLP multi-export (`OTLP_ENDPOINTS`, opt-in)
- `backend/registry.py` - Component registry for Agent-as-Config persistence (`create_registry()` factory)
- `backend/a2a/executor.py` - `AgnoAgentExecutor` wraps Agno agents for A2A message handling (asyncio.to_thread for sync agent)
- `backend/a2a/server.py` - Builds AgentCards + mounts `A2AStarletteApplication` per agent
- `backend/agents/` - Agent definitions (knowledge, mcp, web_search, reasoning, data)
- `backend/teams/research_team.py` - Multi-agent research team (coordinate mode)
- `backend/workflows/research_workflow.py` - Quality-gated research pipeline (Loop + Condition)
- `backend/tools/` - Custom tools (search, awareness, approved_ops with @approval, introspect schema, save validated query, save_discovery for FAQ-building, m365 MCP tools, tool hooks)
- `backend/tools/m365.py` - MCPTools factory with contextvars header_provider for per-request Graph token
- `backend/tools/hooks.py` - Tool hooks: audit_hook (logging), m365_write_guard (StopAgentRun on write ops)
- `backend/context/` - Context modules (11-table semantic_model, intent_routing, business_rules, source_registry)
- `backend/knowledge/loaders.py` - PDF/CSV document loaders from `data/docs/`
- `backend/evals/` - LLM-based eval harness (Rich CLI, TestCase/GradeResult dataclasses, string matching + LLM grading + golden SQL comparison + source citation checking)
- `backend/scripts/` - Data loading scripts (load_sample_data, load_knowledge)
- `backend/db/session.py` - PostgresDb and Knowledge factory functions
- `backend/db/url.py` - Database URL builder from env vars
- `tests/` - Integration tests (health, agents, teams, schedules)
- `frontend/src/store.ts` - Zustand state (endpoint default: localhost:8000)
- `frontend/src/api/` - Browser-side API client (fetch, Bearer token auth)
- `backend/agents/m365_agent.py` - Read-only M365 agent (opt-in via M365_ENABLED)
- `frontend/src/app/settings/` - Settings hub + M365 connect/disconnect page
- `frontend/src/api/m365.ts` - M365 API client (status, connect, disconnect)
- `backend/mcp/config.py` - MCP_GATEWAY_ENABLED flag, lazy singleton GatewayClient, get_gateway_tools_factory()
- `backend/mcp/gateway_client.py` - GatewayClient: JWT generation (jti+exp), gateway CRUD
- `backend/mcp/tools_factory.py` - Gateway-aware header_provider + tools factory
- `backend/mcp/routes.py` - Proxy routes: /mcp/servers (list, get, register, delete)
- `backend/mcp/schemas.py` - Pydantic models (MCPServerInfo, MCPServerRegister, MCPServerResponse)
- `backend/mcp/validation.py` - BYOMCP URL validation (HTTPS-only, no private IPs, no cloud metadata)
- `frontend/src/api/mcp.ts` - MCP Gateway API client (list, register, delete servers)
- `frontend/src/app/settings/integrations/page.tsx` - MCP Integrations settings page
- `docker-compose.yaml` - Dev compose (3 core services + optional docs/m365/gateway profiles)
- `docker-compose.prod.yaml` - Prod compose (GHCR images, same profile structure)

## Agents

1. **Knowledge Agent** (`knowledge-agent`): RAG with pgvector hybrid search, file browsing (FileTools), FAQ-building (save_intent_discovery), structured source registry, confidence signaling with citations, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), intent routing, common search patterns
2. **MCP Agent** (`mcp-agent`): Connects to external tools via MCP protocol, full LearningMachine, learns tool usage patterns
3. **Web Search Agent** (`web-search-agent`): Web research via DuckDuckGo, full LearningMachine, learns search patterns and source reliability
4. **Reasoning Agent** (`reasoning-agent`): Chain-of-thought reasoning (2-6 steps), full LearningMachine, learns effective reasoning approaches
5. **Data Analyst** (`data-agent`): Read-only PostgreSQL queries (Dash pattern) with dual knowledge system (curated `data_knowledge` + dynamic `data_learnings`), full LearningMachine, runtime schema introspection, validated query saving, F1 dataset support, and insight-focused instructions
6. **M365 Agent** (`m365-agent`): Read-only Microsoft 365 access (OneDrive, SharePoint, Outlook, Calendar, Teams) via Softeria MCP server, OBO token exchange, per-user MSAL isolation, three-layer read-only enforcement (Graph scopes + `--read-only` flag + `m365_write_guard` hook), opt-in via `M365_ENABLED=true`

## Teams

1. **Research Team** (`research-team`): Coordinate-mode multi-agent research (web_researcher + analyst), safety parameters (max_iterations=5, num_history_runs=5, add_datetime_to_context)

## Workflows

1. **Research Workflow** (`research-workflow`): Quality-gated research pipeline (Search → Loop refinement → Conditional analysis)

## Dependencies (pyproject.toml)

agno, fastapi[standard], openai, pgvector, psycopg[binary], sqlalchemy, mcp, opentelemetry-\*, opentelemetry-exporter-otlp-proto-http, openinference-instrumentation-agno, a2a-sdk[all], litellm, ddgs, fastmcp, pypdf, aiofiles, pandas, httpx, rich
Dev: mypy, ruff, pytest, requests, pandas-stubs

## Frontend Dependencies (package.json)

next, react, react-dom, tailwindcss, zustand, framer-motion, @radix-ui/\*, react-markdown, nuqs

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
- `mise run evals:run` - LLM-based evaluation suite (`-c` category, `-v` verbose, `-g` LLM grading, `-s` source checking, `--direct` no API; golden SQL runs automatically)
- `mise run agent:cli` - run agent via CLI (`-- <module> [-q question]`)
- `mise run load-sample-data` - load F1 sample data into PostgreSQL
- `mise run load-knowledge` - populate vector DB with curated knowledge (`--recreate` to rebuild)
- `mise run auth:generate-token` - generate dev JWT tokens
- `mise run schedules:setup` - initialize scheduler tables
- `mise run frontend:setup` / `frontend:dev` / `frontend:build`
- `mise run frontend:lint` / `frontend:format` / `frontend:typecheck` / `frontend:validate`
- `mise run gateway:up` - start MCP Gateway (`--prod`, `--m365`)
- `mise run gateway:logs` - tail gateway logs (`--prod`)
- `mise run docs:dev` - preview docs site locally (port 3333)
- `mise run docs:validate` - validate docs build + check broken links

## Adding an Agent

1. Create `backend/agents/my_agent.py` with Agent definition
2. Import and register in `backend/main.py` agents list
3. Restart containers

## Authentication & RBAC

**Provider**: Microsoft Entra ID (Azure AD) via custom JWT middleware
**Pattern**: `EntraJWTMiddleware` on FastAPI `base_app` → `AgentOS(base_app=base_app)`. No `authorization=True` on AgentOS.
**Mode**: Opt-in — auth disabled (passthrough) when any of `AZURE_TENANT_ID`/`AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_AUDIENCE` is unset

### Backend auth package: `backend/auth/`

- `config.py` — `AuthConfig` dataclass (reads 8 env vars; `enabled` property)
- `jwks_cache.py` — OIDC discovery → in-memory JWKS (kid→RSAPublicKey); background refresh every 1h
- `middleware.py` — `EntraJWTMiddleware`; validates RS256; sets `request.state` fields per AgentOS contract
- `scope_mapper.py` — `ROLE_SCOPE_MAP`; maps Entra App Roles → Agno scope strings
- `models.py` — SQLAlchemy ORM: `auth_users`, `auth_teams`, `auth_team_memberships`, `auth_denied_tokens`
- `graph.py` — Microsoft Graph API v1.0 client (delegated + app credentials; 429 handling)
- `sync_service.py` — Login sync + background group sync; deprovisioned user denial
- `security_headers.py` — `SecurityHeadersMiddleware` (CSP, X-Frame-Options, etc.)
- `routes.py` — `/auth/health`, `/auth/me`, `/auth/sync`, `/auth/teams`, `/auth/users`; slowapi rate limits
- `dependencies.py` — FastAPI `Depends` helpers for scope enforcement
- `m365_token_service.py` — OBO token exchange with per-user MSAL cache (Fernet-encrypted to PostgreSQL)
- `m365_routes.py` — `/m365/status`, `/m365/connect`, `/m365/disconnect`; `warm_m365_cache()` at startup
- `m365_middleware.py` — `M365TokenMiddleware`: per-request Graph token propagation via contextvars

### Frontend auth package: `frontend/src/auth/`

- `msalConfig.ts` — `PublicClientApplication` singleton (null when unconfigured; SSR-safe)
- `authProvider.tsx` — `MsalProvider` wrapper; passes through when unconfigured
- `useAuth.ts` — `useMsal()` wrapper; silent token acquisition with redirect fallback
- `useTokenSync.ts` — Syncs MSAL access token → Zustand `authToken` every 5 minutes
- `AuthUserButton.tsx` — Sidebar login/logout UI; replaces manual token entry when configured

### App Roles (Azure) → Scopes (Agno)

| Role        | Key Scopes                 |
| ----------- | -------------------------- |
| GlobalAdmin | `agent_os:admin` (bypass)  |
| Admin       | Full CRUD all resources    |
| TeamLead    | run, sessions, memories    |
| Developer   | read, run, sessions        |
| DevOps      | metrics, traces, schedules |
| InfoSec     | read-only all              |
| User        | basic read, sessions       |

### Key env vars

Backend: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_AUDIENCE`, `FRONTEND_URL`
Frontend (build-time): `NEXT_PUBLIC_AZURE_CLIENT_ID`, `NEXT_PUBLIC_AZURE_TENANT_ID`, `NEXT_PUBLIC_REDIRECT_URI`

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
- `AZURE_TENANT_ID` / `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_AUDIENCE` (all 4 required to enable Entra ID auth; empty = passthrough mode)
- `FRONTEND_URL` (CORS allowed origin, default: http://localhost:3000)
- `JWT_SECRET_KEY` (legacy HS256 auth; superseded by Entra ID when Azure vars are set)
- `NEXT_PUBLIC_AZURE_CLIENT_ID` / `NEXT_PUBLIC_AZURE_TENANT_ID` / `NEXT_PUBLIC_REDIRECT_URI` (frontend MSAL config, baked at build time)
- `TRACING_ENABLED` (set to `true` for trace-to-PostgreSQL via Agno)
- `OTLP_ENDPOINTS` (comma-separated OTLP URLs for multi-export — Langfuse, Phoenix, etc.)
- `OTLP_AUTH_HEADERS` (comma-separated auth headers parallel to `OTLP_ENDPOINTS`)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (legacy single-endpoint fallback; prefer `OTLP_ENDPOINTS`)
- `A2A_ENABLED` (set to `true` to expose agents via A2A protocol at `/a2a/agents/{id}`)
- `A2A_BASE_URL` (base URL for AgentCard discovery, default: http://localhost:8000)
- `M365_ENABLED` (set to `true` to enable M365 integration; requires Azure auth vars; registers M365 agent + `/m365/` routes)
- `M365_MCP_URL` (Softeria MCP server URL, default: http://apollos-m365-mcp:9000/mcp)
- `M365_MCP_PORT` (host port for MCP server, default: 9000)
- `M365_CACHE_KEY` (Fernet key for token cache encryption; derives from AZURE_CLIENT_SECRET if unset)
- `MCP_GATEWAY_ENABLED` (set to `true` to route MCP traffic through ContextForge gateway; opt-in)
- `MCP_GATEWAY_URL` (ContextForge gateway URL, default: http://apollos-mcp-gateway:4444)
- `MCP_GATEWAY_JWT_SECRET` (shared JWT secret for gateway service auth)
- `NEXT_PUBLIC_DEFAULT_ENDPOINT` (default endpoint shown in frontend UI, default: http://localhost:8000)
- `NEXT_PUBLIC_OS_SECURITY_KEY` (optional: pre-fill auth token in frontend)

## Documentation

- Mintlify site in `docs/` (MDX pages, `docs.json` config)
- Preview on port 3333 (`mise run docs:dev`) to avoid frontend port conflict
- Style guide at `docs/CLAUDE.md` (excluded from Mintlify build via `.mintignore`)
- Sections: Getting started, Agents, Teams, Workflows, Configuration (environment, security, telemetry, A2A, M365, MCP Gateway, Docker), Reference, Contributing

## Security & CI/CD

- CodeQL scanning on push/PR to main + weekly (Python, JS/TS, Actions)
- CI workflows use pinned action SHAs for supply-chain security
- CI workflows use mise tasks (not raw commands) for consistency
- Explicit `permissions` block on all workflows (least-privilege)
- Docker images publish to GHCR (ghcr.io/<owner>/apollos-backend, apollos-frontend, apollos-docs)
- Docs image builds on push to main (docs/\*\* changes), backend/frontend images build on release
