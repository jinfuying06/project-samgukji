# Data Workspace

이 프로젝트는 **원본 corpus**, **실제 분석용 데이터**, **앱 DB 입력용 데이터**, **실행 DB**, **테스트 fixture**를 분리합니다. 실제 데이터와 DB 파일은 Git에 커밋하지 않습니다.

## 저장 구역

```text
data/
├── private/                  실제 데이터: 전부 Git 제외
│   ├── raw/                  원본 크롤링 데이터, 불변
│   │   └── inbox/            처음 넣는 위치
│   ├── analysis/             정규화 corpus, 분석 테이블, 모델 입력
│   └── curated/              검수 완료된 앱 DB import용 export
├── runtime/                  SQLite/임시 DB/캐시, 전부 Git 제외
├── schemas/                  커밋: 데이터 계약(JSON Schema)
├── manifests/                커밋 가능: 안전한 템플릿·비민감 메타데이터
├── fixtures/                 커밋 가능: 합성 또는 권리 확인된 극소량 테스트 자료
├── DATA_ZONES.md
├── PRIVATE_DATA_SETUP.md
└── APP_DATABASE_POLICY.md
```

대규모 또는 비공개 데이터는 저장소 밖에 두고 `.env`의 `TKAF_PRIVATE_DATA_ROOT`로 연결하는 방식을 우선합니다.

## 데이터 흐름

```text
private/raw (immutable)
  → inventory + checksum
  → private/analysis/normalized
  → private/analysis/tables + results
  → human/evaluator approval
  → private/curated/app_export
  → validated import job
  → runtime application database
```

앱은 `private/raw`나 임시 분석 테이블을 직접 읽지 않습니다. 앱 DB에는 승인된 curated export만 들어갑니다.

## 첫 raw 데이터 투입

분류가 확실하면 아래에 놓습니다.

```text
data/private/raw/inbox/history_base_zh/
data/private/raw/inbox/history_annotations_zh/
data/private/raw/inbox/romance_zh/
```

분류가 불확실하면 원래 폴더 구조 그대로 다음에 놓습니다.

```text
data/private/raw/inbox/unclassified/<original-folder>/
```

그다음 Data Engineer는 원본을 이동하거나 덮어쓰지 않고 인벤토리만 작성합니다. `PRIVATE_DATA_SETUP.md`를 따릅니다.

## Commit policy

커밋 가능:

- 스키마, migration, import/analysis 코드
- 데이터 사전과 비민감 manifest
- 합성 fixture
- 집계 결과 중 권리·재식별·원문 유출 검토를 통과한 것

커밋 금지:

- 크롤링 원문과 현대 번역문
- 실제 분석용 정규화 corpus와 feature table
- 전체 evidence span export
- 임시/최종 SQLite·DuckDB·vector DB
- embeddings, caches, checkpoints
- 원문을 복구할 수 있는 대량 파생 데이터

