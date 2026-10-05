import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = (ROOT / "skills/finlab/SKILL.md", ROOT / ".agents/skills/finlab/SKILL.md")


class AuthenticationGuidesTest(unittest.TestCase):
    def test_supported_login_and_deprecation_are_aligned(self):
        sections = []
        for path in GUIDES:
            with self.subTest(guide=str(path.relative_to(ROOT))):
                text = path.read_text()
                prerequisites = text.split("## Prerequisites\n", 1)[1]
                section = prerequisites.split("3. **", 1)[1].split("\n## Language", 1)[0]
                sections.append(section)
                for instruction in (
                    "python -m finlab login", "finlab.login()",
                    "python -m finlab token --env", "python -m finlab migrate",
                    "FINLAB_REFRESH_TOKEN", "FINLAB_SESSION_ID", "FINLAB_API_KEY",
                    "client-side", "server-side", "No removal version or date",
                ):
                    self.assertIn(instruction, section)
                self.assertNotIn("still works on current releases", section)
                self.assertNotIn("API Token is set", section)
                examples = re.findall(r"```(?:bash|python)\n(.*?)```", section, re.S)
                self.assertTrue(examples)
                self.assertTrue(all("FINLAB_API_TOKEN" not in code for code in examples))
        self.assertEqual(*sections)


if __name__ == "__main__":
    unittest.main()
