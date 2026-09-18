# Problem Definition

Status: `HYPOTHESIS — finalize at B0`

- User problem: 삼국지 인물·사건을 정사와 연의의 차이를 보존한 채 데이터로 분석하고 이해하는 것이 어렵다 (PROJECT_BRIEF.md §1).
- Current workaround: `[TBD — no direct user research yet; PROJECT_BRIEF.md does not state what users currently do instead]`
- Why existing options fail: 기존 콘텐츠는 정사와 연의를 혼합하고, 능력치가 불투명하며, 출전 없는 AI 답변과 정적인 인물 소개에 그친다 (PROJECT_BRIEF.md §1 "기존 방식의 한계").
- Decision or action to improve: 사용자가 인물 평가를 그대로 소비하지 않고 사건·출처·분석 기준을 직접 확인하며 비교 가설을 탐색하게 한다. 학습 게임 개념이 선택되면 사용자가 분석 개념을 직접 적용하고 결과를 설명할 수 있어야 한다 (PROJECT_BRIEF.md §1).
- Evidence the problem exists: `[TBD — PROJECT_BRIEF.md states the problem as a hypothesis, not as validated user research; no interview/usage evidence is on file]`
- Desired measurable outcome: 사용자 노출 claim의 근거 연결률 100%, 정사/연의 출처 혼동 오류 0건(PROJECT_BRIEF.md §7 성공 지표). 사용자 행동 지표(재방문, 완료율 등)는 제품 개념이 B0에서 정해진 뒤에만 정의 가능 `[TBD]`.
- Harm if wrong: 허구를 역사 사실로 오인, 번역/판본 왜곡, 인기 편향 강화, 불투명한 점수의 권위화, 저작권 침해 (PROJECT_BRIEF.md §5).
- Explicit non-goals: 전 인물 데이터베이스, 성격/정신 진단, 단일 "최강" 순위, 사용자 간 경쟁, 자동 생성 사실의 무검수 공개 (PROJECT_BRIEF.md §4 "명시적 제외"). 게임화 점수를 실제 인간 집단/현대인 평가에 전용하는 것, 출처 없는 사실 생성, 정사와 연의의 무표시 혼합도 금지 (PROJECT_BRIEF.md §5 "금지된 사용").

## First vertical slice

`For 삼국지 팬이자 비전공자~매니아를 아우르는 사용자 (PROJECT_BRIEF.md §2), use 관도대전 또는 적벽대전 관련 정사/연의 근거 구절 (D0/R0 확정 대기, 인물 3~5명·근거 20~40개 규모) 로 만든 검증된 분석을 evidence ID가 달린 점수·비교 설명으로 전달하고, [explorer / learning game / hybrid — B0 결정 대기] 형태로 제공하여 [사용자가 정사·연의 차이를 스스로 근거로 확인하는 경험 — 세부 학습/의사결정 목표는 B0 이후 확정] 하게 한다.`

이 slice의 핵심 빈칸(분석 유형, 제품 형태, 최종 학습/의사결정 목표)은 concept_decision.yaml의 B0 결정 없이는 추측으로 채우지 않는다.
