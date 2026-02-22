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
│   ├── telemetry.py           # Dual-layer observability: trace-to-DB (Agno) + OTLP multi-export (opt-in)
│   ├── registry.py            # Component registry for Agent-as-Config persistence (tools/functions/models/dbs)
│   ├── cli.py                # Shared Rich CLI module for direct agent testing
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── knowledge_agent.py   # Agentic RAG agent (hybrid search, learning, user profiles)
│   │   ├── mcp_agent.py         # MCP tool-use agent (external services via MCP)
│   │   ├── web_search_agent.py  # Web research agent (DuckDuckGo)
│   │   ├── reasoning_agent.py   # Chain-of-thought reasoning agent
│   │   ├── data_agent.py        # Data analyst agent (read-only PostgreSQL)
│   │   └── m365_agent.py        # M365 agent (read-only Graph via MCP, opt-in)
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
│   │   ├── save_query.py        # Save validated SQL queries to knowledge base
│   │   ├── save_discovery.py    # Save intent-to-location mappings for FAQ-building
│   │   ├── m365.py              # M365 MCP tools factory (contextvars header_provider)
│   │   └── hooks.py             # Tool hooks: audit_hook, m365_write_guard
│   ├── context/             # Context modules for agents
│   │   ├── __init__.py
│   │   ├── semantic_model.py    # 11-table semantic model (Agno + F1) for data agent
│   │   ├── business_rules.py    # Business rules, metrics, gotchas from JSON
│   │   ├── intent_routing.py    # Intent routing guide for knowledge agent
│   │   └── source_registry.py   # Structured source metadata for knowledge agent
│   ├── knowledge/           # Document loaders and knowledge assets
│   │   ├── __init__.py
│   │   ├── loaders.py           # PDF/CSV loaders from data/docs/
│   │   ├── sources/             # Structured source metadata JSON
│   │   │   └── knowledge_sources.json  # Knowledge base capabilities and search tips
│   │   └── patterns/            # Common search strategy patterns
│   │       └── common_patterns.md      # How-to guide for searching the knowledge base
│   ├── evals/               # LLM-based evaluation harness
│   │   ├── __init__.py
│   │   ├── grader.py            # LLM grader (GradeResult) + golden SQL comparison + source citation checking
│   │   ├── test_cases.py        # TestCase dataclass with golden SQL/path, 15 F1 + 10 knowledge + 1 web cases
│   │   ├── run_evals.py         # Rich CLI runner (string match, LLM grade, SQL compare, source check, API/direct)
│   │   ├── reliability_evals.py # Tool-call reliability evals (ReliabilityEval) for agents and research team
│   │   └── judge.py             # Agent-as-judge post_hook factory (AgentAsJudgeEval, opt-in via AGENT_JUDGE_ENABLED)
│   ├── scripts/             # Data loading scripts
│   │   ├── __init__.py
│   │   ├── load_sample_data.py  # Download and load F1 data (1950-2020) into PostgreSQL
│   │   └── load_knowledge.py    # Load table/query/business knowledge into vector DB
│   ├── a2a/                 # A2A protocol integration (expose agents as A2A-compliant servers)
│   │   ├── __init__.py
│   │   ├── executor.py          # AgnoAgentExecutor — wraps Agno agents for A2A message handling
│   │   └── server.py            # AgentCard builder + A2AStarletteApplication mount helpers
│   ├── mcp/                 # MCP Gateway integration (ContextForge)
│   │   ├── __init__.py
│   │   ├── config.py             # MCP_GATEWAY_ENABLED flag, lazy singleton, get_gateway_tools_factory()
│   │   ├── gateway_client.py     # GatewayClient: JWT generation (jti+exp), gateway CRUD
│   │   ├── tools_factory.py      # Gateway-aware header_provider + tools factory
│   │   ├── routes.py             # Proxy routes: /mcp/servers (list, get, register, delete)
│   │   ├── schemas.py            # Pydantic models (MCPServerInfo, MCPServerRegister, MCPServerResponse)
│   │   └── validation.py         # BYOMCP URL validation (HTTPS-only, no private IPs)
│   ├── maintenance.py       # Scheduled maintenance: memory optimization (MemoryManager) + usage warnings
│   └── db/                  # Database layer
│       ├── __init__.py      # Re-exports: get_postgres_db, get_eval_db, create_knowledge, db_url
│       ├── session.py       # PostgresDb factory + eval DB factory + Knowledge factory (pgvector hybrid)
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
│   │   │   └── settings/    # Settings pages (hub + M365 + MCP Integrations)
│   │   ├── components/      # React components
│   │   │   ├── chat/        # Chat UI (ChatArea, Sidebar, Messages, Multimedia)
│   │   │   └── ui/          # shadcn/ui primitives (button, dialog, select, etc.)
│   │   ├── api/             # API client (browser-side fetch to backend)
│   │   │   ├── os.ts        # AgentOS API functions (agents, teams, sessions, runs)
│   │   │   ├── m365.ts      # M365 API client (status, connect, disconnect)
│   │   │   ├── mcp.ts       # MCP Gateway API client (list, register, delete servers)
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
│   ├── agent/               # Agent tasks
│   │   └── cli              # Run agent via CLI (docker exec)
│   ├── schedules/           # Scheduler tasks
│   │   └── setup            # Initialize scheduler tables
│   ├── docker/              # Docker-specific tasks
│   │   ├── up               # Start full stack (--prod, --docs, --m365, --gateway)
│   │   ├── down             # Stop all services (--prod, --m365, --gateway)
│   │   ├── logs             # Tail logs (--prod, --m365, --gateway)
│   │   └── build            # Build all images locally (--platform amd64|arm64)
│   ├── gateway/             # MCP Gateway tasks
│   │   ├── up               # Start gateway (--prod, --m365)
│   │   └── logs             # Tail gateway logs (--prod)
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
│   ├── entrypoint.sh        # Container entrypoint — DB wait, banner, exec command
│   └── init-contextforge-db.sh  # Creates contextforge database on first PostgreSQL init
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
│   ├── configuration/       # Environment, security, telemetry, A2A, M365, Docker config
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
│   ├── test_schedules.py    # Scheduler endpoint tests
│   ├── test_m365_token_service.py  # OBO token service tests (7)
│   ├── test_m365_model.py          # M365Connection model tests (4)
│   ├── test_m365_tools.py          # MCP tools layer tests (5)
│   ├── test_m365_middleware.py     # Token middleware tests (4)
│   ├── test_m365_hooks.py          # Tool hook tests (3)
│   └── test_m365_integration.py   # M365 integration tests (3, skip when disabled)
├── example.env              # Template for .env (LiteLLM, model, DB, auth, telemetry, frontend config)
└── README.md                # Setup guide, agent docs, common tasks
```

## Dependency Management

### Backend (Python)

Uses **uv native project management** (not pip-compatibility mode):

| Operation           | Command               |
| ------------------- | --------------------- |
| Add a dependency    | `uv add <package>`    |
| Remove a dependency | `uv remove <package>` |
| Upgrade all deps    | `uv lock --upgrade`   |
| Sync environment    | `mise run setup`      |

**Lockfile**: `uv.lock` (cross-platform TOML, auto-managed, committed to git)
**Dev deps**: Defined in `[dependency-groups]` (PEP 735)

### Frontend (Node.js)

Uses **pnpm** for package management:

| Operation            | Command                                |
| -------------------- | -------------------------------------- |
| Install deps         | `mise run frontend:setup`              |
| Add a dependency     | `cd frontend && pnpm add <package>`    |
| Remove a dependency  | `cd frontend && pnpm remove <package>` |
| Build for production | `mise run frontend:build`              |

**Lockfile**: `frontend/pnpm-lock.yaml` (committed to git)
**Dev deps**: Defined in `devDependencies` in `frontend/package.json`

## Entry Points

| Entry Point      | Path                                | Command                 | Description                               |
| ---------------- | ----------------------------------- | ----------------------- | ----------------------------------------- |
| API Server       | `backend/main.py`                   | `mise run docker:up`    | Starts Apollos AI FastAPI server on :8000 |
| Frontend UI      | `frontend/`                         | `mise run frontend:dev` | Starts Next.js dev server on :3000        |
| Knowledge Loader | `backend/agents/knowledge_agent.py` | `mise run load-docs`    | Loads default docs into vector DB         |
| Full Stack       | `docker-compose.yaml`               | `mise run docker:up`    | Core services (DB + backend + frontend)   |
| Docs Site        | `docs/Dockerfile`                   | `mise run docs:docker`  | Documentation on :3333                    |
| Watch Mode       | `docker-compose.yaml`               | `mise run dev`          | Auto-sync code + rebuild on dep changes   |

## Core Modules

### backend/models.py

- **Exports**: `get_model()` factory function
- **Purpose**: Shared model factory — all agents use this instead of inline `LiteLLMOpenAI`
- **Config**: `MODEL_ID`, `LITELLM_BASE_URL`, `LITELLM_API_KEY` env vars

### backend/cli.py

- **Exports**: `run_agent_cli()` function
- **Purpose**: Shared Rich CLI module for running agents directly from the command line
- **Features**: Single-question mode (`-q`), interactive prompt loop, session persistence (`-s`), user linking (`-u`), markdown rendering (`-m`), reasoning display (`--show-reasoning`), configurable exit commands, streaming toggle

### backend/agents/knowledge_agent.py

- **Exports**: `knowledge_agent` (Agent instance), `knowledge_learnings` (Knowledge), `load_default_documents()` function
- **Purpose**: RAG agent using pgvector hybrid search over ingested documents
- **Features**: Agentic memory, intent routing, confidence signaling with citation patterns, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), guardrails, session summaries, structured source registry, custom tools (FileTools, search_content, list_knowledge_sources, add_knowledge_source, save_intent_discovery)
- **Knowledge source**: Loads from `docs.agno.com` + PDF/CSV files from `data/docs/` + common search patterns from `backend/knowledge/patterns/`

### backend/agents/mcp_agent.py

- **Exports**: `mcp_agent` (Agent instance), `mcp_learnings` (Knowledge)
- **Purpose**: Tool-use agent connecting to external services via MCP protocol
- **MCP endpoint**: `https://docs.agno.com/mcp`
- **Features**: Agentic memory, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), guardrails, session summaries

