import json
import shutil

import pytest

from app.backend.importers.import_curated_export import (
    ImportRejected,
    import_export,
    validate_manifest,
)
from app.backend.migrations.migrate import apply_migrations


def test_import_is_idempotent(fresh_db, curated_export_dir):
    result = import_export(curated_export_dir, fresh_db)
    assert result == "already_imported"


def test_reject_bad_checksum(tmp_path, curated_export_dir):
    broken = tmp_path / "broken_export"
    shutil.copytree(curated_export_dir, broken)
    with open(broken / "evidence.json", "a", encoding="utf-8") as f:
        f.write("\n")  # mutate content after manifest was written -> checksum mismatch

    with pytest.raises(ImportRejected, match="Checksum mismatch"):
        validate_manifest(broken)


def test_reject_missing_approval_ref(tmp_path, curated_export_dir):
    broken = tmp_path / "no_approval_export"
    shutil.copytree(curated_export_dir, broken)
    with open(broken / "manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["approval_ref"] = ""
    with open(broken / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    with pytest.raises(ImportRejected):
        validate_manifest(broken)


def test_reject_bad_rights_status(tmp_path, curated_export_dir):
    broken = tmp_path / "bad_rights_export"
    shutil.copytree(curated_export_dir, broken)
    with open(broken / "manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["rights_review_status"] = "not_reviewed"
    with open(broken / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    with pytest.raises(ImportRejected):
        validate_manifest(broken)


def test_failed_import_leaves_previous_version_active(tmp_path, curated_export_dir):
    """Simulate a corrupt evidence.json (schema-invalid content, but checksum
    still matches manifest -- e.g. hand-edited by mistake) causing a mid-import
    exception. The already-imported version must remain active afterward."""
    db_path = tmp_path / "rollback_test.sqlite3"
    apply_migrations(db_path)

    good = curated_export_dir
    assert import_export(good, db_path) == "imported"

    # Build a second "export" that will pass manifest/checksum validation but
    # blow up during the INSERT step (missing a required key the importer expects).
    import hashlib

    corrupt_dir = tmp_path / "corrupt_export"
    shutil.copytree(good, corrupt_dir)
    with open(corrupt_dir / "manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["export_id"] = manifest["export_id"] + "-corrupt"

    with open(corrupt_dir / "persons.json", encoding="utf-8") as f:
        persons = json.load(f)
    del persons[0]["canonical_name_zh"]  # importer's SQL will KeyError on this
    with open(corrupt_dir / "persons.json", "w", encoding="utf-8") as f:
        json.dump(persons, f, ensure_ascii=False)

    # Recompute checksum for the file we just mutated so it still passes the
    # checksum check and reaches the actual insert logic.
    def sha(path):
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    for entry in manifest["files"]:
        entry["sha256"] = sha(corrupt_dir / entry["relative_path"])
    with open(corrupt_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    with pytest.raises(KeyError):
        import_export(corrupt_dir, db_path)

    import sqlite3

    conn = sqlite3.connect(str(db_path))
    active = conn.execute("SELECT export_id FROM dataset_versions WHERE is_active = 1").fetchall()
    assert len(active) == 1
    assert active[0][0] == manifest["export_id"].replace("-corrupt", "")  # original still active
    # the corrupt version must not have been partially committed
    count = conn.execute(
        "SELECT COUNT(*) FROM dataset_versions WHERE export_id = ?", (manifest["export_id"],)
    ).fetchone()[0]
    assert count == 0
