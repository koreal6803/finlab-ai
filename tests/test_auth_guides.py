import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = (ROOT / "skills/finlab/SKILL.md", ROOT / ".agents/skills/finlab/SKILL.md")


def login_section(path):
    text = path.read_text()
    start = text.index("3. **Logged in to FinLab**")
    return text[start:text.index("\n## ", start)]


class AuthenticationGuidesTest(unittest.TestCase):
    def test_supported_login_and_deprecation_are_aligned(self):
        section, mirror = (login_section(path) for path in GUIDES)
        self.assertEqual(section, mirror)
        for instruction in (
            "python -m finlab login", "finlab.login()",
            "python -m finlab token --env", "python -m finlab migrate",
            "FINLAB_REFRESH_TOKEN", "FINLAB_SESSION_ID", "FINLAB_API_KEY",
            "client-side", "server-side", "No removal version or date",
        ):
            self.assertIn(instruction, section)
        self.assertIn("```bash\n", section)
        self.assertNotRegex(section, r"```(?:bash|python)\n[^`]*FINLAB_API_TOKEN")


if __name__ == "__main__":
    unittest.main()
