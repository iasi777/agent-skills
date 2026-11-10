#!/usr/bin/env python3
"""Locate a named Hermes profile without changing the runtime. JSON output only."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
TOKEN = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.@-]*\Z')


def fail(code, **fields):
    return {'status': 'error', 'error': code, **fields}


def command_for(target, profile, skill, project):
    for key in ('hermes_root', 'python', 'data_root'):
        if not isinstance(target.get(key), str) or not target[key].startswith('/') or '\x00' in target[key]:
            raise ValueError('invalid runtime path')
    args = [target['python'], '-B', '-', profile, skill or '', project or '', target['hermes_root'], target['data_root']]
    container = target.get('container')
    if container:
        if not TOKEN.fullmatch(container):
            raise ValueError('invalid container')
        args = ['podman', 'exec', '-i', '-w', target['hermes_root'], container, *args]
    if target.get('transport') == 'ssh':
        host = target.get('host', '')
        if not TOKEN.fullmatch(host):
            raise ValueError('invalid SSH alias')
        return ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                '-o', 'ConnectTimeout=10', host, shlex.join(args)]
    if target.get('transport') == 'local':
        return args
    raise ValueError('invalid transport')


def query(config_path, target_name, profile, skill=None, project=None, timeout=30):
    try:
        config = json.loads(Path(config_path).expanduser().read_text())
        if not isinstance(config, dict) or not isinstance(config.get('targets'), dict):
            raise ValueError('invalid config')
        if config['schema_version'] != 1:
            return fail('unsupported_config_version')
        selected = target_name or config.get('default_target')
        if not selected or selected not in config['targets']:
            return fail('target_not_configured')
        target = config['targets'][selected]
        if not isinstance(target, dict):
            raise ValueError('invalid target')
        command = command_for(target, profile, skill, project)
    except FileNotFoundError:
        return fail('config_missing')
    except (OSError, ValueError, KeyError, TypeError):
        return fail('config_invalid')
    context = {'target': selected, 'profile': profile,
               'runtime': {k: target[k] for k in ('transport', 'host', 'container', 'hermes_root', 'python', 'data_root') if k in target}}
    try:
        probe = Path(__file__).with_name('hermes_probe.py').read_text()
        process = subprocess.run(command, input=probe, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return fail('timeout', **context)
    except OSError:
        return fail('launcher_unavailable', **context)
    if process.returncode:
        code = 'ssh_unavailable' if target['transport'] == 'ssh' and process.returncode == 255 else 'runtime_unavailable'
        return fail(code, exit_code=process.returncode, **context)
    try:
        result = json.loads(process.stdout)
        if not isinstance(result, dict) or result.get('status') not in ('ok', 'conflict', 'error'):
            raise ValueError('invalid probe response')
        return {**context, **result}
    except ValueError:
        return fail('unexpected_probe_response', **context)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='~/.config/writing-skills/hermes-targets.json')
    parser.add_argument('--target', help='Configured runtime name; otherwise use the configured default')
    parser.add_argument('--profile', required=True, help='Explicit Hermes profile name, including default when intended')
    parser.add_argument('--skill', help='Skill folder name to check for conflicts')
    parser.add_argument('--project-dir', help='Absolute project path inside the runtime; inspect its project skill roots')
    parser.add_argument('--timeout', type=int, default=30, help='Total query deadline in seconds (1–120)')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.profile) or not 1 <= args.timeout <= 120:
        parser.error('Provide a profile name (letters, digits, hyphens, underscores; max 64) and a timeout between 1 and 120')
    if args.skill and (len(args.skill) > 64 or not NAME.fullmatch(args.skill)):
        parser.error('Invalid skill folder name')
    if args.project_dir and not args.project_dir.startswith('/'):
        parser.error('--project-dir must be an absolute runtime path')
    result = query(args.config, args.target, args.profile, args.skill, args.project_dir, args.timeout)
    print(json.dumps(result, ensure_ascii=False))
    return {'ok': 0, 'conflict': 3, 'error': 1}[result['status']]


if __name__ == '__main__':
    sys.exit(main())
