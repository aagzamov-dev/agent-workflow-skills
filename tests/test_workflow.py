"""Isolated filesystem and local-Git integration checks; no AI clients are launched."""

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
        self.command('install', '--skip-skill', 'model-router', '--skip-skill', 'change-impact',
                     '--skip-skill', 'unslop', '--skip-skill', 'explain-clearly')
        self.assertFalse((self.home / '.codex/AGENTS.md').exists())
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())

    def test_unslop_only_manages_both_client_entrypoints(self):
        self.command('install', '--skip-skill', 'model-router', '--skip-skill', 'change-impact',
                     '--skip-skill', 'engineering-review', '--skip-skill', 'prompt-craft',
                     '--skip-skill', 'explain-clearly', '--without-profiles')
        for relative, skill_root in (('.codex/AGENTS.md', '~/.agents/skills'),
                                     ('.claude/CLAUDE.md', '~/.claude/skills')):
            content = (self.home / relative).read_text()
            self.assertIn(skill_root + '/unslop/SKILL.md', content)
            self.assertNotIn('model-router/SKILL.md', content)
            self.assertNotIn('change-impact/SKILL.md', content)
            self.assertNotIn('explain-clearly/SKILL.md', content)
        self.command('install')

    def test_explanation_only_manages_both_client_entrypoints(self):
        self.command('install', '--skip-skill', 'model-router', '--skip-skill', 'change-impact',
                     '--skip-skill', 'engineering-review', '--skip-skill', 'prompt-craft',
                     '--skip-skill', 'unslop', '--without-profiles')
        state = json.loads((self.home / '.agent-workflow-skills/install.json').read_text())
        self.assertEqual(state['skills'], ['explain-clearly'])
        for relative, skill_root in (('.codex/AGENTS.md', '~/.agents/skills'),
                                     ('.claude/CLAUDE.md', '~/.claude/skills')):
            content = (self.home / relative).read_text()
            self.assertIn(skill_root + '/explain-clearly/SKILL.md', content)
            self.assertNotIn('model-router/SKILL.md', content)
            self.assertNotIn('unslop/SKILL.md', content)
        self.command('install')

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

    def test_refresh_upgrades_old_explanation_blocks(self):
        installer = self.repo / 'scripts/workflow.py'
        current = installer.read_text()
        old = current.replace(
            "    if 'explain-clearly' in skills:\n" + next(
                line + '\n' for line in current.splitlines()
                if 'lines.append' in line and '/explain-clearly/SKILL.md' in line), '')
        self.assertNotEqual(old, current)
        installer.write_text(old)
        self.command('install', '--without-profiles')
        paths = [self.home / name for name in ('.codex/AGENTS.md', '.claude/CLAUDE.md')]
        for path in paths:
            self.assertNotIn(b'/explain-clearly/SKILL.md', path.read_bytes())
            path.write_bytes(b'Private prefix\r\n' + path.read_bytes() + b'Private suffix\r\n')
        installer.write_text(current)
        self.command('install')
        for path in paths:
            content = path.read_bytes()
            self.assertTrue(content.startswith(b'Private prefix\r\n'))
            self.assertTrue(content.endswith(b'Private suffix\r\n'))
            self.assertEqual(content.count(b'/explain-clearly/SKILL.md'), 1)

    def test_refresh_upgrades_old_blocks_without_touching_private_text(self):
        # Model the previous installer, which selected Unslop without its directive.
        installer = self.repo / 'scripts/workflow.py'
        current = installer.read_text()
        old = current.replace(
            "    if 'unslop' in skills:\n" + next(
                line + '\n' for line in current.splitlines()
                if 'lines.append' in line and '/unslop/SKILL.md' in line), '')
        self.assertNotEqual(old, current)
        installer.write_text(old)
        self.command('install')
        state_file = self.home / '.agent-workflow-skills/install.json'
        old_state = json.loads(state_file.read_text())
        self.assertIn('unslop', old_state['skills'])
        paths = [self.home / relative for relative in ('.codex/AGENTS.md', '.claude/CLAUDE.md')]
        for path in paths:
            self.assertNotIn(b'/unslop/SKILL.md', path.read_bytes())
            path.write_bytes(b'Private prefix\r\n' + path.read_bytes() + b'Private suffix\r\n')
        before = [path.read_bytes() for path in paths]
        installer.write_text(current)
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
