#!/usr/bin/env python3
"""Deterministic gate score calculator.

This script does not replace expert review. It validates declared category
scores, derives hard blockers from machine-readable checks, and writes an
auditable decision record.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS = {
    "evidence_quality": 12,
    "source_layer_and_entity_integrity": 10,
    "coding_reliability": 10,
    "data_reproducibility": 10,
    "statistical_validity": 10,
    "score_traceability": 10,
    "llm_grounding": 10,
    "product_consistency": 8,
    "experience_integrity": 5,
    "usability_accessibility": 7,
    "engineering_quality": 5,
    "operational_readiness": 3,
}

BOOLEAN_BLOCKERS = {
    "schema_validation_pass": (True, "schema_validation_failed"),
    "reproducible_run_pass": (True, "analysis_not_reproducible"),
    "missing_value_scored_as_zero": (False, "missing_value_scored_as_zero"),
    "authorized_assets_only": (True, "unauthorized_translation_or_game_asset"),
    "double_coded_calibration_set": (True, "coding_calibration_missing"),
    "unit_tests_pass": (True, "unit_tests_failed"),
    "integration_tests_pass": (True, "integration_tests_failed"),
    "contract_tests_pass": (True, "contract_tests_failed"),
}

ZERO_REQUIRED = {
    "unsupported_llm_claims": "unsupported_llm_claims",
    "source_layer_leakage_cases": "source_layer_regression",
    "orphan_evidence_refs": "orphan_evidence_refs",
    "unresolved_entity_collisions": "entity_alias_collision",
    "accessibility_critical_issues": "accessibility_critical_issues",
    "open_critical_bugs": "open_critical_bugs",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("evaluation input must be a JSON object")
    return value


def validate_scores(scores: dict) -> None:
    missing = sorted(set(WEIGHTS) - set(scores))
    extra = sorted(set(scores) - set(WEIGHTS))
    if missing or extra:
        raise ValueError(f"category mismatch: missing={missing}, extra={extra}")
    for name, value in scores.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100")


def derived_blockers(checks: dict) -> list[str]:
    blockers: list[str] = []
    for name, (expected, blocker) in BOOLEAN_BLOCKERS.items():
        if checks.get(name) is not expected:
            blockers.append(blocker)
    for name, blocker in ZERO_REQUIRED.items():
        value = checks.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != 0:
            blockers.append(blocker)
    return blockers


def evaluate(payload: dict) -> dict:
    scores = payload.get("category_scores", {})
    checks = payload.get("automatic_checks", {})
    validate_scores(scores)
    if not isinstance(checks, dict):
        raise ValueError("automatic_checks must be an object")

    declared = payload.get("hard_blockers", [])
    if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
        raise ValueError("hard_blockers must be a list of strings")

    blockers = sorted(set(declared + derived_blockers(checks)))
    weighted = sum(scores[name] * weight for name, weight in WEIGHTS.items()) / 100
    total = round(weighted, 2)

    if blockers:
        decision = "fail"
    elif total >= 85:
        decision = "pass"
    elif total >= 80:
        decision = "conditional_pass"
    else:
        decision = "fail"

    return {
        "target_id": payload.get("target_id", "unknown"),
        "gate": payload.get("gate", "unknown"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "total_score": total,
        "hard_blockers": blockers,
        "weights": WEIGHTS,
        "category_scores": scores,
        "automatic_checks": checks,
        "evidence": payload.get("evidence", []),
        "evaluator_notes": payload.get("evaluator_notes", ""),
        "warning": "Declared scores require independent evidence; this calculator does not verify expert judgments.",
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python evals/run_eval.py INPUT.json OUTPUT.json", file=sys.stderr)
        return 2
    input_path, output_path = map(Path, argv[1:])
    try:
        result = evaluate(load_json(input_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(f"{result['decision']} score={result['total_score']} blockers={len(result['hard_blockers'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
