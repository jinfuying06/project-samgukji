# Product Concept Options

Status: `DECIDED AT B0 (2026-09-17) — Hybrid selected`. See `handoffs/DECISIONS.md#D-009` and `product/concepts/concept_decision.yaml`. This file is kept as the historical comparison record; do not retroactively edit the Explorer/Learning-game scoring rows to make Hybrid look predetermined.

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

Scoring convention: 5 = most favorable to that option, 1 = least favorable. For cost/risk criteria (MVP build cost, Content production cost, Rights/asset risk), 5 means *low* cost/risk. Scores below are the Product Manager track's (C0) provisional evidence-based judgment for B0 review — they are not a selection and must be checked by the human owner and against D0/R0 findings.

| Criterion | Weight | Explorer | Learning game | Hybrid | Evidence/notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Target-user clarity | 15 | 3 | 4 | 3 | PROJECT_BRIEF §2 1차 사용자는 "게임 능력치·스토리 탐색을 즐기는 일반 사용자"로 학습게임에 더 근접. Explorer의 1차 promise(근거 비교 탐색)는 2차 사용자(디지털 인문학 학습자)에게 더 명확함 → concept_options.md 자체의 "Risk: 일반 사용자에게 학습 곡선과 반복 동기가 약할 수 있음" 참고. Hybrid는 두 사용자를 동시에 노려 우선순위가 흐려짐. |
| Raw-data feasibility | 15 | 4 | 3 | 3 | D0 확인 사실(요약): private raw는 HISTORY_BASE 65개 + ROMANCE 120개 JSON뿐이고 HISTORY_ANNOTATION 0개(주석 사료 없음). Explorer의 핵심 루프(정사/연의 비교)는 이 두 층위만으로 최소 가치 제공 가능. Learning game/Hybrid는 여기에 더해 "정답/허용오차", 코딩 라벨, 난이도별 콘텐츠까지 추가 가공이 필요해 동일 raw 대비 준비 비용이 더 큼. |
| Differentiation | 15 | 4 | 4 | 3 | Explorer: "출처 층위 유지 비교 탐색"은 기존 삼국지 콘텐츠(서사 요약·단일 능력치, PROJECT_BRIEF §1 "기존 방식의 한계")와 뚜렷이 다름. Learning game: "실제 역사 데이터로 배우는 분석 게임"도 팬덤·교육 시장 모두에서 드묾. Hybrid는 이론상 최대 차별화지만 두 가치 제안이 희석될 실행 리스크가 있어 보수적으로 낮게 평가. |
| MVP build cost | 10 | 4 | 2 | 2 | README.md와 concept_options.md 모두 "8비트 전투/커리큘럼/게임 밸런스 제작 범위가 큼"을 Learning game 리스크로 명시. Explorer는 검색·비교·근거카드 중심의 상대적으로 단순한 CRUD형 UI. Hybrid는 두 UI를 모두 구현해야 함. |
| Content production cost | 10 | 4 | 2 | 2 | Explorer는 근거 구절+코딩만으로 화면 구성 가능. Learning game은 근거 구절 외에 단계별 설명, 퀴즈/정답 기준, 픽셀 아트·모션 자산이 추가로 필요(README 완료 정의의 vertical slice 범위에도 없음). Hybrid는 둘 다 필요. |
| Repeat/fun potential | 10 | 3 | 4 | 3 | Explorer는 새 인물/사건 탐색으로 재방문은 가능하나 concept_options.md에 명시된 "반복 동기가 약할 수 있음" 리스크가 남음. Learning game은 승패 연출과 단계적 진행이 반복 루프를 만들기 쉬움(단, 실제 재미 검증 데이터는 아직 없음 — 가설 수준). Hybrid는 잠재력은 있으나 축소된 첫 MVP에서 온전히 발휘되기 어려움. |
| Learning measurability | 10 | 2 | 4 | 3 | Explorer는 "학습 성과"를 목표로 설계되지 않아 측정 지표가 약함(성공지표 표의 코더 합치도는 연구 품질 지표이지 사용자 학습 지표가 아님). Learning game은 정답/허용오차·단계 진행이 있어 학습 측정이 구조적으로 더 쉬움(측정 도구 자체는 아직 미설계, 가설 수준). Hybrid는 게임 모드에서만 측정 가능. |
| Rights/asset risk | 10 | 3 | 2 | 2 | 공통 리스크: crawled raw의 출처 URL·현대 번역 저작권 상태가 D0/R0에서 아직 미확정(OPEN_QUESTIONS Q-003). Explorer는 텍스트 근거 인용 위주라 research/source_policy.md의 "짧은 발췌+위치 참조" 원칙으로 위험을 낮출 여지가 있음. Learning game/Hybrid는 8비트 캐릭터·사운드 등 별도 제작/라이선스 자산이 추가로 필요해 권리 리스크가 더 큼. |
| Personal motivation | 5 | 2 | 5 | 5 | Human project owner's direct B0 answer: "학습게임과 하이브리드 쪽에 높은 점수" — Learning game and Hybrid scored high (5), Explorer scored lower (2) by inference since it was not named. Exact numeric split beyond "high" was not specified further; recorded here as given, not estimated by an agent. |

Weighted total including Personal motivation, human-provided: Explorer 350/500 (70.0%), Learning game 330/500 (66.0%), Hybrid 280/500 (56.0%). Despite Explorer scoring highest on this matrix, **B0 selected Hybrid** (`handoffs/DECISIONS.md#D-009`) — the human project owner's decision is authoritative over the matrix total; the matrix is evidence input, not the decision rule itself.

## Minimum evidence before selection

- read-only raw inventory and source-layer feasibility
- one small representative sample inspected
- one candidate analysis and user-facing explanation sketched
- one core-loop paper prototype per serious option
- estimated work and asset/licensing risk
- explicit human decision recorded at B0

