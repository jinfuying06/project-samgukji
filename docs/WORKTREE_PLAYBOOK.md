# Git Worktree Playbook

## 언제 병렬화할까

다음을 모두 만족할 때만 backend/frontend 또는 독립 검토를 병렬로 수행합니다.

- 입력 계약이 승인됨
- 각 작업의 쓰기 경로가 겹치지 않음
- 공통 파일 수정 담당자가 한 명임
- merge 순서와 검증 담당이 정해짐

## 예시

저장소에서 첫 커밋을 만든 뒤, 저장소의 **부모 디렉터리**에서 역할별 worktree를 만듭니다.

```bash
git worktree add ../tkaf-backend -b agent/backend
git worktree add ../tkaf-frontend -b agent/frontend
git worktree add ../tkaf-review -b agent/review
```

각 VS Code 창을 별도 폴더로 열고 역할별 세션을 시작합니다.

```text
tkaf-backend  → app/backend, backend tests
tkaf-frontend → app/frontend, frontend tests
tkaf-review   → read-only review, evals output only
```

## 공유 파일 소유권

병렬 작업 중 다음 파일은 Orchestrator만 수정하는 것을 권장합니다.

- `PROJECT_BRIEF.md`
- `handoffs/PROJECT_STATE.md`
- `handoffs/CURRENT_TASK.md`
- `orchestration/*.yaml`
- `app/architecture/api_contract.yaml`

필요한 변경은 직접 고치지 않고 handoff에 change request로 적습니다.

## Merge 전 확인

```bash
python scripts/validate_structure.py
python -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

같은 파일 충돌은 자동 선택하지 말고, 승인된 계약과 최신 decision log를 기준으로 해결합니다.

