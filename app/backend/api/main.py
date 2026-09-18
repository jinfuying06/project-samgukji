"""TKAF backend API -- implements app/architecture/api_contract.yaml exactly
for the 적벽대전 vertical slice. Reads only the runtime DB (never raw or
private-analysis data at request time, per app/architecture/system.md)."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .db import DB
from .llm_client import build_llm_client
from .llm_validator import InterpretationValidationError, validate_and_check

SOURCE_LAYERS = {"HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE", "LATER_INTERPRETATION", "GAME_DATA"}
METRIC_KINDS = {"coverage", "label_frequency", "divergence"}
ANSWER_MODE_LAYERS = {
    "정사": {"HISTORY_BASE", "HISTORY_ANNOTATION"},
    "연의": {"ROMANCE"},
    "비교": {"HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"},
    "게임": {"GAME_DATA"},
}

app = FastAPI(title="TKAF API — 적벽대전 Vertical Slice", version="1.0.0-slice")

# Overridable in tests via app.state.db
app.state.db = DB()

# --- minimal rate limiting for /ask (system.md: 429 at the API layer) ---
_ASK_WINDOW_SECONDS = 60
_ASK_MAX_PER_WINDOW = 30
_ask_hits: dict[str, deque] = defaultdict(deque)


def _rate_limited(client_key: str) -> bool:
    now = time.monotonic()
    q = _ask_hits[client_key]
    while q and now - q[0] > _ASK_WINDOW_SECONDS:
        q.popleft()
    if len(q) >= _ASK_MAX_PER_WINDOW:
        return True
    q.append(now)
    return False


def error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error_code": error_code, "message": message})


class AskRequest(BaseModel):
    event_id: str
    question: str = Field(min_length=1)
    answer_mode: str


@app.get("/v1/events/{event_id}")
def get_event(event_id: str):
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.active_dataset_version(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        event = db.get_event(conn, dv["dataset_version_id"], event_id)
        if event is None:
            return error_response(404, "event_not_found", f"Unknown event_id: {event_id}")
        event["dataset_version"] = db.dataset_version_ref(conn)
        return event
    finally:
        conn.close()


@app.get("/v1/events/{event_id}/people")
def get_event_people(event_id: str):
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.active_dataset_version(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        event = db.get_event(conn, dv["dataset_version_id"], event_id)
        if event is None:
            return error_response(404, "event_not_found", f"Unknown event_id: {event_id}")
        people = db.get_people_for_event(conn, dv["dataset_version_id"], event_id)
        return {"event_id": event_id, "dataset_version": db.dataset_version_ref(conn), "people": people}
    finally:
        conn.close()


@app.get("/v1/people/{person_id}/evidence")
def get_person_evidence(
    person_id: str,
    event_id: str | None = Query(default=None),
    source_layer: str | None = Query(default=None),
):
    if source_layer is not None and source_layer not in SOURCE_LAYERS:
        return error_response(400, "invalid_source_layer", f"Unknown source_layer: {source_layer}")
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.active_dataset_version(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        person = db.get_person(conn, dv["dataset_version_id"], person_id)
        if person is None:
            return error_response(404, "person_not_found", f"Unknown person_id: {person_id}")
        evidence = db.get_evidence_for_person(conn, dv["dataset_version_id"], person_id, event_id, source_layer)
        return {"person_id": person_id, "dataset_version": db.dataset_version_ref(conn), "evidence": evidence}
    finally:
        conn.close()


@app.get("/v1/events/{event_id}/metrics")
def get_event_metrics(event_id: str, kind: str | None = Query(default=None)):
    if kind is not None and kind not in METRIC_KINDS:
        return error_response(
            409,
            "no_composite_score",
            f"'{kind}' is not a supported metric kind in this slice (only {sorted(METRIC_KINDS)}); "
            "no composite/display score exists yet (analysis/scoring_model.md).",
        )
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.active_dataset_version(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        result = db.get_metrics(conn, dv["dataset_version_id"], event_id, kind)
        if result is None:
            return error_response(404, "event_not_found", f"No metrics for event_id: {event_id}")
        result["event_id"] = event_id
        result["dataset_version"] = db.dataset_version_ref(conn)
        return result
    finally:
        conn.close()


@app.get("/v1/events/{event_id}/relationships")
def get_event_relationships(event_id: str, source_layer: str | None = Query(default=None)):
    if source_layer is not None and source_layer not in SOURCE_LAYERS:
        return error_response(400, "invalid_source_layer", f"Unknown source_layer: {source_layer}")
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.active_dataset_version(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        edges = db.get_relationships(conn, dv["dataset_version_id"], event_id, source_layer)
        return {
            "event_id": event_id,
            "dataset_version": db.dataset_version_ref(conn),
            "edges": edges,
            "no_centrality_computed": True,
        }
    finally:
        conn.close()


@app.get("/v1/version")
def get_version():
    db: DB = app.state.db
    conn = db.connect()
    try:
        dv = db.dataset_version_ref(conn)
        if dv is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        return dv
    finally:
        conn.close()


@app.post("/v1/ask")
def ask(payload: AskRequest, request: Request):
    if payload.answer_mode not in ANSWER_MODE_LAYERS:
        return error_response(400, "invalid_answer_mode", f"Unknown answer_mode: {payload.answer_mode}")

    client_key = request.client.host if request.client else "unknown"
    if _rate_limited(client_key):
        return error_response(429, "rate_limited", "Too many /ask requests -- please retry later.")

    db: DB = app.state.db
    conn = db.connect()
    try:
        dv_row = db.active_dataset_version(conn)
        if dv_row is None:
            return error_response(404, "no_active_dataset", "No dataset version is currently active")
        dvid = dv_row["dataset_version_id"]

        event = db.get_event(conn, dvid, payload.event_id)
        if event is None:
            return error_response(400, "event_not_found", f"Unknown event_id: {payload.event_id}")

        allowed_layers = ANSWER_MODE_LAYERS[payload.answer_mode]
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        input_refs = {
            "result_json_run_id": dv_row["run_id"],
            "evidence_matrix_checksum": dv_row["evidence_matrix_checksum"],
        }

        # 게임 mode always abstains in this slice -- no GAME_DATA source exists
        # (analysis/llm_contract.md rule 6). Never call the LLM for it.
        if payload.answer_mode == "게임":
            return {
                "interpretation_id": f"interp-{payload.event_id}-gamedata-refuse",
                "answer_mode": "게임",
                "status": "insufficient_evidence",
                "generated_at": now,
                "model": {"name": "n/a", "version": "n/a"},
                "prompt_version": "n/a",
                "input_refs": input_refs,
                "abstention_reason": "이 슬라이스에는 승인된 GAME_DATA 소스가 없습니다 (analysis/scoring_model.md).",
                "claims": [],
            }

        evidence_rows: list[dict] = []
        for pid_row in conn.execute(
            "SELECT DISTINCT person_id FROM event_participants WHERE dataset_version_id = ? AND event_id = ?",
            (dvid, payload.event_id),
        ).fetchall():
            for layer in allowed_layers:
                evidence_rows.extend(
                    db.get_evidence_for_person(conn, dvid, pid_row["person_id"], payload.event_id, layer)
                )
        # de-dupe by evidence_id (a row can involve multiple people)
        seen = set()
        dedup = []
        for e in evidence_rows:
            if e["evidence_id"] not in seen:
                seen.add(e["evidence_id"])
                dedup.append(e)
        evidence_rows = dedup

        valid_evidence_ids = {
            r["evidence_id"]
            for r in conn.execute(
                "SELECT evidence_id FROM evidence WHERE dataset_version_id = ? AND event_ref = ?",
                (dvid, payload.event_id),
            ).fetchall()
        }
        valid_metric_ids = {
            r["metric_id"]
            for r in conn.execute(
                "SELECT metric_id FROM metrics WHERE dataset_version_id = ? AND event_ref = ?",
                (dvid, payload.event_id),
            ).fetchall()
        }

        client = build_llm_client()
        context = {"evidence": evidence_rows, "now": now, "input_refs": input_refs}

        last_error: InterpretationValidationError | None = None
        for attempt in range(2):
            raw = client.generate(
                event_id=payload.event_id, question=payload.question, answer_mode=payload.answer_mode, context=context
            )
            try:
                validate_and_check(raw, valid_evidence_ids, valid_metric_ids)
                return raw
            except InterpretationValidationError as e:
                last_error = e
                continue

        # Never pass through an unvalidated response, even once, even on retry
        # (app/architecture/system.md's LLM response validator "must not do").
        return {
            "interpretation_id": f"interp-{payload.event_id}-validation-failed",
            "answer_mode": payload.answer_mode,
            "status": "insufficient_evidence",
            "generated_at": now,
            "model": {"name": "n/a", "version": "n/a"},
            "prompt_version": "n/a",
            "input_refs": input_refs,
            "abstention_reason": f"internal validation failure: {'; '.join(last_error.reasons) if last_error else 'unknown'}",
            "claims": [],
        }
    finally:
        conn.close()
