import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "skills/finlab/SKILL.md"


def login_section():
    text = GUIDE.read_text()
    start = text.index("3. **Logged in to FinLab**")
    return text[start:text.index("\n## ", start)]


class AuthenticationGuideTest(unittest.TestCase):
    def test_login_section_lists_supported_flows_and_deprecation(self):
        section = login_section()
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
