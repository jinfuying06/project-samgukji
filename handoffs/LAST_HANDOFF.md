# Handoff

- Task ID: `TASK-S1-GUANDU-DATA-ANALYSIS`
- Stage/track: S1-equivalent, second event (breadth expansion, not a new S0→S1 lifecycle)
- Boundary: `none` — data/research-stage work only, no gate opened or requested
- From role: `orchestrator` (data-engineer + researcher + analyst roles performed directly in one session, per the human owner's direct combined request, same pattern as the prior depth-first session)
- Status: `DONE`
- Target commit/run ID: uncommitted working tree at handoff time; A1-equivalent run `run-20260919T014246Z`
- Timestamp: 2026-09-19

## Summary

Human owner said "그러면 대전별로 데이터분석 자료 만들기부터 다시 시작해" (restart from building data-analysis materials, organized per battle) — choosing option 3 ("expand breadth") from `handoffs/PROJECT_STATE.md`'s prior next-steps menu. 관도대전 (Battle of Guandu) was selected as the second event: it's the only other battle named anywhere in the project's founding documents alongside 적벽대전 (`docs/VERTICAL_SLICE_PLAN.md`, `docs/DOMAIN_BLUEPRINT.md`, `data/ingestion_report.md`).

A full S1-equivalent pass was run, mirroring 적벽대전's own D1→R1→A1 method exactly:
1. **Scope**: a keyword scan (官渡/烏巢/袁紹) across the *entire* raw corpus (all 65 history juan, all 120 romance hui) found the real distribution before committing to a juan/hui range — history hits spread across 17 juan (matching `data/ingestion_report.md`'s original note almost exactly), romance concentrated in a tight 回22–32 arc.
2. **D1-equivalent**: `data/pipelines/build_guandu_sample.py`, same non-destructive `〈〉`-bracket extraction as `build_chibi_sample.py`. Scoped to HISTORY_BASE juan {01,06,9,10,14,17}, ROMANCE 回{22,25,26,30,31,32}. All 6 sampled juan's brackets balanced.
3. **R1-equivalent**: `research/coding_manual_guandu.md` + `research/evidence_matrix_guandu.csv`, 25 real coded evidence spans across 9 persons (3 sharing `person_id`s with the 적벽대전 cast on purpose — 曹操/郭嘉/關羽). Reused 7 existing coding labels; added exactly 3 new ones (`rival_character_assessment`, `strategic_defection`, `punished_for_correct_dissent`) where 관도대전's actual narrative mechanism (repeated defections, an advisor executed for having been proven right) had no real analogue in 적벽대전's label set. `checksum_sha256_12` computed programmatically for every row, not hand-typed.
4. **A1-equivalent**: `analysis/pipelines/compute_guandu_result.py` → `analysis/outputs/guandu_result.json`, schema-validated, 4 pre-registered cross-layer divergence cases.

Full detail: `handoffs/phase_reports/S1_GUANDU_COMPLETION.md`, `handoffs/DECISIONS.md#D-036`.

**Explicitly not done:** no second/double-coding pass (this event's evidence is one full validation tier behind 적벽대전's); most of the extracted 205-paragraph candidate pool remains uncoded (25 coded); no app/backend/frontend change — `event.chibi` is still the only event the running app serves.

## Changed paths

- `data/pipelines/build_guandu_sample.py` (new)
- `research/coding_manual_guandu.md`, `research/evidence_matrix_guandu.csv` (new)
- `analysis/pipelines/compute_guandu_result.py` (new)
- `analysis/outputs/guandu_result.json`, `analysis/outputs/guandu_run_manifest.json` (new, committed — `.gitignore` given 2 new narrow exceptions matching D-015's precedent, content-safety-checked: aggregate counts + evidence_id references only)
- `handoffs/{DECISIONS,PROJECT_STATE,CURRENT_TASK}.md`, `handoffs/phase_reports/S1_GUANDU_COMPLETION.md` (new)

## Validation run

| Command/check | Result | Evidence path |
| --- | --- | --- |
| `python data/pipelines/build_guandu_sample.py` | PASS — 866 candidates, 0 duplicate hashes, 6/6 juan brackets balanced | terminal, `guandu_run_manifest.json` (private) |
| `python analysis/pipelines/compute_guandu_result.py` | PASS — 45 metrics, 16 edges, deterministic | terminal |
| `guandu_result.json` vs `result.schema.json` | PASS (`jsonschema` validation) | terminal |
| `python scripts/validate_structure.py` | PASS (38 files) | terminal |
| `python scripts/check_data_boundaries.py` | PASS | terminal |
| `python -m pytest tests/ -q` | PASS (59/59, unaffected — this track touched no backend code) | terminal |
| `git status --short` | PASS — no private/raw/runtime paths tracked | terminal |

## Validation not run

- No second independent coder (LLM-LLM or human) has coded any of these 25 rows — see "Explicitly not done" above and the coding manual's own "Inter-coder reliability" section.
- The 4 divergence-case classifications are this single coder's own qualitative judgment, not cross-checked.
- No rights/legal re-review specific to this event (relies on the same owner-confirmed basis as 적벽대전, D-012, since it's the same two source works — not re-asked explicitly this time).

## Assumptions and risks

- Person-id reuse (`person.cao_cao`/`person.guo_jia`/`person.guan_yu` shared across both events) assumes the human owner wants the same real person tracked as one identity across battles, not per-event-forked identities. This seemed the obviously correct call (they're the same historical person) but was not explicitly asked.
- The 3 new coding labels are a judgment call about what's "genuinely new" vs. reusable — a different coder might have forced these into existing labels instead, or split them differently. Flagged, not hidden, in the coding manual's own header.

## Blockers / open decisions

- None technical. Next step is the human owner's choice among `handoffs/PROJECT_STATE.md`'s "Next steps" options (now including 관도대전-specific ones: code more of its pool, double-code it, or start deciding multi-event app architecture).

## Recommended next role

- Role: `human project owner`, then whichever role the chosen direction implies
- Objective: pick a direction from `handoffs/PROJECT_STATE.md`'s "Next steps"
- Required inputs: `handoffs/phase_reports/S1_GUANDU_COMPLETION.md`, `research/coding_manual_guandu.md`, `analysis/outputs/guandu_result.json`

## Stage-transition status

- Boundary reached: `no` — not a stage boundary, data/research-stage follow-up work
- Completion report: `handoffs/phase_reports/S1_GUANDU_COMPLETION.md`
- Human approval required: `no` (matches D-029's stance — same as the prior depth-first pass)
- Approval recorded: N/A