### backend/agents/web_search_agent.py

- **Exports**: `web_search_agent` (Agent instance), `web_search_learnings` (Knowledge)
- **Purpose**: Web research agent using DuckDuckGo search + news
- **Features**: Agentic memory, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), guardrails, session summaries, source citations

### backend/agents/reasoning_agent.py

- **Exports**: `reasoning_agent` (Agent instance), `reasoning_learnings` (Knowledge)
- **Purpose**: Chain-of-thought reasoning with configurable step depth (2-6 steps)
- **Features**: Agentic memory, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), guardrails, session summaries, `reasoning=True`

### backend/agents/data_agent.py

- **Exports**: `data_agent` (Agent instance), `data_knowledge` (Knowledge), `data_learnings` (Knowledge)
- **Purpose**: Self-learning data analyst with dual knowledge system (Dash pattern)
- **Features**: Agentic memory, full LearningMachine (learned_knowledge, user_profile, user_memory, session_context), guardrails, session summaries, dual knowledge (curated + learnings), business rules context, insight-focused instructions
- **Tools**: PostgresTools (show_tables, describe_table, summarize_table, inspect_query), `introspect_schema`, `save_validated_query`

### backend/agents/m365_agent.py

- **Exports**: `m365_agent` (Agent instance)
- **Purpose**: Read-only M365 agent accessing OneDrive, SharePoint, Outlook, Calendar, Teams via Softeria MCP server
- **Features**: Guardrails, LearningMachine, tool_hooks (audit_hook + m365_write_guard), MCPTools with header_provider
- **Activation**: Conditional import in `backend/main.py` when `M365_ENABLED=true`

