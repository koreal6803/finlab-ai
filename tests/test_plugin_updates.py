import json
from pathlib import Path
import unittest


class PluginUpdatesTest(unittest.TestCase):
    def test_plugin_uses_commit_version_instead_of_a_fixed_version(self):
        root = Path(__file__).resolve().parents[1]
        for tool in ('.claude-plugin', '.cursor-plugin'):
            manifest = json.loads((root / tool / 'plugin.json').read_text())
            marketplace = json.loads((root / tool / 'marketplace.json').read_text())

            # Either version field overrides git commit based update detection.
            self.assertNotIn('version', manifest)
            for plugin in marketplace['plugins']:
                self.assertNotIn('version', plugin)


if __name__ == '__main__':
    unittest.main()
