# Apollos AI

Deploy a multi-agent system on Docker, powered by the [Agno](https://docs.agno.com) framework.

## What's Included

| Agent | Pattern | Description |
|-------|---------|-------------|
| Knowledge Agent | Agentic RAG | Answers questions from a knowledge base. |
| MCP Agent | MCP Tool Use | Connects to external services via MCP. |

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

Answers questions using hybrid search over a vector database (Agentic RAG).

**Load documents:**

```sh
docker exec -it apollos-backend python -m backend.agents.knowledge_agent
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

## Common Tasks

### Add your own agent

1. Create `backend/agents/my_agent.py`:

```python
from os import getenv

from agno.agent import Agent
from agno.models.litellm import LiteLLMOpenAI
from backend.db import get_postgres_db

my_agent = Agent(
    id="my-agent",
    name="My Agent",
    model=LiteLLMOpenAI(
        id=getenv("MODEL_ID", "gpt-5-mini"),
        base_url=getenv("LITELLM_BASE_URL", "http://localhost:4000/v1"),
    ),
    db=get_postgres_db(),
    instructions="You are a helpful assistant.",
)
```

1. Register in `backend/main.py`:

```python
from backend.agents.my_agent import my_agent

agent_os = AgentOS(
    name="Apollos AI",
    agents=[knowledge_agent, mcp_agent, my_agent],
    ...
)
```

1. Restart: `docker compose restart`

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
| `mise run docker:up` | Start the full stack (build + detach) |
| `mise run docker:down` | Stop all services |
| `mise run docker:logs` | Tail logs from all services |
| `mise run docker:build` | Build multi-arch Docker image |
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
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |
| `DB_USER` | No | `ai` | Database user |
| `DB_PASS` | No | `ai` | Database password |
| `DB_DATABASE` | No | `ai` | Database name |
| `RUNTIME_ENV` | No | `prd` | Set to `dev` for auto-reload |
| `IMAGE_TAG` | No | `latest` | Docker image tag for backend and frontend |
| `NEXT_PUBLIC_OS_SECURITY_KEY` | No | - | Pre-fill auth token in the frontend UI |

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Discord](https://agno.com/discord)
