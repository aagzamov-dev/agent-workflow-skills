# Codex routing

Use installed custom agents when available. The repository supplies `workflow-worker` using `gpt-6.1-sol`, and `workflow-planner` and `workflow-reviewer` using `gpt-6-astra` under `codex/agents/`.

The personal install destination is `~/.codex/agents/`. Agent files use TOML. Verify access to the configured models and support for their reasoning settings. If the host instead exposes explicit model selection on its delegation tool, use that supported interface with the same roles.

Use normal speed by default. The worker and reviewer start at medium reasoning, and the planner at low reasoning. These are adjustable starting settings. Increase effort only when the actual task needs deeper investigation.

Delegate implementation to Sol when the parent uses a different model and the host supports delegation. The current parent investigates and prepares; invoke the planner read-only only for an unresolved consequential architecture or migration decision without an adequate parent plan, or an explicit request. Give its accepted conclusions to the worker.

Every implementation task, including small, documentation, and configuration edits, gets one independent Astra review at the end, with depth matched to risk. Finish relevant tests, obvious fixes, and requested configuration or installation refresh first. The boundary is the agreed outcome, not each edit, check, installation, commit, or follow-up; do not combine unrelated work to evade review. Honor explicit review requests.

Use compact isolated reviewer context by default, without a full conversation fork: scope, acceptance criteria, constraints, actual changes and identified snapshot, relevant caller locations, and test evidence. Allow source inspection and evidence-led scope expansion. Ask for concise findings without quotas or exhaustive tiny-change audits. The parent/Sol integrates authorized corrections and verifies affected behavior, distinguishing later corrections from the reviewed snapshot. Do not automatically repeat a full review. Another pass for unresolved consequential uncertainty requires explaining the gap and obtaining user approval; an explicit additional-review request is approval. Missing required evidence prevents a readiness claim. Each assigned agent returns to the parent without further dispatch.

Custom-agent instructions do not establish a separate permission sandbox. Host permissions and current authorization still apply. A running parent retains its own model.

See [official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) for installation, supported settings, and precedence.
