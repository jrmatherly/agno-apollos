# Apollos AI

Deploy a multi-agent system on Docker, powered by the [Agno](https://docs.agno.com) framework.

## What's Included

### Agents

| Agent | Pattern | Description |
|-------|---------|-------------|
| Knowledge Agent | Agentic RAG | Answers questions from a knowledge base with file browsing, FAQ-building, source citations, and per-user learning. |
| MCP Agent | MCP Tool Use | Connects to external services via MCP, learns tool usage patterns. |
| Web Search Agent | Web Research | Searches the web using DuckDuckGo, learns search patterns and source reliability. |
| Reasoning Agent | Chain-of-Thought | Self-learning reasoning patterns with configurable depth. |
| Data Analyst | SQL Analysis | Read-only PostgreSQL queries with dual knowledge system, personalized per-user experience. |
| M365 Agent | MCP Tool Use | Read-only access to OneDrive, SharePoint, Outlook, Calendar, and Teams via Microsoft Graph. Opt-in (`M365_ENABLED=true`). |

### Teams

| Team | Mode | Description |
|------|------|-------------|
| Research Team | Coordinate | Multi-agent research combining web search and analysis. |

### Workflows

| Workflow | Steps | Description |
|----------|-------|-------------|
| Research Workflow | Search → Quality Loop → Analysis | Iterative research with quality gates and conditional deep analysis. |

## Prerequisites

- [mise](https://mise.jdx.dev) (manages Python, uv, Node.js, pnpm, and all dev tasks)
- [Docker](https://docs.docker.com/get-docker/)

## Get Started

```sh
# Install mise (if not already installed)
curl https://mise.run | sh

# Configure environment
cp example.env .env
# Edit .env and add your LiteLLM API key and proxy URL

# Install tools and dependencies
mise install
mise run setup

# Start the application
mise run docker:up

# Load documents for the knowledge agent
mise run load-docs
```

Confirm Apollos AI is running at [http://localhost:8000/docs](http://localhost:8000/docs).

### Open the Web UI

The self-hosted frontend is available at [http://localhost:3000](http://localhost:3000).

The default backend endpoint is `http://localhost:8000`. You can change this in the sidebar.

To use the cloud-hosted UI instead, go to [os.agno.com](https://os.agno.com) and add your local endpoint.

## The Agents

### Knowledge Agent

Answers questions using hybrid search over a vector database (Agentic RAG). Features file browsing (FileTools), FAQ-building (save_intent_discovery), structured source registry, confidence signaling with citation patterns, intent routing, learning system, and user profiles.

**Load documents:**

```sh
mise run load-docs
```

**Try it:**

```
What is Agno?
How do I create my first agent?
What documents are in your knowledge base?
```

### MCP Agent

Connects to external tools via the Model Context Protocol.

**Try it:**

```
What tools do you have access to?
Search the docs for how to use LearningMachine
Find examples of agents with memory
```

### Web Search Agent

Searches the web for current information with source citations.

**Try it:**

```
What are the latest developments in AI?
```

### Reasoning Agent

Step-by-step reasoning with configurable depth (2-6 steps).

**Try it:**

```
Walk me through the pros and cons of microservices vs monoliths.
```

### Data Analyst Agent

Queries PostgreSQL with read-only tools, dual knowledge system (curated metadata + dynamic learnings), runtime schema introspection, and validated query saving. Includes F1 dataset (1950-2020) with 5 tables.

**Load F1 sample data and knowledge:**

```sh
mise run load-sample-data
mise run load-knowledge
```

**Try it:**

```
What tables are available in the database?
How many races has Lewis Hamilton won?
Which team has the most constructor championships?
Show me the fastest lap records at Monza
```

## Common Tasks

### Add your own agent

1. Create `backend/agents/my_agent.py`:

```python
from agno.agent import Agent
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

from backend.db import get_postgres_db
from backend.models import get_model

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=get_model(),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
    pre_hooks=[PIIDetectionGuardrail(mask_pii=False), PromptInjectionGuardrail()],
    enable_agentic_memory=True,
    markdown=True,
    enable_session_summaries=True,
)
```

2. Register in `backend/main.py`:

```python
from backend.agents.my_agent import my_agent

agent_os = AgentOS(
    name="Apollos AI",
    agents=[..., my_agent],
    ...
)
```

3. Restart: `docker compose restart`

### Add tools to an agent

Agno includes 100+ tool integrations. See the [full list](https://docs.agno.com/tools/toolkits).

```python
from agno.tools.slack import SlackTools
from agno.tools.google_calendar import GoogleCalendarTools

my_agent = Agent(
    ...
    tools=[
        SlackTools(),
        GoogleCalendarTools(),
    ],
)
```

### Add dependencies

```sh
# Add a package (auto-updates uv.lock)
uv add <package>

# Rebuild container
docker compose up -d --build
```

### Use a different model provider

1. Add your API key to `.env` (e.g., `ANTHROPIC_API_KEY`)
2. Update agents to use the new provider:

```python
from agno.models.anthropic import Claude

model=Claude(id="claude-sonnet-4-5")
```
1. Add dependency: `uv add anthropic`

---

## Development Tasks

This project uses [mise](https://mise.jdx.dev) to manage tools (Python, uv) and development tasks. Run `mise tasks` to see all available tasks.

| Task | Description |
|------|-------------|
| `mise run setup` | Install all dependencies (`--ci` for locked mode) |
| `mise run format` | Format code (`--check` for CI check-only mode) |
| `mise run lint` | Lint code (ruff check) |
| `mise run typecheck` | Type-check code (mypy) |
| `mise run validate` | Run all checks (format-check, lint, typecheck) |
| `mise run dev` | Start stack in watch mode (hot-reload) |
| `mise run docker:up` | Start full stack (`--prod` for GHCR images, `--docs` to include docs) |
| `mise run docker:down` | Stop all services (`--prod` for production) |
| `mise run docker:logs` | Tail logs (`--prod` for production) |
| `mise run docker:build` | Build all images locally (`--platform amd64\|arm64`) |
| `mise run db` | Start only the database service |
| `mise run load-docs` | Load knowledge base documents |
| `mise run ci` | Run full CI pipeline |
| `mise run clean` | Clean build artifacts and caches |
| `mise run release` | Create a GitHub release (interactive version prompt) |
| `mise run frontend:setup` | Install frontend dependencies (`--ci` for frozen lockfile) |
| `mise run frontend:dev` | Start frontend dev server (port 3000) |
| `mise run frontend:build` | Build frontend for production |
| `mise run frontend:lint` | Lint frontend code (ESLint) |
| `mise run frontend:format` | Check frontend formatting (Prettier) |
| `mise run frontend:typecheck` | Type-check frontend code (TypeScript) |
| `mise run frontend:validate` | Run all frontend checks |
| `mise run docs:dev` | Preview docs site locally (port 3333) |
| `mise run docs:validate` | Validate docs build and check broken links |
| `mise run docs:docker` | Start docs in Docker (`--prod` for GHCR image) |
| `mise run test` | Run integration tests (requires running backend) |
| `mise run evals:run` | Run eval suite (`-c` category, `-v` verbose, `-g` LLM grading, `-s` source checking, `--direct`) |
| `mise run agent:cli` | Run agent via CLI (`-- <module> [-q question]`) |
| `mise run load-sample-data` | Load F1 sample data into PostgreSQL |
| `mise run load-knowledge` | Populate vector DB with curated knowledge (`--recreate` to rebuild) |
| `mise run auth:generate-token` | Generate dev JWT tokens for RBAC testing |
| `mise run schedules:setup` | Initialize scheduler tables |

### CLI Testing

Run agents directly without the API server:

```sh
# Interactive mode
mise run agent:cli -- data_agent

# Single question
mise run agent:cli -- reasoning_agent -q "Compare REST vs GraphQL"

# With session persistence
mise run agent:cli -- knowledge_agent -s my-session -q "What is Agno?"
```

### Local Development (without Docker)

```sh
# Install tools and deps
mise install
mise run setup
source .venv/bin/activate

# Start PostgreSQL (required)
mise run db

# Run the app
uv run python -m backend.main
```

### Using Docker Compose Watch

For automatic hot-reload with dependency rebuild:
```sh
mise run dev
```

This syncs code changes into the container and rebuilds when `pyproject.toml` or `uv.lock` change.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LITELLM_API_KEY` | Yes | - | LiteLLM Proxy API key |
| `LITELLM_BASE_URL` | No | `http://localhost:4000/v1` | LiteLLM Proxy URL |
| `MODEL_ID` | No | `gpt-5-mini` | LLM model ID |
| `EMBEDDING_MODEL_ID` | No | `text-embedding-3-small` | Embedding model ID |
| `EMBEDDING_DIMENSIONS` | No | `1536` | Embedding vector dimensions |
| `DB_HOST` | No | `apollos-db` | Database host (use Docker service name) |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `RUNTIME_ENV` | No | `dev` | Set to `dev` for auto-reload, `prd` for production |
| `IMAGE_TAG` | No | `latest` | Docker image tag for backend and frontend |
| `GHCR_OWNER` | No | `jrmatherly` | GHCR image owner (used by `docker-compose.prod.yaml`) |
| `NEXT_PUBLIC_DEFAULT_ENDPOINT` | No | `http://localhost:8000` | Default AgentOS endpoint shown in the UI |
| `AZURE_TENANT_ID` | No | - | Entra ID tenant ID. All 4 required to enable auth. |
| `AZURE_CLIENT_ID` | No | - | Entra ID application (client) ID |
| `AZURE_CLIENT_SECRET` | No | - | Client secret for Microsoft Graph API access |
| `AZURE_AUDIENCE` | No | - | Token audience (`api://{AZURE_CLIENT_ID}`). Both `api://` and bare GUID forms accepted. |
| `AUTH_DEBUG` | No | `True` (dev) | Log diagnostic 401 details: missing tokens, expired tokens, audience mismatches. |
| `FRONTEND_URL` | No | `http://localhost:3000` | CORS allowed origin |
| `JWT_SECRET_KEY` | No | - | Legacy HS256 auth. Superseded by Entra ID when Azure vars are set. |
| `DOCUMENTS_DIR` | No | `data/docs` | Knowledge agent file browsing directory |
| `M365_ENABLED` | No | `false` | Enable Microsoft 365 integration (opt-in) |
| `M365_MCP_URL` | No | `http://apollos-m365-mcp:9000/mcp` | Softeria MCP server URL |
| `M365_MCP_PORT` | No | `9000` | Host port for MCP server |
| `M365_CACHE_KEY` | No | (derived) | Fernet key for token cache encryption |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | - | OTel trace export endpoint (empty = disabled) |
| `NEXT_PUBLIC_OS_SECURITY_KEY` | No | - | Pre-fill auth token in the frontend UI |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Discord](https://agno.com/discord)
