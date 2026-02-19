---
name: new-mise-task
description: Scaffold a new mise task with correct headers, flags, and conventions
disable-model-invocation: true
---

# New Mise Task

Create a properly structured mise task file.

## Steps

### 1. Gather Details

Ask the user for:
- **Task name** (e.g., "docker/restart", "test", "deploy")
- **Description** (one-line purpose)
- **Flags** (optional, e.g., `--prod`, `--ci`, `--check`)
- **Arguments** (optional, e.g., `[service]`, `[tag]`)
- **Dependencies** (optional, other tasks to run first)

### 2. Determine Path

- Simple tasks: `mise-tasks/{name}`
- Namespaced tasks: `mise-tasks/{namespace}/{name}` (e.g., `mise-tasks/docker/restart`)

### 3. Create Task File

Use this template:

```bash
#!/usr/bin/env bash
#MISE description="{description}"
# Optional headers (include only if needed):
#MISE depends=["{dep1}", "{dep2}"]
#MISE alias="{alias}"
#USAGE flag "--flag-name" help="{flag help text}"
#USAGE option "--option-name <value>" help="{option help text}"
#USAGE arg "[argname]" help="{arg help text}" default="{default}"
set -e

# Task implementation
```

### 4. Conventions

- Always start with `#!/usr/bin/env bash` and `set -e`
- Use `#MISE` for metadata (description, depends, alias)
- Use `#USAGE` for flags, options, and arguments
- Boolean flags: access via `${usage_flagname:-false}`
- Options with values: access via `${usage_optionname:-default}`
- Use `${MISE_PROJECT_ROOT}` for absolute paths
- Interactive prompts must use `read < /dev/tty` and `echo > /dev/tty`
- Make the file executable: `chmod +x mise-tasks/{path}`

### 5. Update mise.toml

Add a comment for the new task in the "Available Tasks" section of `mise.toml`.

### 6. Verify

Run `mise tasks | grep {name}` to confirm mise picks up the new task.
