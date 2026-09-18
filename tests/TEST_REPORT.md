# Test Report — S3 (적벽대전 Vertical Slice, Hybrid)

Status: `S3 QA — 2026-09-18, updated post-D-024`. Per `tests/TEST_PLAN.md`. All commands below were re-run directly by QA, not taken on faith from E1's own reports — where a claim rests only on E1's report and was not independently re-executed, it is marked as such. **Post-QA update:** after the human owner's D-024 review (`handoffs/DECISIONS.md#D-024`), `coding_validation_status` flipped to `human_validated` system-wide; the frontend gained one regression test for the old value's rendering path (32→33), and all suites were re-verified green. This file's counts reflect that update; the qualitative findings below (entity resolution, source-layer non-leakage, etc.) are unaffected by D-024 and were not re-run a third time.

## 1. Test suites executed (QA-run, not just trusted)

| Command | Result | Notes |
| --- | --- | --- |
| `pytest tests/` | **46 passed** | 30 backend (Curated Export Transform, importer incl. rollback-on-corruption, LLM validator, all 7 API endpoints) + 9 pre-existing policy/evaluator tests + 7 new QA golden-case tests (`tests/qa/`) |
| `cd app/frontend && npm test` (vitest) | **33 passed**, 7 files (was 32 before D-024 added a regression test for the old `llm_llm_validated_only` rendering path) | Component tests (SourceModeControl, EvidenceCard, ScoreCard, ContributionBreakdown via ScoreCard states, QuestCard, AIAnswerPanel), 1 screen integration test, 1 contract-drift test file (7 sub-tests) |
| `cd app/frontend && npx tsc --noEmit` | Clean | Re-run, confirmed clean |
| `cd app/frontend && npm run build` | Succeeds | 158KB JS / 8KB CSS output confirmed present in `app/frontend/dist/` |
| `python scripts/validate_structure.py` | **PASS** (38 required files) | Was failing before this pass due to a `node_modules` JSON-scan bug (fixed by orchestrator, D-022); re-confirmed clean post-fix |
| `python scripts/check_data_boundaries.py` | **PASS** | No private/runtime paths tracked |

## 2. QA-authored golden-case checks (new, `tests/qa/test_qa_golden_cases.py`, 7 tests, all passing against the real curated export + a freshly imported SQLite DB — not synthetic fixtures)

| Check | Result | What it proves |
| --- | --- | --- |
| Entity-resolution alias golden set | PASS | 15 known courtesy-names/nicknames (孟德, 玄德, 孔明, 公瑾, 子龍, 常山趙子龍, 奉孝, 雲長, 子敬, 公覆, etc.) each resolve to the correct `person_id`; **0 alias collisions** across all 10 persons |
| `/v1/ask` 정사 mode never cites ROMANCE evidence | PASS | Direct check against `source_layer` of every cited `evidence_id` |
| `/v1/ask` 연의 mode never cites HISTORY_BASE/HISTORY_ANNOTATION evidence | PASS | Reverse-direction check |
| Evidence citation locator reproducibility | PASS | Same `evidence_id` fetched twice returns byte-identical locator/excerpt/label |
| D-017 disclosure (`coding_validation_status`) present on every evidence row and the dataset version | PASS | Checked at both the top-level `/v1/version` and per-row on every evidence record returned by `/v1/people/{id}/evidence` |
| Missing evidence returns an explicit empty list, not a fabricated zero | PASS | 郭嘉 × `HISTORY_ANNOTATION` (a real zero-coverage combination in this slice) returns `"evidence": []`, HTTP 200 |
| Unknown `person_id` is 404, distinct from "zero evidence" | PASS | Confirms these two states are never conflated |

Citation-laundering and missing-D-017-notice rejection at the LLM-validator layer were already covered by backend's own `tests/backend/test_llm_validator.py` (`test_rejects_citation_laundering_unknown_evidence_id`, `test_missing_coding_validation_notice_when_evidence_cited_rejected`) — QA re-ran these (included in the 46 above) rather than duplicating them.

## 3. Code review findings (QA, read-only — no fixes applied outside `tests/qa/`)

