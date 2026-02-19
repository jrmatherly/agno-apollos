FROM node:24-alpine AS base

# ---------------------------------------------------------------------------
# Install dependencies
# ---------------------------------------------------------------------------
FROM base AS deps

RUN corepack enable pnpm

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ---------------------------------------------------------------------------
# Build the application
# ---------------------------------------------------------------------------
FROM base AS builder

RUN corepack enable pnpm

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN pnpm build

# ---------------------------------------------------------------------------
# Production image
# ---------------------------------------------------------------------------
FROM base AS runner

# ---------------------------------------------------------------------------
# OCI Image Labels
# ---------------------------------------------------------------------------
LABEL org.opencontainers.image.title="Apollos AI Frontend" \
      org.opencontainers.image.description="Apollos AI web interface — Next.js + React" \
      org.opencontainers.image.vendor="Apollos AI" \
      org.opencontainers.image.source="https://github.com/jrmatherly/agno-apollos" \
      org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
