"""Read-only runtime probe, streamed to the configured Hermes Python with -B."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys


class SkillMetadataError(Exception):
    pass


def inspect_root(root, skill, parse_frontmatter, excluded_dirs, support_dirs):
    if not root.exists():
        if root.is_symlink():
            raise OSError('unavailable linked root')
        return {'path': str(root), 'exists': False, 'matches': [], 'unscanned_links': []}
    if not root.is_dir():
        raise OSError('not a directory')
    matches = set()
    links = []
    if skill:
        direct = root / skill
        if direct.exists() or direct.is_symlink():
            matches.add(str(direct))

        def onerror(error):
            raise error

        # Use Hermes's exclusions with a strict walker: its stock iterator
        # follows links and silently skips traversal errors.
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
            current = Path(directory)
            has_skill = 'SKILL.md' in files
            dirs[:] = [name for name in dirs if name not in excluded_dirs
                       and not (has_skill and name in support_dirs)]
            if has_skill:
                skill_file = current / 'SKILL.md'
                if current.name == skill:
                    matches.add(str(current))
                if skill_file.is_symlink():
                    links.append(str(skill_file))
                else:
                    try:
                        metadata, _ = parse_frontmatter(skill_file.read_text(encoding='utf-8'))
                        declared_name = metadata.get('name', current.name)
                        if not isinstance(declared_name, str):
                            raise SkillMetadataError()
                    except (OSError, UnicodeError):
                        raise
                    except Exception as error:
                        raise SkillMetadataError() from error
                    if declared_name == skill:
                        matches.add(str(current))
            for name in dirs:
                path = current / name
                if path.is_symlink():
                    links.append(str(path))
                    if name == skill:
                        matches.add(str(path))
    return {'path': str(root), 'exists': True, 'matches': sorted(matches), 'unscanned_links': sorted(links)}


def probe(profile, skill, project, hermes_root, data_root):
    configured_root = Path(data_root).resolve()
    if not configured_root.is_dir():
        return {'status': 'error', 'error': 'data_root_not_found'}
    # This process only: pin the instance before importing Hermes modules.
    os.environ['HERMES_HOME'] = str(configured_root)
    sys.path.insert(0, hermes_root)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from hermes_cli.profiles import normalize_profile_name, get_profile_dir, profile_exists
            normalized = normalize_profile_name(profile)
            home = Path(get_profile_dir(normalized))
            expected_home = configured_root if normalized == 'default' else configured_root / 'profiles' / normalized
            if home.resolve() != expected_home or not home.resolve().is_relative_to(configured_root):
                return {'status': 'error', 'error': 'profile_root_mismatch'}
            exists = profile_exists(normalized) and home.is_dir()
    except (ImportError, AttributeError):
        return {'status': 'error', 'error': 'unsupported_hermes_profile_api'}
    except (ValueError, SystemExit):
        return {'status': 'error', 'error': 'invalid_profile'}
    if not exists:
        return {'status': 'error', 'error': 'profile_not_found', 'profile': normalized}
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from agent.skill_utils import parse_frontmatter, EXCLUDED_SKILL_DIRS, SKILL_SUPPORT_DIRS
    except (ImportError, AttributeError):
        return {'status': 'error', 'error': 'unsupported_hermes_skill_api'}

    def inspect(path):
        return inspect_root(path, skill, parse_frontmatter, EXCLUDED_SKILL_DIRS, SKILL_SUPPORT_DIRS)

    roots = [inspect(home / 'skills')]
    if project:
        project_path = Path(project)
        if not project_path.is_dir():
            return {'status': 'error', 'error': 'project_not_found'}
        roots.extend(inspect(project_path / folder / 'skills') for folder in ('.hermes', '.agents'))
    conflicts = [match for root in roots for match in root['matches']]
    incomplete = any(root['unscanned_links'] for root in roots)
    result = {
        'status': 'conflict' if conflicts else 'error' if incomplete else 'ok',
        'profile': normalized,
        'data_root': str(configured_root),
        'profile_home': str(home),
        'skills_dir': str(home / 'skills'),
        'destination': str(home / 'skills' / skill) if skill else None,
        'runtime_uid': os.geteuid(),
        'roots_checked': roots,
        'conflicts': conflicts,
        'conflict_check': 'partial' if incomplete else 'checked' if skill else 'not_requested',
        'project_check': 'checked' if project else 'not_requested',
        'limitations': ['External skill roots, legacy flat Markdown skills and project trust are not inspected.',
                        'Symlinked subdirectories and skill files are reported but not followed.',
                        'This checks locations and declared names, not effective skill discovery or model execution.'],
    }
    if incomplete:
        result['error'] = 'skill_scan_incomplete'
    return result


if __name__ == '__main__':
    try:
        result = probe(*sys.argv[1:])
    except PermissionError:
        result = {'status': 'error', 'error': 'runtime_permission_denied'}
    except (SkillMetadataError, UnicodeError):
        result = {'status': 'error', 'error': 'skill_metadata_invalid'}
    except Exception:
        result = {'status': 'error', 'error': 'runtime_probe_failed'}
    print(json.dumps(result, ensure_ascii=False))
