import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
spec = importlib.util.spec_from_file_location('hermes_target', SCRIPTS / 'hermes_target.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        package = self.root / 'hermes_cli'
        package.mkdir()
        (package / '__init__.py').write_text('')
        (package / 'profiles.py').write_text('''from pathlib import Path
import os
ROOT = Path(os.environ['HERMES_HOME'])
def normalize_profile_name(name):
    if name not in ('chosen', 'missing'): raise ValueError('invalid')
    return name
def get_profile_dir(name): return ROOT / 'profiles' / name
def profile_exists(name): return get_profile_dir(name).is_dir()
''')
        helpers = self.root / 'agent'
        helpers.mkdir()
        (helpers / '__init__.py').write_text('')
        (helpers / 'skill_utils.py').write_text("""import json
EXCLUDED_SKILL_DIRS = {'node_modules', '.archive'}
SKILL_SUPPORT_DIRS = {'scripts', 'references', 'assets', 'templates'}
def parse_frontmatter(text):
    if not text.startswith('---'): return {}, text
    return json.loads(text.split('---', 2)[1]), ''
""")
        self.data = self.root / 'data'
        self.home = self.data / 'profiles/chosen'
        self.home.mkdir(parents=True)
        self.config = self.root / 'targets.json'
        self.config.write_text(json.dumps({'schema_version': 1, 'default_target': 'test', 'targets': {
            'test': {'transport': 'local', 'hermes_root': str(self.root), 'python': sys.executable, 'data_root': str(self.data)}}}))

    def test_named_profile_and_no_writes(self):
        before = sorted(str(p) for p in self.root.rglob('*'))
        result = client.query(self.config, None, 'chosen', 'example')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['destination'], str(self.home / 'skills/example'))
        self.assertFalse((self.home / 'skills').exists())
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob('*')))

    def test_missing_profile_never_falls_back(self):
        result = client.query(self.config, None, 'missing')
        self.assertEqual(result['error'], 'profile_not_found')
        self.assertNotIn('destination', result)

    def test_existing_nested_and_project_skills(self):
        nested = self.home / 'skills/category/example'
        nested.mkdir(parents=True)
        (nested / 'SKILL.md').write_text('private content must not appear in output')
        project = self.root / 'project'
        local = project / '.agents/skills/example'
        local.mkdir(parents=True)
        result = client.query(self.config, None, 'chosen', 'example', str(project))
        self.assertEqual(result['status'], 'conflict')
        self.assertEqual(set(result['conflicts']), {str(nested), str(local)})
        self.assertNotIn('private content', json.dumps(result))

    def test_broken_destination_link_is_conflict(self):
        (self.home / 'skills').mkdir()
        (self.home / 'skills/example').symlink_to(self.root / 'absent')
        self.assertEqual(client.query(self.config, None, 'chosen', 'example')['status'], 'conflict')

    def test_timeout_and_error_output_are_bounded(self):
        with patch.object(client.subprocess, 'run', side_effect=subprocess.TimeoutExpired('x', 1)):
            self.assertEqual(client.query(self.config, None, 'chosen')['error'], 'timeout')
        process = subprocess.CompletedProcess([], 2, '', 'sensitive stderr')
        with patch.object(client.subprocess, 'run', return_value=process):
            result = client.query(self.config, None, 'chosen')
        self.assertEqual(result['error'], 'runtime_unavailable')
        self.assertNotIn('sensitive', json.dumps(result))

    def test_explicit_profile_required(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'hermes_target.py')], capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_missing_or_invalid_configuration(self):
        self.assertEqual(client.query(self.root / 'absent', None, 'chosen')['error'], 'config_missing')
        for data in ([], {'schema_version': 1, 'targets': []}, {'schema_version': 1, 'default_target': 'x', 'targets': {'x': []}}):
            self.config.write_text(json.dumps(data))
            self.assertEqual(client.query(self.config, None, 'chosen')['error'], 'config_invalid')

    def test_missing_project_is_not_reported_as_checked(self):
        result = client.query(self.config, None, 'chosen', 'example', str(self.root / 'absent'))
        self.assertEqual(result['error'], 'project_not_found')

    def test_profile_path_is_rejected_before_connection(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'hermes_target.py'),
                                 '--profile', '../other'], capture_output=True)
        self.assertEqual(result.returncode, 2)

    def skill(self, relative, name):
        folder = self.home / 'skills' / relative
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text('---\n' + json.dumps({'name': name}) + '\n---\nPrivate body')
        return folder

    def test_declared_name_conflict_in_different_folder(self):
        folder = self.skill('category/unrelated-folder', 'example')
        result = client.query(self.config, None, 'chosen', 'example')
        self.assertEqual(result['status'], 'conflict')
        self.assertEqual(result['conflicts'], [str(folder)])
        self.assertNotIn('Private body', json.dumps(result))

    def test_hermes_support_and_cache_directories_are_excluded(self):
        self.skill('parent', 'parent')
        self.skill('parent/references/example', 'example')
        self.skill('node_modules/example', 'example')
        self.assertEqual(client.query(self.config, None, 'chosen', 'example')['status'], 'ok')

    def test_invalid_metadata_never_reports_clean(self):
        self.skill('broken', None)
        result = client.query(self.config, None, 'chosen', 'example')
        self.assertEqual(result['error'], 'skill_metadata_invalid')

    def test_unscanned_link_never_reports_clean(self):
        (self.home / 'skills').mkdir()
        other = self.root / 'other'
        other.mkdir()
        (self.home / 'skills/category').symlink_to(other)
        result = client.query(self.config, None, 'chosen', 'example')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['conflict_check'], 'partial')

    def test_data_root_is_independent_of_callers_environment(self):
        for name in ('other-a', 'other-b'):
            other = self.root / name
            (other / 'profiles/chosen').mkdir(parents=True)
            with patch.dict(os.environ, {'HERMES_HOME': str(other)}):
                result = client.query(self.config, None, 'chosen')
                self.assertEqual(os.environ['HERMES_HOME'], str(other))
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['profile_home'], str(self.home))

    def test_missing_data_root_is_not_inferred(self):
        config = json.loads(self.config.read_text())
        del config['targets']['test']['data_root']
        self.config.write_text(json.dumps(config))
        with patch.object(client.subprocess, 'run') as run:
            self.assertEqual(client.query(self.config, None, 'chosen')['error'], 'config_invalid')
            run.assert_not_called()

    def test_profile_symlink_cannot_escape_configured_instance(self):
        self.home.rmdir()
        outside = self.root / 'outside'
        outside.mkdir()
        self.home.symlink_to(outside)
        self.assertEqual(client.query(self.config, None, 'chosen')['error'], 'profile_root_mismatch')

    def test_shell_arguments_are_quoted(self):
        target = {'transport': 'ssh', 'host': 'example', 'container': 'hermes',
                  'python': '/opt/hermes/python', 'hermes_root': '/opt/hermes', 'data_root': '/opt/data'}
        args = client.command_for(target, "bad; touch /tmp/no", None, None)
        import shlex
        self.assertIn("bad; touch /tmp/no", shlex.split(args[-1]))
        self.assertIn('StrictHostKeyChecking=yes', args)


if __name__ == '__main__':
    unittest.main()
