"""LLM response validator (app/architecture/system.md's "LLM response
validator" component). Every LLM output is validated against
analysis/schemas/interpretation.schema.json AND cross-checked against the
DB for citation laundering before it may reach a client -- structure is
checked, never the model's self-report of compliance
(app/architecture/threat_model.md)."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[3]


class InterpretationValidationError(RuntimeError):
    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


_schema_cache: dict | None = None


def load_interpretation_schema() -> dict:
    global _schema_cache
    if _schema_cache is None:
        path = REPO_ROOT / "analysis" / "schemas" / "interpretation.schema.json"
        with open(path, encoding="utf-8") as f:
            _schema_cache = json.load(f)
    return _schema_cache


def validate_schema(payload: dict) -> list[str]:
    schema = load_interpretation_schema()
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{list(e.path)}: {e.message}" for e in sorted(validator.iter_errors(payload), key=lambda e: list(e.path))]


def cross_check_citations(payload: dict, valid_evidence_ids: set[str], valid_metric_ids: set[str]) -> list[str]:
    """Citation-laundering control (threat_model.md): schema pattern-matching
    an evidence_id/metric_id string doesn't prove it exists -- check the DB."""
    problems = []
    for claim in payload.get("claims", []):
        for ref in claim.get("evidence_refs", []):
            if ref not in valid_evidence_ids:
                problems.append(f"claim {claim.get('claim_id')} cites unknown evidence_id '{ref}'")
        for ref in claim.get("metric_refs", []):
            if ref not in valid_metric_ids:
                problems.append(f"claim {claim.get('claim_id')} cites unknown metric_id '{ref}'")
    return problems


def validate_and_check(payload: dict, valid_evidence_ids: set[str], valid_metric_ids: set[str]) -> None:
    """Raises InterpretationValidationError if the payload is not safe to return."""
    reasons = validate_schema(payload)
    # Only cross-check citations if the payload is at least schema-shaped enough to have claims.
    if not reasons:
        reasons.extend(cross_check_citations(payload, valid_evidence_ids, valid_metric_ids))
    if reasons:
        raise InterpretationValidationError(reasons)
