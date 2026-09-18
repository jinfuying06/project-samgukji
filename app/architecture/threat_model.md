# Threat and Misuse Model — 적벽대전 Vertical Slice

Status: `S3/E0 ACTIVE — 2026-09-17`. Refines the starter model below for the concrete architecture in `app/architecture/system.md`.

## Assets

- Source/edition metadata and permitted excerpts (`data/schemas/evidence.schema.json`'s `permitted_excerpt`, ≤200 chars, owner-confirmed public domain per D-012 — still not a documented legal opinion).
- `research/evidence_matrix.csv`'s coding labels and the `analysis/outputs/result.json` descriptive metrics (no composite score exists to protect yet).
- The **coding-validation status** (D-017: LLM-LLM only, κ=0.90) — this is trust-relevant metadata, not just a footnote, and must not be strippable from any response.
- External LLM API credentials.
- Curated export packages and the runtime DB's integrity/versioning.

No user accounts exist in this slice, so there is no user PII/activity-data asset yet (see `app/architecture/system.md`'s auth decision) — the "Human approval" and "Open items" sections below still list what must exist before that changes.

## Key threats — separated by call path (LLM path vs. deterministic pipeline path)

### LLM call path (`/v1/ask` → external LLM → response validator)

| Threat | Example | Control |
| --- | --- | --- |
| Prompt injection from source text | A `permitted_excerpt` or user question contains text engineered to make the LLM ignore its instructions | Excerpts sent to the LLM are short (≤200 chars), sourced only from the curated DB (never raw), and treated as data, never as instructions, in the prompt template; the response validator checks structure, not the LLM's self-report of compliance |
| Citation laundering | LLM cites an `evidence_id`/`metric_id` that doesn't exist, or restates a claim without a real ref | `analysis/schemas/interpretation.schema.json` structurally requires ≥1 real-pattern `evidence_refs`/`metric_refs` per claim; the backend additionally cross-checks cited IDs against the runtime DB before returning (schema pattern-matching alone doesn't prove the ID exists) |
| Fabricated score/ranking | User asks "누가 최강인가" and the LLM invents a composite number | `analysis/llm_contract.md` rule 4 + this slice's `Metrics` endpoint literally has no score-kind metric to cite — the validator rejects any claim whose `metric_refs` don't resolve to a real `metric_id` in `result.json` |
| Coding-validation disclosure omitted | LLM answer cites evidence but drops the D-017 notice | Schema-enforced (`coding_validation_notice` required whenever any claim has non-empty `evidence_refs`); additionally mirrored at the API layer via `EvidenceSpan.coding_validation_status` so the frontend has a second, independent source for the disclosure even if an LLM response were somehow malformed |
| Secret/key leakage via logs or prompt | LLM API key or a user's raw question logged in plaintext alongside model output | Secrets in env vars only (`.env`, never committed — `.env.example` pattern already in this repo); structured logs redact the request body's `question` field from long-term storage beyond a short debugging TTL |
| Rate/cost abuse | Repeated `/v1/ask` calls used to run up LLM spend | Per-request timeout, one external call per request (no chained agent loop, per `system.md`'s cost decision), `429` rate limiting at the API layer |

### Deterministic pipeline path (ingestion → coding → analysis → curated export → import)

| Threat | Example | Control |
| --- | --- | --- |
| Source-layer leakage | Curated export accidentally tags a `ROMANCE` paragraph as `HISTORY_BASE` | `data/pipelines/build_chibi_sample.py`'s bracket-based split + `data/quality_report.json`'s `annotation_bracket_check`; Curated Export Transform must re-validate `source_layer` against `data/schemas/evidence.schema.json`'s enum before import, reject on mismatch |
| Entity/alias poisoning | An alias string is applied to the wrong `person_id` | `person.schema.json`'s `alias_collision_note` field + D1's "never invent an alias" rule; importer rejects a person record with an unexplained alias collision |
| Curated export integrity failure | A partially-written export package is imported, corrupting the runtime DB | Importer validates `app_export_manifest.schema.json`, verifies every file checksum, imports atomically/idempotently; a failed import leaves the previously-approved version serving (`data/APP_DATABASE_POLICY.md`) — this is a hard requirement on the not-yet-built importer, not optional |
| Unapproved data reaching production | Someone points the importer at an export package that was never reviewed | Importer rejects any package without an approval reference (per `app/backend/importers/README.md`, already in the repo) |
| Rights violation | A future annotation/translation layer with unclear rights gets exported and served publicly | D-012 covers only the original 《三國志》/《三國演義》 text; any new source added later needs its own rights check before the Curated Export Transform is allowed to include it — this is a process gate, not a technical control this architecture can enforce alone |
| Popularity/engagement gaming | A future community feature lets user votes influence displayed scores | Out of scope for this slice (no user accounts) — flagged so it isn't accidentally introduced without its own threat review later |

## Human approval required (unchanged from starter, still applies)

- New source/translation publication.
- Codebook or default weight change (there is no default weight yet in this slice — first weight model proposal itself needs this approval).
- Adjudication of disputed high-impact evidence (see the RM-C049-P2/RM-C049-P6 adjudication precedent in `research/intercoder_reliability.md`).
- Public release of any external game-data comparison/asset (none approved yet, per `product/gamification_spec.md`).
- Any move from "LLM-LLM validated" to "human validated" coding status (D-017) is itself a fact that should be recorded as a decision, not silently flipped in the DB.

## Open items (resolved or explicitly deferred, per E0 scope)

- **Authentication/authorization**: resolved for this slice — none required for public-read paths (`app/architecture/system.md`). Deferred: an admin/approval role for curated-export publishing, needed before any human-in-the-loop approval workflow is built.
- **Abuse rate limits**: resolved at a contract level (`429` in `api_contract.yaml`); exact limits are an implementation parameter, not an architecture decision, deferred to E1.
- **Incident and takedown process**: deferred — no public user-generated content exists in this slice to take down; revisit if/when a community feature is proposed (explicitly out of scope per `product/gamification_spec.md`).
- **Backup/rollback**: resolved — the importer's "leave previous approved version serving on failed import" rule (`data/APP_DATABASE_POLICY.md`) is this slice's rollback mechanism; no additional backup infrastructure is justified at this data volume.

---

*Below this line: the original starter scaffold's remaining generic entries not already superseded above.*

| Threat | Example | Control |
| --- | --- | --- |
| Score manipulation | 커스텀 가중치를 기본 점수로 공유 | N/A yet — no score exists in this slice to manipulate; revisit when a weighting model is proposed |
