#!/usr/bin/env python3
"""Install linked skills and update this checkout using Python's standard library."""

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
BLOCK_START = b'<!-- agent-workflow-skills:begin -->'
BLOCK_END = b'<!-- agent-workflow-skills:end -->'
BLOCK_MARKER = b'<!-- agent-workflow-skills:'


@dataclass
class EntrypointEdit:
    previous: bytes | None
    content: bytes
    backup: bool


def exists(path):
    return os.path.lexists(path)


def is_junction(path):
    if os.name != 'nt' or not exists(path):
        return False
    return os.lstat(path).st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.workflow-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def directory_link(source, destination):
    if os.name == 'nt':
        environment = os.environ.copy()
        environment['WORKFLOW_LINK_SOURCE'] = str(source)
        environment['WORKFLOW_LINK_DESTINATION'] = str(destination)
        command = (
            "$ErrorActionPreference = 'Stop'; "
            'New-Item -ItemType Junction -Path $env:WORKFLOW_LINK_DESTINATION '
            '-Target $env:WORKFLOW_LINK_SOURCE | Out-Null'
        )
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
            env=environment, capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode:
            raise RuntimeError(f'Cannot create directory junction: {result.stderr.strip()}')
    else:
        destination.symlink_to(source, target_is_directory=True)


def remove_directory_link(path):
    # Never recurse through a link into the source checkout.
    if path.is_symlink():
        path.unlink()
    elif is_junction(path):
        path.rmdir()
    else:
        raise RuntimeError(f'Refusing to remove a non-link directory: {path}')


def matching_link(destination, source):
    is_link = destination.is_symlink()
    if os.name == 'nt':
        is_link = is_link or is_junction(destination)
    return is_link and destination.resolve() == source.resolve()


def locations(home):
    # --home supplies an isolated installation root, including in tests.
    return {
        'codex': (home / '.agents/skills', home / '.codex/agents'),
        'claude': (home / '.claude/skills', home / '.claude/agents'),
    }


def read_entrypoint(path):
    if not exists(path):
        return None
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or getattr(info, 'st_reparse_tag', 0):
        raise RuntimeError(f'Global instructions must be a regular file: {path}')
    content = path.read_bytes()
    try:
        content.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise RuntimeError(f'Global instructions must use UTF-8: {path}') from None
    return content


def split_managed_block(path, content, record):
    data = content or b''
    # Leave the BOM in place, including when the file originally held only a BOM.
    bom_length = 3 if data.startswith(b'\xef\xbb\xbf') else 0
    if record is None and BLOCK_MARKER not in data:
        return data, b''
    if record and data.count(BLOCK_MARKER) == 2 and data.count(BLOCK_START) == data.count(BLOCK_END) == 1:
        start = data.index(BLOCK_START)
        end = data.index(BLOCK_END) + len(BLOCK_END)
        if data[end:end + 2] == b'\r\n':
            end += 2
        elif data[end:end + 1] == b'\n':
            end += 1
        separator = record['separator'].encode('ascii')
        offset = start - len(separator)
        if (bom_length <= offset <= start < end and data[offset:start] == separator
                and (start == bom_length or data[start - 1:start] == b'\n')
                and hashlib.sha256(data[offset:end]).hexdigest() == record['hash']):
            return data[:offset], data[end:]
    raise RuntimeError(f'Global instructions contain changed or unrecognized managed markers: {path}. '
                       'Reconcile the managed block before installing.')


def add_managed_block(content, client, skills):
    newline = b'\r\n' if b'\r\n' in content else b'\n'
    separator = b'' if not content.removeprefix(b'\xef\xbb\xbf') or content.endswith(b'\n') else newline
    skill_root = '~/.agents/skills' if client == 'codex' else '~/.claude/skills'
    lines = [BLOCK_START.decode('ascii'), '']
    if 'model-router' in skills:
        lines.append(f'- For every request, read `{skill_root}/model-router/SKILL.md` and apply its routing policy.')
    if 'change-impact' in skills:
        lines.append(f'- Before meaningful implementation, read `{skill_root}/change-impact/SKILL.md`.')
    lines.extend(['', BLOCK_END.decode('ascii'), ''])
    block = separator + newline.join(line.encode('ascii') for line in lines)
    record = {'hash': hashlib.sha256(block).hexdigest(), 'separator': separator.decode('ascii')}
    return content + block, record


