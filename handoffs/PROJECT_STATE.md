# Project State

- Project status: `S3_APPROVED_WITH_CONDITIONS_MILESTONE_REACHED`
- Active stage: `S3 architecture_and_implementation` — **B3 approved_with_conditions** (D-025, `handoffs/APPROVALS.md`). The 적벽대전 vertical slice (Hybrid concept) has a working, tested implementation end to end: raw corpus → curated data → runtime DB → API → frontend, with an AI answer path that only ever cites real evidence and discloses its own validation status.
- Active tracks: none running
- Active task: none — the S0→S3 pipeline for this vertical slice is complete under the recorded approval scope
- Current owner: `human project owner` (next-step decision, not a gate)
- Next boundary: `S4 release_decision` — **not opened.** B3's approval is explicitly scoped to internal development/demo use, not public release; opening S4 (a real release decision) is a separate future choice the human hasn't made yet.
- Research Gate: `PASSED_FOR_B1`, human-reviewed but not from-scratch-double-coded (D-024; residual gap explicitly accepted at B3 via D-025)
- Design Gate: `PASSED_FOR_B2`
- Release Gate: `NOT_READY` (S4 not opened)
- Last updated: `2026-09-18`

## Completed

- Repository scaffold created.
- **S0 → B0 approved** (concept=Hybrid, sample=적벽대전, annotation extracted in-place, rights owner-confirmed). `handoffs/phase_reports/S0_COMPLETION.md`.
- **S1 → B1 approved** (D1 pipeline+schemas, R1 coding manual+22 evidence spans, A1 reproducible result, P1 product-planning set; Q-010 addressed via LLM-LLM κ=0.90). `handoffs/phase_reports/S1_COMPLETION.md`.
- **S2 → B2 approved** (U1 design activated + real-data-grounded component spec, L1 schema-validated LLM contract; D-018/D-019 reconciliations). `handoffs/phase_reports/S2_COMPLETION.md`.
- **S3 → B3 approved_with_conditions**:
  - E0: architecture, 7-endpoint API contract, threat model, 2 ADRs.
  - D-016 expansion: cast 5→10 persons, evidence 22→30 spans (D-021); a real hardcoded-cast bug found and fixed in the process (D-020).
  - E1: backend (FastAPI+SQLite, curated-export transform, atomic importer, all 7 endpoints, LLM validator with citation cross-check) and frontend (Vite+React+TS, all 6 screens, design-token theme) — both independently re-verified by the orchestrator, not just trusted (46 backend + 33 frontend tests passing).
  - Three real cross-cutting bugs found (independently, by two implementation tracks) and fixed (D-022): `validate_structure.py` node_modules crash, a stale post-B0 test, a missing D-017 schema field.
  - QA: 0 critical/blocker defects, 7 new golden-case tests (entity resolution, source-layer non-leakage, citation reproducibility, D-017 exposure, missing-evidence handling).
  - Two independent Evaluator rounds, both `fail` on the same hard blocker (`coding_calibration_missing`) despite genuine score improvement (81.79→84.61) after the human's real review (D-024).
  - **Human owner explicitly overrode the fail and approved B3** (D-025, Q-011 option (b)), with the override's scope and residual-risk disclosure recorded precisely in `handoffs/APPROVALS.md` — not a blanket "approved."
- `handoffs/OPEN_QUESTIONS.md` and `handoffs/DECISIONS.md` updated through D-025; Q-011 resolved.

## In progress

- Nothing active. The vertical-slice pipeline (S0→S3) is complete under its recorded, conditional approval.

## Blocked

- Nothing is blocked. The project is at a natural pause point — a real decision point for the human, not a technical blocker.

## Committed follow-ups (carry forward into any future work on this project)