### backend/tools/m365.py

- **Exports**: `m365_mcp_tools()` factory, `set_graph_token()`, `clear_graph_token()`, `_graph_token_var` (ContextVar)
- **Purpose**: MCPTools factory with contextvars-based header_provider for per-request Graph token injection
- **Pattern**: Returns `[]` when `M365_ENABLED` is unset; returns `[MCPTools(...)]` when enabled

### backend/tools/hooks.py

- **Exports**: `audit_hook`, `m365_write_guard`
- **Purpose**: Tool hooks for M365 integration — audit logging and write operation blocking
- **Key pattern**: `m365_write_guard` raises `StopAgentRun` for `m365_send/create/update/delete/upload/move` prefixes

### backend/auth/m365_token_service.py

- **Exports**: `OBOTokenService`, `get_obo_service()`, `encrypt_cache()`, `decrypt_cache()`
- **Purpose**: OBO token exchange with per-user MSAL ConfidentialClientApplication isolation
- **Persistence**: Fernet-encrypted SerializableTokenCache in PostgreSQL

### backend/auth/m365_routes.py

- **Exports**: `m365_router`, `warm_m365_cache()`
- **Purpose**: API routes (`/m365/status`, `/m365/connect`, `/m365/disconnect`) + startup cache warming

### backend/auth/m365_middleware.py

