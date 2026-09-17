# System Architecture

Status: `DRAFT — populate after Research and Design Gates`

## Intended boundaries

| Component | Responsibility | Must not do |
| --- | --- | --- |
| Source registry | 판본·권리·위치·source layer | 분석 결론 생성 |
| Ingestion/coding pipeline | 근거 span, entity, code, adjudication | 미검증 자동 라벨 공개 |
| Analytics engine | 네트워크·구성지표·점수·confidence | LLM 자유 계산 |
| Knowledge/query layer | evidence-backed retrieval | 층위 무시 병합 |
| LLM interpretation | 모드별 설명·비교 | raw 데이터 통계 계산 |
| API | 계약·권한·run/version 제공 | 스키마 없는 출력 |
| Web app | 탐색·게임 루프·근거 표시 | 점수 의미 재해석 |
| Evaluation pipeline | regression·grounding·Gate 지표 | 제품 데이터 수정 |

## Trust boundaries

- Browser ↔ API
- API ↔ database/graph store
- Backend ↔ external LLM
- Pipeline ↔ source files
- Admin/adjudicator ↔ public content

## Required decisions

- Storage: relational, graph, or hybrid `[TBD]`
- Background jobs and queue `[TBD]`
- LLM provider/model and data policy `[TBD]`
- Authentication and roles `[TBD]`
- Deployment topology `[TBD]`
- Observability and cost budget `[TBD]`

## Failure principles

- 근거 조회 실패 시 추정 답변 대신 명시적 unavailable 상태
- 분석 버전 불일치 시 결과 표시 차단
- LLM 실패 시 검증된 수치/근거 UI는 유지하되 자동 설명은 비활성
- source layer 또는 evidence ref 검증 실패 시 공개 경로에서 격리

