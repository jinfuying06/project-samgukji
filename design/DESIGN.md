# TKAF Design Standard

Status: `STARTER — activate after B1; replace or refine before B2 development approval`

이 파일은 프로젝트의 **공식 시각·인터랙션 디자인 기준**입니다. 외부에서 준비한 `design.md`가 있다면 내용을 이 파일에 붙여넣거나 이 파일을 교체하되, 아래의 도메인 필수 규칙은 유지합니다.

## 1. Design direction

- Product character: 역사 아카이브의 신뢰감 + 전략 게임의 탐험성
- Desired feeling: 지적 호기심, 발견, 비교, 근거를 확인하는 재미
- Avoid: 고서풍 장식 과다, 모바일 가독성을 해치는 붓글씨, 출처보다 화려한 능력치 연출, 특정 인물을 객관적 최강처럼 보이게 하는 UI
- Primary platform: mobile-first responsive web

## 2. Information hierarchy

모든 핵심 분석 화면은 다음 순서를 기본으로 합니다.

1. 현재 보고 있는 인물·사건과 source mode
2. 점수 또는 핵심 관찰
3. 데이터 커버리지·신뢰도·기준 버전
4. 점수 구성 요소
5. 사건과 근거 카드
6. 원문 위치·판본·번역 정보
7. AI 설명과 제한사항

화면이 작아도 `점수 → 근거 → 출처` 경로를 숨기지 않습니다.

## 3. Source-layer language

다음 구분은 전 화면에서 동일한 텍스트 라벨과 시각 표현을 사용합니다.

| Layer | Required label | Meaning |
| --- | --- | --- |
| `HISTORY_BASE` | 정사 | 정사 본문 |
| `HISTORY_ANNOTATION` | 정사 주석 | 배송지주 등 주석·인용 사료 |
| `ROMANCE` | 연의 | 문학 작품의 서사 |
| `LATER_INTERPRETATION` | 연구·해석 | 현대 연구 또는 후대 해석 |
| `GAME_DATA` | 게임 | 외부/프로젝트 게임 수치 |

- 색상만으로 source layer를 구분하지 않습니다.
- 비교 화면에서는 동일 사건의 층위를 병렬로 보여줍니다.
- 사용자가 현재 선택한 source mode를 항상 확인할 수 있어야 합니다.

## 4. Score presentation

- 기본 점수, 사용자 커스텀 점수, 외부 게임 수치를 서로 다른 라벨과 컨테이너로 표시합니다.
- 점수와 함께 모델 버전, 데이터 커버리지, confidence 또는 “근거 부족” 상태를 표시합니다.
- `0`, `알 수 없음`, `해당 없음`을 시각적으로 구분합니다.
- 단일 종합 순위보다 구성 요소와 근거를 우선합니다.
- 사용자가 가중치를 바꾸면 “사용자 설정 점수” 표시를 제거할 수 없게 합니다.

## 5. Gamification

- 보상 대상: 양쪽 출처 확인, 반대 근거 확인, 점수 공식 열람, 가중치 실험, 근거 기반 퀴즈 완료
- 배지와 퀘스트는 역사적 진실을 맞혔다는 표현보다 탐구 행동을 설명합니다.
- 인기투표, 자극적 배신 포인트, 확률형 보상, 과도한 streak와 단일 최강 순위는 기본적으로 사용하지 않습니다.
- 게임 진행 정보가 출처·불확실성보다 강한 시각적 위계를 가져서는 안 됩니다.

## 6. Required component families

### SourceModeControl

- 정사 / 정사 주석 / 연의 / 비교 / 게임
- 키보드 사용 가능
- 선택 상태를 텍스트와 접근성 속성으로 전달

### ScoreCard

- 값, 단위, 모델 버전, coverage, confidence
- 기본/커스텀/외부 게임 유형
- 점수 분해로 이동하는 명확한 동작

### EvidenceCard

- evidence ID, source layer, 작품/판본, 위치
- 인용/프로젝트 번역/의역 상태
- 관련 인물·사건·코딩 라벨
- 모호성 또는 이견 표시

### ContributionBreakdown

- 점수 기여도와 가중치
- 각 기여도에서 evidence까지 이동
- 반올림 전후 합계 일관성

### QuestCard

- 학습/탐구 목표
- 완료 조건
- 확인한 근거와 아직 보지 않은 반대 근거
- 단순 클릭만으로 완료되지 않는 검증 가능한 상태

### AIAnswerPanel

- 현재 답변 모드
- claim별 evidence ref
- 근거 부족/답변 보류 상태
- AI 설명과 검증된 데이터의 시각적 구분

## 7. Required states

모든 데이터 기반 컴포넌트는 다음 상태를 설계합니다.

- default
- loading
- empty
- insufficient evidence
- partial result
- stale result
- error/retryable error
- permission unavailable
- LLM refused/abstained

빈 데이터와 0값을 같은 상태로 표시하지 않습니다.

## 8. Responsive layout

- Mobile: 한 열, source mode와 핵심 컨텍스트를 상단에 유지
- Tablet: 근거와 분석을 단계적으로 병렬 표시
- Desktop: 비교 모드에서 출처별 패널을 나란히 표시하되 읽기 순서를 유지
- 작은 화면에서 넓은 네트워크 그래프만 제공하지 말고 목록/요약 대안을 제공합니다.

## 9. Visualization

- 축, 단위, 분모, 분석 기간과 표본 범위를 표시합니다.
- centrality를 능력 또는 인기의 직접 척도로 이름 붙이지 않습니다.
- 정사와 연의 그래프의 정의가 다르면 직접 겹쳐 비교하지 않습니다.
- 차트의 정밀도는 분석 결과의 정밀도를 넘지 않습니다.
- 핵심 패턴에 텍스트 요약 또는 표 대안을 제공합니다.

## 10. Accessibility baseline

- semantic HTML과 논리적인 heading 구조
- 모든 기능의 키보드 접근
- 명확한 focus 표시와 dialog/drawer focus 관리
- 색상 외의 상태 구분
- 확대와 좁은 화면에서 정보 손실 없음
- 비동기 상태와 오류의 적절한 안내
- 애니메이션 감소 설정 지원
- 차트와 네트워크의 텍스트 대안

세부 검증은 `design/accessibility_checklist.md`를 따릅니다.

## 11. Project-specific tokens

실제 디자인 방향이 정해지면 아래를 채웁니다.

- Color palette: `[TBD]`
- Typography: `[TBD]`
- Spacing scale: `[TBD]`
- Radius/elevation: `[TBD]`
- Motion duration/easing: `[TBD]`
- Breakpoints: `[TBD]`
- Icon style: `[TBD]`

토큰은 코드에 흩어진 상수보다 중앙 theme/token 파일로 구현합니다.

## 12. Decision priority

충돌 시 다음 순서를 따릅니다.

1. 사용자 안전, 출처 무결성, 접근성
2. 승인된 제품 요구와 데이터/API 계약
3. 이 `design/DESIGN.md`
4. `wireframe_brief.md`와 `component_spec.md`
5. 개별 구현 편의

디자인 기준과 제품/데이터 계약이 충돌하면 임의로 해결하지 말고 Orchestrator에게 보고합니다.
