# Stage Completion Report

- Stage: `S1`
- Boundary awaiting approval: `B1`
- Status: `COMPLETE`
- Target commit/run IDs: uncommitted working tree; A1 run `run-20260917T122003Z`
- Completed at: 2026-09-17

## 1. Planned scope

`TASK-S1-DEFINITION`, under the B0-approved scope (concept = Hybrid, sample = 적벽대전, source layers = HISTORY_BASE + ROMANCE + HISTORY_ANNOTATION extracted from existing raw): R1 (evidence/coding definition), D1 (approved sample ingestion), A1 (sample analysis, depends on R1+D1), P1 (product planning), run per `orchestration/workflow.yaml`.

## 2. Completed outputs

| Track | Output | Status | Evidence path |
| --- | --- | --- | --- |
| D1 | Reproducible ingestion pipeline; 1,148 candidate paragraphs (479 HISTORY_BASE / 432 HISTORY_ANNOTATION / 237 ROMANCE) | done | `data/pipelines/build_chibi_sample.py`, `data/quality_report.json` |
| D1 | Data schemas (dataset/person/evidence/event/relationship) | done | `data/schemas/*.schema.json` |
| D1 | Person registry: 5 canonical persons, 16 text-attested aliases, 0 collisions | done | `data/data_dictionary.csv`; full registry (private) at `${TKAF_PRIVATE_DATA_ROOT}/analysis/tables/person_registry.json` |
| R1 | Coding manual: 21 labels, ambiguity rules, explicit "not yet double-coded" notice | done | `research/coding_manual.md` |
| R1 | Evidence matrix: 22 real coded spans (6 HISTORY_BASE / 6 HISTORY_ANNOTATION / 10 ROMANCE), short excerpts + own paraphrase, locators, checksums | done | `research/evidence_matrix.csv` |
| R1 | Analysis criteria: construct-to-variable mapping, divergence procedure, known-conflicts table | done (written by orchestrator from R1's verified content after a subagent tool restriction blocked R1's own write) | `research/analysis_criteria.md` |
| R1 | CR-001 promoted from candidate to `papers.csv` after direct abstract fetch (not full-text) | done, partial verification | `research/papers.csv` |
| A1 | Frozen analysis plan (pre-registered before computing results) | done | `analysis/analysis_plan.md` |
| A1 | Scoring model: slice explicitly stops before subscore/weighting/display-score stages; no composite score produced | done | `analysis/scoring_model.md` |
| A1 | Network analysis plan: 8 edges across 3 layers, no centrality computed at this N | done | `analysis/network_analysis_plan.md` |
| A1 | Reproducible result computation | done | `analysis/pipelines/compute_chibi_result.py`, `analysis/outputs/result.json`, `analysis/outputs/run_manifest.json` |
| P1 | Feature spec, user journeys, screen inventory, gamification spec, acceptance criteria, data-to-UI mapping (contract level) | done | `product/feature_spec.md`, `product/user_journeys.md`, `product/screen_inventory.md`, `product/gamification_spec.md`, `product/acceptance_criteria.md`, `product/data_to_ui_mapping.md` |
| Orchestrator | `.gitignore` narrowed to allow committing `analysis/outputs/result.json`/`run_manifest.json` (B1-required artifacts) | done | `.gitignore`, `handoffs/DECISIONS.md#D-015` |

## 3. Validation results

| Check | Result | Command/method | Evidence |
| --- | --- | --- | --- |
| Repository structure | PASS (38 required files) | `python scripts/validate_structure.py` | terminal, re-run after all four tracks |
| Data boundary check | PASS | `python scripts/check_data_boundaries.py` | terminal, re-run after all four tracks |
| No private/runtime files tracked | PASS | `git status --short` | only expected repo-safe paths modified/untracked; no `tkaf-private-data/` or `data/private/` paths |
| Raw corpus untouched | PASS | D1 self-check + orchestrator re-check | raw files only opened read-only; pipeline writes only to private analysis zone |
| Result reproducibility | PASS | `python analysis/pipelines/compute_chibi_result.py` deterministic re-run against unchanged `evidence_matrix.csv` | `analysis/outputs/run_manifest.json` (input/output SHA-256 recorded) |
| `result.json` schema conformance | PASS (manual validation by A1) | checked against `analysis/schemas/result.schema.json` | A1 handoff |
| Source-layer separation | PASS | manual review of `evidence_matrix.csv`, `result.json` | no row merges HISTORY_BASE/HISTORY_ANNOTATION/ROMANCE into one fact |
| Entity alias collisions | PASS (0 collisions, 16 aliases, all text-attested) | D1 pipeline check | `data/quality_report.json` |
| Missing-value-as-zero check | PASS | manual review — `coverage.*` = 0 is explicitly documented as "no coded span," not a zero score | `analysis/outputs/result.json` §warnings |
| Citation fabrication check | PASS with caveat | CR-001 promoted to `papers.csv` only after a direct abstract fetch; `fulltext_status: abstract_reviewed_fulltext_not_reviewed` — method/results not yet confirmed | `research/papers.csv` |
| Annotation-bracket cross-validation | PASS | D1's pipeline and R1's independent manual reading both converged on the same `〈...〉` (U+3008/U+3009) delimiter convention | `handoffs/DECISIONS.md#D-014` |

## 4. Decisions made

