# Three Kingdoms Analytics Framework (TKAF) Starter

《삼국지》 정사·주석과 《삼국지연의》를 분리해 재현 가능한 데이터로 만들고, 제품 형태를 **탐색 서비스 / 데이터 분석 학습 게임 / 하이브리드** 중 증거를 바탕으로 결정하기 위한 Codex + Claude Code 혼합형 멀티에이전트 템플릿입니다.

핵심 원칙은 세 가지입니다.

1. 채팅 기록이 아니라 저장소의 산출물이 프로젝트의 기억입니다.
2. 계산은 코드가, 설명은 LLM이 담당합니다.
3. 같은 stage의 독립 track은 병렬로 수행하지만 stage boundary는 사용자가 명시적으로 승인해야 넘습니다.
4. 실제 raw·분석·curated 데이터와 runtime DB는 Git에 커밋하지 않습니다.

## 가장 먼저 할 일

1. 저장소 루트에서 메인 AI를 실행하고 `first-prompt.md`의 프롬프트를 전달합니다.
2. 실제 raw corpus는 `data/PRIVATE_DATA_SETUP.md`에 따라 저장소 밖 또는 `data/private/`에 둡니다.
3. `python scripts/validate_structure.py`와 `python scripts/check_data_boundaries.py`를 실행합니다.
4. S0에서 Product Concept, Raw Data Inventory, Research Feasibility를 병렬로 수행합니다.
5. S0 결과를 문서화하고 B0 사용자 승인을 받은 뒤에만 다음 단계로 진행합니다.
6. 제품 방향이 결정된 뒤 첫 번째 세로 절단(vertical slice)은 아래 범위만 완주합니다.
   - 방법론 논문 3~5편
   - 정사/연의에서 동일 사건 1개
   - 인물 3~5명과 근거 구절 20~40개
   - 재현 가능한 Python 분석 1개
   - 구조화 JSON 결과 1개
   - 근거 연결된 LLM 해석 1개
   - 정사/연의 비교 + 점수 근거 화면 1개
   - 평가 결과 1개

## 운영 흐름

```text
S0 Discovery
├─ Product Concept
├─ Raw Data Feasibility
└─ Research Method
        ↓ B0 사용자 승인
S1 Definition
├─ Product Planning
└─ Sample Data/Analysis
        ↓ B1 사용자 승인
S2 UX/UI + LLM Contract
        ↓ B2 개발 시작 승인
S3 Architecture + Implementation + QA
        ↓ B3 사용자 승인
S4 Release Decision
```

각 단계는 다음 순서로만 넘깁니다.

```text
Agent → artifact → QA/Evaluator → stage report → user approval → next stage
```

승인을 기다리는 동안 다음 stage의 “준비 작업”도 하지 않습니다. 문제나 논의사항은 `OPEN_QUESTIONS.md`, 결정은 `DECISIONS.md`, 승인은 `APPROVALS.md`에 기록합니다.

## 포함된 에이전트

| 역할 | 기본 추천 실행기 | 핵심 책임 |
| --- | --- | --- |
| Orchestrator | 둘 중 하나 | 순서, 의존성, 승인, 재작업 라우팅 |
| Researcher | Claude Code | 검색 프로토콜, 근거 행렬, 분석 기준 |
| Data Engineer | Codex | 수집·정제·스키마·계보·재현성 |
| Statistician | Codex 중심 + 교차 검토 | 사전 분석 계획, 통계·모델링, 수치 검증 |
| LLM Analyst | 둘 중 하나 | 계산 결과를 근거로 제한된 해석 생성 |
| Product Manager | Claude Code | 문제·사용자·범위·수용 기준 |
| UX Designer | Claude Code | 흐름·와이어프레임·데이터-UI 연결 |
| Architect | Codex | 시스템 경계, 계약, 보안, ADR |
| Backend | Codex | API·잡·저장소·관측성 |
| Frontend | Codex | 접근 가능한 UI·상태 처리·시각화 |
| QA | Codex | 자동 테스트와 재현 가능한 결함 보고 |
| Evaluator | 교차 모델 권장 | 독립 점수, 차단 이슈, 재작업 판정 |

추천 실행기는 규칙이 아니라 초기 배치입니다. 동일 모델이 산출물과 최종 평가를 모두 담당하지 않도록 교차 검토하는 편이 좋습니다.

## VS Code에서 사용하는 법

### 단일 작업

- Codex: 저장소 루트에서 `codex`
- Claude Code: 저장소 루트에서 `claude`
- 첫 지시: “루트 지침과 `handoffs/CURRENT_TASK.md`를 읽고, 지정된 역할 파일을 따른 뒤 작업하라.”

### 병렬 작업

동시에 수정할 때는 같은 작업 디렉터리를 공유하지 말고 Git worktree를 분리합니다. 예시는 `docs/WORKTREE_PLAYBOOK.md`에 있습니다. 병렬화는 입력 계약이 고정되고 쓰기 경로가 겹치지 않는 작업만 허용합니다.

