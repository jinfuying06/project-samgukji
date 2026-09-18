# Stage Completion Report

- Stage: `S3`
- Boundary awaiting approval: `B3`
- Status: `COMPLETE — gate FAILED twice on automated score, then explicitly overridden and approved by the human owner (D-025)`
- Target commit/run IDs: uncommitted working tree; second Evaluator/`run_eval.py` run dated 2026-09-18
- Completed at: 2026-09-18

## 1. Planned scope

`TASK-S3-ARCHITECTURE-AND-EXPANSION`, under the B2-approved scope: E0 (architecture) and the D-016 cast/evidence expansion pass running in parallel (human owner's explicit "병행" choice), then E1 (backend + frontend, parallel, after E0's contracts froze), then QA, then an independent Evaluator scoring the `implementation_gate` (B3) per `orchestration/gates.yaml`/`scoring.yaml`. After the first evaluation failed, the human owner chose Q-011 option (a) — a real review — and a second independent Evaluator re-scored the gate.

## 2. Completed outputs

| Track | Output | Status | Evidence path |
| --- | --- | --- | --- |
| E0 | System architecture, API contract (7 endpoints), threat model, 2 ADRs | done | `app/architecture/{system.md,api_contract.yaml,threat_model.md,adr/}` |
| Expansion pass | Cast 5→10 persons, evidence 22→30 spans, 2 new coding labels, `result.json` regenerated (60 metrics) | done | `research/evidence_matrix.csv`, `research/coding_manual.md`, `analysis/outputs/result.json` |
| E1/Backend | Curated Export Transform, DB migrations, atomic/idempotent importer, all 7 API endpoints, LLM response validator with citation cross-check | done, 30/30 pytest passing (independently re-run by orchestrator) | `app/backend/**` |
| E1/Frontend | All 6 screens/components (Vite+React+TS), central design-token theme, contract-drift + accessibility tests | done, 32/32 vitest passing (independently re-run by orchestrator) | `app/frontend/**` |
| Orchestrator | 3 real bugs found (independently, by both E1 tracks) and fixed: `validate_structure.py` node_modules crash, stale post-B0 test, missing D-017 field in `evidence.schema.json` | done | `scripts/validate_structure.py`, `tests/test_project_policy.py`, `data/schemas/evidence.schema.json` |
| QA | `tests/TEST_PLAN.md`, `tests/TEST_REPORT.md`, 7 new golden-case tests (entity resolution, source-layer non-leakage, citation reproducibility, D-017 exposure, missing-evidence handling) | done, 0 critical/blocker defects | `tests/TEST_PLAN.md`, `tests/TEST_REPORT.md`, `tests/qa/` |
| Evaluator #1 (independent) | Scored all 12 categories | done — **FAIL**, 81.79, `coding_calibration_missing` | `handoffs/DECISIONS.md#D-023` |
| Orchestrator | 3 documentation-staleness fixes Evaluator #1 found (still said "5 persons/22 rows" post-expansion) | done | `data/quality_report.json`, `analysis/analysis_plan.md` (DEV-001), `product/acceptance_criteria.md` |
| Human owner | Real review of all 30 evidence rows via the delivered artifact — reported no disagreements, including the 2 pre-flagged adjudication cases | done | `research/intercoder_reliability.md` "Human review pass", `handoffs/DECISIONS.md#D-024` |
| Orchestrator | `coding_validation_status` flipped `llm_llm_validated_only` → `human_validated` at the single source of truth, curated export regenerated, DB re-imported, all test/fixture literals updated, full suites re-verified green (backend 46/46, frontend 33/33) | done | `data/pipelines/build_curated_export.py`, `handoffs/DECISIONS.md#D-024` |
| Evaluator #2 (independent, fresh) | Re-scored all 12 categories from scratch with the new fact, independently verified D-024 end-to-end (queried the runtime DB directly, checked frontend rendering, re-ran both test suites) | done — **still FAIL**, 84.61 (+2.82), same hard blocker, with detailed reasoning on why `double_coded_calibration_set` stays `false` | `evals/eval_input.json`, `evals/eval_results.json` |
| Orchestrator | Fixed 2 newly-found stale "current state" claims in required B3 artifacts (`app/architecture/system.md`, `api_contract.yaml`) and updated `tests/TEST_REPORT.md`'s frontend count (32→33) | done | see files above |

## 3. Validation results

| Check | Result | Command/method | Evidence |
| --- | --- | --- | --- |
| Backend test suite | PASS (46/46) | `pytest tests/` — re-run independently by orchestrator, QA, and both Evaluators | terminal, `tests/TEST_REPORT.md` |
| Frontend test suite | PASS (33/33, up from 32 after a D-024 regression test) | `cd app/frontend && npm test` | terminal, `tests/TEST_REPORT.md` |
| Frontend typecheck/build | PASS | `npx tsc --noEmit`, `npm run build` | terminal |
| Repository structure | PASS (38 required files) | `python scripts/validate_structure.py` | terminal |
| Data boundary check | PASS | `python scripts/check_data_boundaries.py` | terminal |
| Entity-resolution, source-layer non-leakage, citation reproducibility, D-017 exposure, missing-evidence handling | PASS (all 5, QA golden cases) | `tests/qa/test_qa_golden_cases.py` | `tests/TEST_REPORT.md` §2 |
| `coding_validation_status` = `human_validated` actually live in the runtime DB (not just the source file) | PASS — Evaluator #2 queried `data/runtime/tkaf.local.sqlite3` directly: 2 `dataset_versions` rows, the active one (`is_active=1`) is `human_validated`; all 30 evidence rows under it show `human_validated`; the old version is retained (not deleted) but inactive | Evaluator #2 report |
| Frontend renders the correct disclosure string for each status, tested | PASS | `EvidenceCard.tsx` + its 3 dedicated tests | Evaluator #2 report |
| **B3 implementation_gate score — round 1** | **FAIL** — weighted total 81.79, 1 hard blocker (`coding_calibration_missing`) | Evaluator #1, `python evals/run_eval.py` | `handoffs/DECISIONS.md#D-023` |
| **B3 implementation_gate score — round 2 (current)** | **FAIL** — weighted total 84.61, same 1 hard blocker | Evaluator #2 (fresh, independent), `python evals/run_eval.py` | `evals/eval_input.json`, `evals/eval_results.json` |

