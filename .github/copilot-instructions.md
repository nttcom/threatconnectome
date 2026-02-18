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
