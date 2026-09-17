# Codex Repository Instructions

이 저장소에서 실행되는 모든 Codex 세션은 이 문서와 자신에게 배정된 `agents/<role>.md`를 함께 따라야 합니다.

## 시작 절차

1. `PROJECT_BRIEF.md`를 읽는다.
2. `handoffs/PROJECT_STATE.md`, `handoffs/DECISIONS.md`, `handoffs/CURRENT_TASK.md`를 읽는다.
3. `orchestration/workflow.yaml`, 관련 gate, 자신의 역할 지침을 읽는다.
4. `orchestration/execution_policy.yaml`과 `handoffs/APPROVALS.md`를 읽는다.
5. `agents/_three_kingdoms_domain.md`를 읽는다.
6. UX/UI·시각화·프론트엔드와 관련된 작업이면 `design/DESIGN.md`를 읽는다.
7. 입력 산출물, 현재 승인된 stage, 쓰기 허용 경로가 준비됐는지 확인한다.
8. 준비되지 않았으면 작업하지 말고 정확한 blocker를 기록한다.

## 공통 계약

- 저장소 파일이 유일한 공유 기억이다. 다른 도구의 채팅 기록을 안다고 가정하지 않는다.
- 한 번에 하나의 역할로 행동한다. 역할 변경은 Orchestrator가 `CURRENT_TASK.md`에 기록해야 한다.
- `CURRENT_TASK.md`의 범위와 허용 경로 밖의 변경은 하지 않는다.
- 기존 사용자 변경을 보존하며, 관련 없는 파일을 되돌리거나 정리하지 않는다.
- 입력이 모호하면 숨은 가정을 구현하지 말고 `handoffs/OPEN_QUESTIONS.md`에 결정이 필요한 질문을 기록한다.
- 결정은 `handoffs/DECISIONS.md`에 남긴다. 중요한 기술 결정은 `app/architecture/adr/`에 ADR로 남긴다.
- 단계 완료 시 `handoffs/LAST_HANDOFF.md`를 갱신한다.
- 현재 승인된 stage 밖의 선행 작업을 하지 않는다. boundary에서 결과 보고서를 작성하고 사용자 승인을 기다린다.
- 사용자의 침묵이나 모호한 답을 승인으로 해석하지 않는다.

## 연구·분석 규칙

- 논문 메타데이터와 근거를 구분한다. 초록만 읽은 자료는 원문 검토로 표시하지 않는다.
- 분석 계획은 결과 확인 전에 고정한다. 변경은 이유, 시각, 영향과 함께 기록한다.
- 통계·집계·변환은 코드로 실행하고 테스트한다. LLM은 숫자를 새로 계산하지 않는다.
- 모든 해석은 `analysis/outputs/result.json`의 필드 또는 `research/evidence_matrix.csv` 항목을 참조한다.
- 상관을 인과로 표현하지 않는다. 불확실성, 표본 한계, 외삽 위험을 노출한다.
- 개인정보 최소화, 데이터 출처, 라이선스, 계보를 기록한다.
- 모든 역사/문학 근거는 source layer, 판본, 위치, 인용/의역 여부를 포함한다.
- 정사, 정사 주석, 연의, 후대 해석, 게임 데이터는 결합 전에 분리 저장한다.
- `data/DATA_ZONES.md`를 따르며 private raw/analysis/curated 데이터와 runtime DB를 커밋하지 않는다.
- 앱은 승인된 curated export만 import하며 raw 또는 분석 workspace를 직접 읽지 않는다.

## 개발 규칙

- 계약 우선: 데이터 스키마 → 분석 결과 스키마 → API 계약 → UI 구현 순서를 유지한다.
- 실패·빈 상태·로딩·권한 부족·부분 데이터 상태를 정상 경로와 함께 구현한다.
- 새로운 동작에는 테스트를 추가한다. 버그 수정은 가능한 경우 재현 테스트부터 작성한다.
- 비밀 키나 실제 민감 데이터는 커밋하지 않는다. `.env.example`에는 키 이름만 둔다.
- 외부 의존성 추가는 목적, 대안, 라이선스/보안 영향을 기록한다.
- UX/UI 구현은 `design/DESIGN.md`, 승인된 사용자 여정과 데이터-UI 매핑을 함께 따라야 한다. 디자인 파일만 보고 데이터 의미를 추측하지 않는다.

## 검증과 보고

- 완료했다고 말하기 전에 관련 테스트와 검증 명령을 실행한다.
- 실행하지 못한 검증은 이유와 잔여 위험을 명확히 적는다.
- 완료 보고에는 변경 파일, 검증 결과, 미해결 위험, 다음 담당자를 포함한다.
- 자신이 만든 결과에 스스로 최종 Gate 승인을 부여하지 않는다.

## 우선순위

1. 사용자와 시스템의 명시적 지시
2. 데이터 안전·연구 무결성·보안
3. `PROJECT_BRIEF.md`와 승인된 결정
4. gate와 역할 계약
5. 구현 편의
