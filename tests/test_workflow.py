"""Isolated filesystem and local-Git integration checks; no AI clients are launched."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1]
NEW_SKILL_TRIGGERS = {
    'engineering-review': 'For every review request, including plain "review"',
    'codebase-design': 'feature that introduces or changes business rules or responsibility for data',
    'code-simplification': 'Before writing or editing code, including a first draft',
    'api-and-interface-design': 'public API or replicating a feature across services',
    'test-driven-development': 'authorized implementation involving business behavior, a bug regression, or replica parity',
}
ENTRYPOINTS = {'.codex/AGENTS.md': '~/.agents/skills', '.claude/CLAUDE.md': '~/.claude/skills'}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='workflow-test-')
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / 'checkout with spaces'
        self.repo.mkdir()
        for name in ('skills', 'codex', 'claude', 'scripts'):
            shutil.copytree(SOURCE / name, self.repo / name, ignore=shutil.ignore_patterns('__pycache__'))
        self.home = self.root / 'isolated home'
        self.home.mkdir()

    def tearDown(self):
        # TemporaryDirectory owns this exact absolute root. Python removes Windows
        # junctions without traversing their source directories.
        self.temporary.cleanup()

    def command(self, *args, ok=True, repo=None):
        checkout = repo or self.repo
        result = subprocess.run(
            [sys.executable, str(checkout / 'scripts/workflow.py'), *args, '--home', str(self.home)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def git(self, repo, *args):
        result = subprocess.run(
            ['git', '-C', str(repo), '-c', 'user.name=Workflow Test', '-c',
             'user.email=workflow-test@example.invalid', *args],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def initialize(self):
        self.git(self.repo, 'init', '-b', 'main')
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Initial fixture')

    def remote_pair(self):
        self.initialize()
        remote = self.root / 'remote.git'
        remote.mkdir()
        self.git(remote, 'init', '--bare')
        self.git(self.repo, 'remote', 'add', 'origin', str(remote))
        self.git(self.repo, 'push', '-u', 'origin', 'main')
        device = self.root / 'second device'
        self.git(self.root, 'clone', '-b', 'main', str(remote), str(device))
        self.command('install', repo=device)
        return device

    def test_install_reinstall_and_atomic_source_replacement(self):
        self.command('install')
        self.command('install')
        source = self.repo / 'skills/change-impact/SKILL.md'
        replacement = source.with_suffix('.new')
        replacement.write_text('Updated through source replacement', encoding='utf-8')
        os.replace(replacement, source)
        for folder in ('.agents', '.claude'):
            installed = self.home / folder / 'skills/change-impact/SKILL.md'
            self.assertEqual(installed.read_text(), source.read_text())
            for relative in ('SKILL.md', 'references/story-video.md', 'scripts/snapshot.mjs'):
                self.assertEqual((self.home / folder / 'skills/unslop' / relative).read_bytes(),
                                 (self.repo / 'skills/unslop' / relative).read_bytes())
            for relative in ('SKILL.md', 'agents/openai.yaml'):
                self.assertEqual((self.home / folder / 'skills/explain-clearly' / relative).read_bytes(),
                                 (self.repo / 'skills/explain-clearly' / relative).read_bytes())
        self.assertFalse((self.home / '.agent-workflow-skills/operation.lock').exists())

    def test_conflict_preflight_and_explicit_backup(self):
        original = self.home / '.agents/skills/engineering-review'
        original.mkdir(parents=True)
        (original / 'SKILL.md').write_text('Personal review rules')
        self.command('install', ok=False)
        self.assertFalse((self.home / '.agents/skills/change-impact').exists())
        self.command('install', '--replace-skill', 'engineering-review')
        backups = list((self.home / '.agent-workflow-skills/backups').rglob('SKILL.md'))
        self.assertEqual([path.read_text() for path in backups], ['Personal review rules'])
        self.assertEqual((original / 'SKILL.md').read_bytes(),
                         (self.repo / 'skills/engineering-review/SKILL.md').read_bytes())

    def test_profile_edit_is_preserved(self):
        self.command('install')
        profile = self.home / '.codex/agents/workflow-reviewer.toml'
        profile.write_text('local profile customization')
        self.command('install', ok=False)
        self.assertEqual(profile.read_text(), 'local profile customization')

    def test_existing_install_adds_light_workers_and_tracks_future_conflicts(self):
        self.command('install')
        state_file = self.home / '.agent-workflow-skills/install.json'
        state = json.loads(state_file.read_text())
        for client, suffix in (('codex', '.toml'), ('claude', '.md')):
            filename = 'workflow-light-worker' + suffix
            (self.home / f'.{client}/agents' / filename).unlink()
            del state['profile_hashes'][f'{client}/{filename}']
        state_file.write_text(json.dumps(state))
        self.command('install', '--check')
        self.assertFalse((self.home / '.codex/agents/workflow-light-worker.toml').exists())
        self.command('install')
        refreshed = json.loads(state_file.read_text())
        for client, suffix in (('codex', '.toml'), ('claude', '.md')):
            filename = 'workflow-light-worker' + suffix
            destination = self.home / f'.{client}/agents' / filename
            self.assertEqual(destination.read_bytes(), (self.repo / client / 'agents' / filename).read_bytes())
            self.assertIn(f'{client}/{filename}', refreshed['profile_hashes'])
            destination.write_text('Local customization')
        self.command('install', ok=False)
        self.assertEqual(state_file.read_text(), json.dumps(refreshed, indent=2) + '\n')
        self.assertEqual((self.home / '.claude/agents/workflow-light-worker.md').read_text(), 'Local customization')

    def test_existing_unmanaged_light_worker_blocks_refresh_before_any_changes(self):
        self.command('install')
        state_file = self.home / '.agent-workflow-skills/install.json'
        state = json.loads(state_file.read_text())
        del state['profile_hashes']['codex/workflow-light-worker.toml']
        state_file.write_text(json.dumps(state))
        local = self.home / '.codex/agents/workflow-light-worker.toml'
        local.write_text('Unmanaged personal profile')
        reviewer = self.home / '.codex/agents/workflow-reviewer.toml'
        previous = reviewer.read_bytes()
        source = self.repo / 'codex/agents/workflow-reviewer.toml'
        source.write_text(source.read_text().replace('"medium"', '"high"'))
        self.command('install', ok=False)
        self.assertEqual(reviewer.read_bytes(), previous)
        self.assertEqual(local.read_text(), 'Unmanaged personal profile')

    def test_saved_selection_and_preflight(self):
        self.command('install', '--check', '--client', 'claude', '--without-profiles')
        self.assertFalse((self.home / '.claude').exists())
        self.command('install', '--client', 'claude', '--without-profiles', '--skip-skill', 'change-impact')
        self.command('install')
        self.assertFalse((self.home / '.agents').exists())
        self.assertFalse((self.home / '.claude/agents').exists())
        self.assertFalse((self.home / '.claude/skills/change-impact').exists())
        entrypoint = (self.home / '.claude/CLAUDE.md').read_text(encoding='utf-8')
        self.assertIn('~/.claude/skills/model-router/SKILL.md', entrypoint)
        self.assertNotIn('change-impact/SKILL.md', entrypoint)

    def test_bootstrap_backs_up_and_preserves_private_bytes(self):
        private = b'\xef\xbb\xbf# Personal rules\r\n\r\nRead caf\xc3\xa9 guidance.'
        codex = self.home / '.codex/AGENTS.md'
        claude = self.home / '.claude/CLAUDE.md'
        for path in (codex, claude):
            path.parent.mkdir()
            path.write_bytes(private)
        self.command('install', '--check')
        self.assertEqual(codex.read_bytes(), private)
        self.assertEqual(claude.read_bytes(), private)
        self.command('install')
        backups = self.home / '.agent-workflow-skills/backups'
        for path, skill_root in ((codex, b'~/.agents/skills'), (claude, b'~/.claude/skills')):
            installed = path.read_bytes()
            self.assertTrue(installed.startswith(private + b'\r\n'))
            self.assertNotIn(b'\n', installed.replace(b'\r\n', b''))
            self.assertIn(skill_root + b'/model-router/SKILL.md', installed)
            self.assertIn(skill_root + b'/change-impact/SKILL.md', installed)
            self.assertIn(skill_root + b'/unslop/SKILL.md', installed)
            self.assertIn(skill_root + b'/explain-clearly/SKILL.md', installed)
            self.assertEqual([item.read_bytes() for item in backups.rglob(path.name)], [private])
            path.write_bytes(installed + b'\r\nNew private text.')
        before = [path.read_bytes() for path in (codex, claude)]
        self.command('install')
        self.assertEqual([path.read_bytes() for path in (codex, claude)], before)
        self.assertEqual(len(list(backups.rglob('*.md'))), 2)

    def test_add_skill_preserves_saved_choices_and_preflight(self):
        self.command('install', '--client', 'claude', '--without-profiles',
                     '--skip-skill', 'unslop', '--skip-skill', 'change-impact')
        state_file = self.home / '.agent-workflow-skills/install.json'
        previous = state_file.read_bytes()
        instructions = (self.home / '.claude/CLAUDE.md').read_bytes()
        self.command('install', '--add-skill', 'unslop', '--check')
        self.assertEqual(state_file.read_bytes(), previous)
        self.assertEqual((self.home / '.claude/CLAUDE.md').read_bytes(), instructions)
        self.assertFalse((self.home / '.claude/skills/unslop').exists())
        self.command('install', '--add-skill', 'unslop')
        self.command('install', '--add-skill', 'unslop')
        state = json.loads(state_file.read_text())
        self.assertEqual(state['clients'], ['claude'])
        self.assertFalse(state['profiles'])
        self.assertNotIn('change-impact', state['skills'])
        self.assertEqual(state['skills'].count('unslop'), 1)
        self.assertFalse((self.home / '.agents').exists())
        refreshed = (self.home / '.claude/CLAUDE.md').read_bytes()
        self.assertNotIn(b'/unslop/SKILL.md', instructions)
        self.assertIn(b'~/.claude/skills/unslop/SKILL.md', refreshed)
        self.assertEqual((self.home / '.claude/skills/unslop/SKILL.md').read_bytes(),
                         (self.repo / 'skills/unslop/SKILL.md').read_bytes())

    def test_refresh_does_not_select_new_skills_implicitly(self):
        self.command('install', '--skip-skill', 'unslop')
        self.command('install')
        state = json.loads((self.home / '.agent-workflow-skills/install.json').read_text())
        self.assertNotIn('unslop', state['skills'])
        for folder in ('.agents', '.claude'):
            self.assertFalse((self.home / folder / 'skills/unslop').exists())
        for relative in ('.codex/AGENTS.md', '.claude/CLAUDE.md'):
            self.assertNotIn('unslop/SKILL.md', (self.home / relative).read_text())

    def test_add_skill_conflict_preserves_state_then_explicitly_backs_up(self):
        self.command('install', '--skip-skill', 'unslop')
        state_file = self.home / '.agent-workflow-skills/install.json'
        previous = state_file.read_bytes()
        original = self.home / '.claude/skills/unslop'
        original.mkdir()
        (original / 'SKILL.md').write_text('Local unslop')
        self.command('install', '--add-skill', 'unslop', ok=False)
        self.assertEqual(state_file.read_bytes(), previous)
        self.assertFalse((self.home / '.agents/skills/unslop').exists())
        self.assertEqual((original / 'SKILL.md').read_text(), 'Local unslop')
        self.command('install', '--add-skill', 'unslop', '--replace-skill', 'unslop')
        backups = list((self.home / '.agent-workflow-skills/backups').rglob('unslop/SKILL.md'))
        self.assertEqual([item.read_text() for item in backups], ['Local unslop'])
        for folder in ('.agents', '.claude'):
            self.assertEqual((self.home / folder / 'skills/unslop/SKILL.md').read_bytes(),
                             (self.repo / 'skills/unslop/SKILL.md').read_bytes())

    def test_add_skill_rejects_invalid_and_conflicting_options(self):
        for args in [('install', '--add-skill', '../unslop'),
                     ('install', '--add-skill', 'unslop', '--skip-skill', 'unslop'),
                     ('update', '--add-skill', 'unslop')]:
            self.command(*args, ok=False)
        self.assertFalse((self.home / '.agent-workflow-skills/install.json').exists())
        self.assertFalse((self.home / '.agents').exists())

    def test_adding_skill_rolls_back_links_backups_and_selection_on_failure(self):
        self.command('install', '--skip-skill', 'unslop')
        spec = importlib.util.spec_from_file_location('workflow_add_module', self.repo / 'scripts/workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state_dir = self.home / '.agent-workflow-skills'
        state_file = state_dir / 'install.json'
        previous = state_file.read_bytes()
        state = module.read_state(state_file)
        entrypoints = {path: (self.home / path).read_bytes()
                       for path in ('.codex/AGENTS.md', '.claude/CLAUDE.md')}
        original = self.home / '.claude/skills/unslop'
        original.mkdir()
        (original / 'SKILL.md').write_text('Local unslop')
        write = module.atomic_write

        def fail_state(path, content):
            if path == state_file:
                raise OSError('injected selection write failure')
            write(path, content)

        with patch.object(module, 'atomic_write', side_effect=fail_state):
            with self.assertRaisesRegex(OSError, 'injected selection write failure'):
                module.install(self.home, state_dir, state['clients'], state['skills'] + ['unslop'],
                               state['profiles'], state, {'unslop'})
        self.assertEqual(state_file.read_bytes(), previous)
        for path, content in entrypoints.items():
            self.assertEqual((self.home / path).read_bytes(), content)
        self.assertFalse((self.home / '.agents/skills/unslop').exists())
        self.assertEqual((original / 'SKILL.md').read_text(), 'Local unslop')

    def test_codex_follows_nonempty_override_precedence(self):
        default = self.home / '.codex/AGENTS.md'
        override = default.with_name('AGENTS.override.md')
        default.parent.mkdir()
        default.write_bytes(b'Private default')
        override.write_bytes(b' \r\n')
        self.command('install', '--client', 'codex')
        self.assertEqual(override.read_bytes(), b' \r\n')
        self.assertIn(b'model-router/SKILL.md', default.read_bytes())
        override.write_bytes(b'Private override\r\n')
        self.command('install')
        self.assertEqual(default.read_bytes(), b'Private default')
        self.assertTrue(override.read_bytes().startswith(b'Private override\r\n'))
        self.assertIn(b'model-router/SKILL.md', override.read_bytes())
        override.unlink()
        self.command('install')
        self.assertIn(b'model-router/SKILL.md', default.read_bytes())

    def test_bootstrap_rejects_unowned_or_changed_markers(self):
        entrypoint = self.home / '.claude/CLAUDE.md'
        entrypoint.parent.mkdir()
        malformed = b'Private text\n<!-- agent-workflow-skills:begin -- >\n'
        entrypoint.write_bytes(malformed)
        self.assertIn('managed markers', self.command('install', '--check', ok=False).stderr)
        self.assertEqual(entrypoint.read_bytes(), malformed)
        self.assertFalse((self.home / '.agents/skills').exists())
        entrypoint.write_bytes(b'Private text\n')
        self.command('install')
        edited = entrypoint.read_bytes().replace(b'For every request', b'Only on weekends')
        entrypoint.write_bytes(edited)
        self.assertIn('managed markers', self.command('install', ok=False).stderr)
        self.assertEqual(entrypoint.read_bytes(), edited)

    def test_version_one_state_without_bootstrap_upgrades(self):
        self.command('install', '--client', 'codex')
        entrypoint = self.home / '.codex/AGENTS.md'
        state_file = self.home / '.agent-workflow-skills/install.json'
        state = json.loads(state_file.read_text(encoding='utf-8'))
        del state['entrypoint_blocks']
        state_file.write_text(json.dumps(state), encoding='utf-8')
        entrypoint.write_bytes(b'Private instructions from before the upgrade')
        self.command('install')
        self.assertTrue(entrypoint.read_bytes().startswith(b'Private instructions from before the upgrade'))
        self.assertIn(b'model-router/SKILL.md', entrypoint.read_bytes())
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())

    def test_skipping_all_bootstrap_skills_leaves_entrypoints_alone(self):
        bootstrap = ('model-router', 'change-impact', 'unslop', 'explain-clearly', *NEW_SKILL_TRIGGERS)
        self.command('install', *(arg for skill in bootstrap for arg in ('--skip-skill', skill)))
        self.assertFalse((self.home / '.codex/AGENTS.md').exists())
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())

    def test_unslop_only_manages_both_client_entrypoints(self):
        self.install_only_skill('unslop')
        for relative, skill_root in (('.codex/AGENTS.md', '~/.agents/skills'),
                                     ('.claude/CLAUDE.md', '~/.claude/skills')):
            content = (self.home / relative).read_text()
            self.assertIn(skill_root + '/unslop/SKILL.md', content)
            self.assertNotIn('model-router/SKILL.md', content)
            self.assertNotIn('change-impact/SKILL.md', content)
            self.assertNotIn('explain-clearly/SKILL.md', content)
        self.command('install')

    def test_explanation_only_manages_both_client_entrypoints(self):
        self.install_only_skill('explain-clearly')
        state = json.loads((self.home / '.agent-workflow-skills/install.json').read_text())
        self.assertEqual(state['skills'], ['explain-clearly'])
        for relative, skill_root in (('.codex/AGENTS.md', '~/.agents/skills'),
                                     ('.claude/CLAUDE.md', '~/.claude/skills')):
            content = (self.home / relative).read_text()
            self.assertIn('Whenever you explain something, read `' + skill_root + '/explain-clearly/SKILL.md`', content)
            self.assertIn('Use diagram mode when requested at any task size', content)
            self.assertIn('proactively show a simple flow diagram for large tasks', content)
            self.assertEqual(content.count('/SKILL.md'), 1)
        self.command('install')

    def install_only_skill(self, selected):
        available = sorted(path.parent.name for path in (self.repo / 'skills').glob('*/SKILL.md'))
        skip = [arg for skill in available if skill != selected for arg in ('--skip-skill', skill)]
        self.command('install', '--without-profiles', *skip)

    def test_fresh_install_links_new_skills_and_generates_scoped_directives(self):
        self.command('install', '--without-profiles')
        for relative, skill_root in ENTRYPOINTS.items():
            content = (self.home / relative).read_text()
            for skill, trigger in NEW_SKILL_TRIGGERS.items():
                path = f'{skill_root}/{skill}/SKILL.md'
                directive, = [line for line in content.splitlines() if path in line]
                self.assertIn(trigger, directive)
                self.assertEqual((self.home / path.removeprefix('~/')).read_bytes(),
                                 (self.repo / 'skills' / skill / 'SKILL.md').read_bytes())

    def test_only_new_skill_manages_entrypoints(self):
        self.install_only_skill('code-simplification')
        for relative, skill_root in ENTRYPOINTS.items():
            content = (self.home / relative).read_text()
            self.assertIn(f'{skill_root}/code-simplification/SKILL.md', content)
            self.assertEqual(content.count('/SKILL.md'), 1)

    def test_review_only_activates_without_profiles_and_refreshes_old_blocks(self):
        self.install_only_skill('engineering-review')
        state_file = self.home / '.agent-workflow-skills/install.json'
        state = json.loads(state_file.read_text())
        self.assertFalse(state['profiles'])
        for relative, skill_root in ENTRYPOINTS.items():
            path = self.home / relative
            content = path.read_text()
            self.assertIn('including plain "review"', content)
            self.assertIn(f'{skill_root}/engineering-review/SKILL.md', content)
            self.assertFalse((self.home / relative.split('/')[0] / 'agents').exists())
            # Simulate the preceding installer, which selected this skill but
            # generated no entrypoint directive for it.
            path.unlink()
        state['entrypoint_blocks'] = {}
        state_file.write_text(json.dumps(state), encoding='utf-8')
        self.command('install', '--check')
        self.assertTrue(all(not (self.home / relative).exists() for relative in ENTRYPOINTS))
        self.command('install')
        for relative, skill_root in ENTRYPOINTS.items():
            self.assertIn(f'{skill_root}/engineering-review/SKILL.md', (self.home / relative).read_text())
        refreshed = json.loads(state_file.read_text())
        self.assertEqual(refreshed['skills'], state['skills'])
        self.assertEqual(refreshed['clients'], state['clients'])
        self.assertFalse(refreshed['profiles'])

    def test_codebase_design_only_links_both_clients_and_refreshes(self):
        self.install_only_skill('codebase-design')
        self.command('install')
        state = json.loads((self.home / '.agent-workflow-skills/install.json').read_text())
        self.assertEqual(state['skills'], ['codebase-design'])
        for relative, skill_root in ENTRYPOINTS.items():
            content = (self.home / relative).read_text()
            self.assertEqual(content.count('/SKILL.md'), 1)
            self.assertIn(f'{skill_root}/codebase-design/SKILL.md', content)
            for filename in ('SKILL.md', 'LICENSE'):
                self.assertEqual((self.home / skill_root.removeprefix('~/') / 'codebase-design' / filename).read_bytes(),
                                 (self.repo / 'skills/codebase-design' / filename).read_bytes())

    def test_existing_install_requires_explicit_multi_add_for_new_skills(self):
        skip = [arg for skill in NEW_SKILL_TRIGGERS for arg in ('--skip-skill', skill)]
        self.command('install', '--client', 'codex', '--without-profiles', *skip)
        state_file = self.home / '.agent-workflow-skills/install.json'
        state_before = state_file.read_bytes()
        self.command('install')
        self.assertEqual(state_file.read_bytes(), state_before)
        self.assertFalse(NEW_SKILL_TRIGGERS.keys() & set(json.loads(state_before)['skills']))
        path = self.home / '.codex/AGENTS.md'
        path.write_bytes(b'Private prefix\r\n' + path.read_bytes() + b'Private suffix\n')
        previous = path.read_bytes()
        for skill in NEW_SKILL_TRIGGERS:
            self.assertNotIn(f'/{skill}/SKILL.md'.encode(), previous)
            self.assertFalse((self.home / '.agents/skills' / skill).exists())
        add = [arg for skill in NEW_SKILL_TRIGGERS for arg in ('--add-skill', skill)]
        self.command('install', *add, '--check')
        self.assertEqual(state_file.read_bytes(), state_before)
        self.assertEqual(path.read_bytes(), previous)
        self.command('install', *add)
        refreshed = path.read_bytes()
        self.assertEqual(refreshed.split(b'<!-- agent-workflow-skills:begin -->')[0],
                         previous.split(b'<!-- agent-workflow-skills:begin -->')[0])
        self.assertTrue(refreshed.endswith(b'Private suffix\n'))
        old_state = json.loads(state_before)
        new_state = json.loads(state_file.read_bytes())
        self.assertEqual(new_state['clients'], old_state['clients'])
        self.assertEqual(new_state['profiles'], old_state['profiles'])
        self.assertEqual(set(new_state['skills']), set(old_state['skills']) | NEW_SKILL_TRIGGERS.keys())
        for skill in NEW_SKILL_TRIGGERS:
            self.assertEqual(refreshed.count(f'/{skill}/SKILL.md'.encode()), 1)
            self.assertTrue((self.home / '.agents/skills' / skill / 'SKILL.md').is_file())
        self.assertFalse((self.home / '.claude').exists())

    def test_skipped_explanation_stays_unselected_on_refresh(self):
        self.command('install', '--skip-skill', 'explain-clearly')
        self.command('install')
        state = json.loads((self.home / '.agent-workflow-skills/install.json').read_text())
        self.assertNotIn('explain-clearly', state['skills'])
        for relative in ('.codex/AGENTS.md', '.claude/CLAUDE.md'):
            self.assertNotIn('explain-clearly/SKILL.md', (self.home / relative).read_text())
        for folder in ('.agents', '.claude'):
            self.assertFalse((self.home / folder / 'skills/explain-clearly').exists())

    def test_add_explanation_preserves_selection_private_text_and_preflight(self):
        self.command('install', '--skip-skill', 'explain-clearly', '--without-profiles')
        state_file = self.home / '.agent-workflow-skills/install.json'
        previous_state = state_file.read_bytes()
        state = json.loads(previous_state)
        paths = [self.home / name for name in ('.codex/AGENTS.md', '.claude/CLAUDE.md')]
        for path in paths:
            path.write_bytes(b'Private prefix\r\n' + path.read_bytes() + b'Private suffix\r\n')
        before = [path.read_bytes() for path in paths]
        self.command('install', '--add-skill', 'explain-clearly', '--check')
        self.assertEqual(state_file.read_bytes(), previous_state)
        self.assertEqual([path.read_bytes() for path in paths], before)
        self.assertFalse((self.home / '.agents/skills/explain-clearly').exists())
        self.command('install', '--add-skill', 'explain-clearly')
        self.command('install')
        installed = json.loads(state_file.read_bytes())
        self.assertEqual(installed['clients'], state['clients'])
        self.assertEqual(installed['profiles'], state['profiles'])
        self.assertEqual(set(installed['skills']), set(state['skills']) | {'explain-clearly'})
        for path in paths:
            content = path.read_bytes()
            self.assertTrue(content.startswith(b'Private prefix\r\n'))
            self.assertTrue(content.endswith(b'Private suffix\r\n'))
            self.assertEqual(content.count(b'/explain-clearly/SKILL.md'), 1)
        for folder in ('.agents', '.claude'):
            self.assertEqual((self.home / folder / 'skills/explain-clearly/SKILL.md').read_bytes(),
                             (self.repo / 'skills/explain-clearly/SKILL.md').read_bytes())

    def test_failed_explanation_add_restores_entrypoints_selection_and_links(self):
        self.command('install', '--skip-skill', 'explain-clearly', '--without-profiles')
        spec = importlib.util.spec_from_file_location('workflow_explain_module', self.repo / 'scripts/workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state_dir = self.home / '.agent-workflow-skills'
        state_file = state_dir / 'install.json'
        previous = state_file.read_bytes()
        state = module.read_state(state_file)
        entrypoints = {path: (self.home / path).read_bytes()
                       for path in ('.codex/AGENTS.md', '.claude/CLAUDE.md')}
        write = module.atomic_write

        def fail_state(path, content):
            if path == state_file:
                raise OSError('injected explanation selection write failure')
            write(path, content)

        with patch.object(module, 'atomic_write', side_effect=fail_state):
            with self.assertRaisesRegex(OSError, 'injected explanation selection write failure'):
                module.install(self.home, state_dir, state['clients'],
                               state['skills'] + ['explain-clearly'], False, state, set())
        self.assertEqual(state_file.read_bytes(), previous)
        for path, content in entrypoints.items():
            self.assertEqual((self.home / path).read_bytes(), content)
        for folder in ('.agents', '.claude'):
            self.assertFalse((self.home / folder / 'skills/explain-clearly').exists())

    def seed_legacy_blocks(self, skill, old_directive=None):
        state_file = self.home / '.agent-workflow-skills/install.json'
        state = json.loads(state_file.read_bytes())
        for relative, skill_root in ENTRYPOINTS.items():
            path = self.home / relative
            lines = path.read_bytes().splitlines(keepends=True)
            skill_path = f'{skill_root}/{skill}/SKILL.md'
            directive, = [line for line in lines if skill_path.encode() in line]
            replacement = old_directive.format(path=skill_path).encode() + b'\n' if old_directive else b''
            block = b''.join(lines).replace(directive, replacement)
            path.write_bytes(b'Private prefix\r\n' + block + b'Private suffix\r\n')
            state['entrypoint_blocks'][relative]['hash'] = hashlib.sha256(block).hexdigest()
        state_file.write_text(json.dumps(state), encoding='utf-8')

    def test_refresh_adds_explanation_directive_for_older_blocks(self):
        self.command('install', '--without-profiles')
        self.seed_legacy_blocks('explain-clearly')
        self.command('install')
        for relative in ENTRYPOINTS:
            content = (self.home / relative).read_bytes()
            self.assertTrue(content.startswith(b'Private prefix\r\n'))
            self.assertTrue(content.endswith(b'Private suffix\r\n'))
            self.assertEqual(content.count(b'/explain-clearly/SKILL.md'), 1)

    def test_refresh_upgrades_old_explanation_wording(self):
        skip = [arg for skill in NEW_SKILL_TRIGGERS for arg in ('--skip-skill', skill)]
        self.command('install', '--without-profiles', *skip)
        self.seed_legacy_blocks(
            'explain-clearly',
            '- When the user asks for an explanation, why or how something works, a comparison or before/after, '
            'or says they do not understand, read `{path}` and apply it. Use simple words and helpful diagrams '
            'or before/after directly in chat.',
        )
        self.command('install')
        for relative in ENTRYPOINTS:
            content = (self.home / relative).read_bytes()
            self.assertTrue(content.startswith(b'Private prefix\r\n'))
            self.assertTrue(content.endswith(b'Private suffix\r\n'))
            self.assertEqual(content.count(b'/explain-clearly/SKILL.md'), 1)
            self.assertIn(b'Whenever you explain something', content)
            for skill in NEW_SKILL_TRIGGERS:
                self.assertNotIn(f'/{skill}/SKILL.md'.encode(), content)

    def test_refresh_upgrades_old_blocks_without_touching_private_text(self):
        # Model the previous installer, which selected Unslop without its directive.
        self.command('install')
        self.seed_legacy_blocks('unslop')
        state_file = self.home / '.agent-workflow-skills/install.json'
        old_state = json.loads(state_file.read_text())
        self.assertIn('unslop', old_state['skills'])
        paths = [self.home / relative for relative in ('.codex/AGENTS.md', '.claude/CLAUDE.md')]
        for path in paths:
            self.assertNotIn(b'/unslop/SKILL.md', path.read_bytes())
        before = [path.read_bytes() for path in paths]
        self.command('install', '--check')
        self.assertEqual([path.read_bytes() for path in paths], before)
        self.assertEqual(json.loads(state_file.read_text()), old_state)
        self.command('install')
        for path in paths:
            content = path.read_bytes()
            self.assertTrue(content.startswith(b'Private prefix\r\n'))
            self.assertTrue(content.endswith(b'Private suffix\r\n'))
            self.assertEqual(content.count(b'/unslop/SKILL.md'), 1)
        new_state = json.loads(state_file.read_text())
        self.assertEqual(new_state['skills'], old_state['skills'])
        self.assertNotEqual(new_state['entrypoint_blocks'], old_state['entrypoint_blocks'])

    def test_rollback_restores_backup_after_link_failure(self):
        spec = importlib.util.spec_from_file_location('workflow_test_module', self.repo / 'scripts/workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = self.home / '.agents/skills/engineering-review'
        original.mkdir(parents=True)
        (original / 'SKILL.md').write_text('Personal review rules')
        state_dir = self.home / '.agent-workflow-skills'
        with patch.object(module, 'directory_link', side_effect=OSError('injected link failure')):
            with self.assertRaises(OSError):
                module.install(self.home, state_dir, ['codex'], ['engineering-review'], False,
                               None, {'engineering-review'})
        self.assertEqual((original / 'SKILL.md').read_text(), 'Personal review rules')
        self.assertFalse((state_dir / 'install.json').exists())

    def test_lock_blocks_concurrent_install(self):
        state_dir = self.home / '.agent-workflow-skills'
        state_dir.mkdir()
        (state_dir / 'operation.lock').write_text('other process')
        result = self.command('install', ok=False)
        self.assertIn('Another operation', result.stderr)
        self.assertFalse((self.home / '.agents').exists())

    def test_failed_state_write_removes_links_and_restores_profiles(self):
        self.command('install')
        spec = importlib.util.spec_from_file_location('workflow_rollback_module', self.repo / 'scripts/workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state_dir = self.home / '.agent-workflow-skills'
        state = module.read_state(state_dir / 'install.json')
        new_profile = self.home / '.codex/agents/workflow-light-worker.toml'
        new_profile.unlink()
        del state['profile_hashes']['codex/workflow-light-worker.toml']
        module.atomic_write(state_dir / 'install.json', (json.dumps(state) + '\n').encode())
        profile = self.home / '.codex/agents/workflow-reviewer.toml'
        previous = profile.read_bytes()
        source = self.repo / 'codex/agents/workflow-reviewer.toml'
        source.write_text(source.read_text().replace('"medium"', '"high"'))
        link = self.home / '.agents/skills/change-impact'
        module.remove_directory_link(link)
        write = module.atomic_write

        def fail_state(path, content):
            if path.name == 'install.json':
                raise OSError('injected state write failure')
            write(path, content)

        with patch.object(module, 'atomic_write', side_effect=fail_state):
            with self.assertRaises(OSError):
                module.install(self.home, state_dir, state['clients'], state['skills'], True, state, set())
        self.assertFalse(os.path.lexists(link))
        self.assertTrue((self.repo / 'skills/change-impact/SKILL.md').exists())
        self.assertEqual(profile.read_bytes(), previous)
        self.assertFalse(new_profile.exists())
        self.assertEqual(module.read_state(state_dir / 'install.json'), state)

    def test_failed_state_write_restores_existing_entrypoint_and_removes_new_one(self):
        spec = importlib.util.spec_from_file_location('workflow_bootstrap_module', self.repo / 'scripts/workflow.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        state_dir = self.home / '.agent-workflow-skills'
        codex = self.home / '.codex/AGENTS.md'
        codex.parent.mkdir()
        original = b'Private instructions\r\nPreserve everything.'
        codex.write_bytes(original)
        write = module.atomic_write

        def fail_state(path, content):
            if path.name == 'install.json':
                raise OSError('injected state write failure')
            write(path, content)

        with patch.object(module, 'atomic_write', side_effect=fail_state):
            with self.assertRaisesRegex(OSError, 'injected state write failure'):
                module.install(self.home, state_dir, ['codex', 'claude'], ['model-router'], False, None, set())
        self.assertEqual(codex.read_bytes(), original)
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())
        self.assertFalse((self.home / '.agents/skills/model-router').exists())
        self.assertFalse((state_dir / 'install.json').exists())

    def test_fast_forward_updates_both_devices_and_profiles(self):
        device = self.remote_pair()
        skill = self.repo / 'skills/change-impact/SKILL.md'
        skill.write_text(skill.read_text() + '\nUpdated upstream.\n')
        profile = self.repo / 'codex/agents/workflow-reviewer.toml'
        profile.write_text(profile.read_text().replace('"medium"', '"high"'))
        installer = self.repo / 'scripts/workflow.py'
        installer.write_bytes(installer.read_bytes().replace(b'For every request, read', b'On each request, read'))
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Update fixture')
        self.git(self.repo, 'push')
        self.command('update', repo=device)
        for folder in ('.agents', '.claude'):
            self.assertIn('Updated upstream.', (self.home / folder / 'skills/change-impact/SKILL.md').read_text())
        self.assertIn('"high"', (self.home / '.codex/agents/workflow-reviewer.toml').read_text())
        self.assertIn('On each request, read', (self.home / '.codex/AGENTS.md').read_text())

    def test_dirty_and_missing_upstream_refuse_update(self):
        self.command('install')
        self.initialize()
        result = self.command('update', ok=False)
        self.assertIn('upstream', result.stderr.lower())
        (self.repo / 'untracked.txt').write_text('preserve this')
        result = self.command('update', ok=False)
        self.assertIn('local changes', result.stderr)

    def test_diverged_branch_refuses_update(self):
        device = self.remote_pair()
        (device / 'local.txt').write_text('local')
        self.git(device, 'add', '.')
        self.git(device, 'commit', '-m', 'Local change')
        before = self.git(device, 'rev-parse', 'HEAD')
        (self.repo / 'remote.txt').write_text('remote')
        self.git(self.repo, 'add', '.')
        self.git(self.repo, 'commit', '-m', 'Remote change')
        self.git(self.repo, 'push')
        self.command('update', repo=device, ok=False)
        self.assertEqual(self.git(device, 'rev-parse', 'HEAD'), before)


if __name__ == '__main__':
    unittest.main()
