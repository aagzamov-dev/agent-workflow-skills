---
name: change-impact
description: Explain consequences before meaningful software implementation and obtain agreement for changes to established workflows or compatibility for existing users. Use for features, fixes, migrations, packaging, and release changes with user-visible effects.
---

# Change Impact

Before editing, inspect the relevant entry points, callers, configuration, and existing behavior. Describe the proposed outcome in plain language. Keep the explanation to four short bullets covering the change, the user's workflow, existing users, and tradeoffs. One sentence is sufficient for a small change. Expand only when a consequence needs a decision.

Identify effects on commands, deployment steps, prerequisites, public interfaces, stored data, settings, and update paths where relevant. State what becomes harder, behaves differently, stops working, or requires migration. Separate established facts from uncertainty. Avoid claiming compatibility from source inspection alone.

Ask for explicit agreement before changing the user's established workflow or breaking compatibility for existing users. Explain the concrete consequence and the smallest compatible option. Feature approval alone does not authorize undisclosed consequences. Honor approval already given for the exact consequence and continue independent authorized work while a decision is pending.

For example, adding offline installation requires checking clean installation and upgrades separately. Existing clients may depend on particular update artifacts, formats, endpoints, signing, and version rules. Preserve supported upgrade paths or disclose and obtain agreement for a migration before changing them.

If new evidence reveals a material consequence during implementation, explain it before the affected edit. Review the final implementation against the disclosed consequences. Verify both existing-user and new-user behavior where applicable.

Finish with a short report of what changed, any action required from the user, verification performed, and unresolved compatibility questions. Never hide material consequences to meet a length target.
