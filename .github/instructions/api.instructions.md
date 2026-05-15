---
applyTo: "api/**"
---
## Local API Rule

This rule applies to all changes under `./api`.
This file is located in `./api`.
Always operate from the repository root.

---

## Command Safety Policy

The agent may run the following commands without confirmation:

- Read-only commands (e.g. grep, rg, cat, ls)
- Commands that modify files within this repository only
- Commands that start or stop local Docker containers defined in this repository
- Test execution commands (e.g. pytest)

Before running commands that affect anything outside the repository
(e.g. global installs, system changes, external services, data deletion),
the agent MUST ask for user confirmation.

---

## Mandatory Actions (Agent)

Whenever code under `./api` is modified, you MUST do the following automatically.

### 1. Update Tests

If API schemas, models, or data structures change:

- Find affected tests under `api/app/tests/`
- Update them to match changed field names, types, and nullability

### 2. Run Static Checks

Always execute:

```bash
cd api
pipenv run black --check --diff ./app
pipenv run ruff check ./app
pipenv run mypy ./app --show-error-codes --no-error-summary
pipenv run codespell ./app
```

### 3. Run API Tests

- If `docker-compose-firebase-local.yml` is running, stop it before running the tests

- Ensure `docker-compose-firebase-test.yml` is running  
  (start it if not running; do NOT restart if already running)

- Always execute tests:

```bash
docker compose -f docker-compose-firebase-test.yml exec testapi pytest -s -vv app/tests/
```

- Stop the test stack only if you started it

## Frontend Type Definitions (`./web/types`) and OpenAPI

The following files are auto-generated and must not be edited manually: ./web/types and ./openapi.json.

### When to regenerate:

If any of the following change:

- API endpoint signatures
- API request/response schemas in `./api/app/schemas.py`
- Field names, types, or nullability in API request/response

### How to regenerate:

- Ensure `docker-compose-firebase-local.yml` is running  
  (start it if not running; do NOT restart if already running)

- Wait for API to be fully running:

  ```bash
  docker compose -f docker-compose-firebase-local.yml logs api | grep -q "Application startup complete"
  ```

- Under this common condition (API running), always run:

```bash
cd web
npm run openapi:update
```

---

## Python Test Standards

For Python tests under `./api`, follow the Given-When-Then structure where it improves readability.

1. **Preferred Structure (Given/When/Then)**:
   - Divide test functions into three sections with comments: `# Given`, `# When`, and `# Then`.
   - `# Given`: Setup phase.
   - `# When`: The action under test.
   - `# Then`: Verification phase.

2. **Pragmatic Application**:
   - If test logic is very simple, do not force this structure unnaturally.
   - Maintain clear separation between setup, action, and assertion even without comments.

3. **Formatting**:
   - Keep a single blank line between `# Given`, `# When`, and `# Then` blocks.
