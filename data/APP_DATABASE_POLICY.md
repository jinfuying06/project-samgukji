# Application Database Policy

## Separation of concerns

The application database is a serving layer, not the analysis workspace and not the historical source of truth.

```text
Private analysis data
  → reviewed/versioned curated export
  → schema validation
  → transactional import
  → application database
```

## Commit rules

Commit database migrations, ORM/schema definitions, import/export code, synthetic fixtures, and safe manifest templates.

Do not commit database files/dumps, vector indices, embeddings, user data, or raw/analysis/curated corpora.

## Curated export contract

An app export includes export ID/time, source and pipeline versions, schema version, source layer, entity resolution version, evidence/rights review, model versions, checksums, and approval reference.

## Runtime behavior

- The app reads only the runtime DB/API, never raw or analysis paths.
- Imports are idempotent and atomic.
- A failed import leaves the previous approved version available.
- Every user-visible score/claim retains run/model/source/evidence references.
- Database migrations and data imports are separate operations.

