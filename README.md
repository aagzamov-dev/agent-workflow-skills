# Agent Workflow Skills

Small, reusable skills for coding agents that explain consequences, protect existing workflows, and review changes with evidence.

Use the shared skills in Codex and Claude Code. Optional agent profiles assign implementation, planning, and review to different models. Model routing is a workflow policy and requires a host with delegation support and access to the configured models.

## Skills

| Skill | Purpose | Example request |
| --- | --- | --- |
| [change-impact](skills/change-impact/SKILL.md) | Explain user-visible consequences before implementation and obtain agreement for workflow changes or compatibility breaks | "Use change-impact before adding offline installation." |
| [engineering-review](skills/engineering-review/SKILL.md) | Review correctness, security, compatibility, and user experience using concrete evidence | "Use engineering-review on this feature and its callers." |
| [prompt-craft](skills/prompt-craft/SKILL.md) | Turn a rough request into a concise, usable prompt for a named AI tool | "Use prompt-craft to improve this Claude Code prompt." |
| [model-router](skills/model-router/SKILL.md) | Keep Sol/Sonnet as parent, delegate bounded work economically, and use stronger review for large or risky work | "Use model-router to implement this feature within my existing workflow." |
| [unslop](skills/unslop/SKILL.md) | Build new screens, implement supplied designs, and polish UI using the current project's conventions | "Build this settings screen to fit the existing app." |
| [explain-clearly](skills/explain-clearly/SKILL.md) | Explain in simple words, with useful diagrams and before/after comparisons directly in chat | "Explain how this works; I do not understand the current explanation." |
| [code-simplification](skills/code-simplification/SKILL.md) | Write readable code from the first draft and simplify existing code while preserving behavior | "Make the order handler easy to follow." |
| [api-and-interface-design](skills/api-and-interface-design/SKILL.md) | Establish the behavior callers depend on when changing a public interface or reproducing a feature in another service | "Reproduce the order endpoint in the new service." |
| [test-driven-development](skills/test-driven-development/SKILL.md) | Verify changed behavior, bug fixes, and service replicas through their public entry points | "Check what happens if the order arrives twice." |

Skills include their supporting references where needed. These are portable public instructions. Personal rules, project-specific skills, credentials, and unrelated installed skills belong in their own managed locations.

Change Impact establishes whether implementation is authorized, clarifies consequential requirements, and explains a simple approach and meaningful downsides before work. Engineering Review independently assesses the result with depth matched to risk, concrete evidence, and practical design, scaling, and maintenance judgment. Both distinguish routine choices from decisions that need the user's answer, and discourage speculative complexity. These instructions guide model behavior; stronger results are not guaranteed, and existing chats need to reload changed instructions. Installation and update commands remain unchanged.

Explain Clearly answers “explain this” in plain language and shows a flow diagram in chat for large tasks. Ask for “diagram mode” at any point, even for a small or medium task. For a symptom report, the agent investigates where the behavior first goes wrong, explains the evidence, and asks before fixing it. If the exact correction is already approved, it proceeds within that scope.

Unslop applies to UI design work: new screens, pages, dialogs and components, supplied design implementation, and visual polish, including UI work within a larger feature. Requests such as "build a settings screen" or "do this design" do not need to name the skill. The managed global instructions direct both clients to read it before that work; backend-only and other nonvisual tasks are outside its scope. Invoke `$unslop` in Codex or `/unslop` in Claude Code explicitly if needed.

For new UI, inspect nearby screens and reuse the project's shell, components, tokens, typography, icons, translations, and interaction patterns from the first version. Preserve supplied design intent and resolve material conflicts with the project before broad changes. For existing UI, audit first and keep polish proportional to the issues found. Existing brand, functionality, and working screens take precedence over the skill's example values. A new visual direction requires agreement when it goes beyond approved work; routine implementation following the current project does not add another approval gate.

Browser use, including headless screenshots and video rendering, requires explicit permission for the current task. Snapshot and story helpers are optional; they need Node.js and Playwright/Chromium, and videos also need ffmpeg. Installation does not install these dependencies. Source inspection remains available without them; report visual verification as incomplete until authorized and performed.

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

On the first installation, select one client with `--client codex` or `--client claude`, omit profiles with `--without-profiles`, or omit individual skills with `--skip-skill NAME`. Choices are saved and reused on subsequent install and update commands. New skill folders added upstream are not automatically selected. Add one explicitly with `install --add-skill NAME`; existing client, profile, and other skill choices remain unchanged. To change clients, remove skills, or change profile selection, inspect and manually remove this installation's links, managed profiles and marked instruction blocks. Keep the backups, remove `install.json`, and install with the new choices. Never recursively delete a link target or the checkout.

