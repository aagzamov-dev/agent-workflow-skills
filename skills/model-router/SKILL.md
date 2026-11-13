---
name: model-router
description: Route each request to the appropriate model for implementation, large-task planning, or independent review. Honor explicit user model choices and keep routine answers on the current model.
---

# Model Router

Classify each request on the current model. Honor explicit model, effort, budget, and delegation choices. A routing decision does not grant implementation authorization. Subagents perform their assigned role and return to the parent.

Apply the question-first gate before dispatch: an active question or request for explanation/advice, including "Explain why this uses cursors, then implement" without a question mark, requires answering first. If proposed or ongoing work is involved, ask permission to proceed and wait for explicit confirmation even when implementation was also requested or previously approved. Purely informational requests with no proposed or ongoing work need only an answer; quoted/code questions and direct fix instructions without a request for explanation/advice do not trigger the gate. Read-only inspection needed to answer is allowed.

While that gate is pending, dispatch no new implementation or mutations; it overrides independent-work and no-repeat-approval guidance. Propagate the pause to running implementing workers using the host's pause/interrupt mechanism at a safe boundary. Collect their state and disclose completed changes and any uninterruptible in-flight work; do not promise instantaneous stoppage or roll back completed work. Resume only after the user's explicit confirmation, with an explicit resume instruction to each worker.

| Task | Route |
| --- | --- |
| Routine question, explanation, or ordinary investigation | Current model |
| Authorized implementation, including small edits and documentation changes | Sol implements in Codex. An independent Astra reviewer checks the final implementation. |
| Large implementation with a multi-module architectural decision, complex migration, or ambiguous multi-stage design | Astra plans first when the parent has not already produced a strong inline plan. Use the same implementation and review route. |
| Explicit review request | Independent Astra review of the requested scope |

Do routine planning on the current model. When the parent is already the selected strong planner, plan inline. Honor explicit requests for Astra planning at any task size and dispatch a separate planner if the user requests one. Use Astra for other work only when the user explicitly asks. Claude Code uses the corresponding Sonnet and Opus roles described below.

Before implementation, provide a short explanation of the change, workflow effects, effects on existing users, and tradeoffs. Obtain agreement for a workflow change or compatibility break unless that specific consequence is already approved. Unknown compatibility requires investigation before claiming it is preserved.

Read the relevant provider reference only when dispatching agents.

- For Codex, read [Codex routing](references/codex.md).
- For Claude Code, read [Claude Code routing](references/claude.md).

Pass the goal, acceptance criteria, authorized scope, important constraints, and relevant source locations to each worker. Provide reviewers access to actual changes, relevant callers, and test evidence. Ask planners for decisions, tradeoffs, and verification criteria rather than exhaustive implementation scripts. Parent agents remain responsible for integrating the result.

Use one implementation owner per overlapping set of files. The parent sends the final implementation to one independent reviewer even when the parent already uses Astra. After fixes, recheck the specific findings and affected behavior. Keep each reviewer read-only and return findings to the parent for integration. Do not spawn recursive chains of planners or reviewers.

Model delegation requires actual host support and available models. If a requested model or agent is unavailable, disclose it and ask before substituting an explicitly required model. If selection was delegated to you, use an available suitable model and state the substitution. Never claim a routing change without an actual dispatch result. A skill cannot replace the parent model for the running turn.

Report the route used and important findings briefly. Evaluate the policy using observed corrections, time, and usage. Do not promise a fixed allowance saving or success on the first attempt.

## Progress updates

For Codex and Claude Code, choose the progress interval at the start. Use 10% milestones of completed scope for normal tasks and 5% milestones for large, multi-stage tasks. Give brief done/next updates, such as "40% - permission checks complete. Checking failure handling next." Percentages are rough estimates of completed scope, not elapsed time, ETAs, or precise measurements. Explain revised estimates when scope changes.

The parent owns one overall percentage in the user chat. Workers report actual milestones to the parent without competing percentages. When several milestones happen together, including on quick tasks, report only the latest reached milestone instead of inventing intermediate messages or activity. Do not report 100% until all requested work, including implementation, review, tests, and publication where requested, is actually complete. Disclose anything blocked or unfinished.