- D-013: 적벽대전 `ROMANCE` range narrowed 回49–61 → 回49–57 (D1, minor/reversible).
- D-014: `HISTORY_ANNOTATION` confirmed extractable in-place via `〈...〉` brackets, cross-validated by two independent tracks; Q-006 fully resolved.
- D-015: `.gitignore` narrowly amended to allow the two B1-required `analysis/outputs/*` files.
- D-001–D-012 remain in force unchanged.

## 5. Problems and open questions

Full detail in `handoffs/OPEN_QUESTIONS.md`. Summary:

- **Q-005** (learning-game difficulty level) — open, non-blocking. P1 deliberately left `L-05` unspecified rather than guessing.
- **Q-009** (user data-literacy assumption) — open, non-blocking. P1 defaults to the more explanatory presentation until answered.
- **Q-010** (updated — addressed, not fully closed) — the human owner chose option (c): a second, context-isolated LLM coder blind-recoded all 22 rows independently. Result: 20/22 exact agreement, Cohen's κ = 0.90 (`research/intercoder_reliability.md`, `handoffs/DECISIONS.md#D-017`). The two disagreements were adjudicated and used to sharpen two label definitions in `research/coding_manual.md`. **This is LLM-LLM agreement, not human validation** — it reduces the severity of the `unvalidated_llm_autocoding_used_as_ground_truth` risk (the manual is shown internally consistent) but does not close it. Human review before B2/production remains a committed follow-up (`handoffs/PROJECT_STATE.md`).
- Minor/non-blocking follow-ups for S2: `analysis/schemas/result.schema.json` has no typed `edges` array (network edge list currently only exists as counts, not a drill-down list); `product/feature_spec.md`'s L-04 quiz-item schema is `[TBD]`; `data/ingestion_report.md`'s juan-56 bracket imbalance (QC-D1-1) should be manually checked if that juan is ever coded.

No B1 hard blocker other than Q-010 was triggered: no fabricated/unverified citation was promoted as verified, rights for the sample are owner-confirmed, the analysis plan was frozen before results, `result.json` validates against its schema, the computation is reproducible, no private data was committed, source layers were never mixed, there are 0 entity alias collisions, no missing value was scored as zero, and no feature spec promises analysis the data can't support.

## 6. Residual risks

- **Q-010 (LLM-as-single-coder)** — the most material item; see above.
- N=22 evidence spans is far too small for any inferential statistic; all A1 outputs are descriptive counts or single-case qualitative classifications (explicitly labeled as such throughout `analysis/outputs/result.json`).
- Coverage gap: `ROMANCE` 回51–57 and 5 of 10 candidate `HISTORY_BASE` juan were ingested by D1 but not yet coded by R1 — any claim about "the full battle" is out of scope.
- `research/papers.csv`'s CR-001 is abstract-verified only; its specific method/results must not be cited as confirmed until full text is read.
- `product/data_to_ui_mapping.md` is a contract-level design against expected field names, not yet reconciled field-by-field against the actual `analysis/outputs/result.json` shape (e.g., no `model_version`/`score_value` fields exist yet in this slice's result, by design — `scoring_model.md` explains why). No conflict was found, but a formal reconciliation pass is recommended in S2.
- `data/ingestion_report.md`'s rights status remains owner-confirmed (D-012), not a documented third-party legal opinion.

## 7. Proposed next-stage scope (S2, pending B1 approval)

- **Next stage:** S2 `ux_ui_and_contract_design` per `orchestration/workflow.yaml` — tracks U1 (ux_designer, replaces `design/DESIGN.md`'s `STARTER` status with the Hybrid-specific design) and L1 (llm_analyst, defines `analysis/llm_contract.md` and `analysis/schemas/interpretation.schema.json` for the `AIAnswerPanel`).
- **Included:** designing the actual screens/components for the 적벽대전 vertical slice using the real `result.json`/`evidence_matrix.csv` shapes now available; defining the LLM interpretation contract that turns A1's coverage/divergence output into an evidence-linked AI answer (정사/연의/비교 modes).
- **Excluded:** production UI/frontend code, 8-bit battle system, full curriculum, any second product concept or event beyond 적벽대전, resolving Q-005/Q-009 speculatively.
- **Carried decision needed before or during S2:** Q-010 resolution (human/double-coding validation approach) should be settled before any evidence from this slice is treated as ground truth beyond internal design work.
- **Carried commitment, required before B2 (D-016):** the human owner confirmed the 5-person/22-evidence cast was deliberately kept small only to validate the pipeline, and that 적벽대전 actually involves more named participants already visible in the extracted data (黃蓋, 關羽, 魯肅, 趙雲, 郭嘉). An expansion pass (more people, more evidence spans, re-running R1/D1/A1 at larger scope) is required before B2/production locks in the current 5-person scope as final. This is not optional cleanup — do not let S2/S3 planning silently treat 5 people as the finished cast.
- **Expected outputs:** `design/DESIGN.md` (no longer `STARTER`), `design/wireframe_brief.md`, `design/component_spec.md`, `design/accessibility_checklist.md`, `analysis/llm_contract.md`, `analysis/schemas/interpretation.schema.json`.

## 8. Approval question

"샘플 분석 결과와 제품 기획을 정렬한 이 범위로 UX/UI 설계를 시작할까요?"

Q-010 has been addressed for B1 purposes (LLM-LLM double-coding check, κ=0.90; human validation remains a committed follow-up before B2 — see `handoffs/PROJECT_STATE.md`). Q-005 and Q-009 can be answered now or deferred into S2/P1 without blocking this transition. D-016 (cast/evidence expansion before B2) is recorded and carried forward.

Do not begin S2 until the user explicitly approves and the approval is recorded in `handoffs/APPROVALS.md`.
