# Coding Standards

---

## ⚠️ STOP — MANDATORY FIRST ACTION BEFORE ANY FILE CHANGE ⚠️

**You MUST do this BEFORE writing a single line of code or modifying any file.**
**This is not optional. Skipping this step is a policy violation.**

**Steps (blocking — do not proceed until all are done):**

1. Identify every top-level directory you plan to modify (e.g., `api`, `web`).
2. For each such directory, read the corresponding directory block in THIS file by calling a file-reading tool on `AGENTS.md`. Do NOT rely on pre-injected context alone.
3. In your response, quote the first line of the relevant directory block (e.g., `## api — Rules for changes under ./api`) as proof that you read it.
4. **Explicitly state in your response: "I have read the [X] block of AGENTS.md."** (Replace `[X]` with the actual directory name, e.g., `api`, `web`.)

**If you did not call a file-reading tool on `AGENTS.md`, you MUST immediately STOP, report the violation, and read `AGENTS.md` before proceeding.**
**If you have not quoted the first line of the relevant directory block, you MUST NOT make any file change.**

When modifying files under a top-level directory whose block exists below, you MUST execute ALL mandatory actions defined in that block — both before and after making changes.
Do not consider the task complete until every mandatory post-action has been executed.

---

## Global Rules

- Source code comments, including TODO/FIXME, MUST be English.
- For Japanese text, follow IPA terminology where applicable:
  https://www.ipa.go.jp/shiken/kubun/sc.html / https://www.ipa.go.jp/security/index.html

### Guidelines for Writing Directory Blocks

- **Avoid ambiguous descriptions**: Vague wording causes inconsistent agent behavior. Write instructions that have only one reasonable interpretation.
- **Avoid excessive detail**: Overly granular rules are hard to maintain. Focus on principles and key constraints rather than exhaustive step-by-step procedures.

### Commands

Commands are subject to the execution environment's approval rules.
Within those limits, treat these as normal project operations:

- Read-only inspection
- Repository-local file changes
- Project-local format, lint, validation, and test commands
- Starting or stopping Docker Compose services defined in this repository

Do not affect external systems, global configuration, or data outside this repository without explicit approval.

---

## api — Rules for changes under `./api`

Applies to all changes under `./api`. Work from the repository root.

### Required

- Update affected tests under `api/app/tests/` when schemas, models, or data structures change.
- Run the smallest useful verification and report what ran or why it was skipped.

- Static checks for touched Python modules when practical:

  ```bash
  cd api
  uv run --locked black --check --diff <files or ./app>
  uv run --locked ruff check <files or ./app>
  uv run --locked mypy <files or ./app> --show-error-codes --no-error-summary
  uv run --locked codespell <files or ./app>
  ```

- Related tests only unless broad/high risk. Before API tests, stop local stack if running; run `docker compose -f docker-compose-firebase-test.yml up -d` only if test stack is not already running:

  ```bash
  docker compose -f docker-compose-firebase-local.yml stop
  docker compose -f docker-compose-firebase-test.yml exec testapi pytest -s -vv <related test files or directories>
  ```

### OpenAPI

Do not manually edit generated files: `web/types` or `web/openapi.json`.

Use `npm run openapi:update` by default. Do not regenerate types from a stale `openapi.json`.

If endpoint signatures, request/response schemas, or field names/types/nullability change, regenerate after restarting the current API:

  ```bash
  docker compose -f docker-compose-firebase-test.yml stop
  docker compose -f docker-compose-firebase-local.yml up -d
  docker compose -f docker-compose-firebase-local.yml restart api
  curl --fail --silent --show-error --output /tmp/openapi-check.json http://localhost/api/internal-api/openapi.json
  cd web
  npm run openapi:update
  ```

- Verify generated diffs reflect the intended API change.
- For Python tests, use Given/When/Then comments where they improve readability.

---

## web — Rules for changes under `./web`

Applies to all changes under `./web`. Work from the repository root.

### Required

- Create/update focused tests under `web/src/**/__tests__/*` for changed behavior.
- Run the smallest useful verification and report what ran or why it was skipped.

  ```bash
  cd ./web
  npm run check
  npm run test -- <related test files>
  ```

- Keep UI components focused on rendering/interaction; move business logic to hooks/utilities/services.
- Delete only localization keys under `web/public/locales` that are clearly unused.
- If missing external specs affect implementation choices, confirm the assumed spec before editing.

### RTK Query

When using RTK Query endpoints defined in `./web/src/services/tcApi.ts`:

- Do not specify `url` at the call site.
- Endpoint URLs MUST be defined only inside `tcApi.ts`.
- If a generated API data type requires `url`, define an API-specific request
  parameter type in `tcApi.ts` using `Pick`.
- Use this style:

```ts
type ExampleRequestParams = Pick<GeneratedApiDataType, "body" | "path" | "query">;
```

- Do not use generic `Omit<T, "url">` or equivalent shared helpers.
- When converting JS call sites, update old-style `tcApi.ts` endpoint definitions to this `Pick` style.
