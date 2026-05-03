import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from stack_core.git_bridge.differ import _diff, _read_git_state


class TestGitBridgeDiff(FrappeTestCase):
    def test_only_on_site(self):
        site = {"blueprints": [{"blueprint_name": "A", "payload": {"x": 1}}]}
        git = {"blueprints": []}
        only_site, only_git, changed = _diff(site, git)
        self.assertEqual(only_site, ["A"])
        self.assertEqual(only_git, [])
        self.assertEqual(changed, [])

    def test_only_in_git(self):
        site = {"blueprints": []}
        git = {"blueprints": [{"blueprint_name": "B", "payload": {"x": 1}}]}
        only_site, only_git, changed = _diff(site, git)
        self.assertEqual(only_site, [])
        self.assertEqual(only_git, ["B"])
        self.assertEqual(changed, [])

    def test_changed(self):
        site = {"blueprints": [{"blueprint_name": "C", "payload": {"x": 1}}]}
        git = {"blueprints": [{"blueprint_name": "C", "payload": {"x": 2}}]}
        _, _, changed = _diff(site, git)
        self.assertEqual(changed, ["C"])

    def test_unchanged(self):
        site = {"blueprints": [{"blueprint_name": "D", "payload": {"x": 1}}]}
        git = {"blueprints": [{"blueprint_name": "D", "payload": {"x": 1}}]}
        only_site, only_git, changed = _diff(site, git)
        self.assertEqual((only_site, only_git, changed), ([], [], []))

    def test_read_git_state_handles_missing_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = _read_git_state(Path(tmp), "test_site")
            self.assertEqual(state["blueprints"], [])
            self.assertEqual(state["workflows"], [])

    def test_read_git_state_reads_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            doctypes = Path(tmp) / "fixtures" / "app" / "doctypes"
            doctypes.mkdir(parents=True)
            (doctypes / "alpha.json").write_text(
                json.dumps({"blueprint_name": "Alpha", "payload": {"x": 1}})
            )
            state = _read_git_state(Path(tmp), "test_site")
            self.assertEqual(len(state["blueprints"]), 1)
            self.assertEqual(state["blueprints"][0]["blueprint_name"], "Alpha")
