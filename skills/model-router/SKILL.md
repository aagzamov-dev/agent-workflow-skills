---
name: model-router
description: Choose direct work, lightweight workers, and stronger planning or review according to task complexity and risk, keeping Sol/Sonnet as the usual parent.
---

# Model Router

Use Sol as the usual Codex parent and Sonnet as the usual Claude Code parent. The parent understands the task, decides the route, integrates changes, and checks the result. A skill cannot switch the running parent model; honor explicit model, effort, budget, and delegation choices. Do not change the user's selected model or client settings automatically.

## Choose the smallest useful route

An explicit division of work takes precedence over the defaults below. When the user chooses the current model for decisions and Sol for code, keep planning, explanations and integration decisions with the selected parent. Use a Sol worker for code edits unless the parent is already verified as Sol. If the requested model is unavailable, explain the limitation and ask before substituting. Apply the agreed review policy after implementation.

Classify after a brief inspection of the request and relevant source. Consider uncertainty, coupled behavior, sensitive boundaries, and verification difficulty, not just line or file count. Reassess if the actual changes become substantially larger or riskier.

| Work | Implementation | Final check |
| --- | --- | --- |
| Questions, explanations, routine investigation and planning | Parent directly | Check the answer against evidence; no automatic agents |
| Tiny obvious edit, such as a label or typo | Parent directly; a handoff usually costs more than it saves | Parent checks the diff and relevant behavior |
| Simple bounded task with clear acceptance checks, worth delegating | One lightweight worker: Terra in Codex, Haiku in Claude Code | Parent reviews the actual diff and check results |
| Ordinary fix or feature | Parent directly; one Sol/Sonnet worker only when isolation or a substantial bounded subtask justifies the handoff | Parent reviews the result and runs relevant checks |
| Large or high-risk change | Parent owns planning and implementation, delegating bounded work when useful | One independent Astra/Opus review after implementation and checks |
| Explicit review request, including plain "review" | Parent gathers scope, actual changes, relevant callers, and test evidence first | Astra/Opus reviews that scope, even when small, unless the user explicitly chooses another reviewer or self-review |

Large work has substantial interacting behavior, cross-module contracts, or a change set too complex for a reliable focused parent check. Many mechanical edits alone do not make work high risk. High-risk examples include authentication/authorization, sensitive data, destructive operations, persistence/migrations, signing/updaters, public compatibility, and difficult concurrency or recovery. A one-line change can qualify. Do not reduce review strength merely because the parent is already a strong model or the client is in a different mode; permission and read-only restrictions still apply.

Parent planning is the default at every size. Use Astra/Opus planning only for an unresolved consequential architecture or migration decision that the parent cannot adequately resolve, or when explicitly requested. Size alone does not require a planner. Never invoke Astra, Opus, or Fable for routine planning or tiny edits automatically.

## Keep handoffs economical

- Do not delegate merely to use a cheaper model. Compare the likely work with the cost of preparing, supervising, and reviewing it. Use one implementation owner per overlapping file set; no automatic parallel workers or planner/worker/reviewer chain.
- Read only the relevant provider reference when dispatch is needed: [Codex](references/codex.md) or [Claude Code](references/claude.md).
- Give workers compact isolated context: goal, authorized scope, acceptance checks, constraints, and relevant source locations. Do not fork the full conversation by default. Workers return changes, actual checks, and unresolved issues; they do not dispatch further agents.
- Escalate Terra/Haiku work to Sol/Sonnet when source inspection reveals complexity, sensitive behavior, or failed checks beyond the worker's scope. Report the evidence; avoid repeated blind attempts. Reclassify the final-review requirement if risk grows.
- The parent gathers review evidence rather than performing a second full audit before the reviewer. Supply the actual diff and identified snapshot, relevant callers, requirements, and check results. Separate staged, unstaged, and relevant untracked changes; include the agreed base for branch reviews. Let the reviewer inspect source and expand scope when evidence warrants it.
- Review once per agreed outcome, after implementation, relevant checks, obvious fixes, and any requested installation refresh. Do not treat every file, follow-up, or correction as a new task, or combine unrelated work to evade review. Parent/Sol/Sonnet applies authorized corrections and verifies them, identifying changes since the reviewed snapshot. Another strong review for unresolved consequential uncertainty requires explaining the gap and obtaining approval; an explicit additional-review request supplies it.

## Boundaries and reporting

Routing does not authorize implementation. Apply applicable authorization rules before dispatch, including answering an active question or advice request first and waiting for explicit permission to start or resume proposed implementation when required. While that gate is pending, dispatch no mutations; pause running implementation workers at a safe boundary, collect their state, and resume only after explicit confirmation. Disclose completed or uninterruptible work without rolling it back automatically.

Before meaningful implementation, briefly explain the change, workflow effects, existing-user effects, and tradeoffs. Obtain agreement for undisclosed workflow changes or compatibility breaks. Preserve host permissions, read-only modes, and testing boundaries. A reviewer stays read-only; missing required evidence prevents a readiness claim.

For multi-step work, choose the progress interval at the start. Give one short update every 10% for normal tasks and every 5% for large, multi-stage tasks. Estimate the share of the requested work completed. Each update states the percentage, what finished, and what comes next. If one operation crosses several milestones, report the latest one once. Use the final answer for 100% after verification. Skip percentage updates for quick answers and single-step tasks.

Verify host/model support before dispatch. If an explicitly required model is unavailable, disclose it and ask before substitution. If model selection was delegated to the parent, use a suitable available model and state the substitution. Do not silently downgrade a required strong review to self-review. Report the actual route briefly. This policy is not a hard usage cap or guaranteed saving. Existing sessions must reload it; installed profiles do not change the running parent model.
