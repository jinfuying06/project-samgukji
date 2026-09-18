#!/usr/bin/env python3
"""Curated export importer (app/backend/importers/README.md, ADR-0003).

Validates an approved curated-export package and imports it into the
runtime SQLite DB, atomically and idempotently:

- validates manifest.json against data/schemas/app_export_manifest.schema.json
- verifies every file's sha256 checksum against the manifest
- rejects a package with no approval_ref (schema-enforced: minLength 1)
  or a rights_review_status outside the schema's approved enum values
- if export_id already exists in dataset_versions, this is a no-op
  (idempotent) -- it does not re-import or error
- runs the whole import in one SQLite transaction; on any failure, rolls
  back completely and leaves the previously-active version serving
  (data/APP_DATABASE_POLICY.md)

Never reads raw or private-analysis data directly -- only the already-built
curated export package (app/architecture/system.md's Importer boundary).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[3]


class ImportRejected(RuntimeError):
    pass


def load_manifest_schema() -> dict:
    with open(REPO_ROOT / "data" / "schemas" / "app_export_manifest.schema.json", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(export_dir: Path) -> dict:
    manifest_path = export_dir / "manifest.json"
    if not manifest_path.exists():
        raise ImportRejected(f"No manifest.json in {export_dir}")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    schema = load_manifest_schema()
    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as e:
        raise ImportRejected(f"manifest.json failed schema validation: {e.message}") from e

    if manifest["rights_review_status"] not in ("approved", "approved_with_limits"):
        raise ImportRejected(f"Unapproved rights_review_status: {manifest['rights_review_status']}")
    if not manifest.get("approval_ref", "").strip():
        raise ImportRejected("Missing approval_ref -- refusing to import an unapproved package")

    for entry in manifest["files"]:
        file_path = export_dir / entry["relative_path"]
        if not file_path.exists():
            raise ImportRejected(f"Manifest references missing file: {entry['relative_path']}")
        actual = sha256_file(file_path)
        if actual != entry["sha256"]:
            raise ImportRejected(
                f"Checksum mismatch for {entry['relative_path']}: manifest={entry['sha256']} actual={actual}"
            )
    return manifest


def load_json(export_dir: Path, name: str):
    with open(export_dir / name, encoding="utf-8") as f:
        return json.load(f)


def import_export(export_dir: Path, db_path: Path) -> str:
    """Returns 'imported' or 'already_imported'."""
    manifest = validate_manifest(export_dir)
    export_id = manifest["export_id"]

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        cur = conn.execute("SELECT dataset_version_id FROM dataset_versions WHERE export_id = ?", (export_id,))
        existing = cur.fetchone()
        if existing is not None:
            return "already_imported"

        dataset_version = load_json(export_dir, "dataset_version.json")
        persons = load_json(export_dir, "persons.json")
        events = load_json(export_dir, "events.json")
        evidence = load_json(export_dir, "evidence.json")
        relationships = load_json(export_dir, "relationships.json")
        metrics_doc = load_json(export_dir, "metrics.json")

        conn.execute("BEGIN")
        cur = conn.execute(
            """INSERT INTO dataset_versions
               (export_id, pipeline_version, run_id, generated_at, coding_validation_status,
                evidence_matrix_checksum, imported_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                export_id,
                dataset_version["pipeline_version"],
                dataset_version["run_id"],
                dataset_version["generated_at"],
                dataset_version["coding_validation_status"],
                dataset_version["evidence_matrix_checksum"],
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        )
        dvid = cur.lastrowid

        for p in persons:
            conn.execute(
                """INSERT INTO persons (dataset_version_id, person_id, canonical_name_zh, canonical_name_ko,
                   aliases_json, alias_collision_note, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (dvid, p["person_id"], p["canonical_name_zh"], p.get("canonical_name_ko"),
                 json.dumps(p["aliases"], ensure_ascii=False), p.get("alias_collision_note"), p.get("notes")),
            )

        for ev in events:
            conn.execute(
                """INSERT INTO events (dataset_version_id, event_id, event_name, event_name_zh, location, outcome,
                   source_layer_coverage_json) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (dvid, ev["event_id"], ev["event_name"], ev.get("event_name_zh"), ev.get("location"),
                 ev.get("outcome"), json.dumps(ev["source_layer_coverage"], ensure_ascii=False)),
            )
            for part in ev["participants"]:
                conn.execute(
                    """INSERT INTO event_participants (dataset_version_id, event_id, person_id, role,
                       source_layer, evidence_refs_json) VALUES (?, ?, ?, ?, ?, ?)""",
                    (dvid, ev["event_id"], part["person_id"], part["role"], part["source_layer"],
                     json.dumps(part.get("evidence_refs", []), ensure_ascii=False)),
                )

        for e in evidence:
            conn.execute(
                """INSERT INTO evidence (dataset_version_id, evidence_id, event_ref, source_layer, work_title,
                   edition_ref, volume_or_chapter, locator_json, permitted_excerpt, coding_label, person_refs_json,
                   confidence, review_status, coding_validation_status, ambiguity_note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    dvid, e["evidence_id"], e["event_ref"], e["source_layer"], e["work_title"], e.get("edition_ref"),
                    e["volume_or_chapter"], json.dumps(e["locator"], ensure_ascii=False), e.get("permitted_excerpt"),
                    e["coding_label"], json.dumps(e.get("person_refs", []), ensure_ascii=False), e["confidence"],
                    e["review_status"], e["coding_validation_status"], e.get("ambiguity_note"),
                ),
            )

        for r in relationships:
            conn.execute(
                """INSERT INTO relationships (dataset_version_id, edge_id, from_person_id, to_person_id,
                   relation_type, direction, start_value, end_value, event_ref, source_layer, confidence,
                   evidence_refs_json, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    dvid, r["edge_id"], r["from_person_id"], r["to_person_id"], r["relation_type"], r["direction"],
                    r.get("start"), r.get("end"), r.get("event_ref"), r["source_layer"], r["confidence"],
                    json.dumps(r["evidence_refs"], ensure_ascii=False), r.get("notes"),
                ),
            )

        event_ref = metrics_doc["event_ref"]
        for m in metrics_doc["metrics"]:
            conn.execute(
                """INSERT INTO metrics (dataset_version_id, event_ref, metric_id, name, value, unit,
                   interval_low, interval_high, method, classification, evidence_ids_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    dvid, event_ref, m["metric_id"], m["name"], m.get("value"), m["unit"],
                    m.get("interval_low"), m.get("interval_high"), m.get("method"),
                    m.get("classification"), json.dumps(m.get("evidence_ids")) if m.get("evidence_ids") else None,
                ),
            )
        conn.execute(
            """INSERT INTO metrics_meta (dataset_version_id, event_ref, analysis_id, run_id, population_n,
               population_description, limitations_json, warnings_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dvid, event_ref, metrics_doc["analysis_id"], metrics_doc["run_id"],
                metrics_doc["population"]["n"], metrics_doc["population"]["description"],
                json.dumps(metrics_doc.get("limitations", []), ensure_ascii=False),
                json.dumps(metrics_doc.get("warnings", []), ensure_ascii=False),
            ),
        )

        conn.execute("UPDATE dataset_versions SET is_active = 0")
        conn.execute("UPDATE dataset_versions SET is_active = 1 WHERE dataset_version_id = ?", (dvid,))
        conn.commit()
        return "imported"
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def resolve_db_path(cli_value: str | None) -> Path:
    if cli_value:
        return Path(cli_value).resolve()
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")
    import os

    url = os.environ.get("TKAF_APP_DATABASE_URL", "")
    if not url.startswith("sqlite:///"):
        raise SystemExit("TKAF_APP_DATABASE_URL must be a sqlite:/// URL (or pass --db)")
    return (REPO_ROOT / url[len("sqlite:///"):]).resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("export_dir", type=Path)
    parser.add_argument("--db", default=None, help="Override DB path (default: TKAF_APP_DATABASE_URL from .env)")
    args = parser.parse_args()

    db_path = resolve_db_path(args.db)
    try:
        result = import_export(args.export_dir, db_path)
    except ImportRejected as e:
        print(f"IMPORT REJECTED: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Import result: {result} (db={db_path})")


if __name__ == "__main__":
    main()
