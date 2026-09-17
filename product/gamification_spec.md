# Evidence-First Gamification Spec

Status: `CANDIDATE — applies only if B0 selects learning-game or hybrid scope`

## Design goal

게임 요소는 체류시간 자체보다 **근거 확인, 출처 비교, 가중치 실험, 반대 사례 탐색**을 보상합니다.

## Core loop

1. Predict: 정사와 연의의 차이 또는 인물 강점을 예상한다.
2. Inspect: 근거 카드와 코딩 기준을 연다.
3. Compare: source mode를 전환해 차이를 확인한다.
4. Tune: 가중치를 바꾸고 점수/순위 변화를 본다.
5. Explain: 변화 이유를 evidence ID와 함께 설명한다.
6. Reflect: 반대 근거 또는 불확실성을 확인한다.

## Safe mechanics

| Mechanic | Rewarded action | Guardrail |
| --- | --- | --- |
| 탐구 배지 | 양쪽 출처와 반대 근거 확인 | “정답 역사” 배지로 표현하지 않음 |
| 사건 퀘스트 | 근거 기반 코드 분류 | 정답 공개 시 코드북과 이견 표시 |
| 가중치 실험 | 공식 변경과 결과 관찰 | 커스텀 점수 라벨 고정 |
| 소스 탐험도 | 검토한 판본/층위 확장 | 원문 접근성 차이를 벌점화하지 않음 |
| 설명 챌린지 | 점수 근거를 올바르게 연결 | LLM 답변은 evidence 검증 후 채점 |

## Avoid by default

- 결제/확률형 보상
- 역사적 비극이나 배신을 자극적 포인트로 소비
- 인기투표를 역사 평가로 표시
- 사용자가 근거를 읽지 않아도 진행되는 streak
- 단일 종합 순위만 전면에 배치

## Metrics

- 근거 카드 열람률
- 비교 모드 완주율
- 반대 근거 확인률
- 커스텀 점수 공유 시 공식/버전 포함률
- 퀴즈 전후 source-layer 오개념 감소
- 재미/재방문과 정확성 지표를 별도 보고