- `app/backend/api/main.py`'s `/v1/ask` filters evidence by `ANSWER_MODE_LAYERS` **before** constructing LLM context, so leakage is structurally prevented upstream of the LLM call, not just caught after the fact by the validator — confirmed by reading the code and by the golden-case tests above.
- `app/backend/api/db.py`'s `get_evidence_for_person` returns `[]` (never a zero-filled placeholder row) when a person/layer combination has no coded evidence — confirmed by code + golden-case test.
- Backend and frontend each independently flagged two real schema-drift items (see `handoffs/DECISIONS.md#D-018`, `#D-022`, `PROJECT_STATE.md`'s committed follow-ups): `analysis/outputs/result.json`'s 4th metric kind (`network_edge_count.*`) isn't in `api_contract.yaml`'s 3-kind enum (handled by routing that data through `/v1/events/{id}/relationships` instead — a reasonable interim design, not silently broken); `locator.paragraph_index` in the curated export is a synthetic per-chapter ordinal, not the ingestion pipeline's real value (documented, not hidden).

## 4. Not run (explicit, per `tests/TEST_PLAN.md` "Out of scope")

- Manual/visual accessibility walkthrough of a running, deployed UI — nothing is deployed in this slice; only automated `jest-axe` checks per component were run (0 violations across all tested components).
- Real external LLM provider (`OpenAILLMClient`) — intentionally unimplemented stub, no key/network in this environment, never called in tests.
- Load/performance testing — out of scope at this data volume.
- End-to-end browser journeys (AC-1 through AC-6 as full user flows) — verified at the API/component level, not click-through in a real browser session.

## 5. Defects found

**None at critical/blocker severity.** No test failures, no discovered correctness bug in the golden-case pass. Three pre-existing tooling/schema issues were found (by E1's own agents, independently, and by re-verification here) and were fixed by the orchestrator before this QA pass began (D-022): the `validate_structure.py` node_modules crash, a stale post-B0 unit test, and a missing `coding_validation_status` field in `data/schemas/evidence.schema.json`. These are recorded as fixed, not as open defects.

## 6. Acceptance-criteria traceability (`product/acceptance_criteria.md`)

| AC | Covered by |
| --- | --- |
| AC-1 (event overview, coverage) | `app/frontend` `EventOverview` test; backend `/v1/events/{id}/people` returns per-layer coverage counts (code-reviewed) |
| AC-2 (person comparison, no merged claims, explicit "no evidence" state) | QA golden case (missing-evidence test); frontend `EvidenceCard`/`SourceModeControl` tests |
| AC-3 (AI answer panel grounding/abstention/연의 labeling/error state) | Backend `test_llm_validator.py` + QA leakage tests; frontend `AIAnswerPanel` tests |
| AC-4 (score breakdown, insufficient-data default, custom-score labeling) | Frontend `ScoreCard` tests (insufficient_data default state) |
| AC-5 (quest completion gating) | Frontend `QuestCard` tests (aria-disabled until both conditions met) |
| AC-6 (quiz locked until evidence seen) | Not implemented this slice (L-04 item schema is `[TBD]`, `product/feature_spec.md`'s explicit non-guess instruction) — frontend ships a "퀴즈 준비 중" placeholder, correctly not a fabricated feature |
| AC-7 (cross-cutting states: loading/empty/stale/error/permission) | Frontend component tests cover default/loading/empty/error per component; `stale`/`permission unavailable` states are specified in `design/component_spec.md` but not separately unit-tested this pass — flagged as a residual risk, not silently assumed done |

## 7. Residual risks

- No real end-to-end browser test exists — everything above is API/component-level. A future pass should exercise the actual built `app/frontend/dist/` against a running backend instance.
- AC-7's `stale result` and `permission unavailable` states are specified but not individually unit-tested — worth a follow-up test before this slice is shown to a real user.
- `tests/qa/` golden cases currently hardcode the 15-alias / 10-person set from this exact expansion pass (D-021); if D-016's further expansion adds more people, this test file's `expected` dict must be extended, not silently left stale.
