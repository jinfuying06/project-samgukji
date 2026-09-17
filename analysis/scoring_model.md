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

