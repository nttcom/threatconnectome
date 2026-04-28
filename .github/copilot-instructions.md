## Coding Standards

This file defines coding standards for implementation work.

Code review guidance has been separated into:

- `.github/instructions/review.instructions.md`

### Python Test Standards

For Python tests, follow the Given-When-Then structure where it improves readability.

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