### 역할 호출 예시

```text
당신은 Researcher다.
agents/researcher.md, PROJECT_BRIEF.md, orchestration/workflow.yaml,
handoffs/CURRENT_TASK.md를 읽고 허용된 경로에만 산출물을 작성하라.
완료 후 handoffs/HANDOFF_TEMPLATE.md 형식으로 인계 내용을 갱신하라.
```

## 게이트와 평가

- `orchestration/execution_policy.yaml`: stage 병렬화와 사용자 승인 규칙
- `orchestration/gates.yaml`: 단계별 필수 산출물과 차단 조건
- `orchestration/scoring.yaml`: 100점 평가표와 최소 통과 점수
- `evals/eval_input.example.json`: 자동 평가 입력 예시
- `evals/run_eval.py`: 결정론적 지표를 계산하는 기본 평가기

실행 예시:

```bash
cp evals/eval_input.example.json evals/eval_input.json
python evals/run_eval.py evals/eval_input.json evals/eval_results.json
```

자동 점수만으로 릴리스하지 않습니다. 통계 방법 적합성, 근거의 직접성, 사용자 위험은 사람 또는 독립 모델이 검토해야 합니다.

## 주요 파일

```text
AGENTS.md                     Codex 공통 지침
CLAUDE.md                     Claude Code 공통 지침
first-prompt.md               메인 AI 팀장에게 전달할 최초 지침
PROJECT_BRIEF.md              프로젝트의 단일 목표 문서
agents/                       역할별 실행 지침
orchestration/                흐름·게이트·라우팅·점수
handoffs/                     현재 작업·결정·인계 기록
research/                     검색 프로토콜·논문·근거·분석 기준
data/                         private raw/analysis/app export/DB 분리 규칙
analysis/                     분석 계획·결과 계약·LLM 계약
product/                      문제·사용자·기능·화면·수용 기준
design/                       공식 DESIGN.md, UX/UI 명세와 체크리스트
app/                          frontend/backend 경계
tests/                        통합·계약·회귀 테스트
evals/                        독립 평가 입력과 결과
docs/                         운영 플레이북
```

## 중요한 금지 사항

- 결과를 본 뒤 분석 가설이나 1차 지표를 조용히 바꾸지 않습니다.
- 논문 원문을 확인하지 않고 인용을 만들지 않습니다.
- LLM에게 원시 데이터의 수치 계산을 맡기지 않습니다.
- 평가 기준을 작업 도중 낮추지 않습니다.
- 민감 데이터, 비밀 키, 원문 데이터셋을 Git에 커밋하지 않습니다.
- 다른 에이전트의 영역을 대규모로 고치지 않습니다.
- 정사와 연의를 하나의 사실 테이블로 합치지 않습니다.
- 언급 빈도만으로 능력치를 만들거나, 기록 공백을 능력 부족으로 해석하지 않습니다.
- 게임 점수와 역사적 사실·연구 결론을 같은 의미로 표시하지 않습니다.
- 확인되지 않은 번역문/문장/출전을 원문 인용처럼 표시하지 않습니다.
- 제품 방향을 S0 결과 전에 학습 게임이나 탐색 서비스로 확정하지 않습니다.
- 앱이 raw/analysis workspace를 직접 읽게 하지 않습니다.
- 승인되지 않은 stage를 미리 시작하지 않습니다.

## 실제 데이터와 앱 DB

```text
private raw 원본 (불변, Git 제외)
→ private analysis 데이터 (실제 분석, Git 제외)
→ 승인된 curated app export (DB 입력, 기본 Git 제외)
→ runtime application DB (Git 제외)
```

저장소에는 스키마, 파이프라인·import 코드, migration, 안전한 manifest template, 합성 fixture만 남깁니다. 자세한 내용은 `data/DATA_ZONES.md`와 `data/APP_DATABASE_POLICY.md`를 따릅니다.

## design.md 적용

프로젝트의 공식 디자인 기준은 `design/DESIGN.md`입니다. 실제로 사용할 design.md가 있다면 이 파일의 내용을 교체하거나 합치면 됩니다. UX Designer와 Frontend Agent는 이 파일을 필수 입력으로 읽으며, Design Gate는 파일이 여전히 `STARTER` 상태이면 통과하지 않습니다.

## 완료 정의

프로젝트는 단순히 “화면이 뜨는 상태”가 아니라 다음을 만족해야 합니다.

- 분석 결과가 데이터와 코드에서 재현됨
- 모든 사용자 노출 주장에 근거 또는 불확실성 표시가 있음
- 데이터 계약과 API 계약이 테스트됨
- 핵심 사용자 흐름이 접근성 기준과 오류 상태를 포함함
- 차단 이슈가 0개이고 Release Gate가 통과됨
