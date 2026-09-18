# Project State

- Project status: `S3_APPROVED_WITH_CONDITIONS_MILESTONE_REACHED`
- Active stage: `S3 architecture_and_implementation` — **B3 approved_with_conditions** (D-025, `handoffs/APPROVALS.md`). The 적벽대전 vertical slice (Hybrid concept) has a working, tested implementation end to end: raw corpus → curated data → runtime DB → API → frontend, with an AI answer path that only ever cites real evidence and discloses its own validation status.
- Active tracks: none running
- Active task: none — the S0→S3 pipeline for this vertical slice is complete under the recorded approval scope; the depth-first follow-up pass below (D-033–D-035) is also complete
- Current owner: `human project owner` (next-step decision, not a gate)
- Next boundary: `S4 release_decision` — **not opened.** B3's approval is explicitly scoped to internal development/demo use, not public release; opening S4 (a real release decision) is a separate future choice the human hasn't made yet.
- Research Gate: `PASSED_FOR_B1`, human-reviewed but not from-scratch-double-coded (D-024; residual gap explicitly accepted at B3 via D-025)
- Design Gate: `PASSED_FOR_B2`
- Release Gate: `NOT_READY` (S4 not opened)
- Last updated: `2026-09-19`

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
- **Depth-first follow-up pass (2026-09-19, D-033–D-035), human owner's explicit choice of option 2:**
  - Learning-game copy for `Quest`/`Quiz`/`EventOverview` rewritten to the same elementary ("초등학생도 이해") level as the weight-lab intro (D-030).
  - `OpenAILLMClient` actually implemented (was a `NotImplementedError` stub) — real OpenAI Chat Completions call, prompt built from `analysis/llm_contract.md` + the real `interpretation.schema.json`, caller (not the model) fills in `interpretation_id`/`generated_at`/`model`/`input_refs`. Provider failures degrade to an honest `insufficient_evidence` response, never a raw 500 (`LLMProviderError`, caught in `main.py`'s existing retry loop). 13 new tests, all mocking `requests.post` — no paid API ever called by the suite. `.env`/`.env.example` pre-configured (`TKAF_LLM_PROVIDER=openai`, `TKAF_LLM_MODEL=gpt-4o-mini`) so filling in `OPENAI_API_KEY` is the only remaining step; see `app/backend/README.md`.
  - Real-browser accessibility testing added: `tests/e2e/accessibility.spec.ts` (Playwright + `@axe-core/playwright`, `npm run test:e2e`), going beyond the jsdom-based `jest-axe` component tests. Found and fixed **3 real bugs** (D-033/D-034/D-035): `QuestCard` couldn't actually be completed by a real user (no button for the required HISTORY_BASE evidence); 6 color tokens failed WCAG AA contrast against their real rendered badge backgrounds (fixed in `tokens.css`) plus 5 of 6 screens missing/skipping `<h1>`; `QuestCard`'s "완료" button did nothing when clicked (a separate, spec-undocumented button was silently doing the real work instead). All 8 e2e tests pass after fixes; `design/accessibility_checklist.md` updated honestly (PASS/PARTIAL per what was actually covered, real assistive-technology testing still explicitly `NOT_TESTED` — an agent cannot do that).
  - Full regression: backend `pytest` 59/59, frontend `vitest` 49/49, `tsc -b` clean, `validate_structure.py`/`check_data_boundaries.py` PASS.

## In progress

- Nothing active. The vertical-slice pipeline (S0→S3) is complete under its recorded, conditional approval.

## Blocked

- Nothing is blocked. The project is at a natural pause point — a real decision point for the human, not a technical blocker.

## Committed follow-ups (carry forward into any future work on this project)

- **The coding-validation gap is real, partial, and now two-tiered.** `research/evidence_matrix.csv` has 48 rows: the original 30 are LLM-LLM double-coded (κ=0.90) + human-reviewed (D-024, `coding_validation_status: human_validated`); the **18 rows added in the "더많은원문코딩" expansion (D-028) are LLM-coded only, not yet human-reviewed at all** (`coding_validation_status: llm_llm_validated_only`). The system correctly tracks this per-row and at the dataset level (verified directly against the runtime DB), and the UI/API never claims more validation than actually happened. B3's approval (D-025) covers the original 30-row gap for internal/demo use only — it does **not** automatically cover the new 18 rows, which have an even thinner validation history (no human review at all yet, not even the audit-style pass D-024 gave the original 30). **Before any future public-release decision, both tiers must be re-examined.**
- Q-005 (learning-game difficulty level) and Q-009 (primary user's data-literacy default) remain open, non-blocking for internal work but should be resolved before any UI aimed at real users.
- The 5 D-016-added persons (黃蓋/關羽/魯肅/趙雲/郭嘉) still have shallower coverage than the original 5, though less shallow after D-028's expansion — don't present all 10 as equally well-evidenced.
- `design/accessibility_checklist.md` (2026-09-19 update): real-browser automated testing now exists and most rows are `PASS`/`PARTIAL` on that basis (see the checklist file for exactly what each covers) — but **real assistive-technology testing (an actual human with a screen reader) has still never been done**, and no automated result should be read as covering that. Needed before any real deployment.
- Schema-drift items still open: `result.json`'s `network_edge_count.*` isn't in `api_contract.yaml`'s metrics enum (network data now lives in a separate `edges`/`network_summary` top-level field instead, per D-027 — not merged into `metrics[]`); the curated export's `paragraph_index` is a synthetic ordinal, not the ingestion pipeline's real value; `data/pipelines/build_curated_export.py` independently recomputes its own relationship edges rather than sharing a single source of truth with `analysis/pipelines/compute_chibi_result.py`'s `edges` output (`analysis/network_analysis_plan.md`) — worth unifying next time either pipeline is touched.
- 關羽 was checked twice now (D-026, D-028) for a qualifying cross-layer divergence pair and genuinely has none in the currently-coded material — stop re-checking him without new evidence being coded first.
- No SAST/dependency-vulnerability scan has been run.
- Tooling note (not urgent): `evals/run_eval.py`'s `double_coded_calibration_set` check is a generic, gate-agnostic blocker even though `orchestration/gates.yaml` only lists it as a `recommended_target` under B1, not a named hard blocker under `implementation_gate` (B3). Worth fixing in the eval tooling itself someday, on its own merits.
- Remaining uncoded material (not urgent, known): `ROMANCE` 回52 (partial), 55, 58–61; most of `HISTORY_BASE` juan 10/31/48/56 (reviewed twice now, judged not cast-relevant); juan 55's remaining non-cast rows.

## Next steps (human decision, not a gate question)

- **D-030/D-031/D-032 (2026-09-18): "What-if weight-lab" shipped and live-verified.** Q-005 (elementary-level explanation) and Q-009 (dual persona: data-analyst vs casual fan) resolved. Q-012 resolved as option (a) only (real weight-sensitivity, no fictional counterfactual layer) and implemented: `ContributionBreakdown.tsx` now lets a user move independent 정사/정사주석/연의 weight sliders for one person and see, per `coding_label`, how emphasis shifts — never collapsed into one number, never ranked, missing-layer coverage shown as an explicit warning not a fabricated zero. Verified live against the real backend (not mocks) with a headless browser: 曹操 연의=100% isolates exactly the 5 documented labels; 趙雲 정사=100% correctly shows the zero-coverage banner. `npm test` 46/46, backend `pytest` unaffected at 46/46, `tsc`/`build` clean.
- D-029: human owner explicitly declined to be a routine manual-review bottleneck going forward for new evidence rows — the `coding_validation_status` per-row disclosure remains the safeguard, not a review requirement, for this internal-scope project.
- **D-033–D-035 (2026-09-19): human owner chose option 2 (depth-first) and it's now done** — elementary-level copy for the remaining learning-game screens, real-browser accessibility testing (which found and fixed 3 real bugs, see `## Completed`), and `OpenAILLMClient` fully wired (only `OPENAI_API_KEY` remains to be filled in by whoever has one).

Remaining reasonable next directions, none pre-selected:
1. Treat this as done for now.
2. Continue depth-first further: real assistive-technology (screen reader) testing by an actual human — the one accessibility gap no agent can close; resolve the remaining `PARTIAL` rows in `design/accessibility_checklist.md`; actually paste a real `OPENAI_API_KEY` and try the live LLM path end to end.
3. Expand breadth: more events (e.g. 관도대전) or more of the already-crawled-but-unused raw corpus.
4. Move toward an actual S4 release decision (would require re-examining the coding-validation gap and real deployment first).
