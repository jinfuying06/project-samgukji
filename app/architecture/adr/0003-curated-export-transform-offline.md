# ADR 0003: Curated Export Transform Is an Offline Batch Step, Not Inline Backend Code

- Status: Accepted
- Date: 2026-09-17

## Context

`research/evidence_matrix.csv` (research working format: free-text `locator`, `;`-joined `person_refs`, string `confidence`) does not match `data/schemas/evidence.schema.json` (curated-export contract: structured `locator` object, array `person_refs`, 0–1 float `confidence`) — logged as D-018. Something has to normalize one into the other before the API can serve schema-conformant `EvidenceSpan` records.

## Decision

This normalization runs as an **offline, human/CI-triggered batch step** ("Curated Export Transform," `app/architecture/system.md`) that reads the research CSV + `analysis/outputs/result.json`, produces a versioned curated export package under `${TKAF_PRIVATE_DATA_ROOT}/curated/app_export/`, and is imported by the existing `app/backend/importers/` component — never computed inline in the backend's request path.

## Consequences

- The backend API never touches `research/evidence_matrix.csv` or the private analysis zone at request time — it only ever reads the runtime DB, preserving `data/APP_DATABASE_POLICY.md`'s separation.
- Every field-format decision this transform makes (e.g., mapping `confidence: "high"|"medium"` → a specific 0–1 float, parsing `divergence.*`'s `method` text into a typed `classification`/`evidence_ids` pair) becomes an explicit, versioned, reviewable step — not a live guess made per-request. Whoever implements this transform (Data Engineer, future task) must document the exact mapping rule as its own ADR addendum or code comment, not invent one silently per field.
- A new curated export must be generated and re-imported every time `research/evidence_matrix.csv` or `analysis/outputs/result.json` changes (e.g., after the D-016 expansion pass) — the API will keep serving the previously-imported version until that happens, which is correct behavior (`data/APP_DATABASE_POLICY.md`'s "failed/absent import leaves the previous approved version serving"), not a bug.
- This also means the transform is the single place that must copy `research/intercoder_reliability.md`'s current validation status (`llm_llm_validated_only`) into every `EvidenceSpan.coding_validation_status` field — if D-017 is ever resolved by human validation, updating that one flag (and re-running the transform) is what flips the disclosure everywhere, rather than needing to change many places.
