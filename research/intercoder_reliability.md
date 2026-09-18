# Inter-Coder Reliability — 적벽대전 Vertical Slice

Status: `COMPLETE v1 — 2026-09-17`. Addresses `handoffs/OPEN_QUESTIONS.md#Q-010` per the human owner's chosen option (independent second coding pass + agreement statistic).

## Important framing — read before citing this number

**Both coders in this check are LLM agents, not humans.** This is a real, methodologically legitimate consistency check on whether `research/coding_manual.md`'s label definitions can be applied the same way by two independent readers — but it is **not** the human-validated "golden set" that `agents/_three_kingdoms_domain.md` asks for ("최초 표본은 최소 두 코더가 독립 코딩"). Do not cite this kappa value as evidence that the coding is "human-validated." It shows the manual is *internally consistent*, not that its labels are *historically/critically correct*.

## Method

1. `research/evidence_matrix.csv`'s 22 rows were stripped of `coding_label`, `ambiguity_note`, `confidence`, `extraction_reviewer`, and `review_status`, producing a blinded input (`research/_blind_coding_pass2_input.csv`).
2. A second coder — a fresh agent session with **no access to** `evidence_matrix.csv`, `analysis_criteria.md`, `analysis/outputs/result.json`, or any other file that could reveal the first coder's labels or worked examples — independently read each excerpt and `research/coding_manual.md`'s 21-label set, and assigned one label per row (`research/_blind_coding_pass2_output.csv`).
3. Agreement was computed with a script (not by hand): exact agreement rate and Cohen's kappa (accounts for chance agreement given each rater's label-frequency distribution).

Reproduce: the comparison script's logic is recorded here rather than as a separate committed file (it is a ~15-line one-off comparison of two already-committed CSVs); given the CSVs are fixed, re-running the same computation on `research/evidence_matrix.csv`'s `coding_label` column vs. `research/_blind_coding_pass2_output.csv`'s `coding_label` column reproduces these numbers exactly.

## Result

| Metric | Value |
| --- | --- |
| N (evidence spans) | 22 |
| Exact agreement | 20/22 = 90.9% |
| Expected chance agreement (pe) | 4.75% |
| Cohen's kappa | **0.90** |

By the conventional Landis & Koch (1977) benchmark, κ ≈ 0.90 is "almost perfect" agreement. **Caveat this project must not ignore:** with 21 possible labels and most labels used only once or twice across 22 rows, the chance-agreement baseline (pe) is mechanically very low (4.75%), which inflates kappa relative to a task with fewer, more balanced categories. A high kappa here mainly says "these two readers rarely picked wildly different labels for the same excerpt," not "there is no room for interpretive disagreement" — the two real disagreements below show genuine, defensible interpretive splits even within this small sample.

## Disagreements and adjudication

