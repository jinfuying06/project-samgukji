# Backend Workspace

FastAPI + SQLite backend for the 적벽대전 vertical slice, implementing `app/architecture/api_contract.yaml`'s
7 endpoints against a curated-export-imported runtime DB. See `handoffs/phase_reports/S3_COMPLETION.md`
for the full implementation report.

The backend never reads raw or private analysis data at runtime — only the imported curated export.
See `data/APP_DATABASE_POLICY.md`.

## Running locally

```
pip install -r app/backend/requirements.txt
python app/backend/migrations/migrate.py data/runtime/tkaf.local.sqlite3
python app/backend/importers/import_curated_export.py data/runtime/tkaf.local.sqlite3
uvicorn app.backend.api.main:app --reload
```

## Enabling a real LLM (`/v1/ask`)

By default `/v1/ask` uses `MockLLMClient` — deterministic, no network call, no cost, and it's what
every automated test uses. To use a real OpenAI-compatible model instead, set in `.env` (see
`.env.example`; never commit real values):

```
OPENAI_API_KEY=sk-...      # the only value you actually need to fill in
TKAF_LLM_PROVIDER=openai   # already set in .env.example
TKAF_LLM_MODEL=gpt-4o-mini # already set in .env.example; override for a different model
```

`build_llm_client()` (`app/backend/api/llm_client.py`) only switches to `OpenAILLMClient` when both
`TKAF_LLM_PROVIDER=openai` and `OPENAI_API_KEY` are set — leave the key blank and the app keeps
running end-to-end on the mock, no other change needed. `OpenAILLMClient` builds its prompt from
`analysis/llm_contract.md`'s rules plus the actual `interpretation.schema.json`, asks the model for
JSON-mode output, and lets the caller (not the model) fill in `interpretation_id`/`generated_at`/
`model`/`input_refs`. Every response, mock or real, still goes through the same schema + citation
validator (`llm_validator.py`) before it can reach a client — a real key does not bypass that.
Provider-call failures (timeout, bad key, malformed response) never surface as a raw 500; `/v1/ask`
retries once and then returns an honest `insufficient_evidence` response instead
(`app/backend/api/main.py`). Tests for the real client (`tests/backend/test_llm_client.py`) mock
`requests.post` — no paid API call is ever made by the test suite.

