@.github/copilot-instructions.md
@.github/instructions/coding.instructions.md
@.github/instructions/api.instructions.md
@.github/instructions/web.instructions.md
@.github/instructions/review.instructions.md

## MANDATORY FIRST ACTION — Read Instructions Before Any File Change

**This is a blocking requirement. You MUST complete the following steps BEFORE making any file change.**

1. Identify every top-level directory you plan to modify (e.g., `api`, `web`).
2. For each directory, use the `view` tool to read `.github/instructions/{directory}.instructions.md` if it exists.
3. Only after reading ALL relevant instruction files, proceed with analysis and changes.

Do NOT make any file change until you have explicitly read the instruction files for every affected directory.
Code changes made without reading instruction files first violate this policy.

## Mandatory Actions by Directory

When modifying files under any top-level directory, if `.github/instructions/{directory}.instructions.md` exists,
you MUST read it and execute ALL mandatory actions defined in it — both before and after making changes.
Do not consider the task complete until every mandatory post-action has been executed.
