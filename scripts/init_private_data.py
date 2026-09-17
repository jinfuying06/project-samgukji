#!/usr/bin/env python3
"""Create a non-destructive private data directory layout."""

from __future__ import annotations

import sys
from pathlib import Path


SUBDIRS = (
    "raw/inbox/history_base_zh",
    "raw/inbox/history_annotations_zh",
    "raw/inbox/romance_zh",
    "raw/inbox/unclassified",
    "analysis/normalized",
    "analysis/tables",
    "analysis/notebooks_output",
    "analysis/results",
    "curated/app_export",
    "manifests",
)


def validate_target(raw: str) -> Path:
    target = Path(raw).expanduser().resolve()
    forbidden = {Path("/").resolve(), Path.home().resolve(), Path.cwd().resolve()}
    if target in forbidden:
        raise ValueError("choose a dedicated private-data directory, not /, home, or the repository root")
    return target


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python scripts/init_private_data.py PRIVATE_DATA_ROOT", file=sys.stderr)
        return 2
    try:
        target = validate_target(argv[1])
        for relative in SUBDIRS:
            (target / relative).mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        print(f"private data initialization failed: {exc}", file=sys.stderr)
        return 1
    print(target)
    for relative in SUBDIRS:
        print(f"- {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

