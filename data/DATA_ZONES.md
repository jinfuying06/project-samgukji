# Data Zone Contract

## Zone A — Immutable source raw

- Path: `${TKAF_PRIVATE_DATA_ROOT}/raw` 또는 `data/private/raw`
- Purpose: 크롤링 당시 파일의 원형 보존
- Allowed writes: 최초 복사와 manifest 생성뿐
- Forbidden: rename, overwrite, encoding conversion in place, source-layer merge
- Version identity: original relative path + byte size + SHA-256

## Zone B — Private analysis workspace

- Path: `${TKAF_PRIVATE_DATA_ROOT}/analysis` 또는 `data/private/analysis`
- Purpose: 정규화 corpus, 문단/구절 테이블, 코딩 결과, EDA, 통계·네트워크 입력/출력
- Git: never commit
- Rebuild requirement: raw + committed pipeline + manifest에서 재생성 가능해야 함
- Important: 이 구역의 데이터는 앱이 직접 소비하지 않음

## Zone C — Approved app export

- Path: `${TKAF_PRIVATE_DATA_ROOT}/curated/app_export` 또는 `data/private/curated/app_export`
- Purpose: 검수 완료된 인물·사건·근거 메타데이터·점수·관계의 DB import package
- Git: never commit by default
- Entry criteria: schema, source-layer, entity, evidence/rights, model/version, export approval

## Zone D — Runtime database

- Path: `data/runtime` 또는 별도 database service
- Purpose: 앱 검색/화면/LLM retrieval용 serving database
- Git: never commit
- Contents: migrations로 생성하고 approved app export를 import
- Rule: 로컬 DB 파일은 소스 오브 트루스가 아님

## Zone E — Repository-safe assets

- Paths: `data/schemas`, `data/manifests`, `data/fixtures`
- Purpose: 계약, 안전한 메타데이터, 테스트
- Git: commit allowed
- Fixture rule: 합성 또는 명시적으로 권리가 확인된 극소량만

## Cross-zone controls

| From | To | Allowed only when |
| --- | --- | --- |
| Raw | Analysis | reproducible pipeline, no overwrite |
| Analysis | Curated | validation + rights + evaluator approval |
| Curated | Runtime DB | versioned import and transaction |
| Any private zone | Fixtures | synthetic/redacted and independently reviewed |
| Runtime DB | Analysis | forbidden by default; prevent feedback contamination |

