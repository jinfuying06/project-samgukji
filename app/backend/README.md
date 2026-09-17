# Backend Workspace

Implementation begins only after the API contract is reviewed and the relevant task is assigned.

Expected modules:

- source/evidence registry
- entity and alias resolver
- event/relationship query
- analytics score service
- source-constrained retrieval
- LLM response validation
- audit/version metadata
- schema migrations and an atomic curated-export importer

Every endpoint must return or preserve `run_id`, model/schema version, source mode, and evidence references where applicable.

The backend never reads raw or private analysis data at runtime. See `data/APP_DATABASE_POLICY.md`.

