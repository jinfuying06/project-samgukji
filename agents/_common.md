# Common Agent Contract

## 세션 입력

모든 에이전트는 다음을 읽습니다.

- `PROJECT_BRIEF.md`
- `handoffs/PROJECT_STATE.md`
- `handoffs/DECISIONS.md`
- `handoffs/CURRENT_TASK.md`
- `orchestration/workflow.yaml`
- `orchestration/execution_policy.yaml`
- `handoffs/APPROVALS.md`
- 자신의 역할 파일
- `agents/_three_kingdoms_domain.md`
- UX/UI·시각화·프론트엔드 작업인 경우 `design/DESIGN.md`

## 실행 규칙

1. 입력, 산출물, 완료 조건, 허용 쓰기 경로를 작업 전에 재진술한다.
2. 읽기와 진단은 넓게 할 수 있지만 쓰기는 지정 경로로 제한한다.
3. 추측이 결과를 바꾸면 `OPEN_QUESTIONS.md`에 기록하고 기다린다.
4. 작업 범위 안의 사소하고 되돌릴 수 있는 결정은 직접 내리고 기록한다.
5. 재현 가능한 명령, seed, 버전, 입력 해시를 가능한 한 남긴다.
6. 다른 역할의 승인된 산출물을 바꿔야 하면 직접 수정하지 말고 변경 요청을 만든다.
7. 완료 시 `LAST_HANDOFF.md`를 갱신한다.
8. 현재 stage boundary에 도달하면 `PHASE_COMPLETION_TEMPLATE.md`로 보고하고 사용자 승인을 기다린다.

## 공통 금지

- 출처, 실행 결과, 테스트 결과를 꾸며내지 않는다.
- 실제로 실행하지 않은 검증을 통과로 표시하지 않는다.
- 민감정보나 자격 증명을 저장소에 기록하지 않는다.
- Gate 점수를 올리기 위해 기준, 데이터, 테스트를 약화하지 않는다.
- 범위 밖 리팩터링이나 대규모 포맷팅을 하지 않는다.
- 오류를 숨기는 fallback이나 빈 예외 처리를 추가하지 않는다.
- 승인되지 않은 다음 stage를 미리 시작하거나 “준비 차원”에서 파일을 만들지 않는다.
- private 데이터나 runtime DB를 커밋하지 않는다.

## 표준 완료 보고

- 한 일과 하지 않은 일
- 생성/변경 파일
- 실행한 검증과 결과
- 남은 위험/가정
- 막힌 항목과 필요한 결정
- 다음 추천 역할
