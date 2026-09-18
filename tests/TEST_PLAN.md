# Test Plan — S3 (적벽대전 Vertical Slice, Hybrid)

Status: `S3 QA — 2026-09-18`. Risk-based allocation across the implementation delivered by E1 (`app/backend/`, `app/frontend/`), against `product/acceptance_criteria.md` (AC-1–AC-7), `orchestration/gates.yaml`'s `implementation_gate` (B3), and `agents/_three_kingdoms_domain.md`'s hard blockers.

## Risk tiers and allocation

| Risk area | Why it's high-risk here | Test type | Owner |
| --- | --- | --- | --- |
| Source-layer leakage in `/v1/ask` | A single leaked `ROMANCE` citation into a 정사 answer (or vice versa) is a named domain hard blocker, not a cosmetic bug | Integration (real DB + real FastAPI app, mock LLM) | QA (new, `tests/qa/`) |
| Citation-laundering / unsupported LLM claims | `orchestration/gates.yaml` names this a hard blocker at B1 and B3 both | Unit (validator) + integration (API round-trip) | Backend (existing) + QA (new) |
| Entity-resolution / alias collisions | 10-person cast with real courtesy names/nicknames (孟德, 玄德, 孔明, 公瑾, 子龍...); a collision would silently merge two people | Golden-case (real curated export data, not synthetic fixtures) | QA (new) |
| D-017 disclosure omission | Coding is LLM-LLM validated only; a UI/API path that drops this disclosure would misrepresent evidence quality to a user | Unit (schema) + integration (every evidence-bearing endpoint) | Backend (existing, schema-level) + QA (new, endpoint-level) |
| Missing-value-as-zero | Named domain hard blocker; `coverage=0` and `person not found` are different states and must never be conflated | Integration (real empty-layer query + real 404 query) | QA (new) |
| Curated-export/import integrity | A partial import corrupting the runtime DB would break every downstream guarantee | Unit + integration (checksum, manifest, rollback-on-corruption) | Backend (existing) |
| Contract drift (frontend mocks vs. frozen `api_contract.yaml`) | Backend and frontend were built in parallel by separate agents — the only thing keeping them aligned is the shared schema | Contract test (loads real `api_contract.yaml` + `interpretation.schema.json` at test time) | Frontend (existing) |
| Accessibility (color-only meaning, keyboard, ARIA) | Explicit `design/DESIGN.md`/`accessibility_checklist.md` requirement; a critical-path a11y failure is a B3 hard blocker (`accessibility_critical_issues: 0`) | Automated (`jest-axe` per component) + manual checklist (deferred, no built/deployed UI to click through yet) | Frontend (existing, automated) / not yet run (manual) |
| Full user journeys end-to-end (browser) | No running deployed instance exists in this environment | **Not run** — see Residual risks | — |
| Repo-structure/data-boundary scripts | A silent breakage here would hide real problems from every future stage | Script re-run | QA (verification) |

## Out of scope for this pass

- Load/performance testing (single-event, ≤30-evidence-row demo slice — not yet a concern per `app/architecture/system.md`'s stated scale).
- Real external LLM provider behavior (`OpenAILLMClient` is an intentionally unimplemented stub — no key/network in this environment, and tests must never call a paid API per `agents/backend.md`).
- Visual/manual accessibility walkthrough of a running, deployed app (nothing is deployed yet in this slice — S3 delivers code + automated tests, not a hosted instance).
- Q-005/Q-009-dependent behavior (both still open, non-blocking; no test asserts a specific difficulty level or literacy default beyond what `product/acceptance_criteria.md` already fixes as the interim default).
