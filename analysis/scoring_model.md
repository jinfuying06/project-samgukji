# Explainable Game Score Model

## Position

점수는 연구 결론이나 인물의 본질적 가치가 아니라 **버전이 있는 분석·놀이 모델**입니다.

## Pipeline

```text
evidence span
→ adjudicated code
→ code contribution
→ opportunity/coverage adjustment
→ subscore
→ versioned weight
→ display score + confidence + explanation
```

## Required fields per score

- `score_id`, `model_version`, `person_id`, `source_mode`
- included event/time scope
- subscore values and weights
- contribution rows with code/evidence IDs
- coverage: reviewed sources/spans and known gaps
- confidence and sensitivity range
- normalization cohort
- generated timestamp/run ID

## Missingness

- no evidence = unknown, not zero
- insufficient coverage can suppress a score
- the UI must distinguish `0`, `unknown`, and `not applicable`

## Weighting

- Default weights require research/evaluator approval.
- User weights create a `custom_score`, never overwrite the default.
- Weight changes must show which components and ranks changed.
- Score/rank stability must be tested across reasonable weights.

## Comparison modes

- `history_base_score`
- `history_annotation_score`
- `romance_score`
- `custom_score`
- `external_game_score` (only if rights permit)

Cross-mode “gap” is shown as a difference between models, not proof that one source is false.

## 적벽대전 vertical-slice application (S1/A1, 2026-09-17)

`analysis/outputs/result.json` (run `run-20260917T122003Z`) deliberately stops **before** the last two pipeline stages (subscore → versioned weight → display score) for this slice:

- N=22 evidence spans across 5 persons and 3 layers is too small to fit or justify default weights — there is no research/evaluator-approved weighting yet, and the `weighting` rule above requires one before any `display score` exists.
- What the slice *does* produce, per person × source layer: an evidence-span **coverage count** (`coverage.*` metrics) and a **coding-label frequency** tally (`label_frequency.*` metrics). These are candidate inputs to a future subscore, not scores themselves — a `coverage` value of `0` means "no coded span in this layer for this person in this slice," never a `0` ability rating (see "Missingness" above).
- Three pre-registered **source-layer divergence classifications** (`divergence.*` metrics, `compatible`/`complementary`/`contradictory`) exist for specific person/claim pairs (see `analysis/analysis_plan.md` §5). These are qualitative comparisons, not a numeric "divergence score," and must not be averaged into one.
- No `history_base_score`, `history_annotation_score`, `romance_score`, or `custom_score` exists yet for this slice. P1's `ScoreCard`/`EvidenceCard`/`ContributionBreakdown` components should render the coverage counts, label list, and divergence classifications directly — not a synthesized score — until a real weighting model is proposed and approved (S2 or later).
- No cross-person ranking ("who is the strongest leader at Red Cliffs") is supported by this data and none should be built from it.

## What-if weight-lab formula (Q-012 option (a), D-031, 2026-09-18)

Human owner's explicit request: let a user move weights between 정사/정사주석/연의 and see, for one person, how the *emphasis* on their coded evidence shifts — without producing a composite ability score or a cross-person ranking (both remain forbidden above). This is a `score_type: user_custom` sandbox only; it never populates a `default` score, and no default weighting model exists or is implied by this formula.

### Inputs

- A person `person_id` already selected in the UI.
- All of that person's evidence rows from `research/evidence_matrix.csv` (already returned in full — every `source_layer`, every `coding_label` — by the existing `GET /v1/people/{person_id}/evidence` call with no `source_layer` filter; **no backend or schema change is required**, see "Implementation note" below).
- Three independent user-set weights, one per layer: `w_HISTORY_BASE`, `w_HISTORY_ANNOTATION`, `w_ROMANCE`, each a slider in `[0.0, 1.0]`. **These are independent, not required to sum to 1.** This is a deliberate choice: the tool is not estimating a single calibrated probability distribution over "which source is more true" — it is letting the user ask "what does this person look like if I weight 정사 at 100% and 연의 at 0%?" as one query and "what if I weight both at 100%?" as another, equally legitimate query. Forcing normalization would misleadingly imply the weights are a rigorous belief distribution, which they are not.

### Formula

For every distinct `coding_label` that appears at least once among the person's evidence rows:

```text
raw_count(label, layer)      = number of this person's evidence rows with this coding_label AND this source_layer
weighted_emphasis(label)     = Σ_layer  raw_count(label, layer) × w_layer
raw_total(label)             = Σ_layer  raw_count(label, layer)          (unweighted, for reference/rounding-check)
```

Output one `ContributionBreakdown` row per label:

```text
{ label, weighted_emphasis (rounded to 1 decimal for display, full precision retained internally),
  raw_total, per_layer_counts: { HISTORY_BASE, HISTORY_ANNOTATION, ROMANCE }, evidence_ids: [...] }
```

Rows are sorted by `weighted_emphasis` descending for display, but **this ordering is not a "top trait" ranking of the person** — it only reflects which of *this person's own coded behaviors* are emphasized more under the *user's own chosen weights*, and must be labeled as such (e.g. heading: "이 가중치에서 부각되는 서술" not "능력치 순위").

