# Coding Manual — 관도대전 (Battle of Guandu)

Status: `DRAFT v0.1 — single-coder pass (R1-equivalent), 2026-09-19`

Scope: second event in the per-battle expansion (`handoffs/DECISIONS.md#D-036`), following the same non-destructive extraction method and coding discipline already validated for 적벽대전 (`research/coding_manual.md`). Covers `HISTORY_BASE` (陳壽《三國志》, juan 01/06/10/14/17), `HISTORY_ANNOTATION` (裴松之注, same `〈...〉` bracket convention), and `ROMANCE` (羅貫中《三國演義》, 回22/25/26/30 coded so far — 回9/32 extracted into the candidate pool but not yet coded). This is a first pass sized similarly to 적벽대전's original B1 validation slice (9 persons / 25 evidence spans), not an exhaustive coding of the full extracted candidate pool (`${TKAF_PRIVATE_DATA_ROOT}/analysis/tables/guandu_evidence_candidates.jsonl`, 866 paragraphs; 205 keyword-matched) — juan 09 (largely 夏侯淵's unrelated later campaigns) and most of juan 06's non-沮授/田豐 material remain uncoded, deliberately, rather than padded to hit a number.

## Non-negotiable rules

Same as `research/coding_manual.md`'s "Non-negotiable rules" section (`HISTORY_BASE`/`HISTORY_ANNOTATION`/`ROMANCE` never merged; frequency is not a capability score; missing evidence is recorded as missing, never 0; no clinical/psychological diagnosis from narrative text). Not restated here — read that section, it applies verbatim to this event too.

## Reused labels (from `research/coding_manual.md`, no redefinition needed)

`joint_military_command`, `decisive_leadership_under_dissent`, `subordinate_initiated_strategy`, `source_conflict_note`, `strategic_self_awareness`, `loyalty_override_duty`, `combat_skill_display` all recur in this event's coded rows with the exact same definitions as the 적벽대전 manual. See that file for their definitions; not copied here to avoid drift between two copies of the same rule.

## New labels (this event)

| Label | Definition | Include example | Exclude example |
| --- | --- | --- | --- |
| `rival_character_assessment` | A party is quoted directly assessing a named rival's personal/leadership character (not merely their troop strength or logistics) as the stated basis for a military decision or for predicting an outcome | 曹操 on 袁紹: "志大而智小，色厲而膽薄" (HB-J01-P1); 荀彧 on 袁紹's staff (HB-J10-P1) | A passage assessing only troop numbers, terrain, or supplies with no character commentary (that's a plain `observation`, no label needed, or code `military_setback_attribution` if it explains a specific defeat) |
| `strategic_defection` | A named party abandons their side and joins the opponent, with a documented grievance, fear, or opportunistic motive stated as the cause -- and the defection materially affects the campaign's outcome | 許攸 defecting after 袁紹 would not meet his financial demands (HB-J01-P4); 張郃 defecting after being falsely blamed for the defeat (HB-J17-P2) | A routine battlefield surrender with no stated personal grievance/motive (that's a plain `observation`); a party switching sides between wholly separate campaigns years apart with no causal link to a specific setback |
| `punished_for_correct_dissent` | A named advisor is imprisoned, killed, or otherwise punished specifically because their earlier-rejected advice is later proven correct by events -- not for a new, separate offense | 袁紹 executing 田豐 explicitly because his rejected advice was vindicated by the defeat (HB-J06-P5: "吾不用田豐言，果爲所笑") | An advisor who is simply overruled with no later punishment (code `decisive_leadership_under_dissent` instead); an advisor punished for an unrelated act of disloyalty |

## Actor/target and polarity

- Same `primary_actor`/`subject_of_claim` convention as `research/coding_manual.md`.
- Scored cast for this event (9 persons, real text confirms all): 曹操/袁紹/荀彧/郭嘉/許攸/張郃/沮授/田豐/關羽. 曹操/郭嘉/關羽 are **shared `person_id`s with the 적벽대전 cast** (`data/pipelines/build_guandu_sample.py`'s `CANONICAL_PERSONS`) -- a new event does not fork an existing real person's identity. Supporting figures recorded in `person_refs` when directly relevant to a scored person's row but not themselves scored: 審配, 郭圖, 逢紀, 顏良, 文醜, 淳于瓊, 張遼, 劉備.

## Ambiguity handling

- `strategic_defection` (許攸): two different HISTORY_BASE passages give two different proximate causes for the same defection -- HB-J01-P4 (武帝紀: 袁紹's stinginess) vs HB-J10-P2/HB-J01-P4's own note (荀彧傳, confirmed by HB-J10-P2: 審配 arresting 許攸's family). Neither passage is itself an annotation flagging the other as wrong, so this is recorded via `ambiguity_note` on both rows rather than coded `source_conflict_note` (reserved for cases an annotation explicitly flags, per the reused label's own definition).
- `strategic_defection` (張郃): by contrast, this one *is* explicitly flagged by 裴松之 as a real discrepancy between 武帝紀/袁紹傳's account and 張郃's own biography -- coded as `source_conflict_note` at HA-J17-P1, citing both HB-J01-P5 and HB-J17-P2.
- `punished_for_correct_dissent` (RM-C030-P2, 沮授): ROMANCE has 袁紹 imprison 沮授 alongside 田豐 before the battle starts. The HISTORY_BASE record (HB-J06-P4) only has 沮授 losing part of his command (reassigned to 郭圖) before the battle, not imprisoned -- he is captured only later, during the retreat, and killed afterward for trying to return to 袁紹. This is a genuine `contradictory`-type divergence (ROMANCE escalates a real event into a stronger, undocumented claim), not just a coverage gap -- flagged in both rows' `ambiguity_note`.

## Coverage note (honest, not padded)

25 evidence rows: 15 `HISTORY_BASE`, 4 `HISTORY_ANNOTATION`, 6 `ROMANCE`. `HISTORY_ANNOTATION` coverage is thinner proportionally than 적벽대전's (which had a dedicated annotation-heavy juan); most of this event's richest annotation material (裴松之's extensive quotes from 獻帝傳/魏書/曹瞞傳 in juan 01/06) describes context *around* the battle (Cao Cao's self-justifications, biographical background) rather than the battle's own decision points, so fewer of those paragraphs met the bar for a scored row. Not a data gap -- the extracted candidate pool (`guandu_evidence_candidates.jsonl`) has 364 `HISTORY_ANNOTATION` paragraphs available if a future pass wants to code more of it.

## Inter-coder reliability — not yet run

Unlike 적벽대전 (`research/intercoder_reliability.md`), no second independent coding pass has been done for this event yet. `coding_validation_status` for every row in this matrix should be treated as `llm_llm_validated_only`-equivalent-but-not-even-that -- it is a **single uncorroborated coding pass**, one step earlier in the validation pipeline than 적벽대전's original 22-row B1 state. This must not be silently upgraded to look equivalent to 적벽대전's current (post-D-024 human-reviewed) status anywhere downstream.