def plan_entrypoints(home, clients, skills, state):
    previous_blocks = (state or {}).get('entrypoint_blocks', {})
    wanted = {'model-router', 'change-impact'}.intersection(skills)
    plans = []
    blocks = {}
    for client in clients:
        if client == 'codex':
            default = '.codex/AGENTS.md'
            override = '.codex/AGENTS.override.md'
            override_content = None
            if wanted or override in previous_blocks:
                override_content = read_entrypoint(home / override)
            # A managed block alone must not give the override file precedence.
            override_private = b''
            if override_content is not None:
                override_private = b''.join(split_managed_block(
                    home / override, override_content, previous_blocks.get(override),
                ))
            active = override if override_private.decode('utf-8-sig').strip() else default
            candidates = (default, override)
        else:
            active = '.claude/CLAUDE.md'
            candidates = (active,)
        for key in candidates:
            should_manage = key == active and wanted
            previous_block = previous_blocks.get(key)
            if not should_manage and previous_block is None:
                continue
            path = home / key
            previous = override_content if client == 'codex' and key == override else read_entrypoint(path)
            if previous is None and not should_manage:
                continue
            prefix, suffix = split_managed_block(path, previous, previous_block)
            content = prefix
            if should_manage:
                content, blocks[key] = add_managed_block(prefix, client, skills)
            content += suffix
            if content != previous:
                plans.append(('entrypoint', EntrypointEdit(previous, content, previous_block is None), path))
    return plans, blocks


def read_state(state_file):
    if not state_file.exists():
        return None
    state = json.loads(state_file.read_text(encoding='utf-8'))
    if state.get('version') != 1:
        raise RuntimeError('Unsupported installation state version.')
    if Path(state['repo']).resolve() != REPO:
        raise RuntimeError('This home is registered to another checkout. Use that checkout.')
    return state


@contextmanager
def installation_lock(state_dir):
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = state_dir / 'operation.lock'
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise RuntimeError(
            f'Another operation may be running. If it has exited, remove the stale lock: {lock}'
        ) from None
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink()


def make_plan(home, clients, skills, profiles, state, replacements):
    plans = []
    conflicts = []
    installed_profiles = (state or {}).get('profile_hashes', {})
    for client in clients:
        skill_root, agent_root = locations(home)[client]
        for name in skills:
            source = REPO / 'skills' / name
            if not (source / 'SKILL.md').is_file():
                raise RuntimeError(f'Selected skill is missing: {name}. Resolve it before updating.')
            destination = skill_root / name
            if matching_link(destination, source):
                continue
            if exists(destination) and name not in replacements:
                conflicts.append(str(destination))
            else:
                plans.append(('skill', source, destination))
        if profiles:
            suffix = '.toml' if client == 'codex' else '.md'
            for name in ('workflow-planner', 'workflow-reviewer', 'workflow-worker'):
                source = REPO / client / 'agents' / (name + suffix)
                if not source.is_file():
                    raise RuntimeError(f'Missing profile: {source}')
                destination = agent_root / source.name
                key = f'{client}/{source.name}'
                if exists(destination):
                    if destination.is_symlink() or not destination.is_file():
                        conflicts.append(str(destination))
                        continue
                    current = digest(destination)
                    previous = installed_profiles.get(key)
                    if previous is not None and current != previous:
                        conflicts.append(str(destination))
                        continue
                    if previous is None and current != digest(source):
                        conflicts.append(str(destination))
                        continue
                    if current == digest(source):
                        continue
                plans.append(('profile', source, destination))
    if conflicts:
        raise RuntimeError(
            'Existing files require a decision; nothing was installed:\n  '
            + '\n  '.join(conflicts)
            + '\nCompare or skip conflicting skills. To back up and replace a skill, '
            'use install --replace-skill NAME. Locally edited profiles require manual reconciliation.'
        )
    entrypoints, blocks = plan_entrypoints(home, clients, skills, state)
    return plans + entrypoints, blocks


def install(home, state_dir, clients, skills, profiles, state, replacements, check=False):
    plans, blocks = make_plan(home, clients, skills, profiles, state, replacements)
    for kind, source, destination in plans:
        if kind == 'entrypoint':
            print(f'{kind}: {destination}')
        else:
            print(f'{kind}: {destination} <- {source}')
    if check:
        print('Installation preflight passed. No installed files changed.')
        return
    undo = []
    try:
        for kind, source, destination in plans:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if kind == 'skill':
                if exists(destination):
                    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    backup = state_dir / 'backups' / timestamp / destination.relative_to(home)
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    destination.rename(backup)
                    undo.append(('backup', destination, backup))
                    print(f'Backup saved: {backup}')
                directory_link(source, destination)
                undo.append(('link', destination, None))
            elif kind == 'entrypoint':
                if read_entrypoint(destination) != source.previous:
                    raise RuntimeError(f'Global instructions changed during installation: {destination}')
                if source.previous is not None and source.backup:
                    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    backup = state_dir / 'backups' / timestamp / destination.relative_to(home)
                    atomic_write(backup, source.previous)
                    print(f'Backup saved: {backup}')
                atomic_write(destination, source.content)
                undo.append(('entrypoint', destination, source.previous))
            else:
                previous = destination.read_bytes() if destination.exists() else None
                atomic_write(destination, source.read_bytes())
                undo.append(('profile', destination, previous))
        hashes = {}
        if profiles:
            for client in clients:
                agent_root = locations(home)[client][1]
                suffix = '.toml' if client == 'codex' else '.md'
                for name in ('workflow-planner', 'workflow-reviewer', 'workflow-worker'):
                    filename = name + suffix
                    hashes[f'{client}/{filename}'] = digest(agent_root / filename)
        new_state = {
            'version': 1, 'repo': str(REPO), 'clients': clients, 'skills': skills,
            'profiles': profiles, 'profile_hashes': hashes, 'entrypoint_blocks': blocks,
        }
        atomic_write(state_dir / 'install.json', (json.dumps(new_state, indent=2) + '\n').encode())
    except BaseException:
        for action, destination, previous in reversed(undo):
            if action == 'link':
                remove_directory_link(destination)
            elif action == 'backup':
                previous.rename(destination)
            elif previous is None:
                destination.unlink()
            else:
                atomic_write(destination, previous)
        raise
    print('Installed. Start a fresh Codex or Claude session to load current instructions.')


