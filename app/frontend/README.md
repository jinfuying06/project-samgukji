# Frontend Workspace

Implementation begins after Design Gate and API contract freeze.

First screen target:

- event/person selector
- `정사 | 정사 주석 | 연의 | 비교 | 게임` mode control
- score with coverage/confidence and contribution breakdown
- evidence cards with edition/locator
- weight-tuning sandbox labeled as custom
- source-constrained AI question panel
- game progress based on evidence exploration

All loading, empty, insufficient-evidence, stale, error, and refused states must be implemented.

## S3/E1 implementation status (2026-09-17)

Implemented for the 적벽대전 vertical slice: all 6 screens (event overview, person comparison,
score breakdown, AI answer panel, quest, quiz-placeholder) and all 6 `design/DESIGN.md`§6
component families, against `app/architecture/api_contract.yaml`.

**Stack: Vite + React 18 + TypeScript, tested with Vitest + Testing Library + jest-axe.**
Chosen over a heavier framework or hand-rolled Web Components because this is a single-event,
6-screen vertical slice with no SSR/multi-app requirement — React + Testing Library gives the
fastest path to accessible, well-tested components without an unjustified build/tooling
decomposition (`agents/architect.md`'s "근거 없는 마이크로서비스 분해를 하지 않습니다" applies
here by extension: don't over-tool a small slice either). No router library — a 6-screen app
with one event doesn't need one; `src/App.tsx` is a small state-based screen switcher.

### Layout

- `src/theme/tokens.css` — central design-token file implementing `design/DESIGN.md`§11 (light
  palette on bare `:root`, dark redefined under `prefers-color-scheme`/`[data-theme]`).
- `src/theme/components.css` — component styles built on those tokens; no hex/px constants
  scattered in component code.
- `src/api/types.ts`, `src/api/client.ts` — TypeScript types and a thin fetch wrapper mirroring
  `app/architecture/api_contract.yaml` exactly; never invents a field the contract doesn't define.
- `src/api/mocks/fixtures.ts` — mock responses shaped like the not-yet-implemented Curated Export
  Transform's output (D-018), built from the real `research/evidence_matrix.csv`/`result.json`
  content, for local dev before a real backend is running.
- `src/components/*` — the 6 `DESIGN.md`§6 component families.
- `src/screens/*` — the 6 `design/wireframe_brief.md` screens (S-001..S-006).

### Tests (`npm test`, 32 passing)

- Component tests per family (states, keyboard/ARIA behavior, the D-017 disclosure never being
  suppressible, QuestCard's real completion gate per AC-5, ScoreCard never treating a 0 count the
  same as `insufficient_data`).
- `tests/components/*` each include a `jest-axe` accessibility check (zero violations required).
- `tests/screens/EventOverview.test.tsx` — integration test against a mocked `fetch`, covering
  loading → data and loading → error paths.
- `tests/contract/schemaDrift.test.ts` — **the mock-vs-contract drift check**: loads the frozen
  `app/architecture/api_contract.yaml` at test time (via `js-yaml`), compiles its
  `components.schemas` with `ajv`, and validates every mock fixture against it. Also cross-checks
  the `Interpretation` fixtures against the standalone, authoritative
  `analysis/schemas/interpretation.schema.json` (which `api_contract.yaml` itself says is the
  source of truth for that one schema). If a fixture or the contract drifts, this test fails.

### Known gap carried from E0 (not this track's job to fix)

`data/schemas/evidence.schema.json` (the general curated-export data contract) and
`api_contract.yaml`'s inline `EvidenceSpan` schema (the API-level projection actually used here)
are not byte-identical in required fields — see `product/data_to_ui_mapping.md`'s "Known schema
gap" and `app/architecture/system.md`'s Curated Export Transform row (D-018). This frontend and
its drift test validate against `api_contract.yaml`'s `EvidenceSpan` (the actual wire contract),
which is correct for this track, but whoever implements the Curated Export Transform must ensure
its real output matches that same `api_contract.yaml` shape, not just `evidence.schema.json`.

### Not implemented (explicit non-goals for S3, unchanged)

8-bit battle system, full curriculum, difficulty selector (Q-005 open), quiz item schema (L-04
`[TBD]` — `Quiz.tsx` renders an explicit "퀴즈 준비 중" state instead of guessing one).