For an existing installation, add Unslop with the updated installer from this checkout:

```bash
python scripts/workflow.py install --add-skill unslop --check
python scripts/workflow.py install --add-skill unslop
```

To add the three coding skills to an existing installation, preview the combined change and then install:

```bash
python scripts/workflow.py install --add-skill code-simplification --add-skill api-and-interface-design --add-skill test-driven-development --check
python scripts/workflow.py install --add-skill code-simplification --add-skill api-and-interface-design --add-skill test-driven-development
```

The managed instructions select readability guidance when writing code, interface guidance for public contracts and replicas, and testing guidance for authorized behavior changes. A replica can use all three in one implementation. Select any of them individually with the same command.

To add Explain Clearly to an existing installation while keeping the other saved choices:

```bash
python scripts/workflow.py install --add-skill explain-clearly --check
python scripts/workflow.py install --add-skill explain-clearly
```

If either canonical skill destination already contains a different `unslop`, compare it first, then add `--replace-skill unslop` to back it up and replace it. A separate legacy copy under `~/.codex/skills/unslop` is outside this installer's ownership: move it to a backup outside skill discovery before installing, preserving any customizations. Do not delete a directory link's target. Restart both clients after installation and check discovery; the installer does not test live client activation.

Install and refresh manage a short marked block in `~/.codex/AGENTS.md` or the nonempty `~/.codex/AGENTS.override.md` if it takes precedence, and in `~/.claude/CLAUDE.md` for Claude Code. The block activates the selected coding skills described above, model routing for each request, change-impact guidance before meaningful implementation, and Unslop for UI work. When Explain Clearly is selected, the block calls for plain-language explanations, a flow diagram for large tasks, and diagram mode on request at any size. Skipping a skill omits its directive.

Existing instruction files are backed up before their first managed edit. Keep personal additions outside the markers. An unrecognized block, a modified managed block, or a missing block in a still-active managed file stops preflight until you reconcile it. An existing installation record continues to work with the same options. Run `python scripts/workflow.py install` after pulling this revision to refresh older blocks, or use the existing update command.

Start a fresh client session after setup and verify skill and agent discovery. An existing session may still hold earlier instructions. Ask it to reread the global entrypoint and linked skills if you need to continue there, or restart and resume when the client supports it. Invoke `$change-impact` in Codex or `/change-impact` in Claude Code. The optional profiles are named `workflow-light-worker`, `workflow-worker`, `workflow-planner`, and `workflow-reviewer`.

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

Select **Sol as the usual Codex parent** and **Sonnet as the usual Claude Code parent**. The parent understands the task, chooses whether delegation helps, integrates changes, and checks the result. Installation does not change the selected parent or client settings; the router cannot replace a running parent model. Explicit user model, effort, budget, and review choices take precedence.

| Work | Codex | Claude Code | Final check |
| --- | --- | --- | --- |
| Questions, routine investigation/planning, tiny edits | Sol parent directly | Sonnet parent directly | Parent checks; no automatic agents |
| Simple bounded work worth a handoff | Terra light worker | Haiku light worker | Parent reviews actual changes and checks |
| Ordinary fix or feature | Sol directly; Sol worker only when useful | Sonnet directly; Sonnet worker only when useful | Parent reviews and verifies |
| Large or high-risk change | Sol owns work | Sonnet owns work | One independent Astra/Opus review after implementation and checks |
| Explicit review request, even plain "review" | Parent gathers evidence, then Astra reviews | Parent gathers evidence, then Opus reviews | Honor any explicitly chosen different reviewer or self-review |
| Unresolved consequential architecture/migration decision | Astra planner only when needed | Opus planner only when needed | Implementation review still depends on size/risk |

Large means substantial interacting behavior, cross-module contracts, or changes too complex for a reliable focused parent check. Risk includes permissions, sensitive data, destructive operations, persistence/migrations, signing/updaters, compatibility, and difficult concurrency/recovery. A small sensitive change can need strong review; many mechanical edits do not automatically need it. Reclassify as the actual scope grows. Review routing does not depend on the parent's model or client mode, and never overrides read-only restrictions.

