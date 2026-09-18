# System Architecture — 적벽대전 Vertical Slice (Hybrid)

Status: `S3/E0 ACTIVE — 2026-09-17`. Supersedes the generic `DRAFT` scaffold below the line. Scoped to the Hybrid concept's 적벽대전 vertical slice (B0–B2 approved: `handoffs/DECISIONS.md#D-009`–`#D-019`). Designed to hold when the cast/evidence set expands (D-016) — no component below assumes a fixed person count or evidence count.

## Component boundaries

| Component | Responsibility | Reads | Writes | Must not do |
| --- | --- | --- | --- | --- |
| Ingestion pipeline (`data/pipelines/build_chibi_sample.py`) | Raw → private analysis paragraphs, source-layer split | `${TKAF_PRIVATE_DATA_ROOT}/raw` (read-only) | `${TKAF_PRIVATE_DATA_ROOT}/analysis/**` | Touch runtime DB; run at request time |
| Research coding (R1, human/LLM) | Evidence selection + labeling | private analysis candidate pool | `research/evidence_matrix.csv`, `research/coding_manual.md` | Compute statistics itself (that's the next component) |
| Analysis pipeline (`analysis/pipelines/compute_chibi_result.py`) | Deterministic aggregation: coverage, label frequency, divergence, network edges | `research/evidence_matrix.csv` | `analysis/outputs/result.json`, `run_manifest.json` | Ask an LLM to compute a number; run at request time |
| **Curated Export Transform** (new, addresses D-018 — not yet implemented, owned by Data Engineer in a future task) | Normalize `research/evidence_matrix.csv` (free-text locator, `;`-joined person_refs, string confidence) + `result.json` (text-embedded divergence classification) into `data/schemas/*.schema.json`-conformant records; package as a curated export | `research/evidence_matrix.csv`, `analysis/outputs/result.json`, `data/schemas/*.schema.json`, person registry | `${TKAF_PRIVATE_DATA_ROOT}/curated/app_export/**` (versioned package + `app_export_manifest.schema.json` manifest) | Run inline in a request path; skip schema validation; silently drop the D-017 validation-status field |
| Importer (`app/backend/importers/`) | Validate + atomically import a curated export into the runtime DB | curated export package (checksummed, manifest-validated) | `data/runtime/*.sqlite3` | Read raw or private analysis data directly (per `data/APP_DATABASE_POLICY.md`); import an unapproved package |
| Backend API | Serve event/evidence/metrics from the runtime DB; orchestrate the LLM call for `/v1/ask` | runtime DB only | nothing persistent besides request logs | Read raw/private-analysis zones; let the LLM recompute a metric; return a claim with no `evidence_refs`/`metric_refs` |
| LLM response validator (backend submodule) | Validate every LLM output against `analysis/schemas/interpretation.schema.json` before it reaches a client | LLM raw output | validated response or a structured rejection | Pass through an unvalidated response, even once, even on retry |
| Web app (frontend) | Render the 6 screens/components in `design/wireframe_brief.md`/`component_spec.md` | Backend API only | nothing | Call the LLM directly; read the DB directly; reinterpret a score's meaning |
| Evaluation pipeline (`evals/`) | Regression/grounding checks against `analysis/llm_contract.md`'s worked examples | fixture inputs + backend/LLM outputs | `evals/eval_results.json` | Modify product data |

## Screen/component → service mapping

| Screen (`design/wireframe_brief.md`) | Backend calls |
| --- | --- |
| Event overview | `GET /v1/events/{event_id}` |
| Person comparison | `GET /v1/people/{person_id}/evidence`, `GET /v1/events/{event_id}/metrics?kind=coverage` |
| Score breakdown & weight lab | `GET /v1/events/{event_id}/metrics?kind=label_frequency` (and `divergence`); `ContributionBreakdown` renders `not_yet_available` client-side (no endpoint needed — nothing to fetch, per `component_spec.md`) |
| AI answer panel | `POST /v1/ask` |
| Quest | `GET /v1/people/{person_id}/evidence` (reused; quest-progress state is client-side only, per `product/data_to_ui_mapping.md`) |
| Evidence-linked quiz | Reuses evidence already fetched for the quest; no dedicated endpoint |

## Trust boundaries

- Browser ↔ Backend API (HTTPS; no direct DB or LLM access from the browser).
- Backend ↔ Runtime DB (read-only at request time; the backend never writes product data at request time — only the offline importer writes).
- Backend ↔ External LLM (isolated call path through the response validator; prompt construction uses only DB-sourced short excerpts, never private-analysis-zone full paragraphs — see `threat_model.md`).
- Curated Export Transform (offline/batch, human/CI-triggered) ↔ Private analysis zone (read-only) and ↔ Curated export zone (write, versioned).
- Importer ↔ Curated export zone (read, checksum-verified) and ↔ Runtime DB (write, atomic, idempotent; failed import leaves the previously-approved version serving, per `data/APP_DATABASE_POLICY.md`).

## Required decisions (resolved for this slice)

- **Storage: relational, SQLite.** This slice has one event, 5(+) persons, dozens of evidence rows — no query pattern here needs a graph database. Network edges (`analysis/network_analysis_plan.md`) are stored as a typed `relationship` table (source/target/relation/evidence_id/source_layer/confidence), not a graph store. Revisit only if/when the corpus scales toward the full 65-juan/120-回 range (see ADR-0002).
- **Background jobs/queue: none for this slice.** The Curated Export Transform + Importer run as a manual/CI-triggered script, not a queued job system — import volume and frequency don't justify one yet. `/v1/ask` is synchronous request/response with a timeout, not a queued job.
- **LLM provider/model: configurable via env var** (matches `analysis/llm_contract.md`'s worked examples using `model.name`/`model.version` fields), never hardcoded. **Data policy: only DB-stored, already-short, already-public-domain-confirmed excerpts (`permitted_excerpt`, ≤200 chars per `evidence.schema.json`) are ever sent to the external LLM** — full private-analysis-zone paragraphs are never sent, regardless of model provider.
- **Authentication and roles: none for the public-read demo paths in this slice** (`product/acceptance_criteria.md` AC-3 notes this explicitly). The API is designed role-ready — curated-export approval/publish actions are a separate, unimplemented admin surface, not exposed to the public API in this slice.
- **Deployment topology:** one backend service + one static/SPA frontend + one SQLite file, deployable as a single small unit. No microservice split is justified at this scale (`agents/architect.md` prohibits unjustified decomposition).
- **Observability and cost budget:** every `/v1/ask` response logs `run_id`, `model`, `prompt_version`, and latency; a per-request LLM budget is one external call (no chained multi-call agent loop) to keep cost and latency bounded for this MVP slice; structured logs only — no user accounts exist yet, so no PII to redact beyond IPs/standard request metadata.

## Failure principles

- 근거 조회 실패 시 추정 답변 대신 명시적 unavailable 상태 (`status: insufficient_evidence` from the schema, never a guess).
- 분석 버전(run_manifest) 불일치 또는 curated export import 실패 시 결과 표시를 차단하거나 이전 승인 버전을 유지한다 (`data/APP_DATABASE_POLICY.md`).
- LLM 실패/타임아웃 시 검증된 수치/근거 UI(evidence cards, coverage/label_frequency/divergence)는 정상 표시하되 AI 답변 패널만 error/retryable 상태로 격리한다.
- source layer 또는 evidence ref 검증 실패(스키마 불일치, 존재하지 않는 evidence_id 인용 등) 시 해당 응답은 공개 경로에서 차단되고 validator가 거부한다.
- **D-016**: any endpoint iterating persons/evidence must not assume a fixed count — pagination-ready shapes (arrays), not hardcoded 5-element structures.
- **D-017**: every evidence-bearing response includes a `coding_validation_status` field (never omittable) reflecting the current validation state — the API, not just the LLM contract, carries this disclosure so the frontend can't accidentally drop it. As of D-024 (2026-09-18) the current value is `human_validated` (the human owner reviewed all 30 rows and found no disagreements); this field must keep working for whichever value is true at any given time, not be assumed permanently `llm_llm_validated_only`.

---

*Below this line: the original starter scaffold, kept for history — superseded by the sections above for this slice.*

## Intended boundaries (starter, superseded)

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
