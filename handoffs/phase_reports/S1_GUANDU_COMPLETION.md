# Stage Completion Report

- Stage: `S1-equivalent, second event` (breadth expansion — not a new S0→S1 lifecycle, no new B0/B1 gate opened)
- Boundary awaiting approval: `none` — data/research-stage work only, no product/backend/frontend scope touched. The human owner's own request ("데이터분석 자료 만들기부터") did not ask for a new stage gate.
- Status: `COMPLETE` (for the scope actually attempted — see §4 "Explicitly not covered")
- Target commit/run ID: uncommitted working tree; A1-equivalent run `run-20260919T014246Z`
- Completed at: 2026-09-19

## 1. Planned scope

Human owner's direct request: "그러면 대전별로 데이터분석 자료 만들기부터 다시 시작해" (restart from building data-analysis materials, organized per battle), after choosing option 3 ("expand breadth") from `handoffs/PROJECT_STATE.md`'s prior next-steps menu. 관도대전 (Battle of Guandu) selected as the second event — the only other battle named anywhere in the project's founding documents alongside 적벽대전 (see `handoffs/DECISIONS.md#D-036` for the full selection rationale).

Scope: D1-equivalent extraction + R1-equivalent coding + A1-equivalent aggregation for 관도대전, following the exact same method already validated for 적벽대전. No S2 (design)/S3 (architecture/implementation) work — the human owner's phrase scoped this explicitly to data-analysis materials.

## 2. Completed outputs

| Track | Output | Status | Evidence path |
| --- | --- | --- | --- |
| D1 | Keyword scan (官渡/烏巢/袁紹) across the **entire** raw corpus (65 `history_base_zh` juan, 120 `romance_zh` hui) to identify scope | done | scan method recorded in `handoffs/DECISIONS.md#D-036`; not separately committed as a script (one-off reconnaissance, not a reusable pipeline) |
| D1 | Reproducible extraction pipeline; 866 candidate paragraphs (337 HISTORY_BASE / 364 HISTORY_ANNOTATION / 165 ROMANCE), 205 keyword-matched | done | `data/pipelines/build_guandu_sample.py` |
| D1 | Annotation-bracket check: all 6 sampled juan balanced (0 anomalies, better than 적벽대전's 1-juan anomaly) | done | `guandu_run_manifest.json` (private, `${TKAF_PRIVATE_DATA_ROOT}/analysis/tables/`) |
| D1 | Person registry: 9 canonical persons (3 shared `person_id`s with the 적벽대전 cast, 6 new), text-attested aliases only | done | `data/pipelines/build_guandu_sample.py`'s `CANONICAL_PERSONS`; full registry (private) at `${TKAF_PRIVATE_DATA_ROOT}/analysis/tables/guandu_person_registry.json` |
| R1 | Coding manual: 7 labels reused from 적벽대전's manual unchanged, 3 new labels with include/exclude examples, explicit "not yet double-coded" notice | done | `research/coding_manual_guandu.md` |
| R1 | Evidence matrix: 25 real coded spans (15 HISTORY_BASE / 4 HISTORY_ANNOTATION / 6 ROMANCE), short excerpts, real locators, checksums verified by script (not hand-computed) | done | `research/evidence_matrix_guandu.csv` |
| A1 | Reproducible result computation, including 4 pre-registered cross-layer divergence cases | done | `analysis/pipelines/compute_guandu_result.py`, `analysis/outputs/guandu_result.json`, `analysis/outputs/guandu_run_manifest.json` |

## 3. Validation results

| Check | Result | Command/method | Evidence |
| --- | --- | --- | --- |
| Repository structure | PASS (38 required files) | `python scripts/validate_structure.py` | terminal |
| Data boundary check | PASS | `python scripts/check_data_boundaries.py` | terminal |
| Backend/frontend test suites unaffected | PASS | `python -m pytest tests/ -q` (59/59) | terminal — this track touched no backend/frontend code |
| No private/runtime files tracked | PASS | `git status --short` | only `research/`, `data/pipelines/`, `analysis/pipelines/`, `analysis/outputs/guandu_*.json`, `.gitignore` (2 new exceptions, content-safety-checked per D-015's precedent) touched; no `tkaf-private-data/` path |
| Raw corpus untouched | PASS | pipeline only opens raw files read-only | `build_guandu_sample.py` |
| Result reproducibility | PASS | deterministic re-run against unchanged `evidence_matrix_guandu.csv` | `guandu_run_manifest.json` (input/output SHA-256 recorded) |
| `guandu_result.json` schema conformance | PASS | validated with `jsonschema` against `analysis/schemas/result.schema.json` (same schema as 적벽대전's) | terminal |
| Checksum accuracy | PASS by construction | `checksum_sha256_12` computed programmatically (`sha256(excerpt_zh)[:12]`) for every row, not hand-typed | `gen_guandu_evidence.py` (scratch script, not committed — see below) |

## 4. Explicitly not covered (disclosed, not silently skipped)

- **No second independent coding pass.** This event's `coding_validation_status` is a full tier behind 적벽대전's current state — no LLM-LLM double-coding check (적벽대전's D-017), let alone the human review 적벽대전 later received (D-024). Every `coding_label` here is a single, uncorroborated coder's judgment.
- **Most of the extracted candidate pool remains uncoded.** 205 keyword-matched paragraphs found, 25 coded (~12%). Juan 09 (mostly 夏侯淵's later, unrelated campaigns) and most of juan 06's non-沮授/田豐 material were read but judged not central enough to the battle itself to code, not skipped for lack of time.
- **No product/backend/frontend work.** The app (`app/backend`, `app/frontend`) still only serves `event.chibi`; whether/how to support multiple events is a separate architecture decision nobody has made yet. This report's scope is data/research only, per the human owner's own phrasing.
- **No rights/legal review specific to this event** — same owner-confirmed public-domain basis as 적벽대전 (`handoffs/DECISIONS.md#D-012`) applies, since it is the same two source works, but this was not re-asked explicitly for this event.

## 5. Recommended next role

- Role: `human project owner`
- Objective: decide what happens next with 관도대전 — code more of the existing candidate pool, run a double-coding pass to close the validation gap, move toward supporting multiple events in the app, or pick a third battle. None pre-selected here, matching this project's own convention of not pre-deciding the human's next-step choice.
- Required inputs: this report, `research/coding_manual_guandu.md`, `analysis/outputs/guandu_result.json`.
