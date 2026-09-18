# Acceptance Criteria — S1 Vertical Slice (적벽대전)

Status: `S1 DRAFT`. Given/When/Then per core flow in `product/feature_spec.md` / `product/user_journeys.md`, including error, uncertainty, no-data, and AI-refusal states per `design/DESIGN.md`§7. Default assumption while Q-009 is open: screens default to the more-explanatory presentation (do not assume high data literacy).

## AC-1 Event overview and source-layer coverage (F-00, E-01)

- **Given** the 적벽대전 event has data ingested by D1, **when** the user opens the event overview, **then** the cast list and a per-layer coverage indicator (정사/연의/정사 주석) are shown before any score.
- **Updated per D-019 (S2) and D-021 (S3 expansion, 2026-09-18):** `HISTORY_ANNOTATION` coverage was not thin for the original 5-person cast (6/22 rows, same as `HISTORY_BASE`), and the cast has since grown to **10 persons / 30 evidence rows** (HISTORY_BASE 6 / HISTORY_ANNOTATION 11 / ROMANCE 13) — `SourceModeControl` defaults to 정사/정사 주석/연의 all enabled for the whole cast. **Given** a specific person has 0 evidence rows in a given layer (e.g., 諸葛亮 in `HISTORY_ANNOTATION`), **when** the user views that person in that layer, **then** that person×layer combination shows present-but-insufficient (not hidden, not silently merged into 정사) — the disable/insufficient state is per person×layer, not per layer overall, and this rule must keep working as the cast size changes (D-016) rather than being re-hardcoded to any fixed count.
- **Given** D1's ingestion has not completed, **when** the user opens the event overview, **then** a loading state is shown, not an empty or error state.

## AC-2 Person comparison across source layers (E-02)

- **Given** 周瑜 has ≥1 evidence span in both `HISTORY_BASE` and `ROMANCE` for 적벽대전, **when** the user selects **비교** mode, **then** evidence cards from both layers are shown side by side with `evidence_id`, locator, and quotation-type, and no single merged claim is produced.
- **Given** a person has evidence in only one layer for this event, **when** the user views the comparison, **then** the missing layer shows an explicit "이 층위에서는 근거 없음" state — not a 0 score, not a blank panel.
- **Given** two evidence spans conflict (e.g., 정사 vs 연의 disagree on an action), **when** both are shown, **then** the UI presents them as parallel claims with their own confidence/ambiguity notes, not as one resolved fact (`agents/_three_kingdoms_domain.md`).

## AC-3 AI answer panel (E-03, F-04)

- **Given** the user asks a question scoped to 적벽대전's cast, **when** sufficient evidence exists for the requested mode, **then** the answer includes per-claim `evidence_id` references.
- **Given** insufficient evidence exists for a sub-claim in the requested mode, **when** the panel would otherwise need to guess, **then** it abstains for that sub-claim specifically and states why, rather than answering unsupported.
- **Given** the user is in **연의** mode, **when** the panel answers, **then** the fictional/literary status of the answer is visibly labeled (not presented as historical fact).
- **Given** the AI service is unavailable, **when** the user submits a question, **then** an error/retryable state is shown, distinct from the "insufficient evidence" abstention state.

## AC-4 Score breakdown and custom weight experiment (F-02, E-04)

- **Given** `analysis/outputs/result.json` provides a score for a person/indicator, **when** the user opens the score card, **then** `model_version`, `coverage`, and `confidence` (or an explicit insufficient-evidence status) are shown alongside the value.
- **Given** the user changes a weight in the weight-lab screen, **when** a new score is computed, **then** it is labeled "사용자 설정 점수" and this label persists as long as any weight differs from default — it cannot be dismissed to look like the default score.
- **Given** a sub-indicator has zero observed evidence, **when** the contribution breakdown renders, **then** that sub-indicator shows "근거 없음"/"측정 불가", never a numeric `0` presented as if it were a real observed low value.

## AC-5 Learning-game quest completion (L-01, L-02)

- **Given** the user has not yet opened both a 정사 and a 연의 evidence card for the quest's claim, **when** the user attempts to mark the quest complete, **then** completion is blocked and the UI indicates which layer is still unopened.
- **Given** the user has opened both layers but has not acknowledged a counter-evidence item, **when** the user attempts to complete, **then** completion is still blocked until the counter-evidence checkpoint (L-02) is satisfied.
- **Given** both conditions are satisfied, **when** the user marks the quest complete, **then** the badge/copy shown describes the behavior performed ("양쪽 출처 확인", "반대 근거 확인"), never a historical-truth claim (`product/gamification_spec.md`).

## AC-6 Evidence-linked quiz (L-04)

- **Given** a quiz item is tied to an `evidence_id` the user has already seen in the quest, **when** the user answers, **then** the result view links back to that specific evidence, not a generic explanation.
- **Given** the user has not yet reached the quest step that unlocks a given quiz item, **when** the user tries to access it, **then** it is locked, not answerable ahead of seeing its supporting evidence.

## AC-7 Cross-cutting states (all screens, `design/DESIGN.md`§7)

- **Given** any data-backed component is fetching, **when** rendered, **then** it shows a `loading` state distinguishable from `empty`.
- **Given** a query legitimately returns no evidence/score, **when** rendered, **then** it shows `empty` or `insufficient evidence` (chosen per AC-1/AC-2 rules above) — never treated the same as `error`.
- **Given** a prior result becomes outdated (e.g., pipeline version changes), **when** the cached view is shown before refresh, **then** a `stale result` indicator is shown.
- **Given** a network/service failure occurs, **when** rendered, **then** an `error/retryable error` state with a retry action is shown, distinct from both `empty` and `LLM refused/abstained`.
- **Given** a user lacks permission for a feature (not applicable to this public-read slice today, but designed for), **when** they attempt it, **then** a `permission unavailable` state is shown rather than a silent failure.

## Open dependencies

- AC-1's exact annotation-coverage threshold is not yet set — D1/A1/orchestrator must agree on a number before this criterion is testable; product does not set a data threshold unilaterally.
- L-05 (difficulty level, Q-005) and the data-literacy default (Q-009) may add criteria variants once answered; this document's current criteria assume the single default level and explanatory-first presentation described above.
