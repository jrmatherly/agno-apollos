---
name: validate-all
description: Run full-stack validation (backend + frontend) and report issues with suggested fixes
disable-model-invocation: true
---

# Full-Stack Validation

Run all code quality checks and report results.

## Steps

### 1. Run Validation

Execute `mise run validate` which runs:
- **Backend**: ruff format check, ruff lint, mypy type-check
- **Frontend**: eslint, prettier format check, typescript type-check

### 2. Parse Results

If validation passes, confirm success and stop.

If validation fails, parse the output and organize issues by category:
- **Format errors**: Files that need formatting
- **Lint errors**: Code quality issues with rule IDs
- **Type errors**: Type-check failures with file:line references

### 3. Report

Present a summary table:

| Category | Count | Status |
|----------|-------|--------|
| Backend format | N | pass/fail |
| Backend lint | N | pass/fail |
| Backend types | N | pass/fail |
| Frontend lint | N | pass/fail |
| Frontend format | N | pass/fail |
| Frontend types | N | pass/fail |

### 4. Offer Fixes

For each failing category, offer to fix:
- **Format**: Run `mise run format` (backend) or `mise run frontend:format` with `--fix` flag
- **Lint**: Apply auto-fixes where possible via ruff/eslint `--fix`
- **Types**: Show specific errors and suggest code changes

Ask the user which categories to fix before proceeding.
