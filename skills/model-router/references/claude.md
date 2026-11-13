# Claude Code routing

Use the installed `workflow-worker`, `workflow-planner`, and `workflow-reviewer` agents when available. Claude Code maps the workflow to Sonnet for implementation and Opus for consequential planning and independent final review. The Claude Code profiles cannot dispatch to Codex or Astra automatically. Personal profiles install under `~/.claude/agents/`.

The model aliases resolve according to the installed client and account. Verify availability. Preserve an explicitly selected version or model rather than silently replacing it with an alias.

The current parent investigates and prepares; invoke the planner only for an unresolved consequential architecture or migration decision without an adequate parent plan, or an explicit request. Give its accepted conclusions to the worker. Every implementation task, including small, documentation, and configuration edits, gets one independent Opus review at the end, with depth matched to risk. Finish relevant tests, obvious fixes, and requested configuration or installation refresh first. The boundary is the agreed outcome, not each edit, check, installation, commit, or follow-up; do not combine unrelated work to evade review. Honor explicit review requests.

Use compact isolated reviewer context by default, without the full conversation: scope, acceptance criteria, constraints, separate staged and unstaged diffs, relevant untracked files, caller locations, and test evidence. Identify the reviewed base and snapshot; for branch reviews, include the diff against the agreed base. If evidence is incomplete or too large, provide complete scoped artifacts or narrow the review explicitly. Allow source inspection and evidence-led scope expansion, requesting missing Git or test evidence from the parent. Ask for concise findings without quotas or exhaustive tiny-change audits.

The parent/Sonnet integrates authorized corrections and verifies affected behavior, distinguishing later corrections from the reviewed snapshot. Do not automatically repeat a full review. Another pass for unresolved consequential uncertainty requires explaining the gap and obtaining user approval; an explicit additional-review request is approval. Missing required evidence prevents a readiness claim. The planner and reviewer profiles expose read/search tools. The worker can edit and run commands subject to the host's permissions.

Subagents should perform their assigned role without launching additional agents. If a shared skill is needed in an isolated worker context, provide its file location or relevant instructions explicitly. Do not assume the entire parent conversation is inherited.

See [official subagent documentation](https://code.claude.com/docs/en/sub-agents) for model aliases, tool restrictions, and agent discovery.
