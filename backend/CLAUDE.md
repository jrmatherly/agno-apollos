# Backend — Agent & Agno Conventions

Agent-specific patterns and Agno framework gotchas for `backend/`. See root `CLAUDE.md` for project-wide conventions.

## Agent Conventions

- All agents must have guardrails: `pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()]` — includes inline/ephemeral agents in workflows
- All agents use full LearningMachine stack: `learned_knowledge` (AGENTIC, shared), `user_profile`, `user_memory`, `session_context`
- Agent CLI for direct testing: `python -m backend.agents.<name>` (shared Rich CLI module at `backend/cli.py`)
- Data agent uses dual knowledge system: static `data_knowledge` (curated) + dynamic `data_learnings` (discovered via LearningMachine)

## Agno Framework API Notes

Always verify signatures before using: `python3 -c "import inspect; from agno.X import Y; print(inspect.signature(Y))"`

Docs and examples frequently have wrong parameter names — never assume, always verify.

Known gotchas:

- `@tool` must be outer decorator, `@approval` inner (otherwise mypy error on Function type)
- `@approval(type="audit")` requires explicit HITL flag on `@tool()` (e.g., `@tool(requires_confirmation=True)`). Plain `@approval` auto-sets this.
- Team: use `id=` (not `team_id=`), `mode=TeamMode.coordinate` (not string). Import `from agno.team.team import TeamMode`.
- `member_timeout` and `max_interactions_to_share` do not exist on Team in current version
- Workflow Step: takes `agent=` or `executor=` (no `instructions` or `timeout_seconds` params)
- Condition: takes `evaluator` + `steps` + `else_steps` (not `on_true`/`on_false`)
- Loop `end_condition`: receives `List[StepOutput]`, returns `True` to break. Condition `evaluator`: receives `StepInput`, returns `True` for primary path. Check `step_input.input` for user query (not `previous_step_content` which has accumulated output).
- Knowledge readers: `agno.knowledge.reader.pdf_reader.PDFReader` (not `agno.document.reader`)
- `include_tools`/`exclude_tools`: On base `Toolkit` class, passed via `**kwargs` to PostgresTools etc.
- Model API for direct calls: `model.response(messages=[Message(role="user", content=...)])` (not `model.invoke(str)`)
- `enable_session_summaries` is on Agent (not AgentOS); `enable_mcp_server` is on AgentOS
- `show_tool_calls` is NOT a valid Agent parameter

## M365 Integration (backend/auth/ + backend/tools/)

Opt-in via `M365_ENABLED=true`. Requires Entra ID auth (all 4 Azure vars must be set).

Key patterns:

- **Callable tools factory**: M365 agent uses `tools=m365_tools_factory` (a callable), NOT `tools=m365_mcp_tools()` (a list). AgentOS `mcp_lifespan` eagerly connects all MCPTools in static lists at startup — causes 401 since no user token exists at boot. Callable factories are resolved per-run. Never spread `*m365_mcp_tools()` into other agents' static tool lists.
- OBO token exchange: `OBOTokenService.connect()` is SYNC — call via `asyncio.to_thread()` from async handlers
- Per-user MSAL isolation: each user gets own `ConfidentialClientApplication` with `SerializableTokenCache`
- Token propagation: `M365TokenMiddleware` → `contextvars` → sync `header_provider` callback in MCPTools
- `dict.setdefault()` for thread-safe lazy init of per-user locks and MSAL apps (not check-then-act)
- Three-layer read-only: Graph scopes (`Mail.Read` not `ReadWrite`) + Softeria `--read-only` + `m365_write_guard` tool hook
- `m365_write_guard` raises `StopAgentRun` (from `agno.exceptions`) — not generic `Exception`
- Docker service `apollos-m365-mcp` uses `profiles: [m365]` — started with `mise run docker:up --m365`
- Docker healthcheck: use root `/` (public), not `/mcp` (requires auth)

Key files:

- `backend/auth/m365_token_service.py` — OBO exchange, Fernet encryption, per-user MSAL cache
- `backend/auth/m365_routes.py` — `/m365/status`, `/m365/connect`, `/m365/disconnect`
- `backend/auth/m365_middleware.py` — Per-request Graph token via contextvars
- `backend/tools/m365.py` — MCPTools factory with `header_provider`
- `backend/tools/hooks.py` — `audit_hook` and `m365_write_guard`
- `backend/agents/m365_agent.py` — Dedicated M365 agent (read-only instructions)

