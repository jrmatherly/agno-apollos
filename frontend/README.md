# Apollos UI

The frontend for [Apollos AI](../README.md). A chat interface for AgentOS built with Next.js, Tailwind CSS, and TypeScript.

## Features

- **AgentOS Integration**: Connect to local and live AgentOS instances
- **Modern Chat Interface**: Real-time streaming support
- **Tool Calls Support**: Visualizes agent tool calls and results
- **Reasoning Steps**: Displays agent reasoning process (when available)
- **References Support**: Show sources used by the agent
- **Multi-modality Support**: Images, video, and audio content types
- **Customizable UI**: Built with Tailwind CSS and shadcn/ui

## Quick Start

From the project root:

```sh
# Install all dependencies (backend + frontend)
mise run setup

# Start the full stack (backend + frontend + database)
mise run docker:up

# Or start just the frontend dev server
mise run frontend:dev
```

Open [http://localhost:3000](http://localhost:3000) to access the UI.

## Connecting to the Backend

The frontend connects to the backend API via browser-side fetch. The default endpoint is `http://localhost:8000`.

To change the endpoint:

1. Hover over the endpoint URL in the left sidebar
2. Click the edit option to modify the connection settings

### Authentication (Optional)

If your AgentOS instance requires authentication:

**Option 1: Environment Variable**

Set `NEXT_PUBLIC_OS_SECURITY_KEY` in the root `.env` file:

```sh
NEXT_PUBLIC_OS_SECURITY_KEY=your_auth_token_here
```

**Option 2: UI Configuration**

1. In the left sidebar, locate the "Auth Token" section
2. Enter your authentication token
3. The token will be included as a Bearer token in API requests

## Development

| Task | Command |
|------|---------|
| Install deps | `mise run frontend:setup` |
| Dev server | `mise run frontend:dev` |
| Production build | `mise run frontend:build` |
| Lint (ESLint) | `mise run frontend:lint` |
| Format (Prettier) | `mise run frontend:format` |
| Type-check (TypeScript) | `mise run frontend:typecheck` |
| All checks | `mise run frontend:validate` |

## Stack

| Technology | Purpose |
|------------|---------|
| Next.js 15 | App Router, React framework |
| React 18 | UI library |
| TypeScript 5 | Type safety |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library |
| Zustand | State management |
| Framer Motion | Animations |
| pnpm | Package manager |

## License

This project is licensed under the [MIT License](./LICENSE).
