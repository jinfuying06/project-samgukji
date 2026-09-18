#!/usr/bin/env python3
"""Validate the starter's required files and JSON templates."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Third-party/build directories are never project content and must not be scanned:
# node_modules ships JSONC (comments/trailing commas) tsconfig files that are not
# strict JSON, and none of these directories are ever committed (see .gitignore).
EXCLUDED_DIR_NAMES = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__"}


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)

REQUIRED = [
    "README.md",
    "PROJECT_BRIEF.md",
    "AGENTS.md",
    "CLAUDE.md",
    "first-prompt.md",
    "agents/_common.md",
    "agents/_three_kingdoms_domain.md",
    "agents/orchestrator.md",
    "agents/researcher.md",
    "agents/data_engineer.md",
    "agents/statistician.md",
    "agents/llm_analyst.md",
    "agents/product_manager.md",
    "agents/ux_designer.md",
    "agents/architect.md",
    "agents/backend.md",
    "agents/frontend.md",
    "agents/qa.md",
    "agents/evaluator.md",
    "orchestration/workflow.yaml",
    "orchestration/execution_policy.yaml",
    "orchestration/gates.yaml",
    "orchestration/scoring.yaml",
    "orchestration/routing.yaml",
    "research/source_policy.md",
    "research/coding_manual.md",
    "analysis/scoring_model.md",
    "product/gamification_spec.md",
    "product/concepts/concept_options.md",
    "product/concepts/concept_decision.yaml",
    "design/DESIGN.md",
    "data/DATA_ZONES.md",
    "data/PRIVATE_DATA_SETUP.md",
    "data/APP_DATABASE_POLICY.md",
    "handoffs/APPROVALS.md",
    "handoffs/PHASE_COMPLETION_TEMPLATE.md",
    "scripts/check_data_boundaries.py",
    "evals/TKAF_DOMAIN_RUBRIC.md",
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in sorted(ROOT.rglob("*.json")):
        if _is_excluded(path.relative_to(ROOT)):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

    scoring_path = ROOT / "orchestration/scoring.yaml"
    if scoring_path.is_file():
        text = scoring_path.read_text(encoding="utf-8")
        weights = [int(value) for value in re.findall(r"^\s+weight:\s+(\d+)\s*$", text, re.MULTILINE)]
        if sum(weights) != 100:
            errors.append(f"scoring weights sum to {sum(weights)}, expected 100")

    domain_name = "_three_kingdoms_domain.md"
    for relative in ("AGENTS.md", "CLAUDE.md", "agents/_common.md"):
        path = ROOT / relative
        if path.is_file() and domain_name not in path.read_text(encoding="utf-8"):
            errors.append(f"domain override not referenced by {relative}")

    if errors:
        print("STRUCTURE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"STRUCTURE VALIDATION PASSED ({len(REQUIRED)} required files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