- **Exports**: `M365TokenMiddleware`
- **Purpose**: Per-request Graph token propagation from MSAL cache into contextvars

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

### backend/registry.py

- **Exports**: `create_registry()` factory function
- **Purpose**: Central component registry for Agent-as-Config persistence — maps tools/functions/models/dbs by name so agents can be saved to and loaded from PostgreSQL
- **Contents**: Web search, Postgres, MCP, reasoning tools; custom functions (search, knowledge ops, data tools); default model and database

### backend/a2a/executor.py

- **Exports**: `AgnoAgentExecutor` class
- **Purpose**: Wraps Agno `Agent` instances for A2A protocol message handling
- **Key pattern**: `Agent.run()` is synchronous; uses `asyncio.to_thread()` to avoid blocking the async event loop. `event_queue.enqueue_event()` requires `await`.

### backend/a2a/server.py

- **Exports**: `create_a2a_apps()` factory function, `AGENT_METADATA` dict
- **Purpose**: Builds `AgentCard` discovery documents and `A2AStarletteApplication` instances for each registered agent
- **Mount pattern**: Returns `list[tuple[str, ASGIApp]]` for mounting on the FastAPI app at `/a2a/agents/{id}`

### backend/mcp/config.py

- **Exports**: `MCP_GATEWAY_ENABLED`, `get_gateway_client()`, `get_gateway_tools_factory()`
- **Purpose**: Centralized gateway config — lazy singleton GatewayClient + factory builder
- **Pattern**: `get_gateway_tools_factory("server-name", needs_user_token=True)` returns callable factory or `None`

### backend/mcp/gateway_client.py

- **Exports**: `GatewayClient` class
- **Purpose**: ContextForge API client — JWT generation (jti+exp), gateway CRUD (list, get, register, delete)
- **Key pattern**: RC1 requires `jti` (uuid4) + `exp` claims in service JWTs

### backend/mcp/tools_factory.py

- **Exports**: `create_gateway_header_provider()`, `create_gateway_tools_factory()`
- **Purpose**: Gateway-aware MCPTools factory with header_provider for service JWT + optional user token passthrough
- **Pattern**: Matches M365 `header_provider` convention (sync callable)

### backend/mcp/routes.py

