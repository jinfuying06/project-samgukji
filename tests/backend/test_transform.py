import json


def test_transform_produces_valid_schema_conformant_records(curated_export_dir):
    with open(curated_export_dir / "manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["rights_review_status"] in ("approved", "approved_with_limits")
    assert manifest["approval_ref"].strip()
    for entry in manifest["files"]:
        assert (curated_export_dir / entry["relative_path"]).exists()

    with open(curated_export_dir / "evidence.json", encoding="utf-8") as f:
        evidence = json.load(f)
    assert len(evidence) >= 22  # original 22 + expansion rows
    for e in evidence:
        assert 0.0 <= e["confidence"] <= 1.0
        # D-017: always present and valid; not hardcoded to one value -- rows from a
        # not-yet-human-reviewed extraction pass are correctly "llm_llm_validated_only"
        # (see data/pipelines/build_curated_export.py's per-row logic, fixed 2026-09-18).
        assert e["coding_validation_status"] in ("human_validated", "llm_llm_validated_only")
        assert isinstance(e["person_refs"], list)
        for pid in e["person_refs"]:
            assert pid.startswith("person.")

    with open(curated_export_dir / "persons.json", encoding="utf-8") as f:
        persons = json.load(f)
    assert len(persons) == 10
    ids = [p["person_id"] for p in persons]
    assert len(ids) == len(set(ids))  # no duplicate canonical IDs


def test_transform_rejects_unmapped_person_token():
    import pytest
    from data.pipelines.build_curated_export import TransformError, map_person_tokens

    with pytest.raises(TransformError):
        map_person_tokens("PERSON-DOES-NOT-EXIST")


def test_divergence_method_parsing():
    from data.pipelines.build_curated_export import parse_divergence_method

    parsed = parse_divergence_method(
        "classification=contradictory; evidence_ids=HB-J54-P2,RM-C050-P3; rationale: something happened."
    )
    assert parsed["classification"] == "contradictory"
    assert parsed["evidence_ids"] == ["HB-J54-P2", "RM-C050-P3"]
