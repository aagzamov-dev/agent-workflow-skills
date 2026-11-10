---
name: engineering-review
description: Review software changes, diagnose bugs with evidence, and assess regressions, lifecycle failures, permissions, feature flags, performance, and test coverage. Use for requested code reviews, difficult bug investigations, and the final review of substantial implementation work. Scale to the changed behavior; do not turn routine edits into whole-project audits or edit during a review-only request.
---

# Engineering Review

Produce focused changes and findings that another engineer can verify. Match the user's requested scope and distinguish implementation progress from proven behavior.

## Establish scope and evidence

- Read applicable project instructions and inspect the working tree before edits. Distinguish pre-existing changes from your own; review their interactions without claiming authorship or rewriting unrelated work.
- Translate feature references such as "like Telegram" into concrete acceptance criteria. Infer routine details; clarify only ambiguities that materially affect the result. Do not silently claim feature parity.
- Trace a reported symptom across the actual contract, state, and presentation boundaries. Separate confirmed causes, plausible explanations, and missing evidence. A sidebar preview, successful request, or visible placeholder alone does not prove the complete flow works.
- Identify the executing platform, build preset, feature configuration, and source/binary relationship. A WSL mock or Linux decoder check does not establish behavior in a Windows application.
- For interface changes, examine loading and error states, accessibility, narrow layouts, translations, and interaction feedback. Identify useful architecture and user experience decisions worth preserving.

## Implement within the authorized scope

- Prefer the smallest coherent fix and the existing architecture, components, icon assets, tokens, upload paths, and shared services.
- Preserve permission checks and remote disable controls. Trace their values from source to consumer, including defaults and absent fields. Check disabled states as well as enabled states; adding a new surface must not bypass an existing policy.
- Keep risky recovery, persistence, migration, and unrelated fixes separately reviewable. Do not expand a UI task into cache or message-wiping changes on an unconfirmed hypothesis. If the evidence requires both, explain their relationship and validate both.
- For asynchronous work, check identity, ownership, cancellation, stale callbacks, and replacement. Verify relevant transitions such as navigation, lock, logout, deletion, failure, retry, and shutdown. Avoid per-item players, timers, or subscriptions when a shared service fits.
- For Qt/QML work, consider GUI-thread blocking, QObject and QIODevice lifetimes, signal reentrancy, pooled delegates, and source ownership. Check the composed screen at supported minimum sizes as well as isolated components.
- Leave additional audit findings unchanged when the user requested a report before fixes. Continue authorized work without repeated permission questions.

## Verify efficiently

- Start with targeted repository searches and the established build/test commands. Batch independent reads; broaden investigation only when new evidence requires it. Avoid installing a large toolchain solely to simulate the wrong target platform.
- Prefer a regression test that fails for the original behavior. Test public behavior and important failure or policy transitions rather than implementation-shaped assertions.
- Use the actual application only when live testing is explicitly authorized for this task; otherwise use appropriate authorized non-live checks. Label source inspection, mocks, component tests, decoder tests, builds, and target-platform checks separately. Added tests are not passed tests until executed.
- For requested optimization, examine UI-thread work, decode sizes, eager object creation, repeated settings writes, unbounded queues, and duplicated network work where relevant. Label unmeasured hotspots as risks; reserve performance improvement claims for measurements.
- Once relevant checks pass, inspect the final diff for regressions, debug output, accidental configuration changes, missing requirements, and unnecessary complexity. Repeat tests only when changes or unresolved concerns justify it.

## Report conclusions precisely

- In a review, give a brief readiness verdict and actionable findings ordered by impact. Include a file/line reference, a realistic trigger, the observed or expected failure, and the evidence supporting it. Separate confirmed defects, possible risks, and product limitations. Do not invent issues or assign a numeric quality score unless asked.
- After implementation, state what changed, what was actually verified, what remains unverified, and material risks. Say "implemented" or "candidate fix" when the reported failure has not been reproduced and checked; do not imply merge readiness or target-platform success.
- If an environment prevents required verification, complete the useful authorized work, name the specific limitation, and give the concrete next check. Do not hide the gap behind a successful mock or a list of unrelated passing checks.

## Check disclosed impact and existing users

- Compare actual consequences with the explanation given before implementation. Identify undisclosed changes to established commands, release steps, prerequisites, existing data, settings, and old-client update paths. Treat new installation and existing-user upgrades as separate workflows.
- Verify that workflow changes and compatibility breaks have the user's agreement. Feature approval alone does not authorize an undisclosed consequence. Report missing approval before the affected implementation proceeds.
- Inspect staged, unstaged, and relevant untracked changes separately. For branch reviews, establish the agreed base and inspect the full branch diff. Record which snapshot was reviewed; later edits require checking affected findings again.
- Keep review findings brief and evidence-based. Include severity, file/line evidence, trigger, user consequence, and a practical correction. Separate confirmed defects, suspected risks, missing evidence, and optional improvements.
- For follow-up review, check corrections and affected behavior, expanding scope only when new evidence warrants it. Review verdicts authorize no commit, deployment, or unrelated fix.
