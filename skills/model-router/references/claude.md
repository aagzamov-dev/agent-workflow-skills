# Claude Code routing

Use the installed `workflow-worker`, `workflow-planner`, and `workflow-reviewer` agents when available. Claude Code maps the workflow to Sonnet for implementation and Opus for large-task planning and independent review. The Claude Code profiles cannot dispatch to Codex or Astra automatically. Personal profiles install under `~/.claude/agents/`.

The model aliases resolve according to the installed client and account. Verify availability. Preserve an explicitly selected version or model rather than silently replacing it with an alias.

For large tasks, invoke the planner when the parent lacks a strong inline plan, then give its accepted conclusions to the worker. Send every final implementation and explicit review request to an independent Opus reviewer. Before dispatch, give the reviewer separate staged and unstaged diffs, relevant untracked files, acceptance criteria, and test results. Identify the reviewed base and snapshot so later edits cannot silently invalidate the report. For branch reviews, include the branch diff against the agreed base. If evidence is incomplete or too large, provide complete scoped artifacts or narrow the review explicitly. The reviewer can read surrounding source but must request missing Git or test evidence from the parent. The planner and reviewer profiles expose read/search tools. The worker can edit and run commands subject to the host's permissions.

Subagents should perform their assigned role without launching additional agents. If a shared skill is needed in an isolated worker context, provide its file location or relevant instructions explicitly. Do not assume the entire parent conversation is inherited.

See [official subagent documentation](https://code.claude.com/docs/en/sub-agents) for model aliases, tool restrictions, and agent discovery.
