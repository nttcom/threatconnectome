## Code Review Guidelines

When performing a code review, respond in Japanese.

When performing a code review, if the UI contains Japanese text, verify that the terminology is consistent with IPA (Information-technology Promotion Agency) standard terminology. Reference URLs: https://www.ipa.go.jp/shiken/kubun/sc.html and https://www.ipa.go.jp/security/index.html
If the terminology is consistent with the standard terminology, explicitly state that no issues were found.

### Pytest Code Review Instructions

When reviewing Python test files, encourage the use of the **Given-When-Then** structure with the following guidelines:

1. **Preferred Structure (Given/When/Then)**:
   - Ideally, test functions should be divided into three sections using comments: `# Given`, `# When`, and `# Then`.
   - **# Given**: Setup phase.
   - **# When**: The action being tested.
   - **# Then**: Verification phase.

2. **Flexibility and Suggestions**:
   - If a test lacks these comments, suggest adding them to improve readability.
   - However, if the test logic is extremely simple or if applying the AAA pattern feels forced/unnatural, do not mandate it.

3. **Validation of Intent**:
   - If you identify that a test is complex but the sections are missing or mixed up, point this out and provide a refactoring suggestion.
   - Ensure there is appropriate spacing between logic blocks for clarity, even if comments are not used.

4. **Code Formatting**:
   - Ensure there is a single blank line between the `# Given`, `# When`, and `# Then` sections to improve readability.

5. **Review Language**:
   - Provide review comments in Japanese.

### API Code Review Instructions

When reviewing changes to API schemas, endpoints, or data models, ensure consistency across the frontend and compliance with audit logging requirements using the following guidelines:

1. **UI Types Synchronization**:
   - **Validation**: Whenever a backend API schema (e.g., in `api/app/routers`, `api/app/models.py` , `api/app/schemas.py`) is modified or added, verify that the corresponding frontend type definitions in `web/types` are updated accordingly.
   - **Discrepancy Check**: Pay close attention to field names, data types, and nullability. If the backend marks a field as optional but the UI type marks it as required, flag this to prevent potential runtime errors.

2. **Audit Log Implementation (api/app/utility/api_logging_middleware.py)**:
   - **Requirement**: For any API changes involving data creation, modification, or deletion (POST, PUT, PATCH, DELETE), review whether the logging logic in `api/app/utility/api_logging_middleware.py` requires updates or additions.
   - **Validation**: Ensure that `api/app/utility/api_logging_middleware.py` correctly handles the new/modified API actions to capture essential context: "http_status", "method", "path", "query_params", "request_body", "uid"

3. **Review Feedback Style**:
   - **Proactive Questioning**: If UI types or audit logs are missing, ask: "APIスキーマが更新されていますが、対応するUI用の型定義（types）および監査ログの記録処理が見当たりません。これらを追加する必要がありますか？"
     If there are no UI updates, please display the message: "`npm run openapi:update`実行してください"
   - **Actionable Advice**: Provide specific suggestions for the missing types or log structures to help the developer implement them quickly.

4. **Review Language**:
   - Provide review comments in **Japanese**.