## MCP Gateway Integration (backend/mcp/)

Opt-in via `MCP_GATEWAY_ENABLED=true`. Routes MCP traffic through IBM ContextForge gateway.

Key patterns:

- **Gateway-aware tools factory**: Uses `get_gateway_tools_factory("server-name")` from `backend/mcp/config.py`. Returns a callable factory or `None` (disabled). Agents fall back to direct connection: `get_gateway_tools_factory("m365", needs_user_token=True) or m365_tools_factory`.
- **header_provider pattern**: Gateway factories use `header_provider` (sync callable), NOT `server_params`. Matches the established M365 convention. Agno calls `header_provider(run_context=...)` per-run.
- **Service JWT (RC1)**: ContextForge RC1 requires `jti` + `exp` claims in JWTs. `GatewayClient.create_service_token()` generates compliant tokens via PyJWT.
- **Header passthrough**: `X-Upstream-Authorization` forwards per-user tokens through the gateway. Requires `ENABLE_HEADER_PASSTHROUGH=true` in gateway config (defaults to `false`).
- **BYOMCP validation**: `backend/mcp/validation.py` enforces HTTPS-only for external servers, blocks private IPs and cloud metadata endpoints.
- **RBAC scopes**: `mcp:servers:read`, `mcp:servers:write`, `mcp:servers:delete`, `mcp:tools:call`. Route mappings in `scope_mapper.py`.

Key files:

- `backend/mcp/config.py` — `MCP_GATEWAY_ENABLED` flag, lazy singleton `GatewayClient`, `get_gateway_tools_factory()`
- `backend/mcp/gateway_client.py` — ContextForge API client (JWT generation, gateway list/register)
- `backend/mcp/tools_factory.py` — `create_gateway_header_provider()`, `create_gateway_tools_factory()`
- `backend/mcp/routes.py` — Proxy routes at `/mcp/servers` (list, get, register, delete)
- `backend/mcp/schemas.py` — Pydantic models for proxy responses
- `backend/mcp/validation.py` — BYOMCP URL validation (HTTPS, no private IPs)

## Entra ID Auth Package (backend/auth/)

Located at `backend/auth/`. Handles Microsoft Entra ID JWT validation, RBAC scope mapping,
user/team sync, and auth-specific FastAPI routes.

### Key API contracts

- `auth_config.enabled` → False when Azure vars unset; middleware passes all requests through
- `request.state` fields set by `EntraJWTMiddleware`: `authenticated`, `user_id` (Entra `oid`),
  `scopes` (list of strings), `authorization_enabled`, `accessible_resource_ids`, `token`,
  `session_id`, `dependencies`, `session_state`
- Use `oid` claim for `user_id` — NOT `sub` (sub is app-specific; oid is stable across apps)
- `ROLE_SCOPE_MAP` in `scope_mapper.py` maps Entra App Role values → Agno scope strings

### Gotchas

- `EntraJWTMiddleware` extends `BaseHTTPMiddleware` — do not use `authorization=True` on AgentOS
- JWKS cache fetches from OIDC discovery URL, not a hardcoded endpoint — works with key rotation
- Group membership overage (`_claim_names.groups` present when >200 groups) always triggers Graph API fetch
- Entra `oid` ≠ `sub`: `oid` is the stable cross-app user identifier; always use `oid` as `user_id`
- Token deny list checked per-request via SQLAlchemy; partial index on `expires_at > NOW()` keeps it fast
- `slowapi` rate limiter: limiter instance initialized in `routes.py`, registered on `base_app` in `main.py`
- **Single-app audience**: When SPA client and API resource share one app registration, Azure issues `aud = clientId` (bare GUID) even with `accessTokenAcceptedVersion: 2`. Middleware accepts both `api://clientId` and bare GUID — `AZURE_AUDIENCE` stays as `api://clientId` form.
- **AUTH_DEBUG env var**: Set `AUTH_DEBUG=true` to enable diagnostic 401 logging (missing token, expired, invalid audience — logs actual `aud` value on mismatch). Default: True in dev, False in prod.
- **AuthGuard component**: `frontend/src/components/auth/AuthGuard.tsx` gates the UI. Must check `inProgress === InteractionStatus.None` before calling `loginRedirect()` — calling earlier throws `BrowserAuthError: uninitialized_public_client_application`.
- **Sidebar initialize() gate**: `initialize()` is gated on `!isMsalConfigured || authToken` — prevents unauthenticated API calls before `useTokenSync` completes its first silent token acquisition.
