# Claude Code Repository Instructions

이 저장소는 Codex와 Claude Code가 번갈아 작업하도록 설계되었습니다. 채팅 간 기억을 가정하지 말고 저장소를 통해 상태를 복원하십시오.

## 세션 시작

아래를 순서대로 읽습니다.

1. `PROJECT_BRIEF.md`
2. `handoffs/PROJECT_STATE.md`
3. `handoffs/DECISIONS.md`
4. `handoffs/CURRENT_TASK.md`
5. 배정된 `agents/<role>.md`
6. 관련 `orchestration/*.yaml`
7. `handoffs/APPROVALS.md`
8. `agents/_three_kingdoms_domain.md`
9. UX/UI·시각화·프론트엔드 작업이면 `design/DESIGN.md`

현재 작업에 역할, 입력, 산출물, 쓰기 경로, 완료 조건이 없으면 작업을 시작하지 말고 누락을 명시하십시오.

## 행동 원칙

- 한 세션에서 하나의 역할만 수행합니다.
- 계획·검토 역할일 때 승인 없이 구현 범위를 확장하지 않습니다.
- 구현 역할일 때 제품 요구와 데이터 계약을 임의로 다시 쓰지 않습니다.
- 긴 설명보다 검증 가능한 저장소 산출물을 남깁니다.
- 다른 모델이 이어받을 수 있도록 약어, 숨은 전제, 채팅 참조를 피합니다.
- 같은 파일을 다른 worktree에서 동시에 수정하지 않습니다.
- 디자인 작업자는 `design/DESIGN.md`를 시각 기준으로 사용하되 제품 요구, 데이터 계약, 접근성보다 우선시키지 않습니다.
- 중요한 판단은 `DECISIONS.md`, 열린 질문은 `OPEN_QUESTIONS.md`에 기록합니다.
- 승인된 stage 안에서만 작업하고 boundary에서는 완료 보고서와 승인 질문을 남긴 뒤 기다립니다.
- 실제 raw·분석·curated 데이터 및 runtime DB는 커밋하지 않습니다.

## 연구·LLM 안전

- 존재 여부를 확인하지 않은 논문, DOI, 인용문을 만들지 않습니다.
- 2차 요약만 본 경우 그 사실을 명시합니다.
- 데이터 결과와 문헌 주장을 섞지 말고 출처 유형을 구분합니다.
- LLM 해석은 허용된 JSON 입력만 사용하며, 근거 ID와 불확실성을 포함합니다.
- 정사·주석·연의·후대 게임 자료를 동일한 사실 층위로 병합하지 않습니다.
- 의료·법률·금융 등 고위험 결론은 사람 검토 없이는 최종 권고로 표현하지 않습니다.

## 인계

작업이 끝나면 `handoffs/HANDOFF_TEMPLATE.md` 형식으로 `handoffs/LAST_HANDOFF.md`를 갱신합니다. 반드시 실제 실행한 검증, 실패한 검증, 변경 경로, 다음 작업, blocker를 적습니다.

Evaluator 역할이 아니라면 Gate 통과 여부를 스스로 확정하지 않습니다. Evaluator도 최종 진행 결정은 하지 않으며 Orchestrator에게 점수와 근거를 제출합니다.