- **Exports**: `mcp_router` (APIRouter)
- **Purpose**: Proxy routes to ContextForge gateway — GET/POST `/mcp/servers`, GET/DELETE `/mcp/servers/{id}`
- **Security**: Auth-gated, rate-limited, URL validation on registration

### backend/mcp/validation.py

- **Exports**: `validate_mcp_server_url()`, `URLValidationError`
- **Purpose**: BYOMCP URL validation — HTTPS-only for external servers, blocks private IPs and cloud metadata

### backend/auth/

- **Exports** (`__init__.py`): `EntraJWTMiddleware`, `auth_lifespan`, `auth_router`
- **Purpose**: Microsoft Entra ID JWT authentication, RBAC scope mapping, user/team sync, and auth API routes
- **Key files**:
  - `config.py` — `AuthConfig` (reads 8 env vars; `enabled` property for passthrough mode)
  - `middleware.py` — `EntraJWTMiddleware` (BaseHTTPMiddleware; RS256 validation; sets `request.state`)
  - `jwks_cache.py` — In-memory JWKS cache (OIDC discovery; background refresh; miss throttle)
  - `scope_mapper.py` — `ROLE_SCOPE_MAP`; maps Entra App Roles → Agno scope strings
  - `models.py` — SQLAlchemy ORM: `auth_users`, `auth_teams`, `auth_team_memberships`, `auth_denied_tokens`
  - `database.py` — Async engine + session factory + `create_auth_tables()`
  - `graph.py` — Microsoft Graph API v1.0 client (delegated + app credentials; 429 handling)
  - `sync_service.py` — Login user sync + background group sync + deny list management
  - `dependencies.py` — FastAPI `Depends`: `get_current_user`, `require_scope`
  - `routes.py` — `/auth/health`, `/auth/me`, `/auth/sync`, `/auth/teams`, `/auth/users`; slowapi rate limiter
  - `security_headers.py` — `SecurityHeadersMiddleware` (CSP, X-Frame-Options, etc.)

### backend/main.py

- **Exports**: `agent_os` (AgentOS), `app` (FastAPI app)
- **Purpose**: Creates and configures Apollos AI with all agents, teams, workflows, tracing, scheduler, A2A endpoints
- **Config**: Reads `backend/config.yaml` for UI quick-prompts
- **Features**: Entra ID RBAC auth (opt-in via Azure env vars), MCP server endpoint, dual-layer telemetry, A2A protocol endpoints (opt-in via `A2A_ENABLED`)
- **Auth pattern**: `EntraJWTMiddleware` on `base_app` → `AgentOS(base_app=base_app)`. No `authorization=True`.
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

### frontend/src/auth/

- **Purpose**: MSAL.js v5 authentication integration for Microsoft Entra ID
- **Key files**:
  - `msalConfig.ts` — `PublicClientApplication` singleton (null when unconfigured; SSR-safe)
  - `authProvider.tsx` — `AuthProvider` client component wrapping `MsalProvider`
  - `useAuth.ts` — `useAuth()` hook (login, logout, `getAccessToken()` with silent/redirect fallback)
  - `useTokenSync.ts` — Syncs MSAL access token → Zustand `authToken` every 5 minutes
  - `AuthUserButton.tsx` — Sidebar login/logout UI with user display name
  - `index.ts` — Re-exports
- **Activation**: Set `NEXT_PUBLIC_AZURE_CLIENT_ID` at build time. Empty = falls back to manual token entry.

## Configuration

