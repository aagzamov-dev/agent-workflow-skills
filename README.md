# Agent Workflow Skills

Small, reusable skills for coding agents that explain consequences, protect existing workflows, and review changes with evidence.

Use the shared skills in Codex and Claude Code. Optional agent profiles assign implementation, planning, and review to different models. Model routing is a workflow policy and requires a host with delegation support and access to the configured models.

## Skills

| Skill | Purpose | Example request |
| --- | --- | --- |
| [change-impact](skills/change-impact/SKILL.md) | Explain user-visible consequences before implementation and obtain agreement for workflow changes or compatibility breaks | "Use change-impact before adding offline installation." |
| [engineering-review](skills/engineering-review/SKILL.md) | Review correctness, security, compatibility, and user experience using concrete evidence | "Use engineering-review on this feature and its callers." |
| [prompt-craft](skills/prompt-craft/SKILL.md) | Turn a rough request into a concise, usable prompt for a named AI tool | "Use prompt-craft to improve this Claude Code prompt." |
| [model-router](skills/model-router/SKILL.md) | Route implementation and independent review on each request, with strong planning for large tasks | "Use model-router to implement this feature within my existing workflow." |

Each skill is self-contained except for the router's optional provider references. These are portable public instructions. Personal rules, project-specific skills, credentials, and installed third-party skills belong in their own managed locations.

## Install on a device

Requires Python 3.11 or newer and Git. On Windows, use native Windows Python from Git Bash or a terminal. WSL installations belong to the Linux environment and use Linux paths. Use a stable checkout location and review the repository before installation.

From the repository root, preview and install for both clients with these Bash commands. On systems where Python is named `python3`, substitute that executable.

```bash
python scripts/workflow.py install --check
python scripts/workflow.py install
```

The installer links each selected skill into `~/.agents/skills/` for Codex and `~/.claude/skills/` for Claude Code. Windows uses directory junctions through built-in PowerShell, requiring no Developer Mode. macOS and Linux use directory symlinks. Skills, including their references, read directly from this checkout. Editing an installed skill edits the repository source.

Agent profiles are managed copies under `~/.codex/agents/` and `~/.claude/agents/`. This avoids Windows file-symlink privileges. Re-running install refreshes them and refuses to overwrite locally modified profiles. Change profiles in the repository to share changes with other devices. Model access and supported settings must be verified per client and account.

Existing conflicting skills stop installation before links or profiles change. In particular, an existing personal `engineering-review` may include additional rules. Compare and merge the desired rules into this repository first. To explicitly back up that skill and replace it with a repository link, run the following command.

```bash
python scripts/workflow.py install --replace-skill engineering-review
```

Backups and installation records stay outside the checkout under `~/.agent-workflow-skills/`. The command prints each backup path. It preserves unrelated skills and the user-authored text in global instructions. Ordinary failures roll back completed installation actions. If the process is forcibly terminated, inspect its backup and lock files before retrying; remove a stale `operation.lock` only after confirming the earlier process has exited.

On the first installation, select one client with `--client codex` or `--client claude`, omit profiles with `--without-profiles`, or omit individual skills with `--skip-skill NAME`. Choices are saved and reused on subsequent install and update commands. New skill folders added upstream are not automatically selected. To change the selection, inspect and manually remove this installation's links, managed profiles and marked instruction blocks. Keep the backups, remove `install.json`, and install with the new choices. Never recursively delete a link target or the checkout.

Install and refresh manage a short marked block in `~/.codex/AGENTS.md` or the nonempty `~/.codex/AGENTS.override.md` if it takes precedence, and in `~/.claude/CLAUDE.md` for Claude Code. The block directs the client to read `model-router` on every request and `change-impact` before meaningful implementation, for each of those skills selected for installation. Existing instruction files are backed up before their first managed edit. Keep personal additions outside the markers. An unrecognized block, a modified managed block, or a missing block in a still-active managed file stops preflight until you reconcile it. An existing installation record continues to work with the same options and gains the block on the next install or refresh.

Start a fresh client session after setup and verify skill and agent discovery. An existing session may still hold earlier instructions. Ask it to reread the global entrypoint and linked skills if you need to continue there, or restart and resume when the client supports it. Invoke `$change-impact` in Codex or `/change-impact` in Claude Code. The optional profiles are named `workflow-worker`, `workflow-planner`, and `workflow-reviewer`.

