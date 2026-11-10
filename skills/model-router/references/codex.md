# Codex routing

Use installed custom agents when available. The repository supplies `workflow-worker` using `gpt-6.1-sol`, and `workflow-planner` and `workflow-reviewer` using `gpt-6-astra` under `codex/agents/`.

The personal install destination is `~/.codex/agents/`. Agent files use TOML. Verify access to the configured models and support for their reasoning settings. If the host instead exposes explicit model selection on its delegation tool, use that supported interface with the same roles.

Use normal speed by default. The worker and reviewer start at medium reasoning, and the planner at low reasoning. These are adjustable starting settings. Increase effort only when the actual task needs deeper investigation.

Delegate implementation to Sol when the parent uses a different model and the host supports delegation. For large tasks, invoke the planner read-only when the parent lacks a strong inline plan. Give its accepted conclusions to the worker. Invoke one independent Astra reviewer after every implementation and for explicit review requests. Supply the actual diff, relevant source, and test evidence. The parent performs integration and tracks approval boundaries. Each assigned agent returns to the parent without further dispatch.

Custom-agent instructions do not establish a separate permission sandbox. Host permissions and current authorization still apply. A running parent retains its own model.

See [official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) for installation, supported settings, and precedence.
