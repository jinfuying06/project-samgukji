# Coding Manual — 적벽대전 (Battle of Red Cliffs) Vertical Slice

Status: `DRAFT v0.2 — single-coder pass, S1/R1 + S3-parallel expansion pass (D-016), 2026-09-17`

Scope: this manual covers only the B0-approved first vertical slice (적벽대전), across `HISTORY_BASE` (陳壽《三國志》, juan 01/32/35/47/54), `HISTORY_ANNOTATION` (裴松之注 embedded inline in the same juan, delimited in this crawl by `〈...〉` brackets — see note below), and `ROMANCE` (羅貫中《三國演義》, 回49–52 coded so far; additional 回53–57 material remains available in D1's candidate pool but is not yet coded — see `research/analysis_criteria.md` §Coverage). It is not a general-purpose Three Kingdoms codebook. Cast expanded from 5 to 10 persons in the D-016 expansion pass (added: 黃蓋, 關羽, 魯肅, 趙雲, 郭嘉 — all were already present in the corpus and, in most cases, already referenced as supporting figures in the original 22 rows; the expansion pass promoted them to scored cast members and added targeted new evidence for them).

## Non-negotiable rules (from `agents/_three_kingdoms_domain.md`, restated for this manual)

- `HISTORY_BASE`, `HISTORY_ANNOTATION`, and `ROMANCE` are never merged into one fact table. A label applied to a `ROMANCE` passage never becomes a `HISTORY_BASE` claim about the same person.
- Frequency alone never becomes a capability score. A person with 1 evidence span is not "weaker" than one with 6 — coverage differences are documented, not scored as ability.
- Missing evidence is recorded as missing, never as 0.
- No clinical/psychological diagnosis of a historical figure from narrative text (e.g., Zhou Yu's chapter-49 illness is coded as a *narrative device*, not evidence of an actual medical or personality condition).

## Annotation-layer detection note (informs D1, does not replace D1's extraction pipeline)

In the `history_base_zh` raw files inspected for this slice, Pei Songzhi (裴松之) citations consistently appear inside `〈...〉` angle brackets (e.g., `〈《江表傳》曰：...〉`, `〈孫盛曰：...〉`, `〈《山陽公載記》曰：...〉`). Text inside these brackets is coded as `HISTORY_ANNOTATION`; text outside them is coded as `HISTORY_BASE`. This is R1's working heuristic for this manual coding pass only — D1's `research`/`data` schema and extraction pipeline is the authoritative, reproducible separation and should confirm or correct this bracket-based rule.

## Label set (this slice only)

| Label | Definition | Include example | Exclude example |
| --- | --- | --- | --- |
| `military_setback_attribution` | Text explains a military defeat/retreat and names a cause | "大疫，吏士多死者，乃引軍還" (illness as cause) | A bare statement of retreat with no stated cause |
| `psychosomatic_strategic_anxiety` | `ROMANCE`-only: a party's physical collapse/illness is narratively tied to an unresolved strategic problem, not to a real external cause | 周瑜's chapter-49 collapse, resolved only once the fire-attack plan is complete | Any illness in `HISTORY_BASE`/`HISTORY_ANNOTATION` with a stated external cause (e.g., 大疫) — code that as `military_setback_attribution` instead, never as this label |
| `joint_military_command` | Two or more named parties are credited together for a military outcome | "先主與吳軍水陸並進" | A passage crediting only one named party |
| `minimal_narrative_role` | A person is present in the passage's timeframe but the passage assigns them no direct action in the event | 諸葛亮's one-sentence Red-Cliffs mention in his own `HISTORY_BASE` biography | A passage where the person actively speaks or acts |
| `decisive_leadership_under_dissent` | A leader is shown choosing a position against the majority of their own advisors | 孫權 backing 瑜/肅's resistance against surrender-advocating officials | A leader simply ratifying advisor consensus |
| `subordinate_initiated_strategy` | A named subordinate proposes a tactic that a superior then authorizes/executes | 黃蓋 proposing the fire attack to 周瑜 | A passage where the superior is shown originating the idea themselves |
| `rival_credit_denial` | One party's quoted words minimize or reassign credit/blame away from a rival's stated achievement | 曹操's letter denying 周瑜 credit for the victory | A neutral third-party assessment of credit |
| `strategic_self_awareness` | A party's quoted words show them recognizing their own near-miss or error, without external prompting | 曹操: "向使早放火，吾徒無類矣" | A party blaming only external factors (disease, weather) |
| `source_conflict_note` | The annotation explicitly flags a discrepancy between two source accounts of the same event | 孫盛's note comparing 吳志 and 山陽公載記 on event order | A citation that merely adds detail without flagging conflict |
| `source_bias_flag` | The annotation explicitly attributes a claim to a source's partisan interest | 孫盛: "江表傳之言，當是吳人欲專美之辭" | A citation presented as neutral fact |
| `deceptive_communication` | A party sends a message intended to mislead an adversary as a documented tactic | 黃蓋's feigned-surrender letter (both `HISTORY_ANNOTATION` and `ROMANCE` versions) | Genuine negotiation without documented intent to deceive |
| `peer_praise` | One named party is quoted praising another's competence, unconnected to a specific single action | 孫權 on 周瑜: "公瑾文武籌略，萬人之英" | A generic honorific title with no specific praise content |
| `leadership_attribution_acknowledgment` | A leader is quoted crediting another named person for their own success | 孫權: "孤非周公瑾，不帝矣" | A leader praising a person's character without linking it to an outcome |
| `supernatural_attribution` | `ROMANCE`-only: text assigns a person the ability to influence weather/fate through ritual or foreknowledge | 諸葛亮's 七星壇 wind ritual; his claim to have foreseen Cao Cao's survival by astrology | Any `HISTORY_BASE`/`HISTORY_ANNOTATION` passage — this label is `ROMANCE`-exclusive by construction; a coder finding it needed outside `ROMANCE` must stop and flag `research/analysis_criteria.md`, not apply the label |
| `rival_elimination_attempt` | A party is shown planning to kill or remove a rival/ally outside open battle | 周瑜 ordering 諸葛亮's assassination after the wind ritual | A party expressing anger without a documented removal plan |
| `foresight_escape_planning` | A party is shown having pre-arranged a contingency before the triggering event occurs in-narrative | 諸葛亮 pre-arranging 趙雲's boat before 周瑜's assassination order | An improvised escape with no stated prior arrangement |
| `strategic_manipulation_of_subordinate` | A party deliberately sets a test or trap for a subordinate's loyalty/duty conflict | 諸葛亮 assigning 關羽 to Huarong Road specifically to test him | A routine task assignment with no stated test intent |
| `appeal_to_past_favor` | A party invokes a past personal debt to influence a rival/subordinate's present decision | 曹操 reminding 關羽 of past treatment at Huarong Road | A purely tactical or military argument |
| `loyalty_override_duty` | A party is shown choosing personal loyalty/obligation over a formal order or duty | 關羽 releasing 曹操 despite his military pledge | A party following orders despite personal feelings |
| `leadership_self_reflection_regret` | A leader is quoted explicitly regretting a past decision or acknowledging a specific error | 曹操 mourning 郭嘉, admitting 郭嘉's absence caused the defeat | A leader blaming only external/impersonal factors |
| `fatalistic_strategic_foresight` | `ROMANCE`-only: a party claims foreknowledge of fate/timing (e.g., of another's death) to justify a decision | 諸葛亮: "亮夜觀乾象，操賊未合身亡" | Any claim of foreknowledge based on stated military/intelligence reasoning rather than astrology/fate |
| `alliance_persuasion` *(added in expansion pass, 2026-09-17)* | A party persuades another leader/faction to join or maintain a political-military alliance, as an alternative to a different allegiance or course of action | 魯肅 persuading 劉備 to ally with 孫權 instead of fleeing to 蒼梧太守吳巨 (HA-J32-P2) | A passage simply executing joint military action already agreed (code `joint_military_command` instead) |
| `combat_skill_display` *(added in expansion pass, 2026-09-17)* | `ROMANCE`-only by convention in this slice (no comparable HISTORY_BASE/HISTORY_ANNOTATION combat set-pieces were found for these persons): a party demonstrates individual martial skill in direct action (archery, single combat, a charge) as a narrative highlight, distinct from strategic planning or command | 趙雲's archery rescue of Zhuge Liang (RM-C049-P7); 黃蓋's fire-ship charge and wounding (RM-C049-P8); 趙雲's duel with 陳應 (RM-C052-P1) | A bare statement that a battle occurred without highlighting individual skill; strategic planning or authorization without personal combat action (code `subordinate_initiated_strategy` or similar instead) |
| `reciprocal_combat_mercy` *(added in expansion pass 2, 2026-09-18)* | A party is shown sparing or deliberately not killing an opponent during personal one-on-one combat, out of spontaneous respect earned in that fight itself -- not because of a pre-existing personal debt (that's `appeal_to_past_favor`) or a formal command (`loyalty_override_duty`) | Guan Yu sparing Huang Zhong when his horse stumbles (RM-C053-P3); Huang Zhong repaying by deliberately missing his shot (RM-C053-P4) | A mercy granted because of a prior personal relationship/debt (code `appeal_to_past_favor` instead); an order from a superior to stand down (code `loyalty_override_duty` instead) |

## Actor/target and polarity

- Every row records `primary_actor` (who is credited with the action/statement) separately from `subject_of_claim` when a quote is *about* someone else (e.g., 曹操's letter is `actor=曹操`, `subject_of_claim=周瑜`).
- As of the expansion pass, this slice's scored cast is 曹操/劉備/諸葛亮/孫權/周瑜/黃蓋/關羽/魯肅/趙雲/郭嘉 (10 persons). Remaining supporting figures still outside the cast (程昱, 甘寧, 蔣幹, 龐統, 陳應, etc.) are recorded when they are the actor of a passage directly involving a cast member, but are not themselves scored.
- Negation, irony, and reported speech: none of the 22 coded spans in this pass required negation/irony handling; if a future pass finds sarcastic or reported-secondhand claims, code `polarity_note` explicitly rather than treating the literal words as the claim.

## Ambiguity handling

- `subordinate_initiated_strategy` (HB-J54-P1): coded as *shared* attribution (黃蓋 originates, 周瑜 authorizes) rather than assigning the fire-attack idea solely to either — see `confidence_note` in the evidence row.
- Annotation-block boundaries were determined by bracket-matching, not by re-parsing against a critical edition of 裴注; boundary errors are possible at block edges (see `research/analysis_criteria.md` §Limitations).

## Inter-coder reliability — LLM-LLM check complete, human validation still pending

A second, independent LLM-agent coder blind-coded all 22 rows without seeing R1's labels. Result: 20/22 exact agreement, Cohen's κ = 0.90. Full method, caveats, and the two adjudicated disagreements are in `research/intercoder_reliability.md`. **This is agreement between two AI coders, not human validation** — `agents/_three_kingdoms_domain.md`'s bar of independent *human* coding with a reported agreement statistic is still not met. Do not present this κ value as evidence of historical/critical correctness, only of manual-application consistency. See `handoffs/OPEN_QUESTIONS.md#Q-010` and `handoffs/DECISIONS.md#D-017`.

Two label-boundary clarifications were added as a result of this check:

- `supernatural_attribution` may apply to the setup sentence of a supernatural claim (not only the sentence stating the supernatural act itself) when both are part of the same immediate scene — see RM-C049-P2 in `research/intercoder_reliability.md`.
- Violence staged specifically to make a companion deception message credible is coded `deceptive_communication`, not `rival_elimination_attempt`, which is reserved for violence/removal where the removal itself (not a separate message) is the goal — see RM-C049-P6 in `research/intercoder_reliability.md`.
