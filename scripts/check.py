#!/usr/bin/env python3
"""Check the collection's package layout, local links and Python syntax offline."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    skills = sorted(path for path in (ROOT / 'skills').iterdir() if path.is_dir())
    if not skills:
        errors.append('No skill packages found')
    for skill in skills:
        entry = skill / 'SKILL.md'
        if not entry.is_file():
            errors.append(f'{skill.relative_to(ROOT)}: missing SKILL.md')
            continue
        content = entry.read_text(encoding='utf-8')
        header = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', content, re.S)
        if not header:
            errors.append(f'{entry.relative_to(ROOT)}: missing frontmatter')
            continue
        name = re.search(r'^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$', header[1], re.M)
        if not name or name[1] != skill.name or len(skill.name) > 64:
            errors.append(f'{entry.relative_to(ROOT)}: name must match folder')
        if not re.search(r'^description:\s*\S', header[1], re.M):
            errors.append(f'{entry.relative_to(ROOT)}: missing description')
        if not re.search(r'^metadata:\s*\n(?:[ \t]+.*\n)*?[ \t]+version:\s*\S', header[1], re.M):
            errors.append(f'{entry.relative_to(ROOT)}: missing metadata.version')

    for path in ROOT.rglob('*'):
        if '.git' in path.parts or '__pycache__' in path.parts:
            continue
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            errors.append(f'{relative}: package source must not depend on a local symlink')
            continue
        if not path.is_file():
            continue
        try:
            if path.suffix == '.py':
                ast.parse(path.read_text(encoding='utf-8'), filename=str(relative))
            elif path.suffix == '.json':
                json.loads(path.read_text(encoding='utf-8'))
            elif path.suffix == '.md' and not path.name.endswith('.template.md'):
                text = path.read_text(encoding='utf-8')
                # Template examples in fenced code are not actual document links.
                text = re.sub(r'```.*?```', '', text, flags=re.S)
                for target in re.findall(r'\]\(([^)\s]+)\)', text):
                    if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                        continue
                    target = unquote(target.split('#', 1)[0])
                    resolved = (path.parent / target).resolve()
                    if not resolved.is_relative_to(ROOT) or not resolved.exists():
                        errors.append(f'{relative}: invalid local link {target}')
                    if relative.parts[0] == 'skills':
                        package = ROOT / 'skills' / relative.parts[1]
                        if not resolved.is_relative_to(package):
                            errors.append(f'{relative}: package link escapes its installable folder: {target}')
        except (OSError, UnicodeError, ValueError, SyntaxError) as error:
            errors.append(f'{relative}: {type(error).__name__}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Checked {len(skills)} skill packages, resource links, JSON and Python syntax.')
    return 0


if __name__ == '__main__':
    sys.exit(check())
