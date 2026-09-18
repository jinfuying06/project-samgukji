# Statistical Analysis Plan

Status: `FROZEN v1 — S1/A1, 적벽대전 (Battle of Red Cliffs) vertical slice`
Version: `1.0`
Frozen at: `2026-09-17T12:00:00Z` (before `analysis/pipelines/compute_chibi_result.py` was executed)
Approved by: `[TBD — B1 human approval pending]`

Scope note: this plan covers only the S1 vertical slice defined in `handoffs/CURRENT_TASK.md` and `research/analysis_criteria.md`. **Originally frozen at 22 coded evidence spans / 5 persons** (see §8 Deviations — this scope grew to 30 spans/10 persons during the D-016 expansion pass, and `analysis/pipelines/compute_chibi_result.py` was re-run, not hand-edited). It is not a general-purpose analysis plan for the full corpus.

## 1. Objective

- Research question: 역사·문학 텍스트(정사/주석/연의)의 행동·사건·관계 근거를 재현 가능하게 코딩했을 때, 적벽대전이라는 단일 사건에서 동일 인물에 대한 서술이 출처 층위(source layer)에 따라 어떻게 수렴/발산하는지, 그리고 그 발산을 설명 가능한 지표로 어떻게 표현할 수 있는가 (`research/analysis_criteria.md` §Research question, this slice only).
- Decision supported: whether the Hybrid product concept's "source-layer comparison" core loop is demonstrable end-to-end (evidence → code → structured JSON → user-facing comparison) on one small, real event, per `PROJECT_BRIEF.md`'s first-vertical-slice definition. Not a decision about any person's historical merit.
- Target population: **updated per DEV-001 (§8)** — the 10 named persons 曹操/劉備/諸葛亮/孫權/周瑜/黃蓋/關羽/魯肅/趙雲/郭嘉 as depicted in `research/evidence_matrix.csv`'s 30 rows (originally 5 persons/22 rows at freeze time; `research/analysis_criteria.md` §Population and exclusions).

## 2. Outcomes and predictors

| Role | Variable | Definition | Unit | Timing | Evidence IDs |
| --- | --- | --- | --- | --- | --- |
| Primary outcome | Source-layer divergence classification | Per pre-registered person/claim pair (see §5), one of `compatible`/`complementary`/`contradictory` | categorical | computed once, this run | see §5 case list |
| Secondary outcome | `historical_narrative_weight` | Count of coded evidence rows per person × source_layer | count | computed once, this run | all 30 rows (per DEV-001; originally 22) |
| Secondary outcome | `coding_label` frequency | Count of rows per coding_label | count | computed once, this run | all 30 rows (per DEV-001; originally 22) |
| Secondary outcome | Person-to-person network edges | Count of rows with a real (non-commentator) primary_actor and subject_of_claim, per source_layer | count | computed once, this run | rows with non-empty subject_of_claim |
| Primary predictor | `source_layer` | HISTORY_BASE / HISTORY_ANNOTATION / ROMANCE | categorical | fixed at coding time | all rows |

## 3. Cohort

- Inclusion: every row in `research/evidence_matrix.csv` (30 rows as of DEV-001; originally 22 rows frozen at coding time by R1).
- Exclusion: none — this is a census of the coded set, not a sample drawn from it. Persons outside the (now 10-person) cast (孫盛 as commentator, cited works, and other supporting figures like 陳應) are recorded as supporting actors/edges where they appear but are never given a person-level coverage count.
- Expected sample size: N=30 evidence rows (was N=22 before DEV-001); this is fixed and known in advance, not estimated.
- Power/precision rationale: not applicable. This is a descriptive/qualitative pass over a small, purpose-built coded set, not a hypothesis test with a target power. No inferential claim (p-value, confidence interval on a population parameter) is made anywhere in this plan or its output.

## 4. Data handling

- Missing data: a person with 0 coded rows in a given layer is recorded as `0` under a `coverage.*` metric explicitly labeled "evidence-span coverage count," not as a capability/ability score of zero (`agents/_three_kingdoms_domain.md` — missing evidence is never scored as 0 as an ability judgment). The distinction between "no coded span" and "no ability" must be preserved wherever this number is displayed.
- Outliers: not applicable — no continuous numeric distribution is being summarized.
- Duplicates: `evidence_id` uniqueness was already checked by D1 across the full 1,148-paragraph candidate pool (`data/quality_report.json`); the curated subset (30 rows per DEV-001; originally 22) inherits that guarantee and is re-checked implicitly by treating `evidence_id` as the CSV's de facto primary key.
- Transformations: none. Counts are raw tallies from `evidence_matrix.csv` columns (`person_refs`, `source_layer`, `coding_label`, `primary_actor`, `subject_of_claim`).
- Leakage prevention: not applicable (no train/test split; this is a descriptive aggregation, not a predictive model).

