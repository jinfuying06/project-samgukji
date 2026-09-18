"""QA test fixtures. Reuses the real fixtures from tests/backend/conftest.py
(fresh_db, api_client, curated_export_dir) rather than re-implementing DB/app
setup -- imported, not copied, so the two suites can never silently drift."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tests.backend.conftest import curated_export_dir, fresh_db, api_client  # noqa: F401,E402
