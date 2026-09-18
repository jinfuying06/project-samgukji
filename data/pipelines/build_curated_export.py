#!/usr/bin/env python3
"""Curated Export Transform (ADR-0003, addresses D-018).

Reads the S1 research working formats and normalizes them into
data/schemas/*.schema.json-conformant records, packaged as a versioned
curated export under ${TKAF_PRIVATE_DATA_ROOT}/curated/app_export/<export_id>/.

This is an OFFLINE batch step, never run inline by the backend at request
time (app/architecture/system.md, ADR-0003). Re-run this whenever
research/evidence_matrix.csv or analysis/outputs/result.json changes
(e.g. after a D-016 expansion pass), then run
app/backend/importers/import_curated_export.py to make it live.

Field-mapping rules this transform owns (documented here, not invented
per-request downstream):

- confidence: CSV's "high"/"medium"/"low" strings -> 0.8/0.5/0.2 floats.
  This is a coarse, documented approximation, not a measured probability.
- person_refs: CSV's ";"-joined "PERSON-XXX" tokens -> an array of
  canonical "person.xxx" IDs, via PERSON_TOKEN_TO_ID below. Encountering
  an unmapped PERSON-XXX token is a hard error (fail loud), never a
  silent drop -- this is exactly the class of bug D-020 fixed elsewhere
  (a hardcoded cast list silently undercounting people). Extend the map
  when a future expansion pass adds a person.
- primary_actor / subject_of_claim: free-text Chinese names (e.g. "曹操",
  "孫盛(commentator)", "江表傳(source)"). Only names matching a real
  person's canonical_name_zh resolve to a person_id; commentator/cited-work
  strings are recognized and excluded from relationship edges (they are
  sources describing the event, not participants in it), matching
  analysis/network_analysis_plan.md and app/architecture/threat_model.md.
- locator.paragraph_index: research/evidence_matrix.csv's `locator` column
  is free-text prose (e.g. "paragraph containing first 赤壁 mention"), not
  the ingestion pipeline's original 0-based paragraph_index. KNOWN
  LIMITATION: this transform assigns a synthetic ordinal, unique within
  (work_title, volume_or_chapter), because evidence_matrix.csv does not
  carry the real paragraph_index and this run does not attempt to
  re-match rows against the private candidate pool by content. This is
  schema-conformant but NOT a reproduction of build_chibi_sample.py's
  original locator. Flagged for whoever next touches R1's evidence
  extraction to carry the real paragraph_index through instead.
- divergence.*.method text ("classification=...; evidence_ids=...;
  rationale: ...") is parsed into structured fields on the *curated*
  metrics record (metrics.json), without editing analysis/outputs/result.json
  itself (that file stays exactly as A1 produced it).

Every evidence record gets coding_validation_status from
research/intercoder_reliability.md's current state. Updated to human_validated
on 2026-09-18 after the human project owner completed a real review of all 30
rows (agree/disagree/unsure audit against the assigned labels and project
paraphrase, via the delivered review packet) and reported no disagreements --
see research/intercoder_reliability.md's "Human review pass" section and
handoffs/DECISIONS.md#D-024. This is the one place that value is set; any
future re-coding pass that isn't reviewed the same way should flip it back,
per ADR-0003.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]

# --- Field-mapping tables (documented above; extend, never guess silently) ---

PERSON_TOKEN_TO_ID = {
    "PERSON-CAOCAO": "person.cao_cao",
    "PERSON-SUNQUAN": "person.sun_quan",
    "PERSON-LIUBEI": "person.liu_bei",
    "PERSON-ZHOUYU": "person.zhou_yu",
    "PERSON-ZHUGELIANG": "person.zhuge_liang",
    "PERSON-HUANGGAI": "person.huang_gai",
    "PERSON-GUANYU": "person.guan_yu",
    "PERSON-LUSU": "person.lu_su",
    "PERSON-ZHAOYUN": "person.zhao_yun",
    "PERSON-GUOJIA": "person.guo_jia",
}

CONFIDENCE_MAP = {"high": 0.8, "medium": 0.5, "low": 0.2}

# D-017: current validation state. NOT a single global value -- the human owner's D-024
# review covered only the rows extracted through "R1 (single coder)" and "Expansion pass
# (single coder)" (the original 30 rows, evidence_matrix.csv rows 1-30). Rows added by any
# later pass (e.g. "Expansion pass 2 (single coder)", 2026-09-18, +18 rows) have NOT been
# human-reviewed and must not be marked human_validated just because most of the file is.
# Single source of truth for this per-row decision: coding_validation_status_for_row() below.
HUMAN_REVIEWED_EXTRACTION_REVIEWERS = {"R1 (single coder)", "Expansion pass (single coder)"}


def coding_validation_status_for_row(row: dict) -> str:
    return (
        "human_validated"
        if row.get("extraction_reviewer") in HUMAN_REVIEWED_EXTRACTION_REVIEWERS
        else "llm_llm_validated_only"
    )

EVENT_ID = "event.chibi"
EVENT_NAME = "Battle of Red Cliffs"
EVENT_NAME_ZH = "赤壁之戰"

# research/evidence_matrix.csv's event_ref column uses a different ID convention
# ("BATTLE-CHIBI-001") than data/schemas/event.schema.json's pattern
# (^event\.[a-z0-9_]+$). Same class of ID-convention mismatch as PERSON_TOKEN_TO_ID
# above -- mapped explicitly, extend if a second event is ever added to this CSV.
EVENT_REF_TOKEN_TO_ID = {"BATTLE-CHIBI-001": EVENT_ID}


def map_event_ref(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return EVENT_ID
    if raw not in EVENT_REF_TOKEN_TO_ID:
        raise TransformError(
            f"Unmapped event_ref token '{raw}' in research/evidence_matrix.csv. "
            "Add it to EVENT_REF_TOKEN_TO_ID in this script."
        )
    return EVENT_REF_TOKEN_TO_ID[raw]

SCHEMA_VERSION = "1.0.0-slice"
PIPELINE_VERSION = "build_curated_export.py@1.0.0"


class TransformError(RuntimeError):
    pass


def repo_env():
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")
    private_root = os.environ.get("TKAF_PRIVATE_DATA_ROOT", "../tkaf-private-data")
    private_root_path = (REPO_ROOT / private_root).resolve()
    return private_root_path


def load_person_registry(private_root: Path) -> dict:
    reg_path = private_root / "analysis" / "tables" / "person_registry.json"
    with open(reg_path, encoding="utf-8") as f:
        return json.load(f)


def load_evidence_rows() -> list[dict]:
    path = REPO_ROOT / "research" / "evidence_matrix.csv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_result_json() -> dict:
    path = REPO_ROOT / "analysis" / "outputs" / "result.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_run_manifest() -> dict:
    path = REPO_ROOT / "analysis" / "outputs" / "run_manifest.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def map_person_tokens(person_refs_raw: str) -> list[str]:
    ids = []
    for tok in person_refs_raw.split(";"):
        tok = tok.strip()
        if not tok:
            continue
        if tok not in PERSON_TOKEN_TO_ID:
            raise TransformError(
                f"Unmapped person token '{tok}' in research/evidence_matrix.csv. "
                "Add it to PERSON_TOKEN_TO_ID in this script -- do not silently drop it "
                "(this is exactly the class of bug D-020 fixed elsewhere)."
            )
        ids.append(PERSON_TOKEN_TO_ID[tok])
    return ids


def name_to_person_id(name_zh: str, registry: dict) -> str | None:
    """Resolve a free-text actor/subject name to a person_id, or None for
    commentators/cited works (e.g. '孫盛(commentator)', '江表傳(source)')."""
    if not name_zh:
        return None
    if "(commentator)" in name_zh or "(source)" in name_zh:
        return None
    for pid, rec in registry.items():
        if rec["canonical_name_zh"] == name_zh:
            return pid
    return None


DIVERGENCE_RE = re.compile(
    r"classification=(?P<classification>\w+);\s*evidence_ids=(?P<ids>[^;]+);\s*rationale:\s*(?P<rationale>.*)",
    re.DOTALL,
)


def parse_divergence_method(method: str) -> dict | None:
    m = DIVERGENCE_RE.match(method.strip())
    if not m:
        return None
    return {
        "classification": m.group("classification"),
        "evidence_ids": [e.strip() for e in m.group("ids").split(",") if e.strip()],
        "rationale": m.group("rationale").strip(),
    }


def build_persons(registry: dict) -> list[dict]:
    persons = []
    for pid, rec in registry.items():
        persons.append(
            {
                "person_id": pid,
                "canonical_name_zh": rec["canonical_name_zh"],
                "canonical_name_ko": None,
                "aliases": rec["aliases"],
                "alias_collision_note": rec.get("alias_collision_note"),
                "notes": rec.get("notes"),
            }
        )
    return persons


def build_evidence_and_paragraph_index(rows: list[dict]) -> list[dict]:
    counters: dict[tuple[str, str], int] = {}
    evidence = []
    for row in rows:
        excerpt = row.get("excerpt_zh") or None
        if excerpt is not None and len(excerpt) > 200:
            excerpt = excerpt[:200]

        confidence_str = (row.get("confidence") or "").strip().lower()
        if confidence_str not in CONFIDENCE_MAP:
            raise TransformError(
                f"Unmapped confidence value '{confidence_str}' for {row.get('evidence_id')}"
            )

        key = (row["work_title"], row["volume_or_chapter"])
        counters[key] = counters.get(key, 0)
        paragraph_index = counters[key]
        counters[key] += 1

        evidence.append(
            {
                "evidence_id": row["evidence_id"],
                "source_layer": row["source_layer"],
                "work_title": row["work_title"],
                "edition_ref": row.get("edition") or None,
                "volume_or_chapter": row["volume_or_chapter"],
                "locator": {
                    "paragraph_index": paragraph_index,
                    "annotation_index": None,
                    "char_start": None,
                    "char_end": None,
                },
                "permitted_excerpt": excerpt,
                "coding_label": row["coding_label"],
                "person_refs": map_person_tokens(row.get("person_refs", "")),
                "confidence": CONFIDENCE_MAP[confidence_str],
                "review_status": "single_coded"
                if row.get("review_status") == "extracted_not_double_coded"
                else row.get("review_status", "unreviewed"),
                "coding_validation_status": coding_validation_status_for_row(row),
                "ambiguity_note": row.get("ambiguity_note") or None,
                "event_ref": map_event_ref(row.get("event_ref")),
            }
        )
    return evidence


def build_event(evidence: list[dict], registry: dict) -> dict:
    layers_seen: set[str] = set()
    participants_by_person: dict[str, dict] = {}
    for ev in evidence:
        layers_seen.add(ev["source_layer"])
        for pid in ev["person_refs"]:
            key = (pid, ev["source_layer"])
            if key not in participants_by_person:
                participants_by_person[key] = {
                    "person_id": pid,
                    "role": "participant",
                    "source_layer": ev["source_layer"],
                    "evidence_refs": [],
                }
            participants_by_person[key]["evidence_refs"].append(ev["evidence_id"])

    return {
        "event_id": EVENT_ID,
        "event_name": EVENT_NAME,
        "event_name_zh": EVENT_NAME_ZH,
        "start_time": {"value": None, "uncertainty": "unknown"},
        "end_time": {"value": None, "uncertainty": "unknown"},
        "location": "赤壁",
        "participants": list(participants_by_person.values()),
        "outcome": "曹操軍敗退 (Cao Cao's forces defeated)",
        "source_layer_coverage": sorted(layers_seen),
        "notes": None,
    }


def build_relationships(rows: list[dict], registry: dict) -> list[dict]:
    edges = []
    for row in rows:
        actor_id = name_to_person_id(row.get("primary_actor", ""), registry)
        subject_id = name_to_person_id(row.get("subject_of_claim", ""), registry)
        if not actor_id or not subject_id or actor_id == subject_id:
            continue
        confidence_str = (row.get("confidence") or "").strip().lower()
        edges.append(
            {
                "edge_id": f"edge.{row['evidence_id']}",
                "from_person_id": actor_id,
                "to_person_id": subject_id,
                "relation_type": row["coding_label"],
                "direction": "directed",
                "start": None,
                "end": None,
                "event_ref": map_event_ref(row.get("event_ref")),
                "source_layer": row["source_layer"],
                "confidence": CONFIDENCE_MAP.get(confidence_str, 0.5),
                "evidence_refs": [row["evidence_id"]],
                "notes": None,
            }
        )
    return edges


def build_metrics(result: dict) -> dict:
    metrics = []
    for m in result["metrics"]:
        entry = dict(m)
        if m["metric_id"].startswith("divergence."):
            parsed = parse_divergence_method(m.get("method", ""))
            if parsed:
                entry["classification"] = parsed["classification"]
                entry["evidence_ids"] = parsed["evidence_ids"]
        metrics.append(entry)
    return {
        "event_ref": EVENT_ID,
        "analysis_id": result["analysis_id"],
        "run_id": result["run_id"],
        "population": result["population"],
        "metrics": metrics,
        "limitations": result.get("limitations", []),
        "warnings": result.get("warnings", []),
    }


# DISCOVERED GAP (new, found during E1/backend implementation, flag for orchestrator):
# data/schemas/evidence.schema.json (D1, S1-era) requires ingestion-lineage fields
# (source_id, work_id, text_hash, original_language_text_status, translation_type,
# extraction_reviewer) and forbids additionalProperties -- it describes a raw
# evidence CANDIDATE record, not a coded+curated one. app/architecture/api_contract.yaml's
# EvidenceSpan (E0, S3) requires a different, coding-oriented field set (coding_label,
# confidence as 0-1 float, review_status, coding_validation_status) and its own doc-comment
# claims it IS data/schemas/evidence.schema.json's shape -- it is not; the two were authored
# independently and never diffed against each other. Since api_contract.yaml is the frozen,
# B2-approved, backend/frontend-facing contract, this transform validates evidence records
# against ITS EvidenceSpan shape (embedded below), not the literal evidence.schema.json file.
# This script's write scope does not include editing data/schemas/*.schema.json, so the
# reconciliation of these two schemas is left as an explicit open item for whoever owns
# that file next -- see the final handoff report.
EVIDENCE_CURATED_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "evidence_id", "source_layer", "work_title", "volume_or_chapter", "locator",
        "coding_label", "confidence", "review_status", "coding_validation_status",
    ],
    "properties": {
        "evidence_id": {"type": "string"},
        "source_layer": {"type": "string", "enum": ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE", "LATER_INTERPRETATION", "GAME_DATA"]},
        "work_title": {"type": "string"},
        "edition_ref": {"type": ["string", "null"]},
        "volume_or_chapter": {"type": "string"},
        "locator": {
            "type": "object",
            "required": ["paragraph_index"],
            "properties": {
                "paragraph_index": {"type": "integer", "minimum": 0},
                "annotation_index": {"type": ["integer", "null"]},
                "char_start": {"type": ["integer", "null"]},
                "char_end": {"type": ["integer", "null"]},
            },
            "additionalProperties": False,
        },
        "permitted_excerpt": {"type": ["string", "null"], "maxLength": 200},
        "coding_label": {"type": "string"},
        "person_refs": {"type": "array", "items": {"type": "string", "pattern": r"^person\.[a-z0-9_]+$"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "review_status": {"type": "string", "enum": ["unreviewed", "single_coded", "double_coded", "adjudicated"]},
        "coding_validation_status": {"type": "string", "enum": ["llm_llm_validated_only", "human_validated"]},
        "ambiguity_note": {"type": ["string", "null"]},
        "event_ref": {"type": "string"},
    },
}


def load_schema(name: str) -> dict:
    for base in (REPO_ROOT / "data" / "schemas", REPO_ROOT / "analysis" / "schemas"):
        path = base / name
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(name)


def validate_records(records: list[dict], schema: dict, label: str):
    validator = jsonschema.Draft7Validator(schema) if "draft-07" in schema.get("$schema", "") else jsonschema.Draft202012Validator(schema)
    for i, rec in enumerate(records):
        errors = sorted(validator.iter_errors(rec), key=lambda e: e.path)
        if errors:
            msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
            raise TransformError(f"{label}[{i}] ({rec.get('person_id') or rec.get('evidence_id') or rec.get('edge_id')}) failed schema validation: {msgs}")


def main(approval_ref: str | None = None) -> Path:
    private_root = repo_env()
    registry = load_person_registry(private_root)
    rows = load_evidence_rows()
    result = load_result_json()
    run_manifest = load_run_manifest()

    persons = build_persons(registry)
    evidence = build_evidence_and_paragraph_index(rows)
    event = build_event(evidence, registry)
    relationships = build_relationships(rows, registry)
    metrics = build_metrics(result)

    validate_records(persons, load_schema("person.schema.json"), "persons")
    validate_records([event], load_schema("event.schema.json"), "events")
    validate_records(evidence, EVIDENCE_CURATED_SCHEMA, "evidence")
    validate_records(relationships, load_schema("relationship.schema.json"), "relationships")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    export_id = f"chibi-{result['run_id']}"

    export_dir = private_root / "curated" / "app_export" / export_id
    export_dir.mkdir(parents=True, exist_ok=True)

    evidence_matrix_checksum = next(
        (f["sha256"] for f in run_manifest.get("input_files", []) if f["path"].endswith("evidence_matrix.csv")),
        None,
    )
    if not evidence_matrix_checksum:
        raise TransformError("Could not find evidence_matrix.csv checksum in analysis/outputs/run_manifest.json")

    # Dataset-level summary must not overclaim: only "human_validated" if EVERY row is.
    # A single not-yet-reviewed row (e.g. a fresh expansion pass) makes the honest overall
    # claim "llm_llm_validated_only" -- the per-row field on each evidence record (above)
    # is the accurate, granular source of truth; this is a conservative rollup of it.
    row_statuses = {coding_validation_status_for_row(row) for row in rows}
    dataset_coding_validation_status = (
        "human_validated" if row_statuses == {"human_validated"} else "llm_llm_validated_only"
    )

    dataset_version = {
        "pipeline_version": PIPELINE_VERSION,
        "run_id": result["run_id"],
        "generated_at": generated_at,
        "coding_validation_status": dataset_coding_validation_status,
        "evidence_matrix_checksum": evidence_matrix_checksum,
    }

    files_to_write = {
        "persons.json": persons,
        "events.json": [event],
        "evidence.json": evidence,
        "relationships.json": relationships,
        "metrics.json": metrics,
        "dataset_version.json": dataset_version,
    }
    file_entries = []
    for filename, payload in files_to_write.items():
        path = export_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        record_count = len(payload) if isinstance(payload, list) else 1
        file_entries.append(
            {
                "relative_path": filename,
                "sha256": sha256_file(path),
                "record_type": filename.replace(".json", ""),
                "record_count": record_count,
            }
        )

    approval_ref = approval_ref or "handoffs/APPROVALS.md#B2 (2026-09-17, no dedicated curated-export approval workflow exists yet -- see app/architecture/threat_model.md Open items)"

    manifest = {
        "export_id": export_id,
        "created_at": generated_at,
        "schema_version": SCHEMA_VERSION,
        "source_dataset_versions": [result["run_id"], run_manifest["run_id"]],
        "pipeline_version": PIPELINE_VERSION,
        "entity_resolution_version": "person_id_map@1.0.0",
        "score_model_versions": [],
        "source_layers": sorted({e["source_layer"] for e in evidence}),
        "files": file_entries,
        "rights_review_status": "approved_with_limits",
        "approval_ref": approval_ref,
    }
    validate_records([manifest], load_schema("app_export_manifest.schema.json"), "manifest")

    with open(export_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Curated export written: {export_dir}")
    print(f"  persons={len(persons)} evidence={len(evidence)} relationships={len(relationships)} metrics={len(metrics['metrics'])}")
    return export_dir


if __name__ == "__main__":
    approval = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        main(approval)
    except TransformError as e:
        print(f"TRANSFORM FAILED: {e}", file=sys.stderr)
        sys.exit(1)
