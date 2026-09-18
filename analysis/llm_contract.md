# LLM Interpretation Contract — 적벽대전 Vertical Slice

Status: `S2 DRAFT`. Governs the `AIAnswerPanel` (`product/feature_spec.md` F-04, used by E-03 in Explorer mode and by the AI-assisted parts of the learning-game mode). Defines what an LLM Analyst pass may output when turning `analysis/outputs/result.json` + `research/evidence_matrix.csv` into a user-facing answer. Schema: `analysis/schemas/interpretation.schema.json`.

## 0. What currently exists to interpret — read this before writing any prompt

This slice's `analysis/outputs/result.json` has **no composite/display score**. It has exactly three metric families:

- `coverage.*` — evidence-span counts per person × source layer (not an ability score; `0` means "no coded span," never "score of zero")
- `label_frequency.*` — coding-label tallies across the 22 evidence spans (descriptive counts only)
- `divergence.*` — 3 pre-registered qualitative classifications (`compatible`/`complementary`/`contradictory`) for specific person/claim pairs

`analysis/scoring_model.md` explicitly stops **before** the subscore → weighting → display-score stages for this slice, and `analysis/network_analysis_plan.md` explicitly computes no centrality metric at this N. Any user request that presumes a score, ranking, or "who is best" comparison must be met with an honest correction (`status: insufficient_evidence`), never a fabricated number.

## 1. Answer modes and allowed source layers

| Mode | Allowed `source_layer` | Notes |
| --- | --- | --- |
| 정사 | `HISTORY_BASE`, `HISTORY_ANNOTATION` | `ROMANCE` evidence must never be cited, even as "background context." |
| 연의 | `ROMANCE` only | Must visibly label the answer as fictional/literary, per `agents/_three_kingdoms_domain.md`. |
| 비교 | `HISTORY_BASE`, `HISTORY_ANNOTATION`, `ROMANCE` — shown side by side, never merged | If a layer has no coded evidence for the claim, state that explicitly ("이 층위에는 근거 없음") — silence is never treated as agreement, disagreement, or `0`. |
| 게임 | `GAME_DATA` only | **In this slice, no `GAME_DATA` source has been approved.** Every 게임-mode request in this slice returns `status: insufficient_evidence` — never substitute `HISTORY_BASE`/`ROMANCE` content dressed up as "게임 수치." |

## 2. Claim types

- **`observation`** — directly restates one coded evidence span or one computed metric from `result.json`. Must not paraphrase past what the excerpt/metric actually says.
- **`interpretation`** — connects ≥2 observations. For divergence claims, the LLM Analyst may only **restate/rephrase** a `divergence.*` classification A1 already computed — it may never invent a new classification or apply the compatible/complementary/contradictory framework to a pair A1 did not pre-register.
- **`recommendation`** — narrowly scoped to "what evidence to look at next" (e.g., "정사 주석도 확인해 보세요"). **Never** personalized life/decision advice, and never a moral/character judgment about a historical figure (`agents/llm_analyst.md` 금지: 근거에 없는 진단·예측·개인화 권고 추가 금지).

## 3. Grounding rules

