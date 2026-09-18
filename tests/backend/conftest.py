import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def curated_export_dir(tmp_path_factory):
    """Runs the real Curated Export Transform against the real repo data
    (research/evidence_matrix.csv, analysis/outputs/result.json) -- this is
    an integration fixture, not a mock, since that data is genuinely
    available in this environment and is what the whole pipeline is for."""
    from data.pipelines import build_curated_export

    export_dir = build_curated_export.main()
    return export_dir


@pytest.fixture()
def fresh_db(tmp_path, curated_export_dir):
    """A temp SQLite DB, migrated and imported fresh for each test --
    never touches data/runtime/tkaf.local.sqlite3."""
    from app.backend.migrations import migrate as migrate_mod
    from app.backend.importers import import_curated_export as importer_mod

    db_path = tmp_path / "test_tkaf.sqlite3"
    migrate_mod.apply_migrations(db_path)
    result = importer_mod.import_export(curated_export_dir, db_path)
    assert result == "imported"
    return db_path


@pytest.fixture()
def api_client(fresh_db, monkeypatch):
    from app.backend.api.db import DB
    from app.backend.api import main as main_mod
    from fastapi.testclient import TestClient

    monkeypatch.setenv("TKAF_LLM_PROVIDER", "mock")
    main_mod.app.state.db = DB(db_path=fresh_db)
    return TestClient(main_mod.app)
