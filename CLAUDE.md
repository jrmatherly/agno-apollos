# Apollos AI

## Project Structure

All Python backend code lives under `backend/` as a proper package.
Imports use fully-qualified paths: `from backend.agents.x import y`, `from backend.db import z`.
Docker WORKDIR `/app` is the project root, not the Python package.

## Commands

- `uv run ruff format --check .` - check formatting
- `uv run ruff check .` - lint
- `uv run mypy .` - type check
- `uv sync --dev` - install all deps
- `docker compose watch` - dev mode with hot-reload

## Conventions

- Model provider: `LiteLLMOpenAI` from `agno.models.litellm` (proxy class, uses `base_url`)
- All model/embedding config via env vars (MODEL_ID, EMBEDDING_MODEL_ID, LITELLM_BASE_URL, etc.)
- `agno.*` imports are the Agno framework library. Never rename or replace these.
- New agents go in `backend/agents/`, register in `backend/main.py`
- Keep `agnohq/python:3.12` and `agnohq/pgvector:18` base images
- ruff line-length: 120

## Agno Docs Style

When writing documentation, follow `docs/CLAUDE.md`:
- No em dashes, no "learn how to", no contrastive negation
- Code first, explain after. Tables over prose for comparisons.
