# Codex routing

Select Sol as the usual parent in the client. The router cannot change a running parent's model. Use these installed profiles only when the task justifies delegation:

| Profile | Model | Purpose |
| --- | --- | --- |
| `workflow-light-worker` | `gpt-6.1-terra` | Simple bounded implementation worth handing off |
| `workflow-worker` | `gpt-6.1-sol` | Substantial bounded implementation when a worker is useful |
| `workflow-planner` | `gpt-6-astra` | Unresolved consequential planning or explicit request |
| `workflow-reviewer` | `gpt-6-astra` | One review for large/high-risk changes or an explicit review request |

Tiny edits and ordinary work normally stay with the Sol parent. The parent gathers context for explicit reviews before dispatching Astra; this preparation is not a duplicate full review. For small/ordinary implementation without an explicit review request, the parent checks the actual diff and relevant behavior itself. Reassess if scope or risk grows. Mode and the parent's model do not suppress a required independent review; read-only restrictions still apply.

Pass compact isolated context, not the full conversation. The parent supplies requirements, identified snapshot, separate staged/unstaged diffs, relevant untracked files and callers, and test evidence; add the agreed base and branch diff for branch reviews. Reviewers may inspect source and request missing evidence. Use the shared skill's escalation, authorization, and single-review rules. Each agent returns to the parent without further delegation. Profiles do not create a separate permission sandbox.

Profiles install as TOML under `~/.codex/agents/`. Use normal speed; light workers and planners start at low reasoning, Sol workers and Astra reviewers at medium. Increase effort only when evidence warrants it. Verify access to the exact configured model and effort setting. If the host exposes explicit model selection instead of profiles, use the same role mapping. If a lightweight worker is unavailable and selection was delegated, the parent can perform the work directly and disclose the route; a required Astra review cannot silently become self-review.

See [official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) for supported settings and discovery.

Re-running the existing install command refreshes copied profiles and adds the lightweight worker while preserving saved client/profile selections and refusing locally modified profiles. Reload instructions or start a fresh session; live discovery and model access require client verification.
