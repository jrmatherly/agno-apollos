FROM agnohq/python:3.12

# ---------------------------------------------------------------------------
# OCI Image Labels
# ---------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Apollos AI Backend" \
      org.opencontainers.image.description="Apollos AI multi-agent backend — FastAPI + Agno framework" \
      org.opencontainers.image.vendor="Apollos AI" \
      org.opencontainers.image.source="https://github.com/jrmatherly/agno-apollos" \
      org.opencontainers.image.licenses="Apache-2.0"

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    PYTHONPATH=/app

# ---------------------------------------------------------------------------
# Create non-root user
# ---------------------------------------------------------------------------
RUN groupadd -g 61000 app \
    && useradd -g 61000 -u 61000 -ms /bin/bash app

# ---------------------------------------------------------------------------
# Install dependencies (cached layer - only rebuilds when deps change)
# ---------------------------------------------------------------------------
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# ---------------------------------------------------------------------------
# Install project
# ---------------------------------------------------------------------------
COPY --chown=app:app . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Clean up build artifacts not needed at runtime
RUN rm -rf /app/build /app/ApollosAI.egg-info /app/uv.lock

ENV PATH="/app/.venv/bin:$PATH"

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
RUN chmod +x /app/scripts/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]
