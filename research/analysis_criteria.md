# Evidence-Derived Analysis Criteria

Status: `DRAFT v0.1 — S1/R1, 적벽대전 (Battle of Red Cliffs) vertical slice`. Depends on `research/evidence_matrix.csv` and `research/coding_manual.md`. Every construct below must resolve to one or more `evidence_id` values; a metric with no evidence ID does not belong here.

## Coverage (read before using this file)

- Coded (original S1/R1 pass): `HISTORY_BASE` juan 01 (曹操), 32 (劉備), 35 (諸葛亮), 47 (孫權), 54 (周瑜); `HISTORY_ANNOTATION` embedded in the same juan, delimited by `〈...〉` brackets; `ROMANCE` 回49–50 only.
- **Updated (D-016 expansion pass, S3, 2026-09-18):** grew to 30 evidence spans / 10 persons — added 黃蓋/關羽/魯肅/趙雲/郭嘉.
- **Updated again (expansion pass 2, "더많은원문코딩", S3, 2026-09-18):** grew to 48 evidence spans, same 10 persons (no new persons forced in). Newly coded: `HISTORY_BASE`/`HISTORY_ANNOTATION` juan 55 (黃蓋/韓當/甘寧/魯肅/朱然 biographies, selectively — only rows involving the 10-person cast); `ROMANCE` 回51 (Nanjun/Jingzhou contest), 回53 (Guan Yu vs Huang Zhong at Changsha), 回54 (Zhuge Liang's Chibi-credit rebuttal to Lu Su), 回56–57 (Zhou Yu's death sequence). Juan 10/31/48/56 were reviewed but yielded no rows judged genuinely relevant (mostly unrelated courtiers' biographies with only incidental name mentions of the cast) — not padded with weak matches. Current total: 7 `HISTORY_BASE`, 12 `HISTORY_ANNOTATION`, 29 `ROMANCE` — 48 spans, 10 persons.
- **Not yet coded:** `ROMANCE` 回52 (partially, only 1 row previously coded), 回55, 58–61, and most of `HISTORY_BASE` juan 10/31/48/56 (reviewed, judged not relevant — see above) plus juan 55's remaining rows about persons outside the 10-person cast. If A1/P1 need claims from this uncoded material, it must be coded first, never inferred.

## Research question

역사·문학 텍스트(정사/주석/연의)의 행동·사건·관계 근거를 재현 가능하게 코딩했을 때, 적벽대전이라는 단일 사건에서 동일 인물에 대한 서술이 출처 층위(source layer)에 따라 어떻게 수렴/발산하는지, 그리고 그 발산을 설명 가능한 지표로 어떻게 표현할 수 있는가 (`PROJECT_BRIEF.md` §3 연구 질문의 이 슬라이스 한정 구체화).

## Construct-to-variable mapping

| Construct | Operational definition | Dataset field | Unit | Evidence IDs | Caveats |
| --- | --- | --- | --- | --- | --- |
| `decisiveness_under_pressure` | Presence of a coded span where the person holds a position against dissent or acts under acute threat | `coding_label` = `decisive_leadership_under_dissent` \| `appeal_to_past_favor`/`loyalty_override_duty` (threat proxy) | categorical (present/absent per person per layer) | HB-J47-P1 (孫權); RM-C050-P1/P2 (曹操, by proxy) | Not comparable across layers as one number — report per-layer, never averaged into a single score. |
| `credit_attribution_conflict` | Whether an event's credit is explicitly contested by a named rival in the text itself | `coding_label` = `rival_credit_denial` \| `source_conflict_note` \| `leadership_attribution_acknowledgment` | categorical | HB-J54-P2, HA-J54-P3, HA-J01-P2 | Describes *the historiographical record*, not the person's actual ability. |
| `strategic_originator_vs_authorizer` | Whether the person is coded as originating a tactic vs. authorizing/executing one proposed by a subordinate | `coding_label` = `subordinate_initiated_strategy`, `primary_actor` vs `subject_of_claim` | categorical | HB-J54-P1 (周瑜=authorizer, 黃蓋=originator) | Single data point in this slice — must not generalize to "Zhou Yu never originates strategy." |
| `romance_supernatural_embellishment_count` | Count of `supernatural_attribution` / `fatalistic_strategic_foresight` labels per person | `coding_label` in {`supernatural_attribution`,`fatalistic_strategic_foresight`} | count per person | RM-C049-P2, RM-C050-P4 (both 諸葛亮) | `ROMANCE`-only narrative-device count; never presented as a capability/magic score, and never placed on the same axis as `HISTORY_BASE` data. |
| `self_reflection_after_setback` | Whether the person's own quoted words show regret/acknowledgment of error following the battle | `coding_label` = `leadership_self_reflection_regret` vs `rival_credit_denial`/`strategic_self_awareness` | categorical, cross-layer pair | HB-J54-P2 (曹操, denies fault) vs RM-C050-P3 (曹操, admits fault) | Primary divergence case for this slice — see "Known conflicts" below. |
| `historical_narrative_weight` | Number of coded spans in `HISTORY_BASE`+`HISTORY_ANNOTATION` vs. in `ROMANCE`, per person | count of rows grouped by `person_refs` and `source_layer` | count | all 48 rows (originally 22; see §Coverage) | Coverage/emphasis fact only, not a validated claim that history "ignores" any given person — reflects this sample's coding choices so far. |

## Population and exclusions

- Target population (this slice, updated through expansion pass 2): 10 named persons — 曹操/劉備/諸葛亮/孫權/周瑜 (original 5) plus 黃蓋/關羽/魯肅/趙雲/郭嘉 (D-016) — as depicted in the 적벽대전 episode across `HISTORY_BASE`, `HISTORY_ANNOTATION`, and `ROMANCE`, per the juan/回 ranges in §Coverage.
- Inclusion: any evidence span in `research/evidence_matrix.csv` naming one of the 10 as `primary_actor` or `subject_of_claim`.
- Exclusion: supporting figures outside the 10-person cast (韓當, 甘寧, 朱然, 蔡和, 陳應, etc.) are recorded when a span directly involves a cast member, but are not themselves scored in this slice.
- Generalization boundary: findings apply only to this battle/this coded excerpt set. No claim here generalizes to any person's whole biography, to other battles, or to persons/material outside the 10-person cast and coded juan/回 ranges.

## Primary analysis

- Primary outcome (this slice): the qualitative source-layer divergence classification defined below (compatible / complementary / contradictory), not a numeric score.
- Exposure/predictors: `source_layer`, `person_refs`, `coding_label`.
- Confounders/covariates: not applicable — this is a descriptive coding pass, not a causal or predictive model. `analysis/analysis_plan.md` (A1) decides whether any inferential method applies, and must justify it against this evidence, not the reverse.
- Method justified by evidence: qualitative comparison per evidence row; any quantitative aggregation is A1's proposal to make and justify, not assumed here.
- Effect/uncertainty to report: coding `confidence` (high/medium) and `ambiguity_note` per row; single-coder status (no inter-coder reliability yet, see `research/coding_manual.md`).

### Source-layer divergence procedure

1. Identify evidence rows sharing the same `person_refs` and the same rough moment (e.g., "immediately after the Red Cliffs defeat").
2. List the `coding_label`s applied in each layer.
3. Classify as **compatible** (same underlying claim, different detail), **complementary** (different aspects, no conflict), or **contradictory** (opposite characterization).
4. Do not compute a numeric "divergence score" in S1 — `analysis/scoring_model.md` may propose one in A1, but it must cite this qualitative classification as its input.

**Worked example (ready for A1):** 曹操 self-reflection after Red Cliffs — `HISTORY_BASE` (HB-J54-P2) denies fault and withholds credit from 周瑜; `ROMANCE` (RM-C050-P3) has him admit fault and blame 郭嘉's death. Classification: **contradictory** — same person, opposite self-presentation, near the same event, across two source layers. This is the strongest single divergence case in this slice.

## Secondary and exploratory analyses

- `strategic_originator_vs_authorizer` and `romance_supernatural_embellishment_count` are exploratory descriptive counts only (N too small for any inferential claim); useful as candidate ScoreCard/EvidenceCard content for P1, not as validated research findings.

## Known conflicts in the literature

| Topic | Evidence for A | Evidence for B | Planned treatment |
| --- | --- | --- | --- |
| Event order: did Sun Quan attack Hefei before or after Red Cliffs? | HA-J01-P1's underlying source (山陽公載記, per the annotation) implies Hefei-first | HA-J01-P2: 孫盛 explicitly rules 吳志 (Wu Annals' order: Red-Cliffs-first) as correct | Present both explicitly in any user-facing comparison; do not silently pick one. `research/source_policy.md`'s conflict-handling rule applies. |
| Was 江表傳's account of Liu Bei's decisive role reliable? | HB-J32-P1 (main biography, unqualified) | HA-J32-P1: 孫盛 flags 江表傳 as likely Wu-partisan self-flattery | Surface the bias flag alongside the claim; never present HB-J32-P1 without the adjacent annotation's caveat in any UI reusing this evidence. |
| Who first originated the plan to resist Cao Cao — Zhou Yu (as the base biography implies) or Lu Su (as an annotator explicitly claims)? | HB-J47-P1 (孫權 main biography): credits 瑜/肅 jointly, no origination order stated | HA-J54-P4 (裴松之注 on 周瑜's biography): explicitly states the plan "實始魯肅" (actually originated with Lu Su first) and flags that 周瑜's own main-biography account omits this; HA-J54-P5 (孫盛) independently reinforces Lu Su's originating role from a separate citation | Present both; this is a genuine historiographical credit dispute, not a coverage gap — `analysis/pipelines/compute_chibi_result.py`'s `divergence.lusu_origination_credit` case (classification: contradictory), added post-D-016 expansion. |
| Was Huang Gai's feigned-surrender deception a quiet written ruse, or did it involve a dramatized public execution? | HA-J54-P1 (江表傳, Huang Gai's actual letter): a written deception only, no violence described | RM-C049-P6 (ROMANCE): Zhou Yu stages a mock execution of a spy to make the deception credible | Both layers agree on the underlying tactic and actors; ROMANCE adds a dramatized theatrical element with no denial in the annotation account — `divergence.huanggai_feigned_surrender` (classification: complementary, an elaboration not a contradiction), added post-D-016 expansion. |
| How was Huang Gai actually wounded during the fire attack? | HA-J55-P1 (吳書, quoted in 黃蓋's own biography): hit by a stray arrow amid the chaos, falls into cold water, nearly left for dead until recognized by voice | RM-C049-P8 (ROMANCE): shot in the shoulder specifically while charging his fire ship, shouting his own name | Both agree he was wounded by an arrow and fell into the water; ROMANCE stages a heroic self-announced charge where the annotation describes an anonymous near-fatal accident — `divergence.huanggai_wound` (classification: complementary), added in expansion pass 2 (2026-09-18). **Note:** this closed a gap the original coding pass had flagged as "entirely absent from HISTORY_BASE/HISTORY_ANNOTATION" — juan 55 simply hadn't been coded yet at that point. |
| Who did Zhou Yu recommend as his successor on his deathbed? | HA-J54-P6 (江表傳, Zhou Yu's own letter): explicitly names 魯肅 | RM-C057-P3 (ROMANCE, Sun Quan reading the same letter): confirms Lu Su (子敬) was recommended and is appointed | Both layers agree on the same specific claim with no meaningful conflict — `divergence.zhouyu_lusu_succession` (classification: **compatible**, the strongest same-claim agreement case in this slice), added in expansion pass 2 (2026-09-18). |

### Checked, no comparable cross-layer pair found (not forced into a classification)

As of expansion pass 2 (48 rows, 2026-09-18), 2 of the 10 persons still have no cross-layer comparison possible — this is an honest coverage gap, not "no divergence found":

- **趙雲 (Zhao Yun):** all 3 of his coded rows are `ROMANCE` (RM-C049-P4, RM-C049-P7, RM-C052-P1) — zero `HISTORY_BASE`/`HISTORY_ANNOTATION` rows. His own historical biography (卷36, 蜀書六) was never among the D0/D1-ingested juan at all, so no history-layer comparison is possible from any currently-ingested material, not just currently-coded material — this is a raw-ingestion gap, not a finding that history "omits" him.
- **郭嘉 (Guo Jia):** only 1 coded row total (RM-C050-P3, `ROMANCE`) — no second layer to compare against.

**關羽 (Guan Yu)** was re-checked in expansion pass 2 and still has no qualifying pair: his substantive appearances (RM-C050-P1, RM-C050-P2, RM-C049-P5 — the Huarong Road release episode) are ROMANCE-only, and no `HISTORY_BASE`/`HISTORY_ANNOTATION` row in this set describes that episode (consistent with mainstream scholarship treating Huarong Road as a novelistic invention absent from 正史). HA-J35-P2 (裴松之 comparing 關羽's loyalty to 諸葛亮's) remains thematically adjacent but describes a different claim at a different moment, not the same event — still not treated as a divergence pair.

## Forbidden interpretations

- Do not infer causality from any single narrative account (e.g., "the fire attack caused Cao Cao's later strategic caution") without independent corroboration outside this slice.
- Do not extrapolate any finding beyond 적벽대전/the coded juan-回 ranges in §Coverage/these 10 persons.
- Domain-specific constraints (from `agents/_three_kingdoms_domain.md`): no merging `HISTORY_BASE`/`HISTORY_ANNOTATION`/`ROMANCE` into one fact table; no frequency-as-ability inference; no clinical diagnosis of a historical figure from narrative text (e.g., 周瑜's `psychosomatic_strategic_anxiety` label in `ROMANCE` is a narrative-device tag, not a medical claim); missing evidence is never scored as 0; no numeric "who is the best leader" ranking or composite cross-layer score from this slice's data.
