import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectPolicyTests(unittest.TestCase):
    def test_stage_transitions_require_human_approval(self):
        workflow = (ROOT / "orchestration" / "workflow.yaml").read_text(encoding="utf-8")
        self.assertIn("await_explicit_human_approval", workflow)
        self.assertIn("await_explicit_human_development_approval", workflow)
        self.assertIn("automatic_cross_stage_progress", workflow)

    def test_private_data_ignore_rules_exist(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("data/private/**", ignore)
        self.assertIn("data/runtime/**", ignore)
        self.assertIn("*.parquet", ignore)
        self.assertIn("*.duckdb", ignore)

    def test_packaged_private_data_contains_placeholders_only(self):
        private_root = ROOT / "data" / "private"
        files = [path for path in private_root.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertTrue(all(path.name == ".gitkeep" for path in files))

    def test_app_export_manifest_schema_is_json(self):
        path = ROOT / "data" / "schemas" / "app_export_manifest.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Approved Application Export Manifest")
        self.assertIn("approval_ref", schema["required"])

    def test_concept_is_undecided(self):
        decision = (ROOT / "product" / "concepts" / "concept_decision.yaml").read_text(encoding="utf-8")
        self.assertIn("status: undecided", decision)
        self.assertIn("selected_concept: null", decision)


if __name__ == "__main__":
    unittest.main()

