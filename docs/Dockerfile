FROM node:24-alpine

# ---------------------------------------------------------------------------
# OCI Image Labels
# ---------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Apollos AI Documentation" \
      org.opencontainers.image.description="Apollos AI documentation site — Mintlify" \
      org.opencontainers.image.vendor="Apollos AI" \
      org.opencontainers.image.source="https://github.com/jrmatherly/agno-apollos" \
      org.opencontainers.image.licenses="Apache-2.0"

# ---------------------------------------------------------------------------
# Install Mintlify CLI and serve documentation
# ---------------------------------------------------------------------------
# Uses mint dev as the serving mechanism. The Mintlify CLI is built on
# Next.js internally, so HOSTNAME=0.0.0.0 binds to all interfaces.

WORKDIR /app

RUN npm install -g mint@latest

# Copy documentation content
COPY . .

# Non-root user
RUN addgroup --system --gid 1001 mintlify && \
    adduser --system --uid 1001 mintuser && \
    chown -R mintuser:mintlify /app

USER mintuser

EXPOSE 3333

ENV HOSTNAME="0.0.0.0"

CMD ["mint", "dev", "--port", "3333"]
