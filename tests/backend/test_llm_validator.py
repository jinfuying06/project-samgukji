import pytest

from app.backend.api.llm_validator import InterpretationValidationError, validate_and_check


def _base_payload(**overrides):
    payload = {
        "interpretation_id": "interp-test-1",
        "answer_mode": "비교",
        "status": "ok",
        "generated_at": "2026-09-18T00:00:00Z",
        "model": {"name": "mock", "version": "1.0.0"},
        "prompt_version": "v1",
        "input_refs": {"result_json_run_id": "run-1", "evidence_matrix_checksum": "abc123"},
        "coding_validation_notice": "AI-only validated, not human-validated.",
        "claims": [
            {
                "claim_id": "c1",
                "claim_type": "observation",
                "text": "some observation",
                "evidence_refs": ["HB-J01-P1"],
                "metric_refs": [],
                "confidence": "high",
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_valid_payload_passes():
    payload = _base_payload()
    validate_and_check(payload, valid_evidence_ids={"HB-J01-P1"}, valid_metric_ids=set())


def test_rejects_claim_with_no_refs():
    payload = _base_payload()
    payload["claims"][0]["evidence_refs"] = []
    payload["claims"][0]["metric_refs"] = []
    with pytest.raises(InterpretationValidationError):
        validate_and_check(payload, valid_evidence_ids={"HB-J01-P1"}, valid_metric_ids=set())


def test_rejects_citation_laundering_unknown_evidence_id():
    """Schema pattern-matching alone doesn't prove the ID exists -- this must
    be caught by the DB cross-check (threat_model.md)."""
    payload = _base_payload()
    payload["claims"][0]["evidence_refs"] = ["HB-FAKE-ID-999"]
    with pytest.raises(InterpretationValidationError, match="unknown evidence_id"):
        validate_and_check(payload, valid_evidence_ids={"HB-J01-P1"}, valid_metric_ids=set())


def test_rejects_unknown_metric_id():
    payload = _base_payload()
    payload["claims"][0]["evidence_refs"] = []
    payload["claims"][0]["metric_refs"] = ["metric.does_not_exist"]
    with pytest.raises(InterpretationValidationError, match="unknown metric_id"):
        validate_and_check(payload, valid_evidence_ids=set(), valid_metric_ids={"coverage.person.cao_cao.HISTORY_BASE"})


def test_status_ok_requires_at_least_one_claim():
    payload = _base_payload(claims=[])
    with pytest.raises(InterpretationValidationError):
        validate_and_check(payload, valid_evidence_ids=set(), valid_metric_ids=set())


def test_insufficient_evidence_requires_abstention_reason():
    payload = _base_payload(status="insufficient_evidence", claims=[])
    del payload["coding_validation_notice"]
    with pytest.raises(InterpretationValidationError):
        validate_and_check(payload, valid_evidence_ids=set(), valid_metric_ids=set())


def test_insufficient_evidence_with_reason_passes():
    payload = _base_payload(status="insufficient_evidence", claims=[], abstention_reason="no data")
    del payload["coding_validation_notice"]
    validate_and_check(payload, valid_evidence_ids=set(), valid_metric_ids=set())


def test_missing_coding_validation_notice_when_evidence_cited_rejected():
    payload = _base_payload()
    del payload["coding_validation_notice"]
    with pytest.raises(InterpretationValidationError):
        validate_and_check(payload, valid_evidence_ids={"HB-J01-P1"}, valid_metric_ids=set())
