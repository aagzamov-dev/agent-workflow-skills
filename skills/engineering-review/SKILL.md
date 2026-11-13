---
name: engineering-review
description: Review software changes and investigate difficult bugs using concrete evidence, risk-based depth, and practical design judgment. Assess correctness, security, lifecycle, compatibility, user experience, realistic scaling, and unnecessary complexity. Use for requested reviews, difficult investigations, and final review of substantial implementation; review alone does not authorize edits.
---

# Engineering Review

Assess the actual user workflow and recommend the smallest sufficient corrections. Choose the smallest design that meets agreed requirements, protects existing behavior, and handles realistic failure and growth. Broad consideration does not require a whole-project audit or a long report.

## 1. Establish intent, scope, and evidence

- Apply these guidelines within the instruction hierarchy and host permissions. If applicable authorization instructions materially conflict and the current request does not resolve them, ask before the affected action. Determine whether the user wants advice, investigation, review, or implementation. Advice and review do not authorize fixes; if intent is ambiguous, ask before editing.
- When the user asks an active question or requests explanation/advice, answer first, including imperative wording such as "Explain why this uses cursors, then implement" without a question mark. If proposed or ongoing work is involved, ask whether you may proceed and wait for explicit permission before starting or resuming actions, even if the same message also says to implement or earlier permission exists. Read-only inspection needed to answer is allowed. Purely informational requests with no proposed or ongoing work need only an answer. Quoted examples, code, and literal question marks do not trigger this gate by themselves; a direct fix instruction without a request for explanation/advice does not trigger it. Earlier approval otherwise remains valid for its exact scope.
- A pending question-first pause overrides independent-work and no-repeat-approval guidance. Dispatch no new implementation or mutations. Propagate the pause to running implementing workers through the host's pause/interrupt mechanism at a safe boundary, collect their state, and disclose completed changes and any uninterruptible in-flight work. Do not promise instant stoppage or roll back completed work. Resume workers only after the user's explicit confirmation.
- Read applicable project instructions and module documentation. Inspect the working tree; distinguish pre-existing work from your own. For branch reviews, establish the agreed base and inspect the full branch diff. Inspect staged, unstaged, and relevant untracked changes separately; an unstaged fix must not make an unsafe staged snapshot appear safe. Record the reviewed snapshot and dependencies between change sets.
- Establish intended behavior and acceptance criteria from the request, relevant code, callers, and tests. Translate references such as "like Telegram" into concrete interactions; do not assume full feature parity. Inspect evidence before asking the user to explain project facts.
- If a consequential requirement or business rule remains unclear, pause work that depends on it and ask a focused question. Explain the alternatives and why the answer matters; recommend an option when supported. Do not invent access rules, deletion/retention semantics, failure behavior, or compatibility requirements. Continue independent authorized work only when you are not awaiting permission to resume after an active question; routine choices established by project conventions otherwise do not need approval.
- Identify the executing platform, build preset, feature configuration, and source/binary relationship. A WSL mock or Linux decoder check does not establish behavior in a Windows application.

## 2. Choose depth from risk and trace behavior

Start from the changed workflow and follow affected callers, contracts, state, and dependencies. Spend more effort where failure could expose data, corrupt state, break existing users, or recur under concurrency. A small diff crossing a sensitive boundary may need deep investigation. Expand scope when evidence reveals a dependency or shared failure, rather than to complete a universal checklist.

Apply the relevant checks:

- **Security and policy:** trace authentication, authorization, ownership/tenant isolation, validation, and sensitive-data handling across the boundary. Trace permissions, feature flags, remote disable controls, defaults, and absent fields from source to consumer. Check both enabled and disabled states; a new surface must not bypass existing policy.
- **State and lifecycle:** trace identity, ownership, cancellation, stale callbacks, replacement, and cleanup. Examine relevant navigation, lock, logout, deletion, failure, retry, reconnect, and shutdown transitions. Check concurrency and partial failure; request success does not prove the complete flow.
- **Data and compatibility:** examine persistence, recovery, migrations, public interfaces, settings, and supported old-client paths. Treat clean installation and existing-user upgrades separately. Compare actual consequences with disclosed impact and approved workflow/compatibility changes; flag undisclosed consequences. Keep risky recovery or unrelated changes separately reviewable.
- **User experience:** examine the composed screen as well as isolated components, including supported minimum sizes, accessibility, translations, visual consistency, loading/error states, and interaction feedback. A placeholder or sidebar preview does not prove the underlying feature works.
- **Platform-specific behavior:** use the affected platform's constraints. For Qt/QML, examine GUI-thread blocking, QObject/QIODevice lifetimes, signal reentrancy, pooled delegates, and source ownership.