Both disagreements were reviewed by the orchestrator (acting as adjudicator, per the second coder's own request for a third opinion) against `research/coding_manual.md` and the raw excerpt.

### RM-C049-P2 — 諸葛亮's "萬事俱備，只欠東風" note

- Rater 1 (R1): `supernatural_attribution`
- Rater 2 (second coder): `subordinate_initiated_strategy` (flagged by rater 2 as their lowest-confidence row — noted the label presumes a subordinate relationship that doesn't fit 諸葛亮's status as an allied strategist, not 周瑜's subordinate)
- **Adjudication: keep `supernatural_attribution` (R1's original).** The excerpt is the direct setup line for Zhuge Liang's immediately-following ritual wind-summoning claim (回49) — read as a strategic statement in isolation it looks like ordinary tactical advice, but its narrative function in this specific scene is to set up the supernatural claim. Rater 2's alternative was reasonable from the excerpt text alone but is a worse fit for the scene as a whole, and rater 2 independently flagged it as their own weakest assignment — not a confident competing reading.
- **Manual clarification added** (see `research/coding_manual.md` change below): `supernatural_attribution` may apply to the setup sentence of a supernatural claim, not only the sentence stating the supernatural act itself, when the two are part of the same immediate scene.

### RM-C049-P6 — Zhou Yu's mock execution of 蔡和 before dispatching 黃蓋

- Rater 1 (R1): `deceptive_communication`
- Rater 2 (second coder): `rival_elimination_attempt` (explicitly called this a "toss-up," noting the excerpt literally depicts a killing rather than a message sent to an adversary)
- **Adjudication: keep `deceptive_communication` (R1's original).** The mock execution's narrative purpose (per the surrounding text, not just this one excerpt) is to make the companion feigned-surrender letter credible to Cao Cao — it is staged theater in service of the deception, not an attempt to permanently remove a rival for its own sake. Rater 2's reading is defensible from the excerpt in isolation (a killing is depicted) but the label's definition in the manual is about the *documented tactic's intent*, which here is deception, not elimination.
- **Manual clarification added:** violence performed specifically to make a companion deception message credible is coded `deceptive_communication`; `rival_elimination_attempt` is reserved for violence/removal where the removal itself, not a separate message, is the goal.

## What this does and doesn't resolve

- **Resolves:** the coding manual's label definitions are shown to be applicable with high (though not perfect) consistency by two independent LLM readings — this is real evidence the manual isn't so vague that labels are arbitrary.
- **Did not, on its own, resolve:** human validation. `handoffs/OPEN_QUESTIONS.md#Q-010` remained open in the sense that no human had reviewed any of these rows against the raw text. The human owner chose this LLM-LLM check as an accepted intermediate step, not a substitute for eventual human review before production use (see `handoffs/DECISIONS.md#D-017`). **This gap was closed by the human review pass below.**

## Human review pass (2026-09-18, D-024)

After the S3/B3 implementation gate failed on `coding_calibration_missing` (`handoffs/DECISIONS.md#D-023`), the human project owner chose to do a real review rather than accept the gap or run a second LLM pass (Q-011 option (a)).

- **Method:** the human owner reviewed all 30 evidence rows (the original 22 plus the 8 rows added in the D-016 expansion pass) via a purpose-built, non-technical review artifact — each row presented as: the source-layer badge, a plain-Korean paraphrase of the classical-Chinese excerpt (not a request to read Chinese), the assigned `coding_label` with its plain-language definition, and an agree/disagree/unsure control. The 2 rows the LLM-LLM pass had flagged as adjudicated disagreements (RM-C049-P2, RM-C049-P6) were specifically called out for the reviewer's attention.
- **This is a human *confirmation/audit* pass against already-produced labels and a project-authored paraphrase, not an independent blind re-coding from the raw excerpt.** It is methodologically distinct from, and weaker than, a textbook "second independent human coder computes their own labels from scratch, then agreement is measured against the first coder." It is stronger than no human review at all, and it directly satisfies `data/schemas/evidence.schema.json`'s `coding_validation_status` field's own documented purpose ("whether this evidence's coding has been human-reviewed").
- **Result:** the human owner reported reviewing all 30 rows with no disagreements ("검토완료 모두 문제 없어보임") — including the 2 previously-adjudicated cases.
- **System update:** `coding_validation_status` flipped from `llm_llm_validated_only` to `human_validated` across the curated export, runtime DB, and all API responses (`data/pipelines/build_curated_export.py`'s `CODING_VALIDATION_STATUS` constant; re-exported and re-imported 2026-09-18). This is a real, load-bearing change — not a label swap — since `EvidenceCard.tsx` renders a different, less alarming disclosure string ("사람 검증 완료") once this flips, and that behavior is unit-tested.
- **What remains honestly unresolved:** `double_coded_calibration_set` in the strict two-independent-coders-with-a-computed-agreement-statistic sense (as `agents/_three_kingdoms_domain.md` and `evals/run_eval.py`'s automatic check define it) is still, technically, LLM-LLM only — the human pass was a review/audit, not a second from-scratch coding. Whether this human review substitutes for that automatic check in spirit is a judgment call left to whichever Evaluator re-scores B3, not decided unilaterally here.
