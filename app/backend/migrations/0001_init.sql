-- 0001_init.sql
-- Runtime DB schema for the 적벽대전 vertical slice (Hybrid), per
-- app/architecture/system.md. Migrations change structure only; curated
-- data imports (app/backend/importers/import_curated_export.py) change
-- content -- kept as separate, independently reversible operations
-- (data/APP_DATABASE_POLICY.md).
--
-- Exactly one dataset_versions row has is_active=1 at a time: that is the
-- version every read endpoint serves. A failed import never flips this
-- flag, so the previously-approved version keeps serving
-- (data/APP_DATABASE_POLICY.md's rollback rule).

CREATE TABLE IF NOT EXISTS dataset_versions (
    dataset_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_id           TEXT NOT NULL UNIQUE,
    pipeline_version     TEXT NOT NULL,
    run_id               TEXT NOT NULL,
    generated_at         TEXT NOT NULL,
    coding_validation_status TEXT NOT NULL CHECK (coding_validation_status IN ('llm_llm_validated_only', 'human_validated')),
    evidence_matrix_checksum TEXT NOT NULL,
    imported_at          TEXT NOT NULL,
    is_active            INTEGER NOT NULL DEFAULT 0 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS persons (
    dataset_version_id  INTEGER NOT NULL REFERENCES dataset_versions(dataset_version_id),
    person_id           TEXT NOT NULL,
    canonical_name_zh   TEXT NOT NULL,
    canonical_name_ko   TEXT,
    aliases_json        TEXT NOT NULL,
    alias_collision_note TEXT,
    notes               TEXT,
    PRIMARY KEY (dataset_version_id, person_id)
);

CREATE TABLE IF NOT EXISTS events (
    dataset_version_id  INTEGER NOT NULL REFERENCES dataset_versions(dataset_version_id),
    event_id            TEXT NOT NULL,
    event_name          TEXT NOT NULL,
    event_name_zh       TEXT,
    location            TEXT,
    outcome             TEXT,
    source_layer_coverage_json TEXT NOT NULL,
    PRIMARY KEY (dataset_version_id, event_id)
);

CREATE TABLE IF NOT EXISTS event_participants (
    dataset_version_id  INTEGER NOT NULL,
    event_id            TEXT NOT NULL,
    person_id           TEXT NOT NULL,
    role                TEXT NOT NULL,
    source_layer        TEXT NOT NULL,
    evidence_refs_json  TEXT NOT NULL,
    PRIMARY KEY (dataset_version_id, event_id, person_id, source_layer)
);

CREATE TABLE IF NOT EXISTS evidence (
    dataset_version_id  INTEGER NOT NULL,
    evidence_id         TEXT NOT NULL,
    event_ref           TEXT NOT NULL,
    source_layer        TEXT NOT NULL,
    work_title          TEXT NOT NULL,
    edition_ref         TEXT,
    volume_or_chapter   TEXT NOT NULL,
    locator_json        TEXT NOT NULL,
    permitted_excerpt   TEXT,
    coding_label        TEXT NOT NULL,
    person_refs_json    TEXT NOT NULL,
    confidence          REAL NOT NULL,
    review_status       TEXT NOT NULL,
    coding_validation_status TEXT NOT NULL,
    ambiguity_note      TEXT,
    PRIMARY KEY (dataset_version_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS relationships (
    dataset_version_id  INTEGER NOT NULL,
    edge_id             TEXT NOT NULL,
    from_person_id      TEXT NOT NULL,
    to_person_id        TEXT NOT NULL,
    relation_type       TEXT NOT NULL,
    direction           TEXT NOT NULL,
    start_value         TEXT,
    end_value           TEXT,
    event_ref           TEXT,
    source_layer        TEXT NOT NULL,
    confidence           REAL NOT NULL,
    evidence_refs_json  TEXT NOT NULL,
    notes               TEXT,
    PRIMARY KEY (dataset_version_id, edge_id)
);

CREATE TABLE IF NOT EXISTS metrics (
    dataset_version_id  INTEGER NOT NULL,
    event_ref           TEXT NOT NULL,
    metric_id           TEXT NOT NULL,
    name                TEXT NOT NULL,
    value               REAL,
    unit                TEXT NOT NULL,
    interval_low        REAL,
    interval_high       REAL,
    method              TEXT,
    classification      TEXT,
    evidence_ids_json   TEXT,
    PRIMARY KEY (dataset_version_id, event_ref, metric_id)
);

CREATE TABLE IF NOT EXISTS metrics_meta (
    dataset_version_id  INTEGER NOT NULL,
    event_ref           TEXT NOT NULL,
    analysis_id         TEXT NOT NULL,
    run_id              TEXT NOT NULL,
    population_n        INTEGER NOT NULL,
    population_description TEXT NOT NULL,
    limitations_json    TEXT NOT NULL,
    warnings_json       TEXT NOT NULL,
    PRIMARY KEY (dataset_version_id, event_ref)
);

CREATE INDEX IF NOT EXISTS idx_evidence_event ON evidence(dataset_version_id, event_ref);
CREATE INDEX IF NOT EXISTS idx_relationships_event ON relationships(dataset_version_id, event_ref);
CREATE INDEX IF NOT EXISTS idx_metrics_event ON metrics(dataset_version_id, event_ref);
