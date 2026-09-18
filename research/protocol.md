# Literature Review Protocol

> 검색 결과를 본 뒤 조용히 바꾸지 않습니다. 변경 시 버전, 이유, 영향, 승인자를 기록합니다.

## Review question

- Population / context: 《삼국지》 정사(裴松之注 포함)와 《삼국지연의》의 인물·사건·관계에 대한 텍스트 근거(evidence span) 및 이를 다루는 계량역사학·내용분석·네트워크분석·지식그래프·XAI·내러티브 시각화·게임 밸런스 방법론 문헌.
- Exposure / intervention: 근거 구절을 재현 가능한 코딩 규칙(코드북)으로 라벨링하고, 그 라벨을 설명 가능한 지표(리더십/군사/행정/신뢰 등 구성 지표, 네트워크 지표, 정사-연의 괴리도)로 집계하는 방법.
- Comparator: (a) 정사 vs 연의를 동일 방법으로 각각 계산한 뒤 비교, (b) 빈도 기반 단순 집계 vs 근거 기반 코딩 집계.
- Outcome: 지표의 재현성(동일 입력→동일 출력), 근거 추적성(지표→코드→evidence ID), 코더 간 합치도, 사용자에게 노출 가능한 불확실성 표현 방식.
- Study types: 방법론 논문(계량역사학, 내용분석, 역사 네트워크 분석, 디지털 인문학 지식그래프, XAI, 내러티브 시각화), 삼국지/역사 텍스트에 실제 적용한 응용 논문, 게임 밸런스 분석 논문(학습 게임 가설이 선택될 경우에만 적용). 1차 사료 자체(정사/연의 원문)는 이 문헌 검토가 아니라 `data/`와 D0 인벤토리에서 별도로 다룬다.

## Sources and search

| Source | Query | Date searched | Coverage notes |
| --- | --- | --- | --- |
| Web search (general, via agent WebSearch tool) | "Romance of the Three Kingdoms social network analysis academic paper" | 2026-09-17 | arXiv/IEEE/ResearchGate 결과 다수, 직접 관련도 높음 (CR-001~003) |
| Web search (general) | "cliometrics quantitative history methodology review paper" | 2026-09-17 | 1차 문헌 직접 링크 미확보, encyclopedia 요약만 확인 (CR-006, unverified) |
| Web search (general) | "content analysis coding manual historical text intercoder reliability Krippendorff alpha" | 2026-09-17 | 실무 가이드 논문 확보 (CR-004), 개념 개요만 확보 (CR-005) |
| Web search (general) | "digital humanities knowledge graph historical figures methodology paper" | 2026-09-17 | arXiv 사전인쇄 2건 확보 (CR-007, CR-008) |
| Web search (general) | "explainable AI interpretable scoring model survey paper" | 2026-09-17 | 유사 제목의 서베이 다수 존재, 정확한 저자/판본 미교차검증 (CR-009, CR-010) |
| Web search (general) | "narrative visualization design space Segel Heer paper" | 2026-09-17 | 저자·DOI·1차 PDF까지 확보, 가장 강한 검증 수준 (CR-011) |
| Web search (general) | "game balance analytics methodology academic paper" | 2026-09-17 | arXiv+DOI 확보 1건, 기관 리포지토리 확보 1건 (CR-012, CR-013) |

전체 결과는 `research/candidate_reading_list.csv`에 기록. **이 표의 항목은 모두 candidate이며, 저자/venue/주장을 원문 대조로 검증하기 전에는 `papers.csv`로 승격하지 않는다** (S1 R1 범위).

## Eligibility

### Include

- 정사/연의/역사 텍스트에 재현 가능한 코딩 또는 네트워크 분석을 적용한 방법론 또는 응용 논문
- 텍스트 기반 내용분석의 코더 합치도 측정·보고 방법을 다루는 논문
- 설명 가능한 지표/점수 설계(XAI, 해석가능 모델)를 다루는 논문
- 데이터 기반 서사 시각화 또는 근거-표시 UI 설계 원칙을 다루는 논문
- (학습 게임 가설 선택 시에만) 게임 밸런스의 데이터 기반 분석 방법론

### Exclude

- 저자/venue/식별자를 이번 세션에서 검증하지 못한 문헌 (candidate 상태로만 유지, "unverified_do_not_cite" 표시)
- 삼국지 콘텐츠를 다루지만 방법론 설명 없이 서사 요약/팬 해설만 제공하는 자료
- 원문을 확인할 수 없는 블로그/미디어 기사류 (배경 이해용으로만 참고, 인용 금지)

## Screening

- Deduplication method: candidate_id 기준 수동 중복 제거 (자동 파이프라인은 S1에서 papers.csv 전환 시 도입)
- Title/abstract reviewers: 이번 S0/R0 세션에서는 1인(Researcher 역할 에이전트)이 검색 스니펫만 검토함. **원문 전체를 읽지 않았으므로 fulltext_status는 전부 "not_reviewed"이다.**
- Full-text reviewers: `[TBD — S1에서 배정]`
- Disagreement resolution: `[TBD — S1에서 최소 2인 검토 체계 확정 시 정의]`

## Extraction fields

- Design, setting, population, sample size
- Variable and outcome definitions
- Statistical/modeling method
- Effect estimate and uncertainty
- Missing-data handling
- Bias, limitations, applicability

## Quality/risk-of-bias approach

- Instrument or rubric: `[TBD]`
- Calibration sample: `[TBD]`

## Protocol changes

| Version | Date | Change | Reason | Impact | Approved by |
| --- | --- | --- | --- | --- | --- |
| 0.1 | `[date]` | Initial draft | - | - | `[owner]` |
| 0.2 | 2026-09-17 | S0/R0: filled review question, sources/search log, eligibility, screening status; added candidate_reading_list.csv | S0 feasibility deliverable per orchestration/workflow.yaml R0 track | Researcher (S0/R0) | accepted |

