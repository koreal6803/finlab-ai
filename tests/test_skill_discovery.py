from pathlib import Path
import unittest


class SkillDiscoveryTest(unittest.TestCase):
    def test_only_canonical_skill_is_discoverable(self):
        root = Path(__file__).resolve().parents[1]
        skills = {path.relative_to(root) for path in root.rglob('SKILL.md')}
        self.assertEqual(skills, {Path('skills/finlab/SKILL.md')})


if __name__ == '__main__':
    unittest.main()
