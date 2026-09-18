# Data-to-UI Mapping — S1/S2 Vertical Slice (적벽대전)

Status: `S2 RECONCILED — 2026-09-17`. Reconciled by the orchestrator against the **real** field shapes reported by S1 (D1/R1/A1) and S2/U1's `design/component_spec.md`. Where the original S1-drafted contract-level guess didn't match reality, the real shape wins and the original guess is struck through and kept for history. See `design/component_spec.md` for full per-component detail (props, states, keyboard, a11y) — this table is the field-to-source index.

| Component | UI element | Data field (real) | Type | Source track/artifact |
| --- | --- | --- | --- | --- |
| `SourceModeControl` | mode selector | `source_layer` | enum: `HISTORY_BASE, HISTORY_ANNOTATION, ROMANCE, LATER_INTERPRETATION, GAME_DATA` | matches `data/schemas/evidence.schema.json` exactly |
| `SourceModeControl` | 정사 주석 enabled/disabled | ~~`source_layer_coverage.HISTORY_ANNOTATION.evidence_count`~~ → count rows in `research/evidence_matrix.csv` where `source_layer == HISTORY_ANNOTATION`, per person | int, computed client/server-side, no dedicated coverage field exists | `research/evidence_matrix.csv`. **Real number for this slice: 6/22 overall — not thin** (per-person varies; 諸葛亮 = 0). AC-1's "thin coverage → disable" default should be revisited per-person, not per-layer. |
| `EvidenceCard` | evidence id | `evidence_id` | string, e.g. `"HB-J54-P2"` | `research/evidence_matrix.csv` |
| `EvidenceCard` | layer badge | `source_layer` | enum (same as above) | `research/evidence_matrix.csv` |
| `EvidenceCard` | work/edition/locator | `work_title, edition, volume_or_chapter, locator` | all **free-text strings**, not `data/schemas/evidence.schema.json`'s structured `{paragraph_index, char_start, char_end}` object | `research/evidence_matrix.csv` (CSV shape) vs. `data/schemas/evidence.schema.json` (curated-export shape) — **these two do not match field-for-field; a transform step is required before curated export, not built yet.** See "Known schema gap" below. |
| `EvidenceCard` | quotation status | ~~`quotation_type: original_quote\|project_translation\|paraphrase`~~ → `excerpt_type` | enum, **actual values**: `short_permitted_excerpt`, `project_paraphrase_ellipsis_marked`, `original_zh_only_paraphrase_ellipsis_marked`, `original_zh_only_no_translation_provided` | `research/evidence_matrix.csv`. Does not match `evidence.schema.json`'s `translation_type` enum — same schema-gap note applies. |
| `EvidenceCard` | ambiguity/disagreement flag | `confidence` (**string** `"high"\|"medium"`, not a 0–1 float), `ambiguity_note` | string / string | `research/evidence_matrix.csv` |
| `EvidenceCard` | coding honesty notice | `extraction_reviewer, review_status` (currently always `"R1 (single coder)"` / `"extracted_not_double_coded"`) | string / string | `research/evidence_matrix.csv`. **Must render every time, not hideable** — this is the D-017 disclosure requirement surfacing in the UI, not just in AI answers. |
| `ScoreCard` | value + unit | ~~`score_value, unit`~~ → **no composite score exists in this slice.** Renders one of `coverage.*` (int count), `label_frequency.*` (int count), or `divergence.*` (`value: null`, classification embedded in `method` text) | see `analysis/outputs/result.json`'s `metrics[]` shape | `analysis/outputs/result.json`. `analysis/scoring_model.md` explicitly stops before the display-score stage — this is not a bug, it's this slice's actual state. |
| `ScoreCard` | version | ~~`model_version`~~ → not present anywhere in this slice's output | n/a | none yet — deferred until a real weighting model exists (post-S2) |
| `ScoreCard` | coverage | covered by `coverage.*` metrics directly (see above) — `0` means "no coded span," never a score of zero | int or `null` | `analysis/outputs/result.json` |
| `ScoreCard` | confidence / insufficient-evidence state | no per-metric confidence field yet; use explicit `status: insufficient_data` as this slice's default `score_type` | enum | `design/component_spec.md`'s `ScoreCard` spec |
| `ScoreCard` | score type badge | `score_type` | enum: `default, user_custom, external_game, `**`insufficient_data`**` (4th value added — this slice needs it since no composite score exists)` | product-level contract (F-02/E-04); user_custom is computed client-side, never stored as `default` |
| `ContributionBreakdown` | sub-indicator rows | **no backing data in this slice at all** — component renders `not_yet_available` state, no placeholder numbers | n/a | `analysis/scoring_model.md` confirms no subscore/weight stage has run yet |
| `ContributionBreakdown` | rounding consistency | deferred with the rest of this component until a real weighting model exists | n/a | same as above |
| `QuestCard` | goal/completion condition | `quest_goal, completion_rule: {requires_layers, requires_counter_evidence}` | string / structured predicate | product-level contract, no backing schema needed yet (unchanged from S1 draft) |
| `QuestCard` | evidence seen vs. unseen | `evidence_seen_ids[], counter_evidence_ids[]` | array / array, keyed against real `evidence_id`s | client-side state, keyed against `research/evidence_matrix.csv` IDs |
| `AIAnswerPanel` | answer mode | `answer_mode` | enum: `정사, 연의, 비교, 게임` | `analysis/schemas/interpretation.schema.json` (finalized in S2 by L1) |
| `AIAnswerPanel` | per-claim evidence refs | `claims[].claim_id, claims[].claim_type, claims[].text, claims[].evidence_refs[], claims[].metric_refs[], claims[].confidence, claims[].caveats[]` | array of objects, schema-validated | `analysis/schemas/interpretation.schema.json`, `analysis/llm_contract.md` |
| `AIAnswerPanel` | abstention state | `status: "ok"\|"insufficient_evidence"`, `abstention_reason` | enum / string | same as above |
| `AIAnswerPanel` | coding-validation disclosure | `coding_validation_notice` (mandatory whenever `evidence_refs` is non-empty) | string | `analysis/llm_contract.md` rule 3 (D-017) |

## Known schema gap (flag for S3, not resolved here)

`research/evidence_matrix.csv` (the S1 research working format) and `data/schemas/evidence.schema.json` (the intended curated-app-export contract, `data/DATA_ZONES.md` Zone C) do not match field-for-field: structured `locator` object vs. free-text string, array `person_refs` vs. semicolon-joined string, 0–1 float `confidence` vs. `"high"/"medium"` string, and different excerpt/translation-type enums. **This is not necessarily a bug to "fix" by forcing one to match the other** — a research CSV and a normalized DB-import schema can legitimately differ in shape. What's actually missing is the **transform/mapping pipeline between them**, which has not been built. S3's Architect (E0) and Data Engineer must design this mapping explicitly as part of the curated-export pipeline before any DB import — do not let S3 discover this gap mid-implementation.

## Fields intentionally left unmapped at S2

- Any field implying full-corpus person/event coverage (out of scope for this event-only slice; also see D-016 — expansion is committed, not abandoned).
- Any `GAME_DATA` numeric field — no external game data source has been approved.
- Quiz item schema exact shape (`product/feature_spec.md` L-04 `[TBD]`) — not blocking B2, carried forward.
- `divergence.*`'s `classification`/`evidence_ids` as typed fields (currently embedded as text in `result.json`'s `method` string) — recommended schema extension for whoever next touches `analysis/schemas/result.schema.json`.
