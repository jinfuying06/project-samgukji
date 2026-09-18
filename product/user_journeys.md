# User Journeys — S1 Vertical Slice (적벽대전)

Status: `S1 DRAFT`. Scoped to the 적벽대전 sample only. References features in `product/feature_spec.md`.

## Journey 1 — Explorer user compares 周瑜 across 정사 and 연의

**User:** Primary user (PROJECT_BRIEF §2), degree of expertise unknown (Q-009 open) — journey is written for the more-explanatory default.

1. User opens the 적벽대전 event overview (E-01) and sees the cast (曹操, 孫權, 劉備, 周瑜, 諸葛亮) and which source layers have data (`SourceModeControl` shows 정사/연의 enabled; 정사 주석 enabled only if D1's extraction has usable coverage).
2. User selects 周瑜, chooses **비교** mode, and opens the person comparison view (E-02). Evidence cards for 정사 and 연의 appear side by side, each with `evidence_id`, locator, and quotation-type.
3. User notices a difference between the two portrayals and opens an `AIAnswerPanel` (E-03) to ask "왜 다르게 그려지나?". The panel answers per-claim with evidence refs, in **비교** mode language (병렬 제시, 결론 유보 허용).
4. User opens the score breakdown (F-02/E-04) for one of 周瑜's indicators, sees the full 관측 근거 → 코드 → … → 표시 점수 path, and experiments with custom weights (E-04). The recomputed number is clearly labeled "사용자 설정 점수" and does not replace the default score.
5. **Exit state:** user leaves having seen at least one 정사/연의 conflict with evidence, not a single merged "fact."

**Alternate/edge branches:**
- If 정사 주석 has insufficient extracted coverage for 周瑜 in this event, step 2's comparison shows only 정사/연의 with an explicit "정사 주석: 근거 부족" state instead of silently omitting the option.
- If the AI panel in step 3 lacks evidence for a sub-claim, it abstains for that claim specifically rather than answering with unsupported text (F-04).

## Journey 2 — Learning-game user completes the 적벽대전 quest

**User:** Primary user who chose "학습" entry point. Learning level per L-05 is **OPEN — Q-005 대기**; journey below assumes a single default level.

1. User starts the 적벽대전 quest (`QuestCard`, L-01) with a stated goal (e.g., "曹操가 왜 졌는지, 정사와 연의가 같은 이유를 대는지 확인하기") and a visible completion condition.
2. Quest requires opening at least one 정사 evidence card and one 연의 evidence card for the same claim (L-01).
3. Before the quest reveals any score, it shows the score-formula path as its own step (L-03) — not a footnote after the number.
4. Quest presents a counter-evidence checkpoint (L-02): user must acknowledge one piece of evidence that complicates their working answer before the "complete" state becomes reachable.
5. User answers a short evidence-linked quiz (L-04, 2–4 items) tied to evidence already surfaced in this quest; each answer links back to its supporting `evidence_id`.
6. **Exit state:** quest is marked complete only after steps 2 and 4 are satisfied — a single click on "완료" without opening both source layers and one counter-evidence item cannot complete it (`_three_kingdoms_domain.md` 게이미피케이션 가드레일).

**Alternate/edge branches:**
- If evidence coverage for the chosen claim is too thin to support a counter-evidence checkpoint, the quest surfaces a different claim within the same event rather than faking a checkpoint.
- User may switch to Explorer mode mid-quest (F-00 shared foundation) without losing quest progress; this is a shared-foundation requirement, not a new feature.

## Cross-journey acceptance note

Both journeys must be able to reach an explicit "정사 주석 데이터 부족" state without breaking, since `HISTORY_ANNOTATION` extraction coverage for the 적벽대전 sample is not yet confirmed by D1 at the time this document was written (`handoffs/OPEN_QUESTIONS.md#Q-006`). See `product/acceptance_criteria.md` for the Given/When/Then version of both journeys.