| File                       | Purpose                                                                  |
| -------------------------- | ------------------------------------------------------------------------ |
| `mise.toml`                | Mise config: tools (Python 3.12, uv, Node 24, pnpm), env vars, settings  |
| `mise-tasks/`              | File-based mise tasks (25 dev workflow commands)                         |
| `pyproject.toml`           | Backend metadata, dependencies, [dependency-groups], ruff/mypy config    |
| `uv.lock`                  | Backend lockfile (auto-managed, committed to git)                        |
| `frontend/package.json`    | Frontend metadata, dependencies, scripts                                 |
| `frontend/pnpm-lock.yaml`  | Frontend lockfile (committed to git)                                     |
| `.python-version`          | Pins Python 3.12 for uv, pyenv, and CI                                   |
| `docker-compose.yaml`      | Dev: 3 core + optional docs/m365/gateway (local builds, hot-reload)      |
| `docker-compose.prod.yaml` | Prod: 3 core + optional docs/m365/gateway (GHCR images, no reload)       |
| `backend/config.yaml`      | Agent quick-prompts for the Agno web UI                                  |
| `example.env`              | Template: LiteLLM, model, DB, runtime, Docker, frontend config           |
| `backend/Dockerfile`       | Backend: two-layer cached build, `uv sync --locked`                      |
| `frontend/Dockerfile`      | Frontend: multi-stage standalone build, node:24-alpine                   |
| `docs/Dockerfile`          | Docs: node:24-alpine, Mintlify CLI (`mint dev`)                          |

## CI/CD

| Workflow            | Trigger                              | Steps                                                                                      |
| ------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `codeql.yml`        | Push to main, PR, weekly Mon 6am UTC | CodeQL security scanning: Python, JavaScript/TypeScript, Actions (security-extended suite) |
| `validate.yml`      | Push to main, PR                     | Parallel jobs: backend (format, lint, typecheck via mise) + frontend (validate via mise)   |
| `docker-images.yml` | Release published                    | Parallel jobs: build + push apollos-backend and apollos-frontend images to GHCR            |
| `docs-image.yml`    | Push to main (docs/\*\*)             | Build + push apollos-docs image to GHCR                                                    |

## Key Dependencies

### Backend

| Package                                  | Purpose                                                                         |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| `agno`                                   | Core agent framework (Agent, AgentOS, Knowledge, tools)                         |
| `fastapi[standard]`                      | HTTP API framework with uvicorn                                                 |
| `openai`                                 | OpenAI API client (used by embedder via LiteLLM Proxy)                          |
| `pgvector`                               | Vector similarity search extension for PostgreSQL                               |
| `psycopg[binary]`                        | PostgreSQL adapter (async-capable)                                              |
| `sqlalchemy`                             | ORM / database toolkit                                                          |
| `mcp`                                    | Model Context Protocol client                                                   |
| `opentelemetry-api/sdk`                  | Distributed tracing                                                             |
| `opentelemetry-exporter-otlp-proto-http` | OTLP HTTP trace exporter                                                        |
| `openinference-instrumentation-agno`     | Agno-specific OTel instrumentation                                              |
| `litellm`                                | Multi-provider LLM routing (external proxy, no [proxy] extra)                   |
| `a2a-sdk`                                | Agent-to-Agent protocol SDK (A2AStarletteApplication, AgentCard, AgentExecutor) |
| `ddgs`                                   | Web search backend for web_search_agent                                         |
| `fastmcp`                                | MCP server for AgentOS                                                          |
| `pypdf`                                  | PDF document reader for knowledge loaders                                       |
| `aiofiles`                               | Async file I/O for document loading                                             |
| `pandas`                                 | DataFrame loading for F1 sample data scripts                                    |
| `rich`                                   | Rich CLI output for eval runner                                                 |

**Dev deps** (`[dependency-groups]`): `mypy`, `pandas-stubs`, `ruff`, `pytest`, `requests`

### Frontend

| Package                    | Purpose                                   |
| -------------------------- | ----------------------------------------- |
| `next` (15.5.10)           | React framework (App Router)              |
| `react` / `react-dom` (18) | UI library                                |
| `tailwindcss`              | Utility-first CSS                         |
| `zustand`                  | State management                          |
| `framer-motion`            | Animations                                |
| `@radix-ui/*`              | Accessible UI primitives (shadcn/ui base) |
| `react-markdown`           | Markdown rendering                        |
| `nuqs`                     | URL query state sync                      |

