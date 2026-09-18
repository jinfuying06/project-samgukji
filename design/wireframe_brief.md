# Wireframe Brief — S2 (적벽대전 Vertical Slice, Hybrid)

Status: `S2 DRAFT — 2026-09-17`. Six screens from `product/screen_inventory.md`. Data fields cited are the real S1 shapes (`research/evidence_matrix.csv`, `analysis/outputs/result.json`, `data/schemas/*.schema.json`) — see `design/component_spec.md` for full per-component prop lists and the reconciliation gaps found against `product/data_to_ui_mapping.md`.

## Information hierarchy (applies to every screen, `design/DESIGN.md`§2)

1. 현재 인물/사건 + source mode
2. 점수 또는 핵심 관찰 (this slice: coverage counts / divergence classification — **no composite score exists yet**, see S-003)
3. 데이터 커버리지·신뢰도·기준 버전 (`population.n`, `limitations[]`, `warnings[]` from `result.json`; per-row `confidence` from `evidence_matrix.csv`)
4. 점수 구성 요소 (not populated this slice — see S-003's `insufficient_evidence` default)
5. 사건과 근거 카드 (`evidence_matrix.csv` rows)
6. 원문 위치·판본·번역 정보 (`work_title`, `volume_or_chapter`, `locator`, `excerpt_type`)
7. AI 설명과 제한사항 (S-004, pending L1's `analysis/llm_contract.md`)

## S-001 — Event overview (적벽대전)

- User goal: understand what data exists for this event before choosing a path (탐색 vs 학습).
- Entry: app root / event picker (only one event exists in this slice — no event-list screen needed yet). Exit: → S-002 (탐색) or → S-005 (학습).
- Primary content: cast list (曹操/孫權/劉備/周瑜/諸葛亮 — **not a hardcoded 5, read from `person_refs` distinct values in `evidence_matrix.csv`**, per D-016 the cast will grow), per-layer coverage badge (정사/정사 주석/연의 — all three are populated for this slice, see `component_spec.md` SourceModeControl note on 정사주석 not being thin).
- Primary action: pick a person → S-002, or "학습 시작" → S-005.
- Secondary actions: switch source mode filter on the cast/coverage view (`SourceModeControl`).
- Trust cues: `population.n` (22), `run_id`, event scope note ("이 슬라이스는 적벽대전 一개 사건, 이 5명 한정" with a visible "더 많은 인물 추가 예정" note per D-016 — do not imply this is the complete cast of the battle).

### States (S-001)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | D1 pipeline/API not yet returned | skeleton cast list | — |
| empty | no event data at all | "표시할 사건 데이터 없음" + why | back |
| insufficient evidence | a layer has 0 evidence rows for this event | that layer's badge shows "근거 없음", not hidden | switch layer |
| partial | some persons/layers missing, not all | shown persons + note on gap | continue |
| stale | `run_manifest.json` older than a threshold TBD by orchestrator | "최근 실행: {generated_at}" + refresh | refresh |
| error | fetch failed | safe message + retry | retry |
| permission unavailable | n/a for this public-read slice, designed for future auth | generic message | — |

## S-002 — Person comparison (Explorer, E-02)

- User goal: compare one person across 정사/연의(/정사 주석) for 적벽대전, see where they agree/conflict.
- Entry: from S-001 (person selected) or direct deep link. Exit: → S-003 (score/coverage detail) or → S-004 (ask AI).
- Primary content: `EvidenceCard` list per layer, laid out side by side (desktop, §8) or stacked-with-tabs (mobile). Each card: `evidence_id`, `source_layer` badge, `work_title` + `volume_or_chapter`, `excerpt_zh` (short, per `excerpt_type`), `coding_label`, `confidence`, `ambiguity_note`.
- Primary action: open a card's full context / send it to S-004 as the AI question's subject.
- Secondary actions: toggle 비교 vs single-layer view (`SourceModeControl`).
- Trust cues: per-card `confidence` (high/medium — actual values found in the data, not a 0–1 float, see `component_spec.md`), `review_status` note that this is single-LLM-coded + LLM-LLM-checked, not human-validated (D-017) — shown as a small persistent footnote on this screen, not hidden.

### States (S-002)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | evidence fetch pending | skeleton cards | — |
| empty | person has 0 evidence anywhere for this event | "이 인물의 근거 없음" | back to S-001 |
| insufficient evidence | person has evidence in only one layer (e.g. 劉備: 0 in ROMANCE per `result.json` `coverage.PERSON-LIUBEI.ROMANCE=0`) | missing layer shows "이 층위에서는 근거 없음" card, not blank space (AC-2) | switch person/layer |
| partial | evidence exists but only for part of the event's coded chapters (only 回49–50 coded, not 51–57) | banner: "이 사건 전체가 아니라 回49–50 구간만 코딩됨" | — |
| stale | evidence matrix updated since last cache | stale badge | refresh |
| error | fetch failed | retry | retry |
| permission unavailable | n/a this slice | — | — |

## S-003 — Score breakdown & weight lab (Explorer + reused in L-03)

- User goal: see the full "근거→코드→…→점수" path; for this slice, that path **explicitly stops before a composite score** (`analysis/scoring_model.md`) — the screen must make that stopping point visible, not paper over it.
- Entry: from S-002 (a person's evidence) or from S-005 step 3 (quest). Exit: → S-002 (evidence drill-down) or back to quest.
- Primary content, **for this slice's actual data**: coverage counts (`coverage.<PERSON>.<LAYER>`), coding-label frequency tally (`label_frequency.<label>`), and up to 3 divergence classifications (`divergence.*`) if the selected person/pair has one. No `score_value`, no `model_version` — this screen's "점수" step is replaced by an explicit **"아직 합성 점수 없음"** panel explaining why (N=22 too small, no approved weighting yet), per `analysis/scoring_model.md`.
- Primary action: open the weight-lab control — **shown but disabled**, with the reason text visible ("가중치 모델이 아직 승인되지 않아 지금은 근거 커버리지만 봅니다"), not silently hidden, so the feature's existence is legible without pretending it works today.
- Secondary actions: jump to the specific evidence rows backing a divergence classification (`divergence.*`'s `evidence_ids`, currently embedded in the metric's `method` text — see `component_spec.md` for the flagged schema gap).
- Trust cues: explicit `population.n`, the three `limitations[]` bullets from `result.json`, and D-017's "LLM-coded, not human-validated" note.

### States (S-003)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | result.json fetch pending | skeleton | — |
| empty | person has no metrics at all | "표시할 관측 데이터 없음" | back |
| insufficient evidence (default for "점수" step, this slice) | no composite score exists | "아직 합성 점수 없음" panel (see above) | view coverage instead |
| partial | some metrics present, weight-lab unavailable | coverage/labels shown, weight control disabled | — |
| stale | `run_manifest.json` outdated | stale badge | refresh |
| error | fetch failed | retry | retry |
| permission unavailable | n/a | — | — |

## S-004 — AI answer panel (shared, mode-aware)

- User goal: ask a scoped question and get an evidence-linked answer, or an explicit refusal.
- Entry: from S-002/S-003 (context carried) or a standalone question box. Exit: back to the evidence it cited, or nowhere (dead-end panel is fine).
- Primary content: current `answer_mode` (정사/연의/비교/게임), the answer text, and one `evidence_id` chip per claim (schema pending `analysis/llm_contract.md`/`interpretation.schema.json` from the parallel L1 track — this screen's exact claim-schema will need a reconciliation pass once L1 reports, flagged for the orchestrator, not guessed here).
- Primary action: click an evidence chip → S-002's card for that ID.
- Secondary actions: switch `answer_mode`.
- Trust cues: mode label always visible; 연의 mode answers are visually marked as literary, not historical (per `_three_kingdoms_domain.md` LLM 답변 모드).

### States (S-004)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | LLM call pending | typing/skeleton indicator | cancel if supported |
| empty | no question asked yet | prompt + example questions | ask |
| insufficient evidence / LLM refused/abstained | requested claim has no backing evidence | explicit abstention text + reason, distinct from error | rephrase/ask different question |
| partial | some claims answered, one abstained | mixed rendering, abstained claim clearly marked | — |
| stale | n/a (always live) | — | — |
| error/retryable | AI service unavailable | error state, retry action | retry |
| permission unavailable | n/a this slice | — | — |

## S-005 — Quest (적벽대전, Learning-game, L-01/L-02)

- User goal: complete a guided flow that forces opening both source layers plus one counter-evidence item before "완료" is reachable (AC-5).
- Entry: from S-001 "학습 시작". Exit: → S-006 (quiz) after step gates satisfied, or → Explorer mode mid-quest (shared foundation, progress preserved).
- Primary content: `QuestCard` — stated goal, completion condition, list of `evidence_id`s seen vs. not-yet-seen (client-tracked set against `evidence_matrix.csv` IDs), one flagged counter-evidence item.
- Primary action: open next unseen required evidence card (routes into S-002's `EvidenceCard`, quest chrome layered on top).
- Secondary actions: switch to Explorer without losing quest state.
- Trust cues: explicit progress state (which gates are satisfied), never a fake "완료" enabled before both conditions are real.

### States (S-005)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | quest data/evidence pending | skeleton quest card | — |
| empty | no quest defined for this event yet | n/a this slice (quest exists) | — |
| insufficient evidence | claim chosen for counter-evidence checkpoint has too little evidence to support one | quest surfaces a different claim within the same event (per `user_journeys.md` edge branch), not a fake checkpoint | — |
| partial | one gate satisfied, one not | "완료" visibly disabled, unmet gate named | open remaining evidence |
| stale | evidence matrix changed since quest started | notice + option to refresh quest content | refresh |
| error | fetch failed | retry | retry |
| permission unavailable | n/a | — | — |

## S-006 — Evidence-linked quiz (Learning-game, L-04)

- User goal: answer 2–4 items tied to evidence already seen in S-005.
- Entry: from S-005 after gates satisfied. Exit: → quest-complete state (back to S-005/S-001).
- Primary content: quiz item text, answer options, and after answering, a link back to the specific `evidence_id` that supports the correct answer. **Exact item schema is `[TBD]`** (`product/feature_spec.md` L-04) — this brief specifies the interaction shape, not the final data contract; do not build against a guessed schema.
- Primary action: submit answer.
- Secondary actions: revisit the linked evidence before answering (allowed, not a violation of the quest gate — the quiz item is already unlocked).
- Trust cues: post-answer view always shows the `evidence_id` link, correct or not — the point is evidence-checking behavior, not scoring accuracy (`product/gamification_spec.md`).

### States (S-006)

| State | Trigger | Content | Action |
| --- | --- | --- | --- |
| loading | quiz items pending | skeleton | — |
| empty | quiz item schema not yet implemented | explicit "퀴즈 준비 중" rather than broken UI | back to quest |
| insufficient evidence | n/a (items only unlock after evidence is seen) | — | — |
| partial | some items answered | progress shown | continue |
| stale | n/a | — | — |
| error | submission failed | retry | retry |
| permission unavailable | n/a | — | — |