def git(*arguments):
    result = subprocess.run(
        ['git', '-C', str(REPO), *arguments], capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Git command failed.')
    return result.stdout.strip()


def update(home, state_dir, state):
    if state is None:
        raise RuntimeError('Run install before update.')
    if Path(git('rev-parse', '--show-toplevel')).resolve() != REPO:
        raise RuntimeError('The checkout must be its own Git repository.')
    if git('status', '--porcelain', '--untracked-files=all'):
        raise RuntimeError('Checkout has local changes. Commit or resolve them before update.')
    if not git('branch', '--show-current'):
        raise RuntimeError('Detached HEAD. Select your intended branch before update.')
    git('rev-parse', '--verify', 'HEAD')
    git('rev-parse', '--abbrev-ref', '@{upstream}')
    make_plan(home, state['clients'], state['skills'], state['profiles'], state, set())
    print(git('-c', 'rebase.autoStash=false', '-c', 'merge.autoStash=false',
              'pull', '--ff-only', '--no-rebase'))
    # Use the updated installer in a fresh process after this process releases its lock.
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['install', 'update'])
    parser.add_argument('--home', type=Path, help='Installation home (default: current user)')
    parser.add_argument('--client', choices=['codex', 'claude', 'both'], default=None)
    parser.add_argument('--skip-skill', action='append', default=[])
    parser.add_argument('--replace-skill', action='append', default=[], help='Back up a conflicting skill before linking it')
    parser.add_argument('--without-profiles', action='store_true')
    parser.add_argument('--check', action='store_true', help='Preflight installation without changing installed files')
    args = parser.parse_args()
    if args.command == 'update' and (args.client or args.skip_skill or args.replace_skill or args.without_profiles or args.check):
        parser.error('update uses saved installation choices; install manages options')
    home = (args.home or Path.home()).expanduser().resolve()
    if args.home is None:
        for variable, default in [('CODEX_HOME', home / '.codex'), ('CLAUDE_CONFIG_DIR', home / '.claude')]:
            override = os.environ.get(variable)
            if override and Path(override).expanduser().resolve() != default:
                raise RuntimeError(f'{variable} points to a custom configuration directory. '
                                   'This installer supports standard home locations; configure links manually.')
    state_dir = home / '.agent-workflow-skills'
    refresh = False
    with installation_lock(state_dir):
        state = read_state(state_dir / 'install.json')
        if args.command == 'update':
            refresh = update(home, state_dir, state)
        else:
            available = sorted(path.parent.name for path in (REPO / 'skills').glob('*/SKILL.md'))
            unknown = (set(args.skip_skill) | set(args.replace_skill)) - set(available)
            if unknown:
                parser.error('Unknown skill names: ' + ', '.join(sorted(unknown)))
            if set(args.skip_skill) & set(args.replace_skill):
                parser.error('A skill cannot be both skipped and replaced.')
            clients = ['codex', 'claude']
            skills = [name for name in available if name not in args.skip_skill]
            profiles = not args.without_profiles
            if state:
                clients, skills, profiles = state['clients'], state['skills'], state['profiles']
                if args.client or args.skip_skill or args.without_profiles:
                    parser.error('This home already has saved choices. Reinstall without selection flags.')
            elif args.client and args.client != 'both':
                clients = [args.client]
            install(home, state_dir, clients, skills, profiles, state, set(args.replace_skill), args.check)
    if refresh:
        result = subprocess.run([sys.executable, str(REPO / 'scripts/workflow.py'), 'install', '--home', str(home)])
        if result.returncode:
            print('Git updated, but installation refresh failed. Resolve the reported issue and rerun install.', file=sys.stderr)
        return result.returncode
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
