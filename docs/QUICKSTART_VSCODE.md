# VS Code Quickstart

## 1. 프로젝트 열기

ZIP을 풀고 VS Code에서 폴더를 엽니다. 처음에는 앱 의존성을 설치할 필요가 없습니다. 템플릿 검증만 실행합니다.

```bash
python scripts/validate_structure.py
python -m unittest discover -s tests -p 'test_*.py'
```

## 2. 팀장 AI 시작

VS Code Codex 채팅 또는 터미널 CLI에서 `first-prompt.md`의 `BEGIN PROMPT`~`END PROMPT`를 전달합니다. 실제 raw 데이터 경로가 정해졌다면 `[PRIVATE_DATA_PATH]`를 바꿉니다.

```text
first-prompt.md를 읽고 S0의 C0 Product Concept, D0 Raw Inventory,
R0 Research Feasibility만 실행해. stage boundary를 넘지 마.
```

실제 `design.md`가 준비돼 있다면 구현 전에 그 내용을 `design/DESIGN.md`에 넣고 `Status: STARTER`를 승인된 상태로 바꿉니다. UX/UI와 Frontend Agent는 이 파일을 자동 작업 입력으로 사용합니다.

## 3. S0 병렬 실행

팀장 AI는 같은 stage 안에서 다음 작업만 병렬로 배정할 수 있습니다.

- Product Manager: 세 가지 제품 가설 비교
- Data Engineer: raw corpus read-only inventory
- Researcher: 방법론과 분석 가능성 검토

S0 완료 후 `S0_COMPLETION.md`와 B0 승인 질문이 나오면 결과를 검토하고 명시적으로 승인/수정/거절합니다.

## 4. Codex와 Claude Code를 번갈아 쓰기

- Claude Code가 기획/연구 문서를 만들었다면 Codex 세션에는 채팅을 설명하지 말고 `LAST_HANDOFF.md`를 읽게 합니다.
- Codex가 코드/스키마/테스트를 만들었다면 Claude Code에게 변경 파일과 테스트 결과를 저장소에서 검토하게 합니다.
- 산출물 작성자와 Evaluator는 가능하면 다른 모델/세션으로 둡니다.
- B0/B1/B2/B3 승인 전에는 다음 stage 세션을 시작하지 않습니다.

## 5. 평가

실제 증거로 `evals/eval_input.json`을 만든 뒤:

```bash
python evals/run_eval.py evals/eval_input.json evals/eval_results.json
```

자동 계산기는 선언된 점수의 산술과 차단 조건만 검사합니다. 연구 타당성 점수는 근거 경로와 독립 검토가 필요합니다.
