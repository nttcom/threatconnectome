## Local Web Rule

This rule applies to all changes under `./web`.
This file is located in `./web`.
Always operate from the repository root.

---

## Command Safety Policy

The agent may run the following commands **without user confirmation**:

- Read-only commands and inspection tools

- Commands that modify files **only within this repository**

- Project-scoped `npm` commands executed inside this repository
  for **local formatting, linting, validation, or test execution**, including:
  - `npm run check`
  - `npm run test`
  - `npm test`
  - `npm run format`
  - `npm run lint`
  - `npx vitest`
  - `npx vitest run`

The agent MUST ask for user confirmation before running commands that:

- affect files or systems outside this repository
- install, update, or remove global packages
- change system or environment configuration
- access external services or networks
- delete data outside the repository scope

---

## Mandatory Actions (Agent)

Whenever code under `./web` is modified, you MUST do the following automatically.

---

### 1. Update / Create Tests

You MUST:

- Identify the affected files
- Create or update tests that cover **only the modified behavior**
- Prefer minimal, focused tests over broad integration tests

Test locations:

- `./web/src/**/__tests__/*`

Use existing testing tools and patterns already used in the project
(e.g. React Testing Library, Jest / Vitest).

---

### 2. Run Static Checks

Always execute:

```bash
cd ./web
npm run check
```

This must pass with no errors.

---

### 3. Run Web Tests

Always execute:

```bash
cd ./web
npm run test
```

- All newly added or modified tests must pass

---

## TypeScript Migration Rules (IMPORTANT)

This project is currently **in the middle of migrating from JavaScript to TypeScript**.
The following rules MUST be strictly followed.

### Files You Modify or Add

- All newly created files MUST be written in **TypeScript** (`.ts` / `.tsx`)
- When modifying an existing file:
  - Convert the file to TypeScript **before** making changes
  - Rename `.js` → `.ts`, `.jsx` → `.tsx`
  - Add explicit type definitions whenever reasonably possible

### Files You Do NOT Modify

- Existing files that are unrelated to the change MUST:
  - Remain in JavaScript (`.js` / `.jsx`)
  - NOT be converted to TypeScript unnecessarily

### Prohibited Actions

- Changes made solely for TypeScript migration purposes
- Large-scale or blanket JS → TS conversions
- Adding large numbers of type-only changes that do not affect behavior

TypeScript migration must be done **incrementally and only where changes are required**.

---

## UI and Logic Separation Rule (IMPORTANT)

When modifying or implementing UI components (e.g. React components):

- UI components MUST focus on rendering and user interaction only
- Business logic, data processing, or complex behavior MUST be extracted
  into separate files (e.g. hooks, utilities, or service modules)
- UI components MUST NOT contain substantial business logic
  unless it is strictly presentation-related

---

## Localization Cleanup Rules (IMPORTANT)

Localization strings are defined under `./web/public/locales`.

- If code changes cause localization keys to become unused, those unused keys SHOULD be deleted
- Deletion MUST be limited to keys that are clearly unreferenced by the codebase
- Do NOT delete localization keys speculatively or preemptively

---

## External Specification Confirmation Rule (IMPORTANT)

If a requested change depends on external specifications
(e.g. user-visible behavior, UX meaning, or product requirements)
and those specifications are not clearly defined:

- The agent MUST propose the assumed external specification first
- The agent MUST obtain explicit user confirmation before making any code changes
- Until confirmation, the agent MUST NOT modify files or run modifying commands
- If confirmation is not given, the agent MUST stop and ask for clarification

Do NOT infer or assume external behavior without explicit confirmation.

---
