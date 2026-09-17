# Product Concept Options

Status: `DISCOVERY — no product form selected`

공통 기반은 정사·주석·연의를 구분한 재현 가능한 삼국지 데이터입니다. 아래 세 가지 제품 형태를 S0에서 비교하고, 데이터 타당성 결과와 함께 B0에서 사람이 선택합니다.

## Option A — Analytics Explorer

- Primary user: 삼국지 팬, 디지털 인문학 관심자
- Promise: 인물·사건·관계를 출처와 근거로 비교 탐색
- Core loop: 검색 → 비교 → 근거 → 관점 변경 → AI 질문
- Data needs: 높은 provenance, entity/event graph, 설명 가능한 지표
- Strength: 분석 자산을 가장 직접적으로 활용
- Risk: 일반 사용자에게 학습 곡선과 반복 동기가 약할 수 있음

## Option B — Data Analysis Learning Game

- Primary user: 데이터 분석을 배우고 싶은 삼국지 팬/입문자
- Promise: 실제 삼국지 데이터로 분석 개념을 배우고 게임 결과로 피드백
- Core loop: 개념 → 실습 → 시각화 → 모델 결과 → 8비트 전투 → 해설
- Data needs: 교육용 sample, 정답/허용오차, 단계별 notebook/interactive task
- Strength: 학습 목표와 재미의 차별점
- Risk: 커리큘럼·게임 밸런스·픽셀 모션 제작 범위가 큼
- Guardrail: Win/Lose는 역사적 진실이 아니라 선택한 분석 모델의 결과

## Option C — Hybrid

- Primary user: 탐색 사용자와 학습 사용자
- Promise: 자유 탐색 서비스에 분석 퀘스트·게임 모드 결합
- Core loop: explorer와 guided quest를 오가며 근거와 분석을 학습
- Strength: 장기 확장성이 큼
- Risk: 초기 MVP가 쉽게 비대해짐; 한 모드가 다른 모드의 품질을 희석할 수 있음

## Decision matrix

각 항목을 1~5점으로 평가하고 근거 경로를 적습니다.

| Criterion | Weight | Explorer | Learning game | Hybrid | Evidence/notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Target-user clarity | 15 |  |  |  |  |
| Raw-data feasibility | 15 |  |  |  |  |
| Differentiation | 15 |  |  |  |  |
| MVP build cost | 10 |  |  |  |  |
| Content production cost | 10 |  |  |  |  |
| Repeat/fun potential | 10 |  |  |  |  |
| Learning measurability | 10 |  |  |  |  |
| Rights/asset risk | 10 |  |  |  |  |
| Personal motivation | 5 |  |  |  |  |

## Minimum evidence before selection

- read-only raw inventory and source-layer feasibility
- one small representative sample inspected
- one candidate analysis and user-facing explanation sketched
- one core-loop paper prototype per serious option
- estimated work and asset/licensing risk
- explicit human decision recorded at B0

