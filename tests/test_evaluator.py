import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "evals" / "run_eval.py"
SPEC = importlib.util.spec_from_file_location("run_eval", MODULE_PATH)
run_eval = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(run_eval)


def passing_payload():
    return {
        "target_id": "test",
        "gate": "research_gate",
        "hard_blockers": [],
        "automatic_checks": {
            "schema_validation_pass": True,
            "reproducible_run_pass": True,
            "missing_value_scored_as_zero": False,
            "authorized_assets_only": True,
            "double_coded_calibration_set": True,
            "unit_tests_pass": True,
            "integration_tests_pass": True,
            "contract_tests_pass": True,
            "unsupported_llm_claims": 0,
            "source_layer_leakage_cases": 0,
            "orphan_evidence_refs": 0,
            "unresolved_entity_collisions": 0,
            "accessibility_critical_issues": 0,
            "open_critical_bugs": 0,
        },
        "category_scores": {name: 90 for name in run_eval.WEIGHTS},
    }


class EvaluatorTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(run_eval.WEIGHTS.values()), 100)

    def test_passing_payload(self):
        result = run_eval.evaluate(passing_payload())
        self.assertEqual(result["decision"], "pass")
        self.assertEqual(result["total_score"], 90)
        self.assertEqual(result["hard_blockers"], [])

    def test_blocker_forces_failure(self):
        payload = passing_payload()
        payload["automatic_checks"]["source_layer_leakage_cases"] = 1
        result = run_eval.evaluate(payload)
        self.assertEqual(result["decision"], "fail")
        self.assertIn("source_layer_regression", result["hard_blockers"])

    def test_missing_value_zero_forces_failure(self):
        payload = passing_payload()
        payload["automatic_checks"]["missing_value_scored_as_zero"] = True
        result = run_eval.evaluate(payload)
        self.assertEqual(result["decision"], "fail")


if __name__ == "__main__":
    unittest.main()

