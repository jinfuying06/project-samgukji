# Component Specification — S2 (적벽대전 Vertical Slice, Hybrid)

Status: `S2 DRAFT — 2026-09-17`. Props below are the **real fields** found in `research/evidence_matrix.csv`, `analysis/outputs/result.json`, `analysis/schemas/result.schema.json`, and `data/schemas/*.schema.json` as of S1 completion — not the contract-level guesses in `product/data_to_ui_mapping.md`. Every discrepancy found between that mapping and the real shapes is called out inline and summarized in "Reconciliation gaps" at the end; `product/data_to_ui_mapping.md` itself is outside this track's write path and must be updated by the orchestrator.

## `SourceModeControl`

- Purpose: switch among 정사/정사 주석/연의/비교/게임 (`design/DESIGN.md`§3/§6).
- Data props: `available_layers: SourceLayer[]` where `SourceLayer = "HISTORY_BASE"|"HISTORY_ANNOTATION"|"ROMANCE"|"LATER_INTERPRETATION"|"GAME_DATA"` (enum matches `data/schemas/evidence.schema.json`/`relationship.schema.json`/`event.schema.json` exactly); `active_layer: SourceLayer | "비교"`.
- **Real-data note (corrects an assumption in `product/user_journeys.md`/`acceptance_criteria.md` AC-1):** for this slice's 5-person cast, `HISTORY_ANNOTATION` has **6 of 22** evidence rows — the same count as `HISTORY_BASE` (also 6/22). It is not thin. Default this control to **정사/정사 주석/연의 all enabled** for this cast, not a degraded "정사 주석 disabled" default. AC-1's coverage-threshold decision should be revisited by the orchestrator/statistician with this number in hand, per-person (e.g. 諸葛亮 has 0 `HISTORY_ANNOTATION` rows — that specific person/layer combination should show disabled-with-reason, not the whole layer).
- `GAME_DATA` mode: disabled in this slice (no `GAME_DATA` source approved), shown with reason text, not hidden — matches `product/gamification_spec.md`'s "외부 게임 수치 없음" note.
- Variants: full 5-way control (event overview, comparison screens) vs. compact 3-way (정사/연의/비교 only, used inside a single-person deep-dive where 정사 주석/게임 aren't relevant to the current view).
- States: default, loading (layers not yet known), empty (no layers available at all — should not occur in this slice but must not crash), disabled (per-layer, with visible reason), keyboard-focus.
- Keyboard: roving `tabindex`, arrow-key navigation between pills/tabs, `Enter`/`Space` selects; disabled options are focusable-but-non-activatable so their reason text (via `aria-describedby`) is reachable.
- Accessible name/description: control has `role="tablist"`/`radiogroup`-equivalent semantics; each option's accessible name is its layer label from `design/DESIGN.md`§3's table (e.g. "정사 주석"), never the enum string; selected state exposed via `aria-selected`/`aria-checked`, not color alone.
- Responsive: horizontal row desktop/tablet; horizontally scrollable pill row on mobile — never wraps to a second line (would break §2's "source mode pinned at top" rule).
- Tests: renders correct enabled/disabled set from `available_layers`; keyboard nav order; disabled reason is announced; selecting 비교 mode fans out to the multi-layer comparison layout.

## `EvidenceCard`

- Purpose: render one `research/evidence_matrix.csv` row.
- Data props (**as the CSV actually has them, not as `evidence.schema.json` defines them — see gap below**): `evidence_id: string` (e.g. `"HB-J54-P2"`), `source_layer: SourceLayer`, `work_title: string` (三國志/三國演義), `edition: string` (free text, e.g. `"zh.wikisource.org crawl (edition_ref: TBD by D1)"`), `volume_or_chapter: string` (e.g. `"卷54 周瑜魯肅呂蒙傳"`), `locator: string` (free-text description, e.g. `"paragraph quoting Cao Cao's letter to Sun Quan"` — **not** the structured `{paragraph_index, char_start, char_end}` object `evidence.schema.json` defines), `person_refs: string` (semicolon-joined, e.g. `"PERSON-CAOCAO;PERSON-ZHOUYU"` — **not a JSON array**; component must split on `;` client-side), `event_ref: string`, `primary_actor: string`, `subject_of_claim: string | ""` (empty in 14 of 22 rows), `coding_label: string` (one of 21 values in `research/coding_manual.md`), `excerpt_zh: string`, `excerpt_type: "short_permitted_excerpt"|"project_paraphrase_ellipsis_marked"|"original_zh_only_paraphrase_ellipsis_marked"|"original_zh_only_no_translation_provided"` (**actual values found in the CSV — do not assume this matches `evidence.schema.json`'s `translation_type` enum `none_original_only|publisher|project|paraphrase`, it doesn't**), `checksum_sha256_12: string`, `extraction_reviewer: string` (currently always `"R1 (single coder)"`), `review_status: string` (currently always `"extracted_not_double_coded"` — render this, don't hide it, per D-017), `confidence: "high"|"medium"` (**a string, not the 0–1 float `evidence.schema.json` specifies**), `ambiguity_note: string | ""`.
- Variants: has `subject_of_claim` (shows an actor→subject relation line) vs. actor-only (8 of 22 rows).
- States: default, loading, **empty ("이 층위에서는 근거 없음" — must render as an explicit card-shaped state, not blank space, per AC-2)**, error.
- Keyboard: card is a `button`/`article`+disclosure pattern; `Enter`/`Space` expands full metadata (edition, checksum, reviewer/review_status); collapsed view shows only `evidence_id`, layer badge, excerpt, coding_label.
- Accessible name: `"{primary_actor} 근거, {work_title} {volume_or_chapter}, {layer label}"`; ambiguity note exposed via `aria-describedby` when present.
- Responsive: full-width stacked (mobile), 2-up grid in comparison mode (tablet+).
- Tests: renders the review_status/confidence honesty note every time (never suppressible); empty-layer state renders instead of nothing; excerpt never exceeds ~200 chars (matches `evidence.schema.json`'s `permitted_excerpt.maxLength` even though this CSV uses a different field name).

## `ScoreCard`

- Purpose per `design/DESIGN.md`§6: 값/단위/모델버전/coverage/confidence, 기본/커스텀/외부게임 구분, 분해로 이동.
- **Real-data note (largest gap in this slice):** `analysis/outputs/result.json` has **no `score_value` and no `model_version` at all** — `analysis/scoring_model.md` explicitly stops the pipeline before the subscore/weighting/display-score stages (N=22 too small, no approved weights). What exists is three metric kinds inside `result.json.metrics[]`, each with the shape `{metric_id, name, value, unit, interval_low, interval_high, method}` (per `analysis/schemas/result.schema.json`):
  - `coverage.<PERSON-ID>.<LAYER>` — integer count, `unit: "evidence_span_count"`.
  - `label_frequency.<coding_label>` — integer count, not per-person, `unit: "evidence_span_count"`.
  - `divergence.<case_id>` — **`value: null`**; the actual classification (`compatible`/`complementary`/`contradictory`) and the `evidence_ids` it's based on are embedded as free text inside the `method` string (e.g. `"classification=contradictory; evidence_ids=HB-J54-P2,RM-C050-P3; rationale: ..."`) — **not structured fields**. Flagged as a needed schema extension (`analysis/schemas/result.schema.json` should add `classification` and `evidence_ids` as typed fields on divergence-kind metrics) rather than having the UI parse this string.
- Data props for this slice: `metric_kind: "coverage"|"label_frequency"|"divergence"|"composite_score"`, `value: number|null`, `unit: string`, `population_n: number` (from `result.json.population.n`), `score_type: "default"|"user_custom"|"external_game"|"insufficient_data"` (**`insufficient_data` is a 4th value this slice needs that isn't in `product/data_to_ui_mapping.md`'s 3-value enum — flagged**).
- Default variant for this slice: `metric_kind: "coverage"` or `"label_frequency"`, `score_type: "insufficient_data"` — no `composite_score` variant is renderable yet; when clicked, "분해로 이동" leads to `ContributionBreakdown`'s explicit not-yet-available state, not a fabricated breakdown.
- States: default, loading, empty (no metric for this person/layer), **insufficient evidence (the default composite-score state for this slice, per above)**, partial, stale (`run_manifest.json.executed_at` older than a threshold — threshold TBD, not this track's call), error.
- Keyboard/name: card exposes its `metric_kind` and value in its accessible name, e.g. `"曹操, 정사 근거 수: 2건"`, never a bare number with no label.
- Responsive: same card component at all breakpoints; grid density changes only.
- Tests: never renders a `coverage` count of `0` the same way as a populated card (distinct empty-state per §7); `score_type` label is never omittable once `user_custom` is active (`design/DESIGN.md`§4).

## `ContributionBreakdown`

- Purpose per DESIGN.md: 점수 기여도/가중치, evidence까지 이동, 반올림 일관성.
- **Updated (D-031, Q-012 option (a), 2026-09-18): this component now has real backing data — the "what-if weight-lab."** No `default` composite score exists or is implied; this is exclusively a `score_type: "user_custom"` sandbox letting the user move independent 0–100% weights across `HISTORY_BASE`/`HISTORY_ANNOTATION`/`ROMANCE` and see how emphasis across one person's own coded labels shifts. Full formula, worked example (曹操, real data), and rationale for why labels are never summed into one number: `analysis/scoring_model.md`'s "What-if weight-lab formula" section — implement against that exactly, do not re-derive a different formula.
- **Real props for this slice** (client-computed from `GET /v1/people/{person_id}/evidence`, no backend/schema change needed):
  ```text
  contributions: { label, weighted_emphasis, raw_total, per_layer_counts: {HISTORY_BASE, HISTORY_ANNOTATION, ROMANCE}, evidence_ids: string[] }[]
  weights: { HISTORY_BASE, HISTORY_ANNOTATION, ROMANCE }   // 0..1 each, echoed back
  zero_coverage_layers: SourceLayer[]                       // layers with 0 total evidence for this person — drives the missing-data banner, see below
  score_type: "user_custom"
  ```
- States:
  - `default` — at least one layer has non-zero weight and non-zero evidence; render `contributions` sorted by `weighted_emphasis` descending, heading text must say something like "이 가중치에서 부각되는 서술" — never "능력치 순위" or any wording implying a capability ranking.
  - `zero_coverage_warning` (new, not a generic empty state) — the user has put non-zero weight on a layer listed in `zero_coverage_layers`: show an explicit banner naming that layer and person ("이 인물은 {layer}에 근거가 아예 없습니다 — 가중치를 올려도 반영될 근거가 없습니다"), distinct from `contributions` simply being an empty array for a different reason.
  - `empty` — every weight is 0 (user zeroed out all three sliders): show a neutral "가중치를 조절해 보세요" prompt, not an error.
  - `loading`, `error` — standard, per §7.
  - **Never renders a fabricated weight/contribution number** — every value must trace to a real `evidence_id`; this remains the hard test requirement.
- Interaction: three sliders (or equivalent controls) for the three layers, independent (not linked/normalized to sum to 100 — `analysis/scoring_model.md` explains why), each labeled with its `design/DESIGN.md`§3 layer name and paired with its layer color (never color-only). Changing a slider recomputes `contributions` client-side immediately (no network round-trip needed, per the Implementation note in `scoring_model.md`).
- Keyboard/accessible name: sliders are standard range inputs with visible current-value text (not color-only); each `contributions` row's evidence chips are focusable links to the underlying `EvidenceCard`, matching `AIAnswerPanel`'s existing evidence-chip pattern. The `zero_coverage_warning` banner is announced (e.g. `role="status"`), not silently rendered only visually.
- Tests: `weighted_emphasis` recomputation is verified against `analysis/scoring_model.md`'s worked 曹操 example (정사-only / 주석-only / 연의-only weight settings each produce exactly the label set documented there); never renders a fabricated weight/contribution number; `zero_coverage_warning` fires correctly when a zero-evidence layer is weighted up; heading/labels never use ranking or capability language.

## `QuestCard`

- Purpose: L-01/L-02 guided quest, completion gated on both-layer evidence + one counter-evidence acknowledgment (AC-5).
- Data props (client/product-level — `product/data_to_ui_mapping.md` itself notes "no backing schema needed yet"; this spec keeps that but ties tracking to real IDs): `quest_goal: string`, `completion_rule: {requires_layers: SourceLayer[], requires_counter_evidence: boolean}`, `evidence_seen_ids: string[]` (subset of real `evidence_id`s from `evidence_matrix.csv`), `counter_evidence_ids: string[]` (subset flagged by product as complicating evidence), `status: "locked"|"in_progress"|"gate_unmet"|"complete"`.
- States: default, loading, empty (no quest content for this event — n/a this slice), insufficient evidence (chosen claim too thin for a counter-evidence checkpoint → product substitutes a different claim per `user_journeys.md`), partial (`gate_unmet`, with the specific unmet gate named, not just "미완료"), stale (quest content changed since start), error.
- Keyboard: each required evidence item and the counter-evidence acknowledgment control are independently tab-reachable; "완료" button is present but `aria-disabled` (not removed from the DOM) until `completion_rule` is satisfied, with a live-region announcement of which gate remains.
- Accessible name: quest region has a name describing the goal; progress announced as "{n}/{required} 근거 확인, 반대 근거 {확인됨|미확인}".
- Responsive: single column always (quest is inherently sequential); evidence-seen list collapses to a counter+expandable list on mobile.
- Tests: `status` cannot become `"complete"` unless both `requires_layers` are all represented in `evidence_seen_ids` (matched by `source_layer`) and at least one `counter_evidence_ids` entry is in `evidence_seen_ids` — matches AC-5 exactly.

## `AIAnswerPanel`

- Purpose: mode-aware, evidence-linked AI answers per `agents/_three_kingdoms_domain.md` LLM 답변 모드.
- Data props: **pending reconciliation with the parallel L1 track's `analysis/llm_contract.md`/`analysis/schemas/interpretation.schema.json`** — not finalized here to avoid guessing ahead of that schema. Working shape assumed for this brief only: `answer_mode: "정사"|"연의"|"비교"|"게임"`, `claims: {text: string, evidence_id: string[]}[]`, `status: "answered"|"abstained"`, `abstain_reason: string | null`.
- States: default, loading, empty (no question yet), **insufficient evidence/LLM refused/abstained** (per-claim, not whole-answer, when only some claims lack support), partial (mixed answered/abstained claims), error/retryable (service unavailable, distinct from abstention).
- Keyboard/accessible name: each evidence chip is a separate focusable link to `EvidenceCard`; abstained claims are announced distinctly from answered ones (not just visually greyed out).
- Responsive: full-width panel, evidence chips wrap without truncating the claim text.
- Tests: **explicitly deferred** until L1 delivers the interpretation schema — flag to orchestrator to re-run this component's spec once that lands, per `handoffs/CURRENT_TASK.md`'s note that `data_to_ui_mapping.md`'s `AIAnswerPanel` row cites `analysis/llm_contract.md` as its source.

## Visualization rules (`design/DESIGN.md`§9, applied)

- Any chart of `network_edge_count.*` must show its denominator/scope text ("22개 근거 중, 실제 배우+대상 쌍이 있는 행만") since `analysis/network_analysis_plan.md` explicitly says 14/22 rows have no `subject_of_claim` and are excluded from this count — a bare edge-count number without that caveat overstates precision.
- No centrality metric (degree/betweenness/etc.) is rendered anywhere in this slice — `analysis/network_analysis_plan.md` explicitly declines to compute one at this N; there is no data prop for it because none should exist yet.
- `divergence.*` classifications render as a labeled badge (`compatible`/`complementary`/`contradictory`) plus its two linked `EvidenceCard`s — never as a numeric axis or chart.

## Reconciliation gaps (for the orchestrator to fold into `product/data_to_ui_mapping.md`)

1. `evidence_matrix.csv`'s real columns diverge from `data/schemas/evidence.schema.json`'s formal fields: `locator` is free text not a structured object; `person_refs` is a semicolon-joined string not a JSON array; `confidence` is `"high"|"medium"` not a 0–1 float; `excerpt_type`'s values don't match `evidence.schema.json`'s `translation_type` enum; the CSV has no `source_id`/`work_id`/`text_hash`/`edition_ref`/`permitted_excerpt` fields, using `edition`/`checksum_sha256_12`/`excerpt_zh` instead. Someone (D1/architect) needs to decide whether the CSV or the schema is authoritative before S3 builds an import path.
2. `analysis/outputs/result.json`'s `divergence.*` metrics store `classification` and `evidence_ids` as unstructured text inside `method` — recommend adding typed fields in `analysis/schemas/result.schema.json` before any UI parses that string.
3. No `score_value`/`model_version` exists anywhere in this slice's real output; `product/data_to_ui_mapping.md`'s `ScoreCard` row describing those fields doesn't correspond to anything yet. This spec's `ScoreCard`/`ContributionBreakdown` default to explicit not-yet-available states instead.
4. `HISTORY_ANNOTATION` coverage for the 5 coded persons (6/22) is not thin — `product/acceptance_criteria.md` AC-1's coverage-threshold hedge should be revisited with this number (still correctly cautious per-person, e.g. 諸葛亮 has 0 `HISTORY_ANNOTATION` rows).
5. `AIAnswerPanel`'s exact data contract depends on the parallel L1 track (`analysis/llm_contract.md`) — this spec's props are a placeholder pending that track's report.