## 4. Decisions made

- D-020: bug fix in `compute_chibi_result.py` (hardcoded 5-person cast).
- D-021: D-016 expansion executed (5→10 persons, 22→30 evidence spans).
- D-022: three real bugs found and fixed post-E1.
- D-023: B3 evaluated independently (round 1), result FAIL, 81.79.
- D-024: human owner completed a real review of all 30 rows (Q-011 option (a)); `coding_validation_status` flipped to `human_validated` system-wide.
- (round-2 evaluation itself is not yet a numbered decision — it is a re-measurement, not a new choice; the choice it informs is still open at Q-011.)

## 5. Problems and open questions

- **Q-011 (still open, gate-blocking):** round 2's hard blocker is identical to round 1's — `coding_calibration_missing`, from `double_coded_calibration_set: false`. Evaluator #2's detailed reasoning: this project's own vocabulary defines "double-coded" as an independent second coder producing labels from scratch plus a computed agreement statistic (which already happened once, LLM-to-LLM, κ=0.90). D-024's human pass was explicitly a *confirmation/audit* of already-produced labels against a project paraphrase, not an independent from-scratch coding — so, by the project's own honest description of what it was, it does not produce a comparable statistic, and marking the field `true` would misrepresent what happened. Evaluator #2 credited the real, substantial improvement this caused elsewhere instead: `coding_reliability` rose 74→85, `data_reproducibility` and `statistical_validity` and `product_consistency` also rose (documentation-staleness fixes), for a net category-score gain of +2.82 (81.79→84.61) — but the mechanical hard-blocker check is gate-agnostic and fires regardless of context, per `orchestration/scoring.yaml`'s own rule.
- Evaluator #2 also confirmed independently (not just via the domain judgment call) that `double_coded_calibration_set` is a `recommended_target` under B1 in `orchestration/gates.yaml`, not a named `hard_blocker` under `implementation_gate` (B3) at all — the `coding_calibration_missing` blocker exists purely because `evals/run_eval.py`'s generic `BOOLEAN_BLOCKERS` table applies this check to every gate uniformly, not because B3 itself names it. This is a real, structural mismatch between the general-purpose eval script and the gate-specific rubric, worth fixing at the tooling level regardless of what the human decides about the current gate — but the orchestrator has not modified `evals/run_eval.py` to do so, since changing an evaluation script to produce a more favorable result is exactly the kind of self-serving change the project's rules exist to prevent (`agents/_common.md`: "Gate 점수를 올리기 위해 기준, 데이터, 테스트를 약화하지 않는다"). Any change to `run_eval.py`'s blocker logic should be made on its own merits, reviewed independently, not timed to unblock this specific gate.
- Q-005, Q-009 remain open, non-blocking regardless of Q-011's outcome.

No other B3 hard blocker was triggered in either round: no source-layer mixing, no fabricated composite score, no private data or database committed, a real rollback mechanism exists.

## 6. Residual risks

- **Q-011 remains the single blocking decision**, now with a fuller picture: genuine, measured improvement occurred, and the residual gap is well-understood and precisely characterized rather than vague.
- `usability_accessibility` still scores lowest (65) — `design/accessibility_checklist.md` remains 100% `NOT_TESTED` beyond automated `jest-axe` scans.
- `operational_readiness` dropped 78→70 in round 2 specifically because two of its required input documents contained factually stale "current state" claims (now fixed by the orchestrator, not yet re-verified by a third evaluation).
- Two schema-drift items backend flagged as out-of-scope for it alone (`network_edge_count.*` not in the metrics enum; synthetic `paragraph_index`) — documented, not fixed.
- `OpenAILLMClient` remains an untested stub.
- No SAST/dependency-vulnerability scan has been run.
- The `run_eval.py` tooling mismatch noted in §5 (a B1 `recommended_target` acting as a universal `hard_blocker`) is itself a small piece of unresolved technical debt in the evaluation tooling, independent of this project's specific gate outcome.

## 7. Resolution

The human owner reviewed both evaluation rounds' full results and chose Q-011 option (b): explicitly accept the residual coding-validation gap as a known, disclosed limitation rather than commission option (c) (a genuine blind second human coding pass). This is now recorded as **D-025** and as an `approved_with_conditions` row in `handoffs/APPROVALS.md`, scoped explicitly to continued internal development/demo use of this vertical slice — not to public release. S4 (release decision) has not been opened; that would require re-examining the coding-validation gap on its own terms first.

## 8. Approval question

Not the standard wording, since the gate itself did not pass automatically — but the human owner's explicit approval is recorded per `orchestration/execution_policy.yaml`'s requirements (boundary, approved scope, approver, timestamp, conditions) in `handoffs/APPROVALS.md`'s B3 row.

Any future work that extends this evidence set toward a real public release must re-open and re-examine the coding-validation gap rather than treat this approval as having already settled it.
