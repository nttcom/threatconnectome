## Code Review Guidelines

When performing a code review, respond in Japanese.

### Pytest Code Review Instructions

1. **Flexibility and Suggestions**:
   - If a test lacks Given-When-Then comments, suggest adding them to improve readability.
   - However, if the test logic is extremely simple or if applying the AAA pattern feels forced or unnatural, do not mandate it.

2. **Validation of Intent**:
   - If you identify that a test is complex but the sections are missing or mixed up, point this out and provide a refactoring suggestion.
   - Ensure there is appropriate spacing between logic blocks for clarity, even if comments are not used.

3. **Review Language**:
   - Provide review comments in Japanese.

### API Code Review Instructions

When reviewing changes to API schemas, endpoints, or data models, ensure consistency across the frontend and compliance with audit logging requirements using the following guidelines:

1. **UI Types Synchronization**:
   - **Validation**: Whenever a backend API schema (e.g., in `api/app/routers`, `api/app/models.py`, `api/app/schemas.py`) is modified or added, verify that the corresponding frontend type definitions in `web/types` are updated accordingly.
   - **Discrepancy Check**: Pay close attention to field names, data types, and nullability. If the backend marks a field as optional but the UI type marks it as required, flag this to prevent potential runtime errors.

2. **Audit Log Implementation (`api/app/utility/api_logging_middleware.py`)**:
   - **Requirement**: For any API changes involving data creation, modification, or deletion (POST, PUT, PATCH, DELETE), review whether logging logic in `api/app/utility/api_logging_middleware.py` requires updates or additions.
   - **Validation**: Ensure the logging captures essential context: `http_status`, `method`, `path`, `query_params`, `request_body`, `uid`.

3. **Review Feedback Style**:
   - **Proactive Questioning**: If UI types or audit logs are missing, ask:
     "APIスキーマが更新されていますが、対応するUI用の型定義（types）および監査ログの記録処理が見当たりません。これらを追加する必要がありますか？"
   - If there are no UI updates, display:
     "`npm run openapi:update`実行してください"
   - **Actionable Advice**: Provide specific suggestions for missing types or log structures.

4. **Review Language**:
   - Provide review comments in **Japanese**.
