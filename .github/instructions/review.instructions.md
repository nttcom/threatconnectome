## Code Review Guidelines

When performing a code review:

- Respond in Japanese for all review comments, regardless of the directory or file type being reviewed.
- Go beyond local code improvements and consider the broader architectural intent.
- **Apply `agent.md` / `*.agent.md` rules during review**: For each file being reviewed, locate the nearest `agent.md` or `*.agent.md` (from the file's directory up to the repository root). If the changed code deviates from the policies defined in that file, point it out explicitly.

### General Design Review Principles

For all pull requests:

1. **Understand PR Intent**: Read the PR title, description, and branch name to understand the feature or fix. Identify the user flow or business goal.
2. **Design-Level Suggestions**: If a better architectural approach exists, suggest it proactively. Frame suggestions as alternatives for consideration, not mandates.
3. **Scope Beyond Modified Code**: Check if related files should be updated for consistency. Suggest refactoring opportunities aligned with the PR's goal. If changes indicate incomplete work, ask if follow-up is planned.

### Pytest Code Review Instructions

For Python test files:

1. **Structure Guidelines**:
   - Encourage Given-When-Then comments if they improve readability.
   - However, if the test logic is extremely simple or if applying the Given-When-Then structure feels forced or unnatural, do not mandate it.

2. **Validation of Intent**:
   - If you identify that a test is complex but the sections are missing or mixed up, point this out and provide a refactoring suggestion.
   - Ensure there is appropriate spacing between logic blocks for clarity, even if comments are not used.

### API Code Review Instructions

When reviewing changes to API schemas, endpoints, or data models, ensure consistency across the frontend and compliance with audit logging requirements using the following guidelines:

1. **UI Types Synchronization**:
   - **Validation**: Whenever a backend API schema (e.g., in ` ./api/app/routers`, `./api/app/models.py`, `./api/app/schemas.py`) is modified or added, verify that the corresponding frontend type definitions in `./web/types` are updated accordingly.
   - **Discrepancy Check**: Pay close attention to field names, data types, and nullability. If the backend marks a field as optional but the UI type marks it as required, flag this to prevent potential runtime errors.

2. **Audit Log Implementation (`./api/app/utility/api_logging_middleware.py`)**:
   - **Requirement**: For any API changes involving data creation, modification, or deletion (POST, PUT, PATCH, DELETE), review whether logging logic in `./api/app/utility/api_logging_middleware.py` requires updates or additions.
   - **Validation**: Ensure the logging captures essential context: `http_status`, `method`, `path`, `query_params`, `request_body`, `uid`.

3. **API Design-Level Review**:
   - Beyond schema consistency, consider overall API design: endpoint structure, error handling patterns, versioning strategy, performance implications.
   - If a different approach improves scalability, maintainability, or developer experience, suggest it with reasoning.
   - Check if related API endpoints or data models should be updated for consistency with the PR's goal.

4. **Review Feedback Style**:
   - **Proactive Questioning**: If UI types or audit logs are missing, ask:
     "APIスキーマが更新されていますが、対応するUI用の型定義（types）および監査ログの記録処理が見当たりません。これらを追加する必要がありますか？"
   - If there are no UI updates, display:
     "`npm run openapi:update`実行してください"
   - **Actionable Advice**: Provide specific suggestions for missing types or log structures.
