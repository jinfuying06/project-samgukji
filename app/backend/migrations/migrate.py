#!/usr/bin/env python3
"""Apply schema migrations to the runtime SQLite DB.

Usage: python app/backend/migrations/migrate.py [--db-url sqlite:///path]

Reads TKAF_APP_DATABASE_URL from .env if --db-url is not given. Only
applies structure (CREATE TABLE ...); never touches data (see
data/APP_DATABASE_POLICY.md's migration/import separation).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS_DIR = Path(__file__).resolve().parent


def db_path_from_url(url: str) -> Path:
    if not url.startswith("sqlite:///"):
        raise ValueError(f"Only sqlite:/// URLs are supported by this migration runner, got: {url}")
    rel = url[len("sqlite:///"):]
    return (REPO_ROOT / rel).resolve()


def resolve_db_url(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")
    import os

    url = os.environ.get("TKAF_APP_DATABASE_URL")
    if not url:
        raise SystemExit("TKAF_APP_DATABASE_URL not set (.env) and --db-url not given")
    return url


def apply_migrations(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            sql = sql_file.read_text(encoding="utf-8")
            conn.executescript(sql)
            print(f"Applied {sql_file.name}")
        conn.commit()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", default=None)
    args = parser.parse_args()
    url = resolve_db_url(args.db_url)
    db_path = db_path_from_url(url)
    apply_migrations(db_path)
    print(f"Migrations applied to {db_path}")


if __name__ == "__main__":
    main()
