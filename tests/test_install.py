import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InstallTest(unittest.TestCase):
    def test_clone_fallback_installs_complete_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            bin_dir = sandbox / 'bin'
            bin_dir.mkdir()
            commands = {
                'codex': 'exit 0',
                'uv': 'exit 0',
                'npx': 'exit 1',
                'git': 'for dest; do :; done; mkdir -p "$dest"; cp -R "$SKILL_TEST_REPO/skills" "$dest/skills"',
            }
            for name, body in commands.items():
                command = bin_dir / name
                command.write_text('#!/bin/sh\nset -e\n' + body + '\n')
                command.chmod(0o755)
            env = {**os.environ, 'HOME': str(sandbox),
                   'PATH': f'{bin_dir}:/usr/bin:/bin', 'SKILL_TEST_REPO': str(ROOT)}
            result = subprocess.run(['sh', str(ROOT / 'install.sh')],
                                    cwd=sandbox, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            installed = sandbox / '.codex/skills/finlab'
            skill = (installed / 'SKILL.md').read_text()
            self.assertEqual(skill, (ROOT / 'skills/finlab/SKILL.md').read_text())
            for target in re.findall(r'\]\(([^)]+\.md)\)', skill):
                self.assertTrue((installed / target).is_file(), target)

    def test_only_complete_skill_is_discoverable(self):
        self.assertEqual(list(ROOT.glob('**/SKILL.md')), [ROOT / 'skills/finlab/SKILL.md'])


if __name__ == '__main__':
    unittest.main()
