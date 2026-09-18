"""Read-only DB access for the API. The backend never writes product data
at request time -- only the offline importer writes (app/architecture/system.md)."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

REPO_ROOT = Path(__file__).resolve().parents[3]


def default_db_path() -> Path:
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")
    url = os.environ.get("TKAF_APP_DATABASE_URL", "sqlite:///data/runtime/tkaf.local.sqlite3")
    return (REPO_ROOT / url[len("sqlite:///"):]).resolve()


class DB:
    """Thin wrapper so main.py and tests can point at different sqlite files."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or default_db_path()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def active_dataset_version(self, conn: sqlite3.Connection) -> sqlite3.Row | None:
        return conn.execute(
            "SELECT * FROM dataset_versions WHERE is_active = 1 ORDER BY dataset_version_id DESC LIMIT 1"
        ).fetchone()

    def dataset_version_ref(self, conn: sqlite3.Connection) -> dict | None:
        row = self.active_dataset_version(conn)
        if row is None:
            return None
        return {
            "pipeline_version": row["pipeline_version"],
            "run_id": row["run_id"],
            "generated_at": row["generated_at"],
            "coding_validation_status": row["coding_validation_status"],
            "evidence_matrix_checksum": row["evidence_matrix_checksum"],
        }

    def get_event(self, conn: sqlite3.Connection, dvid: int, event_id: str) -> dict | None:
        row = conn.execute(
            "SELECT * FROM events WHERE dataset_version_id = ? AND event_id = ?", (dvid, event_id)
        ).fetchone()
        if row is None:
            return None
        participants = conn.execute(
            "SELECT * FROM event_participants WHERE dataset_version_id = ? AND event_id = ?", (dvid, event_id)
        ).fetchall()
        return {
            "event_id": row["event_id"],
            "event_name": row["event_name"],
            "event_name_zh": row["event_name_zh"],
            "location": row["location"],
            "outcome": row["outcome"],
            "source_layer_coverage": json.loads(row["source_layer_coverage_json"]),
            "participants": [
                {
                    "person_id": p["person_id"],
                    "role": p["role"],
                    "source_layer": p["source_layer"],
                    "evidence_refs": json.loads(p["evidence_refs_json"]),
                }
                for p in participants
            ],
        }

    def get_people_for_event(self, conn: sqlite3.Connection, dvid: int, event_id: str) -> list[dict]:
        person_ids = [
            r["person_id"]
            for r in conn.execute(
                "SELECT DISTINCT person_id FROM event_participants WHERE dataset_version_id = ? AND event_id = ?",
                (dvid, event_id),
            ).fetchall()
        ]
        people = []
        for pid in person_ids:
            prow = conn.execute(
                "SELECT * FROM persons WHERE dataset_version_id = ? AND person_id = ?", (dvid, pid)
            ).fetchone()
            if prow is None:
                continue
            coverage_rows = conn.execute(
                """SELECT source_layer, COUNT(*) as n FROM evidence
                   WHERE dataset_version_id = ? AND event_ref = ?
                   AND evidence_id IN (
                       SELECT evidence_id FROM evidence e2, json_each(e2.person_refs_json) je
                       WHERE e2.dataset_version_id = ? AND je.value = ?
                   )
                   GROUP BY source_layer""",
                (dvid, event_id, dvid, pid),
            ).fetchall()
            coverage = {r["source_layer"]: r["n"] for r in coverage_rows}
            people.append(
                {
                    "person_id": prow["person_id"],
                    "canonical_name_zh": prow["canonical_name_zh"],
                    "canonical_name_ko": prow["canonical_name_ko"],
                    "aliases": json.loads(prow["aliases_json"]),
                    "evidence_coverage": coverage,
                }
            )
        return people

    def get_person(self, conn: sqlite3.Connection, dvid: int, person_id: str) -> dict | None:
        row = conn.execute(
            "SELECT * FROM persons WHERE dataset_version_id = ? AND person_id = ?", (dvid, person_id)
        ).fetchone()
        if row is None:
            return None
        return {
            "person_id": row["person_id"],
            "canonical_name_zh": row["canonical_name_zh"],
            "canonical_name_ko": row["canonical_name_ko"],
            "aliases": json.loads(row["aliases_json"]),
        }

    def get_evidence_for_person(
        self, conn: sqlite3.Connection, dvid: int, person_id: str, event_id: str | None, source_layer: str | None
    ) -> list[dict]:
        query = """SELECT e.* FROM evidence e, json_each(e.person_refs_json) je
                   WHERE e.dataset_version_id = ? AND je.value = ?"""
        params: list = [dvid, person_id]
        if event_id:
            query += " AND e.event_ref = ?"
            params.append(event_id)
        if source_layer:
            query += " AND e.source_layer = ?"
            params.append(source_layer)
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            result.append(
                {
                    "evidence_id": r["evidence_id"],
                    "source_layer": r["source_layer"],
                    "work_title": r["work_title"],
                    "edition_ref": r["edition_ref"],
                    "volume_or_chapter": r["volume_or_chapter"],
                    "locator": json.loads(r["locator_json"]),
                    "permitted_excerpt": r["permitted_excerpt"],
                    "coding_label": r["coding_label"],
                    "person_refs": json.loads(r["person_refs_json"]),
                    "confidence": r["confidence"],
                    "review_status": r["review_status"],
                    "coding_validation_status": r["coding_validation_status"],
                    "ambiguity_note": r["ambiguity_note"],
                }
            )
        return result

    def evidence_exists(self, conn: sqlite3.Connection, dvid: int, evidence_id: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM evidence WHERE dataset_version_id = ? AND evidence_id = ?", (dvid, evidence_id)
        ).fetchone()
        return row is not None

    def metric_exists(self, conn: sqlite3.Connection, dvid: int, metric_id: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM metrics WHERE dataset_version_id = ? AND metric_id = ?", (dvid, metric_id)
        ).fetchone()
        return row is not None

    def get_metrics(
        self, conn: sqlite3.Connection, dvid: int, event_id: str, kind: str | None
    ) -> dict | None:
        meta = conn.execute(
            "SELECT * FROM metrics_meta WHERE dataset_version_id = ? AND event_ref = ?", (dvid, event_id)
        ).fetchone()
        if meta is None:
            return None
        # DISCOVERED GAP (flag for orchestrator/architect): analysis/outputs/result.json
        # also contains network_edge_count.* metrics, a 4th kind not in
        # app/architecture/api_contract.yaml's documented enum (coverage/label_frequency/
        # divergence). That same information (edge counts) is already properly exposed via
        # GET /v1/events/{event_id}/relationships (the edges array + no_centrality_computed),
        # so this endpoint deliberately excludes network_edge_count.* rather than silently
        # violating the frozen contract's documented 3-kind default. Not fixed by editing
        # api_contract.yaml -- outside this task's write scope (app/architecture/*).
        query = "SELECT * FROM metrics WHERE dataset_version_id = ? AND event_ref = ? AND metric_id NOT LIKE 'network_edge_count.%'"
        params: list = [dvid, event_id]
        if kind:
            query += " AND metric_id LIKE ?"
            params.append(f"{kind}.%")
        rows = conn.execute(query, params).fetchall()
        metrics = [
            {
                "metric_id": r["metric_id"],
                "name": r["name"],
                "value": r["value"],
                "unit": r["unit"],
                "interval_low": r["interval_low"],
                "interval_high": r["interval_high"],
                "method": r["method"],
            }
            for r in rows
        ]
        return {
            "population": {"n": meta["population_n"], "description": meta["population_description"]},
            "metrics": metrics,
            "limitations": json.loads(meta["limitations_json"]),
            "warnings": json.loads(meta["warnings_json"]),
        }

    def get_relationships(
        self, conn: sqlite3.Connection, dvid: int, event_id: str, source_layer: str | None
    ) -> list[dict]:
        query = "SELECT * FROM relationships WHERE dataset_version_id = ? AND event_ref = ?"
        params: list = [dvid, event_id]
        if source_layer:
            query += " AND source_layer = ?"
            params.append(source_layer)
        rows = conn.execute(query, params).fetchall()
        return [
            {
                "edge_id": r["edge_id"],
                "from_person_id": r["from_person_id"],
                "to_person_id": r["to_person_id"],
                "relation_type": r["relation_type"],
                "direction": r["direction"],
                "source_layer": r["source_layer"],
                "confidence": r["confidence"],
                "evidence_refs": json.loads(r["evidence_refs_json"]),
            }
            for r in rows
        ]
