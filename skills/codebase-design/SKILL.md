---
name: codebase-design
description: Place business rules and data responsibilities in clear existing boundaries when implementing a feature that introduces or changes them. Keep small edits proportional; do not use for routine text or styling changes.
---

# Codebase Design

Before implementing the affected behavior, find the existing class, module, or function that owns the rule and the data it changes. Trace its callers and all relevant mutation paths, including background jobs, imports, and administrative actions where present. Use the project's domain language to describe that responsibility.

Keep the rule with its owner so each affected path preserves the same invariants: what must remain true before and after the operation. Put validation and state changes behind that boundary when they must act together. Do not move code or introduce a new layer merely to satisfy a preferred architecture.

Prefer an existing boundary with a small, meaningful interface that hides substantial implementation detail. Add or split a module only when a concrete responsibility becomes easier to understand and change independently; a forwarding wrapper or extra interface with no hidden complexity is not an improvement. Classes, modules, and functions are all valid owners.

Check the changed rule through meaningful observable outcomes and lasting effects, including another mutation path or failure case when it could violate the invariant. Use the project's existing testing approach; leave readability, public contract design, and the testing cycle to their respective guidance rather than repeating them here.

For a small local edit, a brief ownership check is enough. Do not require a design document, abstraction, or restructuring when the existing boundary already fits. Raise unresolved business rules through the applicable clarification and authorization instructions before dependent changes.

Adapted from [Matt Pocock's Codebase Design skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md), with narrower activation and guidance for existing codebases. See [MIT notice](LICENSE).