- **The coding-validation gap is real, partial, and now two-tiered.** `research/evidence_matrix.csv` has 48 rows: the original 30 are LLM-LLM double-coded (κ=0.90) + human-reviewed (D-024, `coding_validation_status: human_validated`); the **18 rows added in the "더많은원문코딩" expansion (D-028) are LLM-coded only, not yet human-reviewed at all** (`coding_validation_status: llm_llm_validated_only`). The system correctly tracks this per-row and at the dataset level (verified directly against the runtime DB), and the UI/API never claims more validation than actually happened. B3's approval (D-025) covers the original 30-row gap for internal/demo use only — it does **not** automatically cover the new 18 rows, which have an even thinner validation history (no human review at all yet, not even the audit-style pass D-024 gave the original 30). **Before any future public-release decision, both tiers must be re-examined.**
- Q-005 (learning-game difficulty level) and Q-009 (primary user's data-literacy default) remain open, non-blocking for internal work but should be resolved before any UI aimed at real users.
- The 5 D-016-added persons (黃蓋/關羽/魯肅/趙雲/郭嘉) still have shallower coverage than the original 5, though less shallow after D-028's expansion — don't present all 10 as equally well-evidenced.
- `design/accessibility_checklist.md` is 100% `NOT_TESTED` beyond automated `jest-axe` scans (nothing has been manually tested or deployed) — the lowest-scoring category (65) in both evaluations. Real testing is needed before any real deployment.
- Schema-drift items still open: `result.json`'s `network_edge_count.*` isn't in `api_contract.yaml`'s metrics enum (network data now lives in a separate `edges`/`network_summary` top-level field instead, per D-027 — not merged into `metrics[]`); the curated export's `paragraph_index` is a synthetic ordinal, not the ingestion pipeline's real value; `data/pipelines/build_curated_export.py` independently recomputes its own relationship edges rather than sharing a single source of truth with `analysis/pipelines/compute_chibi_result.py`'s `edges` output (`analysis/network_analysis_plan.md`) — worth unifying next time either pipeline is touched.
- 關羽 was checked twice now (D-026, D-028) for a qualifying cross-layer divergence pair and genuinely has none in the currently-coded material — stop re-checking him without new evidence being coded first.
- `OpenAILLMClient` is an untested stub — no real external LLM has ever been called; only a deterministic mock is exercised in tests.
- No SAST/dependency-vulnerability scan has been run.
- Tooling note (not urgent): `evals/run_eval.py`'s `double_coded_calibration_set` check is a generic, gate-agnostic blocker even though `orchestration/gates.yaml` only lists it as a `recommended_target` under B1, not a named hard blocker under `implementation_gate` (B3). Worth fixing in the eval tooling itself someday, on its own merits.
- Remaining uncoded material (not urgent, known): `ROMANCE` 回52 (partial), 55, 58–61; most of `HISTORY_BASE` juan 10/31/48/56 (reviewed twice now, judged not cast-relevant); juan 55's remaining non-cast rows.

## Next steps (human decision, not a gate question)

- **D-030/D-031/D-032 (2026-09-18): "What-if weight-lab" shipped and live-verified.** Q-005 (elementary-level explanation) and Q-009 (dual persona: data-analyst vs casual fan) resolved. Q-012 resolved as option (a) only (real weight-sensitivity, no fictional counterfactual layer) and implemented: `ContributionBreakdown.tsx` now lets a user move independent 정사/정사주석/연의 weight sliders for one person and see, per `coding_label`, how emphasis shifts — never collapsed into one number, never ranked, missing-layer coverage shown as an explicit warning not a fabricated zero. Verified live against the real backend (not mocks) with a headless browser: 曹操 연의=100% isolates exactly the 5 documented labels; 趙雲 정사=100% correctly shows the zero-coverage banner. `npm test` 46/46, backend `pytest` unaffected at 46/46, `tsc`/`build` clean.
- D-029: human owner explicitly declined to be a routine manual-review bottleneck going forward for new evidence rows — the `coding_validation_status` per-row disclosure remains the safeguard, not a review requirement, for this internal-scope project.

Remaining reasonable next directions, none pre-selected:
1. Treat this as done for now.
2. Continue depth-first within this slice: rewrite the rest of the learning-game copy (Quest/Quiz/EventOverview) to the same elementary level as the weight-lab intro; real accessibility testing; wire up a real LLM key.
3. Expand breadth: more events (e.g. 관도대전) or more of the already-crawled-but-unused raw corpus.
4. Move toward an actual S4 release decision (would require re-examining the coding-validation gap and real deployment first).