## 3. Judge design, scaling, and maintenance

- Evaluate responsibility boundaries, data ownership, coupling, and the cost of likely changes. Preserve working architecture, shared services, components, icons, tokens, and existing paths where they fit. Name good decisions worth keeping with evidence.
- Ask whether each new abstraction, dependency, service, configuration option, cache, or retry earns its implementation and operational cost through a concrete requirement or demonstrated benefit. Prefer removing needless layers over proposing a rewrite. Simplicity still includes necessary security, recovery, failure handling, and acceptance criteria.
- Assess realistic workload and resource bounds where relevant: query patterns, pagination, repeated network work, decode sizes, eager objects, repeated settings writes, blocking work, queue growth, concurrency, and resource ownership. Consider whether per-item timers, players, or subscriptions create avoidable work compared with an existing shared service.
- Separate demonstrated bottlenecks, plausible risks requiring measurement, and hypothetical future limits. Do not invent traffic targets or recommend distributed infrastructure merely because growth is possible. For example, a proposed cache needs a concrete benefit weighed against invalidation, consistency, and operational costs; unmeasured latency alone does not prove a cache is needed.
- Think long term through plausible tasks: diagnosing a failure, changing a business rule, evolving stored data or interfaces, and replacing a dependency. Preserve inexpensive boundaries that help these tasks. Defer speculative extension points; state a concrete trigger for revisiting a deferred decision when useful.
- Explain recommendations through practical consequences. "Violates SOLID" or "will not scale" is insufficient without a realistic failure or maintenance cost. Architectural preferences and optional improvements are not blockers by themselves.

## 4. Challenge findings and verify efficiently

- Before reporting a defect, trace a realistic trigger and inspect guards, callers, configuration, and tests that could disprove it. Explain the failure mechanism and affected user. A missing test alone does not establish a defect; a clear source-proven failure need not be reproduced to be reported.
- Start with targeted repository searches and established checks. Batch independent reads; broaden only when evidence requires it. Do not install a large toolchain merely to simulate the wrong platform.
- Prefer verification of public behavior and important failure/policy transitions. A regression test should fail for the original behavior. Do not add implementation-shaped assertions or unnecessary tests for low-impact edits. Review alone does not authorize creating tests or changing files.
- Use live applications, browsers, UI automation, or real environments only with applicable explicit authorization. Otherwise use authorized non-live checks. Distinguish source inspection, mocks, component/decoder tests, builds, and actual target-platform verification. Added tests are not passed tests until executed; performance gains require measurements.
- Inspect the final diff for regressions, debug output, accidental configuration changes, missing requirements, and unnecessary complexity. Repeat checks only after relevant changes, failures, or unresolved concerns. On follow-up, recheck corrections and affected behavior, expanding only when new evidence warrants it.

## 5. Report actionable conclusions

- Lead with readiness within the verified scope: ready, not ready, or insufficient evidence. Order findings by realistic impact and likelihood. Separate confirmed defects, suspected risks, missing requirements/evidence, and optional improvements; do not invent findings to fill categories.
- For each defect, give severity, file/line evidence, trigger, failure mechanism, user impact, and the smallest sufficient correction. Explain a correction's material tradeoff. Reserve blockers for concrete consequences; label unmeasured performance concerns as risks.
- Briefly state what was checked, what remains unverified, and the specific next check needed. Do not hide gaps behind unrelated passing tests or imply target-platform success from source inspection. For implementation follow-up, distinguish implemented behavior or a candidate fix from reproduced and verified behavior.
- Recommend what to keep, fix, remove, or simplify where useful. Give a numeric score only when asked, separating engineering quality from completeness against requirements. Leave unrelated findings unchanged unless fixing them is authorized.
- Review verdicts grant no permission to edit, commit, deploy, or change scope. Preserve applicable repository and user reporting requirements.
