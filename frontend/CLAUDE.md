# Frontend — Next.js Conventions

Frontend-specific patterns for `frontend/`. See root `CLAUDE.md` for project-wide conventions.

## Stack

Next.js 15 (App Router), React 18, TypeScript, pnpm, Tailwind CSS, shadcn/ui.
Uses `output: 'standalone'` in `next.config.ts` — required for the multi-stage Docker build.

## Key Files

- `frontend/src/store.ts` — Zustand state store; default API endpoint: `http://localhost:8000`
- `frontend/src/api/` — Browser-side API client (fetch with Bearer token auth)
- `frontend/src/components/` — UI components
- `frontend/src/app/` — Next.js App Router pages and layouts

## Conventions

- **Package manager: pnpm** — never use npm or yarn
- After changing `package.json`, run `mise run frontend:setup` to regenerate `pnpm-lock.yaml`
- Use `--ci` flag (`mise run frontend:setup --ci`) for locked/frozen installs in CI
- **API calls are browser-side (client fetch)** — the backend URL is configured in the UI store (`store.ts`), not via environment variables. Do not add server-side API calls or move the URL to env vars.
- For dev iteration: prefer `mise run frontend:dev` over `mise run dev` — compose watch triggers a full container rebuild on any source change (standalone output can't hot-reload synced files)

## Environment Variables

These are build-time `NEXT_PUBLIC_*` vars — baked into the static bundle:

- `NEXT_PUBLIC_DEFAULT_ENDPOINT` — default backend URL shown in the UI (default: `http://localhost:8000`)
- `NEXT_PUBLIC_OS_SECURITY_KEY` — optional: pre-fills the auth token field in the frontend UI

### MSAL / Entra ID (build-time, optional)

- `NEXT_PUBLIC_AZURE_CLIENT_ID` — Entra ID application (client) ID; empty = MSAL disabled
- `NEXT_PUBLIC_AZURE_TENANT_ID` — Entra ID tenant ID
- `NEXT_PUBLIC_REDIRECT_URI` — MSAL redirect URI after login (default: `http://localhost:3000`)

These must be passed as `build.args` in docker-compose **and** declared as `ARG`/`ENV` in `frontend/Dockerfile`. Setting only `environment:` is not sufficient — Next.js bakes them at build time, not runtime.

## Auth Integration (MSAL.js v5)

- `src/auth/` — MSAL integration package
- When `NEXT_PUBLIC_AZURE_CLIENT_ID` is set (build-time), `AuthProvider` wraps the app with `MsalProvider`
- `useTokenSync()` syncs MSAL access token into Zustand `authToken` every 5 minutes
- All API calls in `src/api/os.ts` already inject `authToken` as `Authorization: Bearer`
- `AuthUserButton.tsx` replaces `AuthToken.tsx` in the sidebar when MSAL is configured
- For local dev without Entra ID: keep `NEXT_PUBLIC_AZURE_CLIENT_ID` empty — falls back to manual token entry

## Forms

- No shadcn `input.tsx` component — use native `<input>` with Tailwind classes (see `settings/integrations/page.tsx` and `settings/m365/page.tsx` for patterns)
- Always associate `<label htmlFor="id">` with `<input id="id">` for accessibility
- Mirror backend Pydantic field constraints as HTML5 attributes (`pattern`, `maxLength`, `title`) on form inputs
