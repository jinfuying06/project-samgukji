# Decision Log

결정은 append-only로 기록합니다. 바뀐 결정은 기존 행을 지우지 말고 새 행에서 `supersedes`를 연결합니다.

| ID | Date | Decision | Rationale | Owner | Status | Supersedes |
| --- | --- | --- | --- | --- | --- | --- |
| D-001 | `[date]` | Artifacts are shared memory | Codex와 Claude Code 간 채팅 의존 제거 | Orchestrator | accepted | - |
| D-002 | `[date]` | Code computes; LLM explains | 수치 오류와 환각 위험 분리 | Research owner | accepted | - |
| D-003 | `[date]` | Evaluator is independent | 자기평가 편향 축소 | Product owner | accepted | - |
| D-004 | `[date]` | Product form remains undecided through S0 | 방향 변경 비용과 조기 확정 방지 | Human owner | accepted | - |
| D-005 | `[date]` | Product and data feasibility run in parallel inside S0 | 독립적인 불확실성을 빠르게 검증 | Orchestrator | accepted | - |
| D-006 | `[date]` | Stage transitions require explicit human approval | 기획·분석·개발 범위 통제 | Human owner | accepted | - |
| D-007 | `[date]` | Raw, analysis, curated app export, and runtime DB are separate private zones | 연구 재현성과 앱 serving 분리 | Data owner | accepted | - |