## 5. Methods

- Descriptive statistics: coverage counts (person × source_layer), coding_label frequency counts, network edge counts (per source_layer and total). All computed by `analysis/pipelines/compute_chibi_result.py`.
- Primary "model": a pre-registered qualitative classification procedure (`research/analysis_criteria.md` §Source-layer divergence procedure), applied to exactly 3 person/claim pairs identified from the evidence set **before running the script**, because they describe the same person's claim/behavior at a comparable moment in two different source layers (as opposed to one layer being silent, which is a coverage fact, not a divergence classification):
  1. `divergence.caocao_selfreflection` — HB-J54-P2 vs RM-C050-P3 (曹操's self-reflection after defeat)
  2. `divergence.liubei_role_reliability` — HB-J32-P1 vs HA-J32-P1 (reliability of 劉備's decisive-role account)
  3. `divergence.fireattack_originator` — HB-J54-P1 vs RM-C049-P2 (who originated the fire-attack idea)
- Assumptions and diagnostics: none of the standard statistical-model assumptions (normality, independence of residuals, etc.) apply — there is no regression/inferential model here. The only "assumption" made explicit is the exclusion rule in §Cohort (claim-vs-silence pairs are not forced into a compatible/complementary/contradictory label).
- Effect size and uncertainty: not applicable in the classical sense (no population parameter is being estimated). Each divergence classification instead carries a written rationale citing the specific `evidence_id`s compared, so a reader can audit the classification directly rather than trust a summary number.
- Multiple comparisons: not applicable (3 pre-registered qualitative classifications, not a battery of significance tests).
- Sensitivity analyses: not applicable at N=30 (per DEV-001; was N=22) with no numeric composite score computed. If a future pass adds a composite/weighted score (`analysis/scoring_model.md`), that pass must add weight-sensitivity and rank-stability analysis before display, per `agents/statistician.md`.

## 6. Exploratory analyses

- `label_frequency.*` (coding_label counts) and `network_edge_count.*` are exploratory descriptive counts, clearly separated in `analysis/outputs/result.json` from the 3 pre-registered divergence classifications. They are candidate content for P1's ScoreCard/EvidenceCard/ContributionBreakdown components, not validated research findings, and must not be presented to users as ranked or weighted scores.

## 7. Reproducibility

- Pipeline command: `python analysis/pipelines/compute_chibi_result.py` (run from the repository root; reads only `research/evidence_matrix.csv`, writes `analysis/outputs/result.json` and `analysis/outputs/run_manifest.json`).
- Environment lock file: none required — the script uses only the Python 3 standard library (`csv`, `json`, `hashlib`, `datetime`, `pathlib`).
- Random seed: not applicable (no randomness in this script).
- Input version/hash: recorded per run in `analysis/outputs/run_manifest.json` (`input_files[0].sha256` for `research/evidence_matrix.csv`).

## 8. Deviations

| ID | Time | Change | Before/after seeing outcomes? | Reason | Impact | Approver |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | 2026-09-17 (S3, parallel with E0) | Cohort grew from 22→30 evidence rows, 5→10 persons (added 黃蓋/關羽/魯肅/趙雲/郭嘉 — 5 new persons using D1's existing candidate pool), 2 new coding labels (`alliance_persuasion`, `combat_skill_display`) | After — the original 3 pre-registered divergence classifications in §5 were already computed on the 22-row set before this expansion; the expansion did not revisit or add new divergence pairs, only new coverage/label_frequency/network_edge rows | Human project owner's explicit D-016 request, executed once B1's pipeline-validation purpose for the original 5-person slice was satisfied | §2's `historical_narrative_weight`, `coding_label` frequency, and network-edge counts (all recomputed by re-running `analysis/pipelines/compute_chibi_result.py` against the expanded CSV — 60 metrics now, up from 43). §5's 3 pre-registered divergence classifications are unchanged (still exactly the same 3 person/claim pairs, same evidence_ids, same classifications) — the expansion added coverage breadth, not new divergence findings, so no pre-registration integrity issue arises. §3 Cohort/§1 Target population text above updated to reflect 10 persons. | Human project owner (D-016 request) |

Any change to §2–§5 after `analysis/outputs/result.json` has been generated must be logged here with a before/after-seeing-outcomes flag, per `agents/_common.md` and `agents/statistician.md`'s prohibition on changing analysis after seeing results.

