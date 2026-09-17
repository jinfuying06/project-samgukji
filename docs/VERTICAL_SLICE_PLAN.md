# First Vertical Slice Plan

Status: `CANDIDATE — choose after B0 concept and data feasibility approval`

## 목적

전체 인물 데이터베이스를 만들기 전에 한 사건에서 **출처→코딩→점수→설명→게임 UI→평가**를 끝까지 관통합니다.

## 사건 선택 기준

- 정사/주석/연의에서 비교 가능한 자료가 있음
- 주요 인물 3~5명으로 제한 가능
- 리더십/전략/관계 코드가 충분함
- 유명 서사와 사료 차이를 사용자가 이해하기 쉬움
- 사용할 판본/번역의 권리를 해결할 수 있음

추천 후보:

- 관도대전: 조조·원소 및 참모 활용, 전략/등용/지휘 코딩
- 적벽대전: 연합·외교·지휘 관계, 정사/연의 네트워크 차이

## Deliverables

### Research

- 방법론 문헌 3~5편 검증
- 선택 사건의 출처 목록과 판본 정책
- evidence span 20~40개
- 코드 5~8개, 이중 코딩 표본과 adjudication

### Data/analysis

- 인물 3~5명, 사건 1개, typed relationships
- 구성 점수 1개와 coverage/confidence
- source-layer별 네트워크 비교 1개
- score/weight sensitivity 사례

### Product

- 비교 화면 1개
- 근거 탐구 퀘스트 1개
- 커스텀 가중치 실험 1개
- 정사/연의/비교 AI 질문 모드

### Evaluation

- source leakage 0
- orphan evidence 0
- unresolved alias collision 0
- unsupported claims 0
- score decomposition exact
- 사용자 5명 수준의 초기 이해/재미 테스트 `[규모는 조정 가능]`

## Out of scope before B0

- 전 시대/전 인물
- 실시간 커뮤니티 경쟁
- 자동 무검수 원문 코딩
- 외부 게임 자산 복제
- “역사적으로 가장 뛰어난 인물”의 단일 정답
- production UI, 전체 커리큘럼, 8비트 전투 구현
- full-corpus normalization or analysis
