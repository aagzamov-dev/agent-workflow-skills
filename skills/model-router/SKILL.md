---
name: model-router
description: Route implementation, consequential planning, and independent final review. Honor explicit user model choices and keep routine answers on the current model.
---

# Model Router

Classify each request on the current model. Honor explicit model, effort, budget, and delegation choices. A routing decision does not grant implementation authorization. Subagents perform their assigned role and return to the parent.

Apply the question-first gate before dispatch: an active question or request for explanation/advice, including "Explain why this uses cursors, then implement" without a question mark, requires answering first. If proposed or ongoing work is involved, ask permission to proceed and wait for explicit confirmation even when implementation was also requested or previously approved. Purely informational requests with no proposed or ongoing work need only an answer; quoted/code questions and direct fix instructions without a request for explanation/advice do not trigger the gate. Read-only inspection needed to answer is allowed.

While that gate is pending, dispatch no new implementation or mutations; it overrides independent-work and no-repeat-approval guidance. Propagate the pause to running implementing workers using the host's pause/interrupt mechanism at a safe boundary. Collect their state and disclose completed changes and any uninterruptible in-flight work; do not promise instantaneous stoppage or roll back completed work. Resume only after the user's explicit confirmation, with an explicit resume instruction to each worker.

| Task | Route |
| --- | --- |
| Routine question, explanation, or ordinary investigation | Current model |
| Authorized implementation, including small edits, documentation, and configuration | Sol implements in Codex, followed by one independent Astra final review with depth matched to risk. |
| Unresolved consequential architecture or migration decision without an adequate parent plan | Astra plans read-only. Feature size alone does not trigger planning. Use the same implementation and final-review route. |
| Explicit review request | Independent Astra review of the requested scope |

Investigate, prepare, and do routine planning on the current model. When the parent has an adequate plan, use it. Honor explicit requests for Astra planning or review at any task size and dispatch a separate planner if requested. Use Astra for other work only when the user explicitly asks. Claude Code uses the corresponding Sonnet and Opus roles described below.

Before implementation, provide a short explanation of the change, workflow effects, effects on existing users, and tradeoffs. Obtain agreement for a workflow change or compatibility break unless that specific consequence is already approved. Unknown compatibility requires investigation before claiming it is preserved.

Read the relevant provider reference only when dispatching agents.

- For Codex, read [Codex routing](references/codex.md).
- For Claude Code, read [Claude Code routing](references/claude.md).

Pass the goal, acceptance criteria, authorized scope, important constraints, and relevant source locations to each worker. Give reviewers compact isolated context by default, without a full conversation fork: scope, acceptance criteria, constraints, the actual diff and identified snapshot, relevant caller locations, and test evidence. Allow source inspection and evidence-led scope expansion. Ask planners for decisions, tradeoffs, and verification criteria rather than exhaustive implementation scripts. Parent agents remain responsible for integrating the result.

Use one implementation owner per overlapping set of files. A task is the agreed outcome, not each file, edit, check, installation, commit, or follow-up; do not group unrelated work to evade review. Finish implementation, relevant tests, obvious fixes, and any requested configuration or installation refresh before the single independent final review, even when the parent already uses Astra. Keep reviewers read-only; request concise findings with depth matched to risk, without finding quotas or an exhaustive audit for tiny changes. Do not spawn recursive chains of planners or reviewers.

After review, the parent/Sol fixes authorized findings and verifies the affected behavior, clearly distinguishing the reviewed snapshot from subsequent corrections. Do not automatically repeat a full review for corrections or routine checks, installation, commits, or follow-ups within the same task. If consequential uncertainty remains and another Astra pass is needed, explain the evidence gap and obtain user approval first; a user-requested additional review supplies that approval. Do not claim readiness while required evidence is missing.

Model delegation requires actual host support and available models. If a requested model or agent is unavailable, disclose it and ask before substituting an explicitly required model. If selection was delegated to you, use an available suitable model and state the substitution. Never claim a routing change without an actual dispatch result. A skill cannot replace the parent model for the running turn.

Report the route used and important findings briefly. These workflow controls are not a hard token cap or guaranteed savings. Evaluate observed corrections, time, and usage; do not promise success on the first attempt.

## Progress updates

For Codex and Claude Code, choose the progress interval at the start. Use 10% milestones of completed scope for normal tasks and 5% milestones for large, multi-stage tasks. Give brief done/next updates, such as "40% - permission checks complete. Checking failure handling next." Percentages are rough estimates of completed scope, not elapsed time, ETAs, or precise measurements. Explain revised estimates when scope changes.

The parent owns one overall percentage in the user chat. Workers report actual milestones to the parent without competing percentages. When several milestones happen together, including on quick tasks, report only the latest reached milestone instead of inventing intermediate messages or activity. Do not report 100% until all requested work, including implementation, review, tests, and publication where requested, is actually complete. Disclose anything blocked or unfinished.
