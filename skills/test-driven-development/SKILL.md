---
name: test-driven-development
description: Test authorized behavior changes and bug fixes, compare replicated microservice features, or use when the user requests TDD. Verify observable outcomes through the project's existing test setup.
---

# Test-Driven Development

Diagnosis and review alone authorize read-only work. Follow the project's approval rules for changes to tests and code. An explicitly authorized fix needs no additional approval for its exact scope, subject to any applicable pause or scope rules.

For a service replica, establish expectations independently of the new implementation. Run the same cases against the reference service and replica in isolation with equivalent starting data. A passing test against the reference is useful evidence of current behavior. Check meaningful outputs and lasting effects, allowing for generated IDs or times when the contract permits variation. If the original cannot be run, use agreed examples, existing fixtures, or documentation and label the comparison as indirect. Include repeat delivery or partial failure when it affects this feature. For example, if one order must create one invoice, deliver the same order twice and check both the response and the number of stored invoices.

For a new or changed outcome, use the following cycle:

1. **Choose a meaningful test.** Identify the user- or caller-visible result that should change and the regression it would catch. Reuse the project's test runner, fixtures, and normal entry point. Add coverage when requested, required, or when existing checks miss a specific regression. Assert outcomes such as returned errors, persisted state, or emitted events when they are part of the contract. Use mocks at boundaries where needed.
2. **Red.** Before editing the implementation, write or adapt a focused test and run it against the old code. Confirm that it reaches the intended path and fails because the expected behavior is missing. If it passes already, check the premise and the assertion. A setup failure does not establish the regression.
3. **Green and refactor.** Make the smallest readable fix that delivers the behavior. Rerun the same check, then run relevant regression checks for existing behavior. If further cleanup is useful and in scope, preserve the contract and rerun affected checks.
4. **Report the evidence.** State what failed before the change, what passed after it, and any unverified behavior. If a pre-change or target-environment check was unavailable, describe the gap and the strongest available substitute.

Inspect unfamiliar test commands before running them. Use permitted isolated checks. Browser and live-environment testing require explicit authorization. Keep changes within the approved test and implementation scope, including tooling and repository operations.

Adapted from [Addy Osmani's Test-Driven Development skill](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md). See [MIT notice](LICENSE).