**Forbidden next step, stated explicitly so no future pass adds it:** do not sum `weighted_emphasis` across labels into one number. `military_setback_attribution` (a retreat's stated cause) and `peer_praise` (an unrelated compliment) are not commensurable quantities — adding them produces a number with no interpretable unit. This is the same reasoning `analysis/network_analysis_plan.md` already used to withhold centrality metrics at this N; it applies with equal force here to combining heterogeneous labels.

### Missingness (per `agents/_three_kingdoms_domain.md` — missing evidence is never scored as 0)

Two distinct kinds of "zero" must never be shown identically:

1. **Label-level zero** (a label this person does have in some layer simply doesn't appear in another layer): this is expected and informative — most labels are naturally sparse per layer. Render normally as `raw_total(label) > 0` with a `per_layer_counts` breakdown showing `0` for the absent layer(s) — this is a real, correctly-computed zero contribution *for that label*, not a missing-data placeholder.
2. **Layer-level zero** (this person has *no* evidence at all in an entire layer — e.g. 趙雲 has zero `HISTORY_BASE`/`HISTORY_ANNOTATION` rows in this slice): before rendering any breakdown, check per layer whether the person's total evidence count in that layer is 0. If the user has set a non-zero weight on a layer where this person has *no* evidence at all, the UI must show an explicit banner ("이 인물은 정사 층위에 근거가 아예 없습니다 — 가중치를 올려도 반영될 근거가 없습니다"), not just silently render an all-zero breakdown that looks like "this layer found nothing about this person's character." This is the same person-level coverage gap already documented in `research/analysis_criteria.md`'s "Checked, no comparable cross-layer pair found" section — reuse that framing, don't re-derive it.

### Worked example — 曹操 (real data, `research/evidence_matrix.csv`, 2026-09-18, reproducible via the snippet below)

曹操 has 10 coded evidence rows in this slice, split 2 `HISTORY_BASE` / 3 `HISTORY_ANNOTATION` / 5 `ROMANCE`, across 10 distinct labels (each label happens to appear in exactly one layer for this person in the current 48-row set):

| Setting | Labels emphasized (weighted_emphasis > 0) |
| --- | --- |
| 정사 100% / 주석 0% / 연의 0% | `military_setback_attribution` (1.0, HB-J01-P1), `rival_credit_denial` (1.0, HB-J54-P2) — nothing else |
| 정사 0% / 주석 100% / 연의 0% | `peer_praise` (1.0, HA-J35-P2), `source_conflict_note` (1.0, HA-J01-P2), `strategic_self_awareness` (1.0, HA-J01-P1) — nothing else |
| 정사 0% / 주석 0% / 연의 100% | `appeal_to_past_favor` (1.0), `fatalistic_strategic_foresight` (1.0), `leadership_self_reflection_regret` (1.0), `loyalty_override_duty` (1.0), `strategic_manipulation_of_subordinate` (1.0) — nothing else |

This is exactly the lesson the human owner asked for: **the same person, three completely different sets of emphasized behavior, purely as a function of which source layer the user chooses to weight** — 정사 alone shows only setback-attribution and credit-denial; 연의 alone shows five entirely different behaviors including self-reflection and loyalty appeals that 정사/주석 never mention for him at all in this coded set. No number was invented to produce this table — reproduce with:

```python
import csv
from collections import defaultdict
rows = list(csv.DictReader(open("research/evidence_matrix.csv", encoding="utf-8-sig")))
counts = defaultdict(lambda: defaultdict(list))
for r in rows:
    if "PERSON-CAOCAO" in [x.strip() for x in r["person_refs"].split(";")]:
        counts[r["coding_label"]][r["source_layer"]].append(r["evidence_id"])
```

### ContributionBreakdown props for this feature (ties to `design/component_spec.md`)

```text
contributions: {
  label: string,                 // coding_label, e.g. "military_setback_attribution"
  weighted_emphasis: number,      // rounded to 1 decimal for display
  raw_total: number,              // unweighted count across all layers, integer
  per_layer_counts: { HISTORY_BASE: number, HISTORY_ANNOTATION: number, ROMANCE: number },
  evidence_ids: string[],
}[]
weights: { HISTORY_BASE: number, HISTORY_ANNOTATION: number, ROMANCE: number }   // currently-applied weights, 0..1 each, echoed back so the UI never has to guess what produced the breakdown
zero_coverage_layers: SourceLayer[]   // layers where this person has 0 total evidence rows at all — drives the missing-data banner above
score_type: "user_custom"           // matches design/DESIGN.md§4 — never "default"
```

### Implementation note (no backend change needed)

`GET /v1/people/{person_id}/evidence` (no `source_layer` query param) already returns every evidence row for a person with both `coding_label` and `source_layer` populated (`app/architecture/api_contract.yaml`'s `EvidenceSpan`). The weight-lab computation above is pure client-side aggregation over an already-fetched response — no new endpoint, schema, or backend logic is required. If a future pass wants this computed server-side (e.g. to share a permalink of one weighting), that would need a new endpoint, but nothing in this slice's scope requires it yet.

