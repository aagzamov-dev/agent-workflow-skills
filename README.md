# Agent Workflow Skills

Small, reusable skills for coding agents that explain consequences, protect existing workflows, and review changes with evidence.

Use the shared skills in Codex and Claude Code. Optional agent profiles assign implementation, planning, and review to different models. Model routing is a workflow policy and requires a host with delegation support and access to the configured models.

## Skills

| Skill | Purpose | Example request |
| --- | --- | --- |
| [change-impact](skills/change-impact/SKILL.md) | Explain user-visible consequences before implementation and obtain agreement for workflow changes or compatibility breaks | "Use change-impact before adding offline installation." |
| [engineering-review](skills/engineering-review/SKILL.md) | Review correctness, security, compatibility, and user experience using concrete evidence | "Use engineering-review on this feature and its callers." |
| [prompt-craft](skills/prompt-craft/SKILL.md) | Turn a rough request into a concise, usable prompt for a named AI tool | "Use prompt-craft to improve this Claude Code prompt." |
| [model-router](skills/model-router/SKILL.md) | Route implementation and one independent final review per task, with strong planning for unresolved consequential decisions | "Use model-router to implement this feature within my existing workflow." |
| [unslop](skills/unslop/SKILL.md) | Build new screens, implement supplied designs, and polish UI using the current project's conventions | "Build this settings screen to fit the existing app." |
| [explain-clearly](skills/explain-clearly/SKILL.md) | Explain in simple words, with useful diagrams and before/after comparisons directly in chat | "Explain how this works; I do not understand the current explanation." |

Skills include their supporting references where needed. These are portable public instructions. Personal rules, project-specific skills, credentials, and unrelated installed skills belong in their own managed locations.

Change Impact establishes whether implementation is authorized, clarifies consequential requirements, and explains a simple approach and meaningful downsides before work. Engineering Review independently assesses the result with depth matched to risk, concrete evidence, and practical design, scaling, and maintenance judgment. Both distinguish routine choices from decisions that need the user's answer, and discourage speculative complexity. These instructions guide model behavior; stronger results are not guaranteed, and existing chats need to reload changed instructions. Installation and update commands remain unchanged.

Explain Clearly applies when the user asks for an explanation, why or how something works, a comparison or before/after, or says they do not understand. It answers the main question first, defines necessary terms, and uses concrete examples, small chat diagrams, or tables when helpful. It adapts the depth to the question rather than forcing a template or making every answer short. Explanations stay directly in chat; HTML, files, and external visuals are not generated unless requested. Invoke `$explain-clearly` in Codex or `/explain-clearly` in Claude Code explicitly if needed.

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

To add Explain Clearly to an existing installation while keeping the other saved choices:

```bash
python scripts/workflow.py install --add-skill explain-clearly --check
python scripts/workflow.py install --add-skill explain-clearly
```

If either canonical skill destination already contains a different `unslop`, compare it first, then add `--replace-skill unslop` to back it up and replace it. A separate legacy copy under `~/.codex/skills/unslop` is outside this installer's ownership: move it to a backup outside skill discovery before installing, preserving any customizations. Do not delete a directory link's target. Restart both clients after installation and check discovery; the installer does not test live client activation.

Install and refresh manage a short marked block in `~/.codex/AGENTS.md` or the nonempty `~/.codex/AGENTS.override.md` if it takes precedence, and in `~/.claude/CLAUDE.md` for Claude Code. For selected skills, the block directs the client to read `model-router` on every request, `change-impact` before meaningful implementation, `unslop` before UI design work, and `explain-clearly` for explanation requests or confusion. Skipping a skill omits its directive. Existing instruction files are backed up before their first managed edit. Keep personal additions outside the markers. An unrecognized block, a modified managed block, or a missing block in a still-active managed file stops preflight until you reconcile it. An existing installation record continues to work with the same options; run `python scripts/workflow.py install` after pulling this revision to refresh older blocks, or use the existing update command. Client adherence still requires a fresh session or an explicit instruction reload and is not guaranteed by file installation alone.

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
| Any implementation, including small, documentation, and configuration edits | Sol, followed by one independent Astra final review with depth matched to risk |
| Unresolved consequential architecture or migration decision without an adequate parent plan | Astra plans read-only. Feature size alone does not trigger planning. Sol implements and Astra reviews once at the end. |
| Explicit review request | Independent Astra review |

Explicit user model choices take precedence. Routine questions, explanations, investigation, preparation, and planning stay on the current model. Honor explicit Astra planning and review requests; use Astra for other work only at the user's explicit request. Claude Code maps implementation to Sonnet and consequential planning and independent final review to Opus. The Claude Code profiles cannot invoke Codex or Astra automatically. The Codex planner starts at low effort and reviewer at medium effort.

The task boundary is the agreed outcome, not each file, edit, check, installation, commit, or follow-up; unrelated work must not be grouped to evade review. Finish implementation, relevant tests, obvious fixes, and requested configuration or installation refresh before the one independent final review. Give the reviewer compact isolated context by default, without a full conversation fork: scope, acceptance criteria, constraints, the actual diff and identified snapshot, relevant caller locations, and test evidence. The reviewer may inspect source and expand scope when evidence warrants it. Findings should be concise, without quotas or exhaustive audits for tiny changes.

After review, the parent/Sol (Sonnet in Claude Code) makes authorized corrections and verifies affected behavior, clearly identifying changes since the reviewed snapshot. Corrections and routine follow-ups within the same task do not trigger another full review automatically. If unresolved consequential uncertainty needs another pass, explain the evidence gap and obtain user approval; an explicit additional-review request supplies approval. Missing required evidence prevents a readiness claim. Subagents return to the parent for integration. Delegation depends on the host and account, and the parent model stays fixed for the current turn. These controls are not a hard token cap or guaranteed savings.

The router also sets shared progress reporting for Codex and Claude Code. Choose 10% milestones for normal tasks or 5% for large tasks at the start, with brief done/next updates based on estimated completed scope, not time or ETAs. The parent owns the overall percentage. Workers supply actual milestones. Report only the latest milestone when steps happen together, and reserve 100% until all requested work, including review, tests, and publication, is complete.

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

Repository code and original skills are MIT. See [LICENSE](LICENSE). The vendored [Unslop skill and its resources](skills/unslop/SKILL.md), adapted from [Damir Sokolovsky's unslop](https://github.com/heydamir/unslop), remain under [CC BY 4.0](skills/unslop/LICENSE); retain their attribution and adaptation notice when redistributing them.