The installer targets standard per-user locations and refuses custom `CODEX_HOME` or `CLAUDE_CONFIG_DIR` overrides. For custom client layouts, configure links manually. `--home PATH` explicitly chooses a separate standard-layout installation root and is useful for isolated verification.

## Update on each device

After publishing the repository, clone it on each device and run installation once. From that checkout, use the following command for daily updates.

```bash
python scripts/workflow.py update
```

The command requires a clean checkout, a current branch with a configured upstream, and an existing installation. It checks installed files for conflicts, runs a fast-forward-only pull, then refreshes managed agent profiles and global instruction blocks using the updated installer. It preserves local changes by refusing dirty or diverged checkouts. Resolve those changes through your normal Git workflow before retrying.

A plain `git pull --ff-only` also updates existing linked skills. Run `python scripts/workflow.py install` afterward to refresh copied profiles and instruction blocks. Start a fresh session to load current instructions. Moving or deleting the checkout breaks its links.

The update command uses the configured upstream and executes the installer from the new revision, so use a remote you trust. If installation refresh fails after Git succeeds, skills already reflect the new checkout. Resolve the reported conflict and rerun install. The command reports this partial outcome and leaves Git history intact.

Edit and optimize skills in the checkout, inspect the diff, commit, and push through your normal Git workflow. Other devices receive those changes when they run the update command. Git remotes, account connections, model access, and permissions are configured separately on each device. An unpublished checkout with no initial commit or upstream cannot pull updates yet.

## Optional copy installation

For a one-time copy instead of links, this Bash snippet copies one selected skill, including references, into both standard skill locations. Existing destinations cause it to stop. Run it from the repository root. It requires Git Bash on Windows or Bash with `cp` on macOS/Linux.

```bash
(
  set -eu
  skill_name=change-impact
  source_dir="$(pwd -P)/skills/$skill_name"
  test -f "$source_dir/SKILL.md"
  for target_dir in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    destination="$target_dir/$skill_name"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      printf 'Existing destination requires manual comparison: %s\n' "$destination"
      exit 1
    fi
  done
  mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"
  for target_dir in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    cp -R "$source_dir" "$target_dir/$skill_name"
  done
)
```

Copied skills need manual refresh after each pull. They are outside the linked installer's ownership until you explicitly back them up and replace them with links. If a copy fails partway, inspect both destinations before retrying.

## Suggested routing

| Work | Route |
| --- | --- |
| Routine question, explanation, or ordinary investigation | Current model |
| Any implementation, including a small edit | Sol, followed by one independent Astra review |
| Large task with a multi-module architectural decision, complex migration, or ambiguous multi-stage design | Astra plans if the parent lacks a strong inline plan. Sol implements and Astra reviews independently. |
| Explicit review request | Independent Astra review |

Explicit user model choices take precedence. Routine planning stays on the current model. Use Astra for other work only at the user's explicit request. Claude Code maps implementation to Sonnet and large-task planning and independent review to Opus. The Claude Code profiles cannot invoke Codex or Astra automatically. The Codex planner starts at low effort and reviewer at medium effort.

The parent sends the final changes, relevant callers, requirements, and test evidence to the reviewer. After corrections, recheck the specific findings and affected behavior. Subagents return to the parent for integration. Delegation depends on the host and account, and the parent model stays fixed for the current turn.

## Verification and contribution

Keep skills focused and descriptions specific. Include concrete user requests when proposing changes, and document the behavior the change should improve. Exercise workflow-preserving changes, ambiguous migrations, existing-user upgrades, unavailable models, and explicit user model choices when validating routing changes.

Run `python -m unittest discover -s tests -v` for isolated filesystem and local-Git integration checks. They exercise links, managed instruction blocks, backups and conflicts, repeat installation, profile protection, rollback, and updating from a local remote. The tests use temporary homes and repositories and do not launch AI clients.

Windows verification covers native directory junctions and the Git Bash copy snippet. macOS/Linux link behavior requires verification on those platforms. Live activation and model delegation must be checked in each installed client. Public model names and client features can change.

## References

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

## License

MIT. See [LICENSE](LICENSE).
