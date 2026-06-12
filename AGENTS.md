# Coding Standards

This file defines coding standards for implementation work.

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

## Global Coding Rules

These rules apply to implementation work across this repository, regardless of directory.

### Language Rules for Source Code Comments (REQUIRED)

- **All source code comments MUST be written in English**
- This applies to:
  - Inline comments
  - Block comments
  - File-level comments
  - TODO / FIXME comments
- Do NOT write comments in Japanese or other languages

### Japanese Terminology Standards

For implementation involving Japanese text, ensure terminology is consistent with IPA (Information-technology Promotion Agency) standard terms.
Reference URLs:

- https://www.ipa.go.jp/shiken/kubun/sc.html
- https://www.ipa.go.jp/security/index.html

### Guidelines for Writing Directory Blocks

- **Avoid ambiguous descriptions**: Vague wording causes inconsistent agent behavior. Write instructions that have only one reasonable interpretation.
- **Avoid excessive detail**: Overly granular rules are hard to maintain. Focus on principles and key constraints rather than exhaustive step-by-step procedures.

### Command Safety Policy

Commands are subject to the execution environment's approval rules.
Within those limits, treat these as normal project operations:

- Read-only inspection
- Repository-local file changes
- Project-local format, lint, validation, and test commands
- Starting or stopping Docker Compose services defined in this repository

Do not affect external systems, global configuration, or data outside this repository without explicit approval.

---

## api — Rules for changes under `./api`

This block applies to all changes under `./api`.
Always operate from the repository root.

### Mandatory Actions (Agent)

Whenever code under `./api` is modified, you MUST do the following automatically.

#### 1. Update Tests

If API schemas, models, or data structures change:

- Find affected tests under `api/app/tests/`
- Update them to match changed field names, types, and nullability

#### 2. Run Targeted Verification

Run the smallest useful verification for the change before reporting completion.
Choose commands based on the files and behavior changed:

- Static checks for touched Python modules when practical:

  ```bash
  cd api
  uv run --locked black --check --diff <changed files or ./app>
  uv run --locked ruff check <changed files or ./app>
  uv run --locked mypy <changed files or ./app> --show-error-codes --no-error-summary
  uv run --locked codespell <changed files or ./app>
  ```

- Related tests only, unless the change is broad or high risk:

  Before running API tests:

  - Run Docker Compose commands from the repository root.
  - If `docker-compose-firebase-local.yml` is running, stop it first to avoid port conflicts.
  - Ensure `docker-compose-firebase-test.yml` is running
    (start it if not running; do NOT restart if already running).

  ```bash
  docker compose -f docker-compose-firebase-test.yml exec testapi pytest -s -vv <related test files or directories>
  ```

- In the final response, explicitly list which checks/tests were run. If a relevant check was skipped, state why.

### Frontend Type Definitions (`./web/types`) and OpenAPI

The following files are auto-generated and must not be edited manually: `./web/types` and `./web/openapi.json`.

#### When to regenerate

If any of the following change:

- API endpoint signatures
- API request/response schemas in `./api/app/schemas.py`
- Field names, types, or nullability in API request/response

#### How to regenerate

- Run Docker Compose commands from the repository root.

- If `docker-compose-firebase-test.yml` is running, stop it first to avoid port conflicts.

- Ensure `docker-compose-firebase-local.yml` is running
  (start it if not running; do NOT restart services other than `api` if already running).

- Always restart the `api` service before fetching OpenAPI, so generated files reflect the latest source code:

  ```bash
  docker compose -f docker-compose-firebase-test.yml stop
  docker compose -f docker-compose-firebase-local.yml up -d
  docker compose -f docker-compose-firebase-local.yml restart api
  ```

- Wait for the current API process to be reachable. Do not rely only on old `Application startup complete` logs:

  ```bash
  curl --fail --silent --show-error --output /tmp/openapi-check.json http://localhost/api/internal-api/openapi.json
  ```

- Then always run:

  ```bash
  cd web
  npm run openapi:update
  ```

- After regeneration, verify `web/openapi.json` and `web/types` reflect the intended API schema changes.

### Python Test Standards

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

---

## web — Rules for changes under `./web`

This block applies to all changes under `./web`.
Always operate from the repository root.

### Mandatory Actions (Agent)

Whenever code under `./web` is modified, you MUST do the following automatically.

#### 1. Update / Create Tests

You MUST:

- Identify the affected files
- Create or update tests that cover **only the modified behavior**
- Prefer minimal, focused tests over broad integration tests

Test locations:

- `./web/src/**/__tests__/*`

Use existing testing tools and patterns already used in the project
(e.g. React Testing Library, Jest / Vitest).

#### 2. Run Targeted Verification

Run the smallest useful verification for the change before reporting completion.
Choose commands based on the files and behavior changed:

- Static checks when practical:

  ```bash
  cd ./web
  npm run check
  ```

- Related tests only, unless the change is broad or high risk:

  ```bash
  cd ./web
  npx vitest run <related test files>
  ```

- In the final response, explicitly list which checks/tests were run. If a relevant check was skipped, state why.

### UI and Logic Separation Rule (IMPORTANT)

When modifying or implementing UI components (e.g. React components):

- UI components MUST focus on rendering and user interaction only
- Business logic, data processing, or complex behavior MUST be extracted
  into separate files (e.g. hooks, utilities, or service modules)
- UI components MUST NOT contain substantial business logic
  unless it is strictly presentation-related

### Localization Cleanup Rules (IMPORTANT)

Localization strings are defined under `./web/public/locales`.

- If code changes cause localization keys to become unused, those unused keys SHOULD be deleted
- Deletion MUST be limited to keys that are clearly unreferenced by the codebase
- Do NOT delete localization keys speculatively or preemptively

### External Specification Confirmation Rule (IMPORTANT)

If a requested change depends on external specifications
(e.g. user-visible behavior, UX meaning, or product requirements)
and those specifications are not clearly defined:

- The agent MUST propose the assumed external specification first
- The agent MUST obtain explicit user confirmation before making any code changes
- Until confirmation, the agent MUST NOT modify files or run modifying commands
- If confirmation is not given, the agent MUST stop and ask for clarification

Do NOT infer or assume external behavior without explicit confirmation.

### RTK Query API Definition Rule (IMPORTANT)

When using RTK Query endpoints defined in `./web/src/services/tcApi.ts`:

- Do not specify `url` at the call site.
- Endpoint URLs MUST be defined only inside `tcApi.ts`.
- If a generated API data type requires `url`, define an API-specific request
  parameter type in `tcApi.ts` using `Pick`.
- Prefer the existing request parameter style:

```ts
type ExampleRequestParams = Pick<GeneratedApiDataType, "body" | "path" | "query">;
```

- Do not use generic `Omit<T, "url">` or an equivalent shared helper for these
  request parameter types unless there is a specific reason.
- When converting a call site from JavaScript to TypeScript, if the existing
  endpoint definition in `tcApi.ts` still requires `url` (old style; historical
  examples include `getDependencies` / `useGetDependenciesQuery`), update that
  definition in `tcApi.ts` to the new style using `Pick` (e.g. as done for
  `getInvitationList` / `useGetInvitationListQuery`). Do NOT leave old-style
  definitions in place.
