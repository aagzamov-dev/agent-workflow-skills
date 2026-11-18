---
name: code-simplification
description: Write readable code from the first draft and simplify authorized changes while preserving caller-visible behavior. Use for new code, readability refactors, or review of unnecessarily complex code.
---

# Code Simplification

- Read nearby code and follow established conventions. Prefer existing domain names and abstractions that make the changed behavior easier to trace.
- Make the normal path, branches, and side effects visible from the first draft. Use descriptive names and straightforward control flow. Use guard clauses where they clarify preconditions, preserving validation order, error precedence, and cleanup.
- Keep related logic together. Extract a helper when its name conveys a meaningful operation or it removes real duplication. Leave one-use forwarding wrappers and speculative abstractions out. Line count is a poor measure of clarity.
- Use brief comments for a non-obvious invariant, compatibility rule, or reason the order of operations matters. Let names and code explain what each line does.
- For a refactor, trace affected callers and preserve their results, errors, side effects, and meaningful ordering. Run relevant existing checks and report any important behavior you could only inspect. Handle any proposed behavior change through the applicable scope and approval rules.
- Apply the same readability criteria in a review and report findings within the authorized scope.

Adapted from [Addy Osmani's Code Simplification skill](https://github.com/addyosmani/agent-skills/blob/main/skills/code-simplification/SKILL.md), which credits the Claude Code Simplifier plugin. See [MIT notice](LICENSE).
