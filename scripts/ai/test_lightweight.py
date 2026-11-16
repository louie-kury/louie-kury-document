"""Validate portable harness configuration, role definitions, and routing."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ROUTING_ENTRIES = ("AGENTS.md", "docs/ai/ROUTING.md")


class LightweightHarnessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="가벼운 하네스 ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        names = ["scripts/ai/harness.py", ".codex/config.toml", ".codex/hooks.json",
                 ".playwright/cli.config.json", "tools/ai/package.json", "tools/ai/package-lock.json"]
        skills = ("project-verify", "project-review", "project-security-review", "project-handoff",
                  "playwright-cli", "vibe-wise", "vibe-wise-reset")
        names.extend(".agents/skills/" + skill + "/SKILL.md" for skill in skills)
        self.roles = ("planner", "implementer", "tester", "reviewer")
        names.extend(".codex/agents/" + role + ".toml" for role in self.roles)
        names.append("AGENTS.md")
        names.extend(path.relative_to(ROOT) for path in (ROOT / "docs").rglob("*.md"))
        for relative in names:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.clean_home = self.root / "empty-home"
        self.clean_home.mkdir()

    def check_configuration(self):
        env = dict(os.environ, HOME=str(self.clean_home),
                   CODEX_HOME=str(self.clean_home / ".codex"))
        return subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/ai/harness.py"), "check-config"],
            cwd=self.root, env=env, capture_output=True, text=True, timeout=5)

    def test_fresh_configuration_needs_no_spec_kit_or_global_plugins(self):
        result = self.check_configuration()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS A:", result.stdout)
        self.assertEqual({path.stem for path in (self.root / ".codex/agents").glob("*.toml")},
                         set(self.roles))
        self.assertFalse((self.root / ".specify").exists())
        self.assertFalse((self.root / "tools/ai/spec-kit").exists())
        self.assertFalse((self.clean_home / ".codex").exists())

    def test_missing_routing_entry_is_rejected(self):
        for entry in ROUTING_ENTRIES:
            with self.subTest(entry=entry):
                path = self.root / entry
                original = path.read_bytes()
                try:
                    path.unlink()
                    self.assert_configuration_rejected()
                finally:
                    path.write_bytes(original)

    def test_broken_local_routing_link_is_rejected(self):
        for entry in ROUTING_ENTRIES:
            path = self.root / entry
            original = path.read_text()
            for destination in ("missing.md", "#missing-heading"):
                with self.subTest(entry=entry, destination=destination):
                    try:
                        path.write_text(f"{original}\n[깨진 링크]({destination})\n")
                        self.assert_configuration_rejected()
                    finally:
                        path.write_text(original)

    def test_disabled_or_invalid_hook_feature_is_rejected(self):
        path = self.root / ".codex/config.toml"
        original = path.read_text()
        self.assertIn("hooks = true", original)
        for setting in ("hooks = false", "", 'hooks = "true"'):
            with self.subTest(setting=setting):
                path.write_text(original.replace("hooks = true", setting))
                self.assert_configuration_rejected()

    def assert_configuration_rejected(self):
        result = self.check_configuration()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("PASS A:", result.stdout)

    def test_each_missing_role_is_rejected(self):
        for role in self.roles:
            with self.subTest(role=role):
                path = self.root / ".codex/agents" / (role + ".toml")
                original = path.read_bytes()
                try:
                    path.unlink()
                    result = self.check_configuration()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("PASS A:", result.stdout)
                finally:
                    path.write_bytes(original)

    def test_blank_required_role_text_is_rejected(self):
        for role in self.roles:
            path = self.root / ".codex/agents" / (role + ".toml")
            original = path.read_bytes()
            for field in ("name", "description", "developer_instructions"):
                for blank in ("", "   "):
                    with self.subTest(role=role, field=field, blank=blank):
                        fields = dict(name=role, description="Test role", developer_instructions="Test scope")
                        fields[field] = blank
                        try:
                            path.write_text("".join(f'{key} = "{value}"\n' for key, value in fields.items()))
                            result = self.check_configuration()
                            self.assertNotEqual(result.returncode, 0)
                            self.assertNotIn("PASS A:", result.stdout)
                        finally:
                            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
