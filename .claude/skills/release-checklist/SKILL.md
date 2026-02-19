---
name: release-checklist
description: Pre-release validation checklist — verify versions, CI, docs, and Docker before running mise run release
disable-model-invocation: true
---

# Release Checklist

Run a pre-release validation to catch issues before `mise run release`.

## Steps

### 1. Version Consistency

Read the current version from these files and confirm they match:
- `pyproject.toml` — `version = "X.Y.Z"`
- `frontend/package.json` — `"version": "X.Y.Z"`

Also confirm `uv.lock` is in sync by running:
```bash
uv lock --check
```

If versions disagree or uv.lock is stale, report which files are out of sync.

### 2. Git State

Verify:
- On `main` branch: `git branch --show-current`
- Working tree is clean: `git status --porcelain`
- Local is up to date with remote: `git fetch origin main && git rev-parse HEAD` vs `git rev-parse origin/main`

Report any issues.

### 3. CI Status

Check the latest CI run on main:
```bash
gh run list --workflow=validate.yml --branch=main --limit=1 --json conclusion,status,headSha,createdAt
```

Report the status. Warn if the latest run is not `success`.

### 4. Docker Build Readiness

Verify key files exist for Docker builds:
- `backend/Dockerfile` exists
- `frontend/Dockerfile` exists
- `frontend/public/.gitkeep` exists (required by frontend Dockerfile COPY)
- `scripts/entrypoint.sh` exists

### 5. Documentation Sync

Spot-check that version references in documentation are not hardcoded to a stale version. Check:
- `README.md` — should not hardcode a specific version number
- `CLAUDE.md` — should not hardcode a specific version number

### 6. Report

Present a summary:

| Check | Status | Details |
|-------|--------|---------|
| Version consistency | pass/fail | ... |
| uv.lock sync | pass/fail | ... |
| Git branch | pass/fail | ... |
| Working tree clean | pass/fail | ... |
| Local up to date | pass/fail | ... |
| CI status | pass/fail | ... |
| Docker files exist | pass/fail | ... |
| Docs version refs | pass/warn | ... |

If all checks pass, tell the user they're ready to run `mise run release`.
If any checks fail, list what needs to be fixed first.
