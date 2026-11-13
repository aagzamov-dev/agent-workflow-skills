---
name: change-impact
description: Establish implementation intent, clarify consequential requirements, and explain the smallest sufficient approach and its downsides before meaningful software changes. Obtain agreement for changes to established workflows or compatibility. Use before features, fixes, migrations, packaging, and release changes; discussing a possible change does not authorize implementation.
---

# Change Impact

Help the user choose knowingly before consequential work. Be concise for small changes; give enough detail when a decision affects users, data, security, or ongoing cost.

## 1. Confirm intent and consequential requirements

- Apply these guidelines within the instruction hierarchy and host permissions. If applicable authorization instructions materially conflict and the current request does not resolve them, ask before the affected action. Determine whether the user wants advice, investigation, review, or implementation. Discussion does not authorize implementation; if intent is ambiguous, ask before changing files.
- When the user asks an active question or requests explanation/advice, answer first. This includes imperative wording such as "Explain why this uses cursors, then implement," even without a question mark. If proposed or ongoing work is involved, ask whether you may proceed and wait for explicit permission before starting or resuming actions, even if the same message also says to implement or earlier permission exists. Read-only inspection needed to answer is allowed. Purely informational requests with no proposed or ongoing work need only an answer. Quoted examples, code, and literal question marks do not trigger this gate by themselves; a direct fix instruction without a request for explanation/advice does not trigger it.
- A pending question-first pause takes precedence over all independent-work and no-repeat-approval guidance. Dispatch no new implementation or mutations while waiting. If implementing workers are running, propagate the pause using the host's pause/interrupt mechanism at a safe boundary; collect their current state and disclose completed changes and any uninterruptible in-flight work. Do not promise instant stoppage or roll back completed work. Resume workers only after the user's explicit confirmation.
- Inspect applicable instructions, relevant code, callers, tests, configuration, and current behavior before asking for facts already established by the project.
- If the desired outcome or a consequential business rule remains unclear, stop work that depends on it and ask a focused question. Explain the alternatives, why the answer changes the result, and your recommendation when supported. Do not silently invent ownership/access rules, what data must survive, deletion/retention semantics, failure behavior, supported platforms, or compatibility requirements.
- While clarification is pending, continue independent authorized work only when you are not awaiting permission to resume after an active question. Make routine choices autonomously when requirements and project conventions establish them. Earlier approval covers its exact scope until a new active question requires the question-first pause; silence or agreement with an explanation does not itself authorize implementation or resumption.

| Request or context | Response |
| --- | --- |
| "Would offline mode help?" | Explain benefits, synchronization conflicts, and maintenance costs; do not implement it. |
| "Add automatic cleanup," with retention rules still unclear after inspection | Ask what may be deleted and when before implementing deletion. |
| "Implement the agreed pagination. Why this approach?" | Answer the question, ask whether you may proceed with implementation, and wait for explicit permission. |
| "Explain why this uses cursors, then implement." | Explain first, ask whether you may proceed, and wait for explicit permission. |

## 2. Explain the approach and meaningful downsides

Before meaningful edits, describe the intended outcome and the smallest design that fully meets agreed requirements, protects existing behavior, and handles realistic failure and growth. Reuse established boundaries and services. Justify added abstractions, dependencies, services, configuration, caches, or retries with concrete benefits that outweigh their complexity and operational cost. Do not build for hypothetical scale or remove required safeguards to make a solution look simple.

Normally use no more than four short bullets covering:

- The planned change, its purpose, and the simplest sufficient approach.
- Effects on the user's commands, workflow, prerequisites, and public interfaces.
- Effects on existing users, data, settings, and supported upgrade/recovery paths.
- Meaningful disadvantages or uncertainties the user may not anticipate, and a simpler alternative when it changes the decision.

Include relevant maintenance, operational cost, performance, privacy/security, migration, or recovery consequences. State what becomes harder, behaves differently, stops working, or requires a prerequisite. Distinguish established consequences from plausible risks; do not manufacture drawbacks for trivial edits. One sentence is enough for a small change. Expand when the user needs more information to decide, and avoid claiming compatibility from source inspection alone.

## 3. Resolve decisions before dependent changes

Ask for explicit agreement before changing an established workflow or breaking compatibility. Explain the concrete consequence and the smallest compatible option. Feature approval alone does not authorize an undisclosed consequence. Also resolve unclear consequential requirements and obtain authorization for scope expansions before acting on them. Do not add another approval gate for routine implementation already covered by the user's instructions, except when an active question requires permission to resume.

Treat clean installation and upgrades from supported versions separately. For example, offline installation may still need to preserve older clients' update artifacts, endpoints, formats, signing, and version rules. A successful clean installation does not establish upgrade compatibility.

If implementation reveals a new material consequence, explain it and resolve the necessary decision before the affected change. Continue only independent authorized work while awaiting the answer, unless the question-first pause is awaiting permission to resume. Review the final implementation against the disclosed consequences and verify both existing-user and new-user behavior where relevant.

Finish briefly with what changed, any action required from the user, what was actually verified, and remaining uncertainty. Never hide a meaningful downside or compatibility gap to meet a length target.
