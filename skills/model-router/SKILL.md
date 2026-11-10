---
name: model-router
description: Route each request to the appropriate model for implementation, large-task planning, or independent review. Honor explicit user model choices and keep routine answers on the current model.
---

# Model Router

Classify each request on the current model. Honor explicit model, effort, budget, and delegation choices. A routing decision does not grant implementation authorization. Subagents perform their assigned role and return to the parent.

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
