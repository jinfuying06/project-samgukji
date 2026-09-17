#!/usr/bin/env python3
"""Fail when private data or runtime DB artifacts are tracked by Git."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = ("data/private/", "data/runtime/")
ALLOWED_PLACEHOLDER = ".gitkeep"
FORBIDDEN_SUFFIXES = (
    ".db", ".sqlite", ".sqlite3", ".duckdb", ".parquet", ".feather",
    ".arrow", ".npy", ".npz", ".pkl", ".joblib", ".faiss", ".embeddings",
)
REQUIRED_IGNORE_SNIPPETS = ("data/private/**", "data/runtime/**", "*.parquet", "*.duckdb")


def tracked_files() -> list[str] | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return [item.decode("utf-8", errors="surrogateescape") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    errors: list[str] = []
    ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for snippet in REQUIRED_IGNORE_SNIPPETS:
        if snippet not in ignore_text:
            errors.append(f"missing .gitignore rule: {snippet}")

    files = tracked_files()
    if files is not None:
        for relative in files:
            if relative.startswith(FORBIDDEN_PREFIXES) and not relative.endswith(ALLOWED_PLACEHOLDER):
                errors.append(f"private/runtime file is tracked: {relative}")
            if relative.lower().endswith(FORBIDDEN_SUFFIXES):
                errors.append(f"data artifact is tracked: {relative}")

    if errors:
        print("DATA BOUNDARY CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    mode = "tracked files checked" if files is not None else "ignore rules checked; initialize Git to inspect tracked files"
    print(f"DATA BOUNDARY CHECK PASSED ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

