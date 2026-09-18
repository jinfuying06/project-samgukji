def test_version_endpoint(api_client):
    r = api_client.get("/v1/version")
    assert r.status_code == 200
    body = r.json()
    # D-017: must always be a valid, present disclosure -- not hardcoded to one value, since
    # it's an honest conservative rollup (human_validated only if EVERY row is; see
    # data/pipelines/build_curated_export.py). As of the 2026-09-18 expansion pass this is
    # "llm_llm_validated_only" because 18 of 48 rows are not yet human-reviewed.
    assert body["coding_validation_status"] in {"human_validated", "llm_llm_validated_only"}
    assert body["evidence_matrix_checksum"]


def test_event_overview(api_client):
    r = api_client.get("/v1/events/event.chibi")
    assert r.status_code == 200
    body = r.json()
    assert body["event_id"] == "event.chibi"
    assert set(body["source_layer_coverage"]) <= {"HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"}
    assert "dataset_version" in body


def test_event_not_found(api_client):
    r = api_client.get("/v1/events/event.does_not_exist")
    assert r.status_code == 404
    assert r.json()["error_code"] == "event_not_found"


def test_event_people_not_fixed_size(api_client):
    """D-016: cast size must not be assumed fixed."""
    r = api_client.get("/v1/events/event.chibi/people")
    assert r.status_code == 200
    people = r.json()["people"]
    assert len(people) == 10  # today's real count -- API itself imposes no fixed size
    for p in people:
        assert "evidence_coverage" in p
        assert isinstance(p["evidence_coverage"], dict)


def test_person_evidence_never_merges_layers(api_client):
    r = api_client.get("/v1/people/person.cao_cao/evidence", params={"event_id": "event.chibi"})
    assert r.status_code == 200
    evidence = r.json()["evidence"]
    assert len(evidence) > 0
    for e in evidence:
        assert e["source_layer"] in {"HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"}
        # D-017: disclosure always present and valid, per-row (not globally hardcoded -- a
        # row's status depends on whether ITS extraction pass was human-reviewed, D-024).
        assert e["coding_validation_status"] in {"human_validated", "llm_llm_validated_only"}


def test_person_evidence_filtered_by_layer(api_client):
    r = api_client.get(
        "/v1/people/person.cao_cao/evidence",
        params={"event_id": "event.chibi", "source_layer": "ROMANCE"},
    )
    assert r.status_code == 200
    evidence = r.json()["evidence"]
    assert all(e["source_layer"] == "ROMANCE" for e in evidence)


def test_person_not_found(api_client):
    r = api_client.get("/v1/people/person.does_not_exist/evidence")
    assert r.status_code == 404


def test_metrics_default_kinds_only(api_client):
    r = api_client.get("/v1/events/event.chibi/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["population"]["n"] > 0
    for m in body["metrics"]:
        assert m["metric_id"].split(".")[0] in {"coverage", "label_frequency", "divergence"}


def test_metrics_rejects_composite_score_request(api_client):
    r = api_client.get("/v1/events/event.chibi/metrics", params={"kind": "display_score"})
    assert r.status_code == 409
    assert r.json()["error_code"] == "no_composite_score"


def test_relationships_never_compute_centrality(api_client):
    r = api_client.get("/v1/events/event.chibi/relationships")
    assert r.status_code == 200
    body = r.json()
    assert body["no_centrality_computed"] is True
    for edge in body["edges"]:
        assert len(edge["evidence_refs"]) >= 1


def test_ask_grounded_response_carries_d017_disclosure(api_client):
    r = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "周瑜는 어떤 인물인가요?", "answer_mode": "비교"},
    )
    assert r.status_code == 200
    body = r.json()
    if body["status"] == "ok":
        assert body["coding_validation_notice"]
        for claim in body["claims"]:
            assert claim["evidence_refs"] or claim["metric_refs"]


def test_ask_game_mode_always_abstains(api_client):
    r = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "누가 최강인가요?", "answer_mode": "게임"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "insufficient_evidence"
    assert body["claims"] == []


def test_ask_invalid_output_never_passed_through(api_client):
    """The mock LLM's FORCE_INVALID_FOR_TEST trigger returns a schema-invalid
    payload; the API must never forward it unvalidated, even once."""
    r = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "FORCE_INVALID_FOR_TEST", "answer_mode": "비교"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "insufficient_evidence"
    assert "internal validation failure" in body["abstention_reason"]


def test_ask_unknown_answer_mode_rejected(api_client):
    r = api_client.post(
        "/v1/ask",
        json={"event_id": "event.chibi", "question": "hi", "answer_mode": "not_a_mode"},
    )
    assert r.status_code == 400
