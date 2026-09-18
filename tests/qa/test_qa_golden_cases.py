"""QA golden-case checks (S3 QA pass, 2026-09-18) that E1's own test suites did
not already cover: entity-resolution aliases, source-layer non-leakage in
/v1/ask, citation-locator reproducibility, mandatory D-017 disclosure
exposure, and explicit missing-evidence handling. Reuses the existing
`app_client`-style fixtures from tests/backend/conftest.py (fresh_db,
api_client) rather than re-implementing DB setup -- this file only adds new
assertions, it does not touch the existing backend test files."""
from __future__ import annotations

import json


def test_entity_resolution_alias_golden_set(fresh_db):
    """Known aliases/courtesy names/nicknames for the 10-person cast must
    resolve to the correct canonical person_id, and no alias may be shared
    by two different persons (agents/qa.md: '동명이인/이명/자/시호의
    entity-resolution golden case')."""
    import sqlite3

    conn = sqlite3.connect(str(fresh_db))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT person_id, aliases_json FROM persons").fetchall()
    finally:
        conn.close()

    alias_to_person: dict[str, str] = {}
    for row in rows:
        for alias_obj in json.loads(row["aliases_json"]):
            alias = alias_obj["alias"]
            assert alias not in alias_to_person, (
                f"alias collision: '{alias}' claimed by both "
                f"{alias_to_person.get(alias)} and {row['person_id']}"
            )
            alias_to_person[alias] = row["person_id"]

    # Golden set: courtesy names / nicknames that must map to the correct person.
    expected = {
        "孟德": "person.cao_cao",
        "曹阿瞞": "person.cao_cao",
        "玄德": "person.liu_bei",
        "劉皇叔": "person.liu_bei",
        "孔明": "person.zhuge_liang",
        "臥龍": "person.zhuge_liang",
        "公瑾": "person.zhou_yu",
        "周郎": "person.zhou_yu",
        "仲謀": "person.sun_quan",
        "子龍": "person.zhao_yun",
        "常山趙子龍": "person.zhao_yun",
        "奉孝": "person.guo_jia",
        "雲長": "person.guan_yu",
        "子敬": "person.lu_su",
        "公覆": "person.huang_gai",
    }
    for alias, expected_person in expected.items():
        assert alias in alias_to_person, f"expected alias '{alias}' not found in curated export at all"
        assert alias_to_person[alias] == expected_person, (
            f"alias '{alias}' resolved to {alias_to_person[alias]}, expected {expected_person}"
        )


def test_ask_history_mode_never_returns_romance_evidence(api_client):
    """정사 mode must only ever cite HISTORY_BASE/HISTORY_ANNOTATION evidence,
    never ROMANCE -- checked against the real evidence table, not just the
    mock's one-claim happy path."""
    resp = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "曹操는 왜 패했나요?", "answer_mode": "정사"},
    )
    assert resp.status_code == 200
    body = resp.json()
    for claim in body.get("claims", []):
        for eid in claim.get("evidence_refs", []):
            ev = api_client.get(f"/v1/people/person.cao_cao/evidence?event_id=event.chibi").json()
            layers = {e["evidence_id"]: e["source_layer"] for e in ev["evidence"]}
            if eid in layers:
                assert layers[eid] != "ROMANCE", f"정사 mode cited a ROMANCE evidence_id: {eid}"


def test_ask_romance_mode_never_returns_history_evidence(api_client):
    """연의 mode must only ever cite ROMANCE evidence, never HISTORY_BASE/
    HISTORY_ANNOTATION (reverse direction of the leakage check above)."""
    resp = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "제갈량은 무엇을 했나요?", "answer_mode": "연의"},
    )
    assert resp.status_code == 200
    body = resp.json()
    for claim in body.get("claims", []):
        for eid in claim.get("evidence_refs", []):
            ev = api_client.get("/v1/people/person.zhuge_liang/evidence?event_id=event.chibi").json()
            layers = {e["evidence_id"]: e["source_layer"] for e in ev["evidence"]}
            if eid in layers:
                assert layers[eid] in ("ROMANCE",), f"연의 mode cited a non-ROMANCE evidence_id: {eid}"


def test_evidence_citation_locator_is_reproducible(api_client):
    """Fetching the same person's evidence twice must return byte-identical
    locator/excerpt/coding_label for the same evidence_id (agents/qa.md:
    '인용 위치 재현성')."""
    first = api_client.get("/v1/people/person.zhou_yu/evidence?event_id=event.chibi").json()["evidence"]
    second = api_client.get("/v1/people/person.zhou_yu/evidence?event_id=event.chibi").json()["evidence"]
    assert first, "expected at least one evidence row for 周瑜"
    by_id_first = {e["evidence_id"]: e for e in first}
    by_id_second = {e["evidence_id"]: e for e in second}
    assert by_id_first.keys() == by_id_second.keys()
    for eid, row in by_id_first.items():
        assert row == by_id_second[eid], f"evidence {eid} was not reproducible across two fetches"


def test_d017_disclosure_present_on_every_evidence_row_and_dataset_version(api_client):
    """coding_validation_status must appear on every evidence row and on the
    dataset version reference -- never omittable (D-017)."""
    version = api_client.get("/v1/version").json()
    # Present and a valid enum value -- not hardcoded to one value. This is a conservative
    # rollup (human_validated only if EVERY row is); currently llm_llm_validated_only since
    # 18/48 rows are from a not-yet-human-reviewed pass (2026-09-18 expansion, D-024 scope).
    assert version["coding_validation_status"] in ("human_validated", "llm_llm_validated_only")

    people = api_client.get("/v1/events/event.chibi/people").json()["people"]
    assert people, "expected at least one person for event.chibi"
    checked_any = False
    for person in people:
        ev = api_client.get(f"/v1/people/{person['person_id']}/evidence?event_id=event.chibi").json()["evidence"]
        for row in ev:
            checked_any = True
            assert "coding_validation_status" in row and row["coding_validation_status"], (
                f"evidence {row['evidence_id']} is missing the D-017 coding_validation_status disclosure"
            )
            assert row["coding_validation_status"] in ("human_validated", "llm_llm_validated_only")
    assert checked_any, "no evidence rows were found to check at all"


def test_missing_evidence_is_explicit_not_zero(api_client):
    """A person/layer combination with zero coded evidence must return an
    explicit empty list the caller can distinguish from 'no such person' or a
    fabricated zero -- never silently coerced to a 0/absent value
    (agents/_three_kingdoms_domain.md: '결측은 0이 아닙니다')."""
    # 郭嘉 (person.guo_jia) has no HISTORY_ANNOTATION rows in this slice.
    resp = api_client.get(
        "/v1/people/person.guo_jia/evidence?event_id=event.chibi&source_layer=HISTORY_ANNOTATION"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["evidence"] == [], "expected an explicit empty list, not an error or a fabricated row"
    # And the person itself must still resolve (this is 'no evidence in this
    # layer', not 'unknown person' -- those are different states).
    person_resp = api_client.get(
        "/v1/people/person.guo_jia/evidence?event_id=event.chibi&source_layer=HISTORY_BASE"
    )
    assert person_resp.status_code == 200


def test_unknown_person_id_is_404_not_empty_list(api_client):
    """An unknown/misspelled person_id must be a 404, not silently rendered
    as 'zero evidence' -- these are different failure states and must not be
    conflated."""
    resp = api_client.get("/v1/people/person.does_not_exist/evidence?event_id=event.chibi")
    assert resp.status_code == 404