1. Every claim requires ≥1 `evidence_refs` (a real `evidence_id` from `research/evidence_matrix.csv`) **or** ≥1 `metric_refs` (a real `metric_id` from `result.json`) — never neither. Enforced structurally by `interpretation.schema.json`.
2. Numbers are copied verbatim from `result.json` (value + unit unchanged) — the LLM never recomputes or derives a new count or statistic. Recomputation is D1/A1's job, not L1's.
3. **Mandatory disclosure (D-017):** any response that cites `research/evidence_matrix.csv` must include `coding_validation_notice`, disclosing that this coding is LLM-LLM validated only (Cohen's κ = 0.90 against a second independent LLM coder, `research/intercoder_reliability.md`) and has **not** been reviewed by a human. This is not optional styling — omitting it misrepresents the evidence's validation status to the user.
4. If a requested score/ranking doesn't exist in this slice, respond with `status: insufficient_evidence` and an `abstention_reason` that names specifically what's missing (e.g., "this slice has not computed a weighted score"), not a vague "unknown."
5. Silence in one source layer for a given claim is reported as "no coded evidence in this layer for this claim in this slice" — never as agreement, disagreement, or a `0` value.
6. 게임-mode requests always resolve to `insufficient_evidence` in this slice (rule 1's table).

## 4. Prohibited

- Emitting any claim without both `evidence_refs` and `metric_refs` empty (schema-enforced).
- Merging `HISTORY_BASE`/`HISTORY_ANNOTATION`/`ROMANCE` content into one undifferentiated claim.
- Inventing a score, ranking, or centrality value not present in `result.json`.
- Personalized advice, clinical/psychological diagnosis, or prediction about a historical figure.
- Presenting `research/evidence_matrix.csv`'s coding as human-validated.
- Any new statistical computation — L1/the runtime LLM only rephrases what D1/A1 already computed.

## 5. Worked examples (both validated against `analysis/schemas/interpretation.schema.json` with the `jsonschema` 4.26.0 validator — including three negative-case checks confirming the schema actually rejects: a claim with empty `evidence_refs`+`metric_refs`, `status:ok` with zero claims, and `insufficient_evidence` missing `abstention_reason`)

### Example A — grounded, `status: ok` (비교 mode)

User question: "曹操는 적벽대전 패배 후 어떻게 반응했나요?"

```json
{
  "interpretation_id": "interp-chibi-caocao-selfreflection-001",
  "answer_mode": "비교",
  "status": "ok",
  "generated_at": "2026-09-17T13:00:00Z",
  "model": { "name": "claude-sonnet-5", "version": "2026-09" },
  "prompt_version": "llm_contract_v1_answer_mode_비교",
  "input_refs": {
    "result_json_run_id": "run-20260917T122003Z",
    "evidence_matrix_checksum": "288a68e027fcd6799d1b15efd5b6f6b27fdc619e83105ca2a00d6c9be5370865"
  },
  "coding_validation_notice": "이 근거 코딩은 AI 단독 검증(2차 AI 코더와의 일치도 Cohen's kappa=0.90)이며, 아직 사람 검증 전 단계입니다. (handoffs/DECISIONS.md#D-017)",
  "claims": [
    {
      "claim_id": "c1",
      "claim_type": "observation",
      "text": "정사(HISTORY_BASE)에서 曹操는 적벽 패전의 책임을 전염병 탓으로 돌리며, 周瑜의 공을 인정하지 않습니다.",
      "evidence_refs": ["HB-J54-P2"],
      "metric_refs": [],
      "confidence": "high"
    },
    {
      "claim_id": "c2",
      "claim_type": "observation",
      "text": "연의(ROMANCE)에서는 曹操가 郭嘉의 죽음을 언급하며 자신의 판단 실수를 스스로 인정합니다.",
      "evidence_refs": ["RM-C050-P3"],
      "metric_refs": [],
      "confidence": "high"
    },
    {
      "claim_id": "c3",
      "claim_type": "interpretation",
      "text": "두 서술은 같은 인물, 비슷한 시점에 대해 정반대의 자기 평가를 보여주는 사례로, 이 프로젝트의 분석 절차상 'contradictory'(상충)로 분류됩니다.",
      "evidence_refs": ["HB-J54-P2", "RM-C050-P3"],
      "metric_refs": ["divergence.caocao_selfreflection"],
      "confidence": "medium",
      "caveats": [
        "이 분류는 정사/연의 각 1개 구절만 비교한 것으로, 두 작품 전체의 曹操 묘사를 대표하지 않습니다.",
        "이 근거는 단일 AI 코더가 최초 코딩했고 2차 AI 코더 검증(kappa=0.90)만 거쳤습니다 — 사람 검증 전입니다."
      ]
    }
  ]
}
```

### Example B — abstention, `status: insufficient_evidence` (게임 mode)

User question: "曹操의 게임 능력치는 몇 점인가요?"

```json
{
  "interpretation_id": "interp-chibi-caocao-gamedata-refuse-001",
  "answer_mode": "게임",
  "status": "insufficient_evidence",
  "generated_at": "2026-09-17T13:05:00Z",
  "model": { "name": "claude-sonnet-5", "version": "2026-09" },
  "prompt_version": "llm_contract_v1_answer_mode_게임",
  "input_refs": {
    "result_json_run_id": "run-20260917T122003Z",
    "evidence_matrix_checksum": "288a68e027fcd6799d1b15efd5b6f6b27fdc619e83105ca2a00d6c9be5370865"
  },
  "abstention_reason": "이 슬라이스에는 승인된 GAME_DATA 소스가 없습니다 (analysis/scoring_model.md). 정사/연의 근거로 게임 능력치를 대신 만들어 답할 수 없습니다.",
  "claims": []
}
```

## 6. Regression/eval hook

Per `agents/llm_analyst.md`'s completion condition ("모델/프롬프트 변경 시 회귀 평가가 있음"), both worked examples above should become the first two fixtures in a future `evals/` interpretation eval set: Example A as a "must-ground-correctly" case, Example B as a "must-abstain" case. Not created in S2 (no eval runner scope was assigned to L1) — flagged for S3/QA.

## 7. Known limitation carried from S1

- Cast/evidence scope is currently 5 persons / 22 evidence spans only (`handoffs/DECISIONS.md#D-016`) — this contract must keep working unmodified once that scope expands; it must never hard-code the 5 names or the number 22.
- Evidence coding is LLM-LLM validated only, not human-validated (`handoffs/DECISIONS.md#D-017`) — rule 3's disclosure requirement exists specifically to keep this visible to end users until that gap is closed.