Routine planning stays with the parent. Do not automatically invoke Astra, Opus, or Fable for tiny work or simple plans, and do not build a planner/worker/reviewer chain by default. Terra/Haiku handles clear bounded tasks only when delegation is worth its preparation and review overhead. Escalate to Sol/Sonnet on demonstrated complexity or failed checks beyond the worker's scope, rather than repeated blind attempts. Use one implementation owner per overlapping file set; parallel workers are not automatic.

| Profile | Codex model | Claude Code alias |
| --- | --- | --- |
| `workflow-light-worker` | `gpt-6.1-terra`, low effort | `haiku` |
| `workflow-worker` | `gpt-6.1-sol`, medium effort | `sonnet` |
| `workflow-planner` | `gpt-6-astra`, low effort | `opus` |
| `workflow-reviewer` | `gpt-6-astra`, medium effort | `opus` |

Use normal speed and increase reasoning only when warranted. Verify model access and actual dispatch in each host; Claude aliases/overrides can affect resolution. Claude profiles do not invoke Codex models. Haiku is the lightweight Claude role; Fable is not configured. See [Claude model selection](https://code.claude.com/docs/en/sub-agents#choose-a-model).

For explicit reviews, Sol/Sonnet gathers scope, requirements, actual changes, relevant callers, and test evidence before handing off to Astra/Opus. It should not duplicate a full audit first. Give workers and reviewers compact isolated context rather than a full conversation fork. Review evidence identifies the snapshot and separates staged, unstaged, and relevant untracked changes; branch reviews include the agreed base and branch diff. Reviewers may inspect source and expand scope when evidence warrants it.

Finish implementation, relevant checks, obvious fixes, and requested installation refresh before the one independent final review of large/high-risk work. Explicit standalone reviews can assess existing or unfinished changes and report gaps. The parent handles authorized corrections and verifies affected behavior, identifying changes since the reviewed snapshot. Corrections and routine follow-ups do not automatically trigger another full review; another pass for consequential uncertainty requires explaining the gap and obtaining approval. Missing required evidence prevents a readiness claim. Small/ordinary implementation gets a parent check unless the user requests a review. Routing does not grant permission to edit, commit, deploy, or run live tests.

### Refresh an existing installation

The existing commands and saved client/skill/profile choices remain supported. Run these Bash commands from this checkout to refresh copied profiles and add the lightweight worker for clients with profiles enabled:

```bash
python scripts/workflow.py install --check
python scripts/workflow.py install
```

Linked skills already reflect this checkout; copied profiles require that refresh. The installer preserves local profile customizations by refusing conflicts, and `--without-profiles` installations stay without profiles. No user data migration or new dependency is required. No automatic model-setting change is made. Start a fresh session or explicitly reload instructions after refreshing; existing chats do not automatically adopt the policy or change parent models. Client discovery, model access, and live routing still need verification. Other devices need this revision through the existing Git/update workflow; uncommitted changes are not available there.

This policy aims to reduce unnecessary passes and context duplication. It is not a hard usage cap or guaranteed saving; compare actual usage and corrections on similar tasks.

## Verification and contribution

Keep skills focused and descriptions specific. Include concrete user requests when proposing changes, and document the behavior the change should improve. Exercise workflow-preserving changes, ambiguous migrations, existing-user upgrades, unavailable models, and explicit user model choices when validating routing changes.

Run `python -m unittest discover -s tests -v` for isolated filesystem and local-Git integration checks. They exercise links, managed instruction blocks, backups and conflicts, repeat installation, profile protection, rollback, and updating from a local remote. The tests use temporary homes and repositories and do not launch AI clients.

Run `node --test tests/test_unslop_story.mjs` for isolated story-helper checks covering asset containment and temporary frame ownership. These checks do not launch a browser or run ffmpeg.

Windows verification covers native directory junctions and the Git Bash copy snippet. macOS/Linux link behavior requires verification on those platforms. Live activation and model delegation must be checked in each installed client. Public model names and client features can change.

## References

- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)

## License

The three adapted coding skills credit Addy Osmani's [agent-skills](https://github.com/addyosmani/agent-skills). Each includes its original MIT notice.

Repository code and original skills are MIT. See [LICENSE](LICENSE). The vendored [Unslop skill and its resources](skills/unslop/SKILL.md), adapted from [Damir Sokolovsky's unslop](https://github.com/heydamir/unslop), remain under [CC BY 4.0](skills/unslop/LICENSE); retain their attribution and adaptation notice when redistributing them.