**Dev deps**: `typescript`, `eslint`, `prettier`, `@types/node`, `@types/react`

## Environment Variables

| Variable                       | Required | Default                            | Description                                                                                   |
| ------------------------------ | -------- | ---------------------------------- | --------------------------------------------------------------------------------------------- |
| `LITELLM_API_KEY`              | Yes      | —                                  | LiteLLM Proxy API key                                                                         |
| `LITELLM_BASE_URL`             | No       | `http://localhost:4000/v1`         | LiteLLM Proxy URL                                                                             |
| `MODEL_ID`                     | No       | `gpt-5-mini`                       | LLM model ID                                                                                  |
| `EMBEDDING_MODEL_ID`           | No       | `text-embedding-3-small`           | Embedding model ID                                                                            |
| `EMBEDDING_DIMENSIONS`         | No       | `1536`                             | Embedding vector dimensions                                                                   |
| `DB_HOST`                      | No       | `localhost`                        | PostgreSQL host                                                                               |
| `DB_PORT`                      | No       | `5432`                             | PostgreSQL port                                                                               |
| `DB_USER`                      | No       | `ai`                               | PostgreSQL user                                                                               |
| `DB_PASS`                      | No       | `ai`                               | PostgreSQL password                                                                           |
| `DB_DATABASE`                  | No       | `ai`                               | PostgreSQL database name                                                                      |
| `DB_DRIVER`                    | No       | `postgresql+psycopg`               | SQLAlchemy DB driver                                                                          |
| `RUNTIME_ENV`                  | No       | `dev`                              | Set to `dev` for auto-reload                                                                  |
| `IMAGE_TAG`                    | No       | `latest`                           | Docker image tag for backend and frontend                                                     |
| `GHCR_OWNER`                   | No       | `jrmatherly`                       | GHCR image owner (used by docker-compose.prod.yaml)                                           |
| `NEXT_PUBLIC_DEFAULT_ENDPOINT` | No       | `http://localhost:8000`            | Default AgentOS endpoint shown in the UI                                                      |
| `NEXT_PUBLIC_OS_SECURITY_KEY`  | No       | —                                  | Pre-fill auth token in the frontend UI                                                        |
| `JWT_SECRET_KEY`               | No       | —                                  | Legacy HS256 auth (deprecated; superseded by Entra ID when Azure vars are set)                |
| `AZURE_TENANT_ID`              | No       | —                                  | Entra ID Directory (tenant) ID; all 4 AZURE\_\* required to enable auth                       |
| `AZURE_CLIENT_ID`              | No       | —                                  | Entra ID Application (client) ID                                                              |
| `AZURE_CLIENT_SECRET`          | No       | —                                  | Client secret for Microsoft Graph API access                                                  |
| `AZURE_AUDIENCE`               | No       | —                                  | Token audience; set to `api://{AZURE_CLIENT_ID}`. Both `api://` and bare GUID forms accepted. |
| `AUTH_DEBUG`                   | No       | `True` (dev) `False` (prod)        | Log diagnostic 401 details: missing tokens, expired tokens, audience mismatches.              |
| `FRONTEND_URL`                 | No       | `http://localhost:3000`            | CORS allowed origin for API responses                                                         |
| `NEXT_PUBLIC_AZURE_CLIENT_ID`  | No       | —                                  | Frontend MSAL client ID (build-time; empty = manual token entry)                              |
| `NEXT_PUBLIC_AZURE_TENANT_ID`  | No       | —                                  | Frontend MSAL tenant ID (build-time)                                                          |
| `NEXT_PUBLIC_REDIRECT_URI`     | No       | `http://localhost:3000`            | MSAL redirect URI after login (build-time)                                                    |
| `TRACING_ENABLED`              | No       | —                                  | Set to `true` to store traces in PostgreSQL via Agno (Layer 1)                                |
| `OTLP_ENDPOINTS`               | No       | —                                  | Comma-separated OTLP endpoint URLs for multi-export (Layer 2)                                 |
| `OTLP_AUTH_HEADERS`            | No       | —                                  | Comma-separated auth headers parallel to `OTLP_ENDPOINTS`                                     |
| `OTEL_EXPORTER_OTLP_ENDPOINT`  | No       | —                                  | Legacy single-endpoint fallback (use `OTLP_ENDPOINTS` for new setups)                         |
| `A2A_ENABLED`                  | No       | —                                  | Set to `true` to expose agents via A2A protocol endpoints                                     |
| `A2A_BASE_URL`                 | No       | `http://localhost:8000`            | Base URL used in AgentCard discovery documents                                                |
| `DOCUMENTS_DIR`                | No       | `./data/docs`                      | Knowledge agent file browsing directory                                                       |
| `M365_ENABLED`                 | No       | `false`                            | Enable Microsoft 365 integration (opt-in)                                                     |
| `M365_MCP_URL`                 | No       | `http://apollos-m365-mcp:9000/mcp` | Softeria MCP server URL                                                                       |
| `M365_MCP_PORT`                | No       | `9000`                             | Host port for MCP server                                                                      |
| `M365_CACHE_KEY`               | No       | (derived)                          | Fernet key for token cache encryption                                                         |
| `MCP_GATEWAY_ENABLED`          | No       | `false`                            | Enable MCP Gateway integration (opt-in via ContextForge)                                      |
| `MCP_GATEWAY_URL`              | No       | `http://apollos-mcp-gateway:4444` | ContextForge gateway URL                                                                      |
| `MCP_GATEWAY_JWT_SECRET`       | No       | —                                  | Shared JWT secret for gateway service auth                                                    |
| `WAIT_FOR_DB`                  | No       | —                                  | Container waits for DB readiness                                                              |
| `PRINT_ENV_ON_LOAD`            | No       | —                                  | Print env vars on container start                                                             |

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
- **Security**: Entra ID RBAC auth (opt-in via `AZURE_*` env vars) — `EntraJWTMiddleware` validates RS256 JWTs, maps App Roles to Agno scopes, and sets `request.state` per AgentOS contract. Passthrough mode (no auth required) when Azure vars are unset. Human-in-the-loop approval workflows (`@approval` decorator on tools).
- **Observability**: Dual-layer observability. Layer 1: `TRACING_ENABLED=true` stores agent traces in PostgreSQL via Agno. Layer 2: `OTLP_ENDPOINTS` exports to Langfuse, Arize Phoenix, Grafana, or any OTLP backend (multi-export, comma-separated, per-endpoint auth). Legacy `OTEL_EXPORTER_OTLP_ENDPOINT` preserved as fallback.
- **A2A Protocol**: `A2A_ENABLED=true` mounts each registered agent as a `A2AStarletteApplication` at `/a2a/agents/{id}`, exposing AgentCard discovery and JSON-RPC messaging with SSE streaming (a2a-sdk v0.3.x).
- **Learning**: All agents use full `LearningMachine` stack (learned_knowledge, user_profile, user_memory, session_context) with domain-specific learning triggers.
- **LLM Provider**: LiteLLM Proxy (all LLM and embedding traffic routes through self-hosted proxy).
- **Frontend**: Next.js 15 with standalone output. Connects to backend via browser-side fetch (not server-side). Default endpoint configurable via `NEXT_PUBLIC_DEFAULT_ENDPOINT` env var (defaults to `http://localhost:8000`).
- **Deployment**: Two compose files: `docker-compose.yaml` (dev, local builds) and `docker-compose.prod.yaml` (prod, GHCR images). Multi-arch images for production.
- **Tooling**: `mise` (task runner + tool manager), `uv` (backend package management), `pnpm` (frontend package management), `ruff` for formatting/linting, `mypy` for type-checking.
