# Gamification Spec — S1 Vertical Slice (적벽대전)

Status: `S1 DRAFT`. Applies only to the learning-game mode of Hybrid (`product/feature_spec.md` §2), scoped to the 적벽대전 event. Governed by `agents/_three_kingdoms_domain.md` 게이미피케이션 가드레일 and `design/DESIGN.md`§5, which override this document if they ever conflict.

## Design intent

Rewards must make the user look at more evidence, not click faster or feel more certain than the evidence supports. If a reward mechanic can be satisfied without the user actually opening evidence, it is out of scope.

## Reward table

| Mechanic | Rewards | Does NOT reward | Guardrail source |
| --- | --- | --- | --- |
| Quest completion (L-01) | Opening both 정사 and 연의 evidence for the same claim | Clicking "완료" alone | `_three_kingdoms_domain.md` |
| Counter-evidence checkpoint (L-02) | Acknowledging ≥1 piece of evidence that complicates the user's first impression | Picking the "expected"/majority answer | `_three_kingdoms_domain.md`, `design/DESIGN.md`§5 |
| Score-formula reveal (L-03) | Opening the full 관측 근거→코드→…→표시 점수 path before seeing a number | Skipping straight to a headline number | `_three_kingdoms_domain.md` 점수와 비교 |
| Weight experiment (E-04, reused in learning mode) | Trying at least one alternative weighting and comparing it to default | N/A — this is opt-in exploration, no completion gate needed | `design/DESIGN.md`§4 |
| Evidence-linked quiz (L-04) | Answering with reference back to the specific `evidence_id` that supports the answer | Guessing without opening the linked evidence first (quiz items are unlockable only after the relevant `QuestCard` step) | `_three_kingdoms_domain.md` |

## Explicitly excluded mechanics (do not implement, do not propose again without a new B0/B1-level decision)

- 인기투표 (popularity voting) of any kind.
- 확률형 보상 (gacha/random-chance rewards).
- 과도한 streak 메커닉이나 역사 왜곡을 유도하는 연속 출석/연속 정답 압박.
- 단일 "최강" 순위 또는 "정답 인물" 배지 — no badge implies one person is objectively the best or the historically "correct" pick.
- 사용자 간 경쟁/리더보드 (explicit non-goal, `product/feature_spec.md`§4).
- 인기 인물에게 자동으로 유리한 보상 배분 (e.g., basing rewards on how often a person is mentioned/chosen — mention frequency is not a merit signal, `agents/_three_kingdoms_domain.md`).

## Score-type separation (mandatory in every rewarded screen)

- **기본 점수 (default score):** project-computed, versioned, never edited by quest completion.
- **사용자 커스텀 점수:** produced only by E-04/weight experiments; always labeled "사용자 설정 점수" and this label cannot be removed once the user changes a weight (`design/DESIGN.md`§4).
- **외부 게임 수치 (`GAME_DATA`):** not present in this S1 slice (no external game data source approved yet) — if introduced later, it must ship with its own label and cannot be blended into either score above.

## Badge/quest copy rules

- Badge and quest text describes the *behavior* performed ("양쪽 출처를 모두 확인했습니다", "반대 근거를 확인했습니다"), never a claim about historical truth ("당신이 맞았습니다"/"이 인물이 최고입니다").
- Any copy implying a historical claim must carry an `evidence_id` reference or must not be written.

## Acceptance hook

See `product/acceptance_criteria.md` "Learning-game quest completion" scenarios for the testable version of the quest-completion and counter-evidence rules above.

## Open item

- Q-005 (difficulty/learning level) may change how many claims/quiz items are presented per session, but does not change any reward rule above — the guardrails in this document apply at every difficulty level.
