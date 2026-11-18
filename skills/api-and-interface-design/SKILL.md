---
name: api-and-interface-design
description: Define caller-visible contracts for public APIs and module boundaries, including when replicating a feature across microservices or migrating an interface that existing consumers depend on.
---

# API and Interface Design

## Define the contract

Use the project's established conventions for inputs, defaults, errors, and validation. Specify what callers can rely on before implementation. Validate untrusted data at the boundary and preserve authorization and ownership checks. Expose only what consumers need to perform their work.

## Check existing behavior before changing it

When reproducing a feature, identify the source service, target service, and exact operation in scope. Capture one normal example and the important boundary or failure cases, including externally visible effects. If the source appears to have a bug, show the evidence and ask which behavior is intended before committing to that expectation.

1. Trace the current entry point, callers, tests, and relevant documentation. Use implementation and caller evidence to find undocumented behavior consumers depend on. Where evidence is incomplete, say which contract is uncertain.
2. Compare old and proposed behavior for affected caller paths. Account for accepted inputs, omissions and defaults, observable results and errors, persisted changes, emitted events, and ordering where consumers rely on it. For operations exposed to partial failure, repeats, or concurrency, check what remains saved or emitted and what a repeat call observes. Include existing data or supported older callers when affected.
3. Preserve those outcomes by default. Describe each intentional deviation in terms of the affected callers and visible consequences, and obtain agreement for any compatibility break or established workflow change that the user has yet to approve.
4. Verify through the normal interface with relevant, permitted checks. Report the behavior verified, approved deviations, and material coverage gaps.

Adapted from [Addy Osmani's API and Interface Design skill](https://github.com/addyosmani/agent-skills/blob/main/skills/api-and-interface-design/SKILL.md). See [MIT notice](LICENSE).
