# Screen Inventory — S1 Vertical Slice (적벽대전)

Status: `S1 DRAFT`. Minimum screen set to support both Hybrid modes for one event (적벽대전), per `product/feature_spec.md`. This is a planning inventory, not implementation — no production UI is built at S1 (`handoffs/CURRENT_TASK.md` "Do not do").

| Screen | Mode | Purpose | Required component families (`design/DESIGN.md`§6) | Feeds from |
| --- | --- | --- | --- | --- |
| Event overview (적벽대전) | Shared | Entry point: event summary, cast list, source-layer coverage at a glance | `SourceModeControl` | F-00, E-01 |
| Person comparison | Explorer | Compare one person across 정사/연의(/정사 주석) for this event | `SourceModeControl`, `EvidenceCard`, `ScoreCard` | F-01, F-03, E-02 |
| Score breakdown & weight lab | Explorer (also reused inside L-03) | Show 관측 근거→코드→…→표시 점수 path; let user try custom weights | `ScoreCard`, `ContributionBreakdown` | F-02, E-04, L-03 |
| AI answer panel | Shared (mode-aware) | Ask a scoped question, get an evidence-linked answer or explicit abstention | `AIAnswerPanel` | F-04, E-03 |
| Quest (적벽대전) | Learning-game | Guided flow requiring both-source-layer evidence + counter-evidence before completion | `QuestCard`, `EvidenceCard` | L-01, L-02 |
| Evidence-linked quiz | Learning-game | 2–4 item quiz tied to evidence already shown in the quest | `QuestCard` (quiz sub-state), `EvidenceCard` | L-04 |

## Explicitly not a separate screen in this slice

- A dedicated "network graph" screen — out of scope for this one-event, 3–5-person slice (would need A1's network-analysis output, not committed to for S1).
- A leaderboard/competition screen — explicit non-goal (`product/feature_spec.md` §4).
- An 8-bit battle screen — explicit non-goal for S1/S2 (`product/feature_spec.md` §2 L-01 note).
- A difficulty-selection screen — blocked on Q-005; do not build speculatively (`product/feature_spec.md` L-05).

## Required states per screen (design/DESIGN.md §7)

Every screen above must design for: default, loading, empty, insufficient evidence, partial result, stale result, error/retryable error, permission unavailable, LLM refused/abstained (AI answer panel only). See `product/acceptance_criteria.md` for the concrete Given/When/Then per state.
