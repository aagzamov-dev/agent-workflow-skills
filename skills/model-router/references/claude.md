# Claude Code routing

Select Sonnet as the usual parent in the client. The router cannot change a running parent's model. Use these installed profiles only when the task justifies delegation:

| Profile | Model | Purpose |
| --- | --- | --- |
| `workflow-light-worker` | `haiku` | Simple bounded implementation worth handing off |
| `workflow-worker` | `sonnet` | Substantial bounded implementation when a worker is useful |
| `workflow-planner` | `opus` | Unresolved consequential planning or explicit request |
| `workflow-reviewer` | `opus` | One review for large/high-risk changes or an explicit review request |

Tiny edits and ordinary work normally stay with the Sonnet parent. The parent gathers context for explicit reviews before dispatching Opus; this preparation is not a duplicate full review. For small/ordinary implementation without an explicit review request, the parent checks the actual diff and relevant behavior itself. Reassess if scope or risk grows. Mode and the parent's model do not suppress a required independent review; read-only restrictions still apply.

Pass compact isolated context, not the full conversation. The parent supplies requirements, identified snapshot, separate staged/unstaged diffs, relevant untracked files and callers, and test evidence; add the agreed base and branch diff for branch reviews. Reviewers may inspect source and request missing evidence. Use the shared skill's escalation, authorization, and single-review rules. Each agent returns to the parent without further delegation. Profiles do not create a separate permission sandbox.

Profiles install under `~/.claude/agents/`. Verify that aliases resolve to available models and preserve explicit model/version choices. Check client overrides and the actual dispatched model rather than assuming profile configuration proves selection. Claude profiles do not invoke Codex models. Haiku is the lightweight role; Fable is not configured by this policy. Do not invoke Opus or Fable automatically for routine planning. Planner/reviewer profiles have read/search tools; workers can edit and run commands subject to host permissions.

See [official subagent documentation](https://code.claude.com/docs/en/sub-agents) for aliases, model overrides, tool restrictions, and discovery.

Re-running the existing install command refreshes copied profiles and adds the lightweight worker while preserving saved client/profile selections and refusing locally modified profiles. Reload instructions or start a fresh session; live discovery and model access require client verification.
