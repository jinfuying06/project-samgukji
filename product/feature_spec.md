# Feature Spec — S1 Vertical Slice (적벽대전, Hybrid concept)

Status: `S1 DRAFT — scoped to the 적벽대전 (Battle of Red Cliffs) vertical slice only`. Concept decided at B0: **Hybrid** (`handoffs/DECISIONS.md#D-009`). Sample: 적벽대전 (`#D-010`). Source layers: `HISTORY_BASE` + `ROMANCE`, plus `HISTORY_ANNOTATION` if D1's extraction from already-crawled raw yields usable coverage (`#D-011`, `handoffs/OPEN_QUESTIONS.md#Q-006`) — every annotation-dependent feature below has an explicit degraded state for when it does not.

Cast (candidate, confirmed by R1/D1, not to exceed 3–5 people per `PROJECT_BRIEF.md`§4): 曹操, 孫權, 劉備, 周瑜, 諸葛亮. Evidence budget: 20–40 spans total across all source layers, per this one event.

Hybrid ships as **two modes sharing one evidence/score foundation** — not two separate products. A user can start in either mode and switch mode without losing their place (same person/event context).

## 0. Shared foundation (both modes depend on this; owned by R1/D1/A1, not by either mode)

| ID | Capability | Data contract | Notes |
| --- | --- | --- | --- |
| F-00 | Source-mode switching (정사 / 정사 주석 / 연의 / 비교 / 게임) | `source_layer` enum per `agents/_three_kingdoms_domain.md` | `SourceModeControl` component (`design/DESIGN.md`§6). 정사 주석 mode is disabled with an "insufficient evidence" state (§7 of DESIGN.md) if D1 reports too little extracted annotation coverage for 적벽대전. |
| F-01 | Evidence card retrieval by person/event | `evidence_id, source_layer, work, edition, locator, quotation_type, confidence` (`research/source_policy.md`) | No evidence is shown without a resolvable `evidence_id`. |
| F-02 | Score breakdown (기본 점수) | `score_value, unit, model_version, coverage, confidence` → `ContributionBreakdown` | Built only from `analysis/outputs/result.json` once A1 delivers it; not implemented ahead of that data. |
| F-03 | Source-layer comparison view | parallel `HISTORY_BASE` vs `ROMANCE` (vs `HISTORY_ANNOTATION` if available) for the same claim/event | Never merges layers into one row; conflicts are shown side by side, not resolved automatically (`_three_kingdoms_domain.md` 출처 층위). |
| F-04 | AI answer panel with evidence refs | `answer_mode ∈ {정사, 연의, 비교, 게임}, claims[].evidence_id[]` | Answer is withheld (not guessed) when evidence for the requested mode/person/event is insufficient. |

## 1. Explorer mode

| ID | Feature | User outcome | Data contract | Traceable to |
| --- | --- | --- | --- | --- |
| E-01 | 적벽대전 event overview | User sees the event, its cast, and which source layers have data for it before choosing where to dig in | `event_id, source_layer_coverage[]` | F-00, F-03 |
| E-02 | Person comparison across source layers | User compares one person's portrayal in 정사 vs 연의 (and 정사 주석 if available) side by side, with evidence, for this one event | F-01, F-03 | `agents/_three_kingdoms_domain.md` 점수와 비교 |
| E-03 | Free-form AI question with evidence IDs | User asks a question scoped to this event/cast and gets an answer with per-claim evidence refs, or an explicit "근거 부족" refusal | F-04 | PROJECT_BRIEF §4 "AI 답변의 근거 ID" |
| E-04 | Custom weight experiment | User adjusts sub-indicator weights and sees a **user custom score** recomputed client-side from the same evidence — never silently replacing or hiding the default score | F-02 | `design/DESIGN.md`§4 "사용자 설정 점수 표시를 제거할 수 없게" |

Non-promise: E-02/E-03 do not claim full-corpus coverage — they are scoped to 적벽대전's cast and evidence set only (PROJECT_BRIEF vertical-slice limit).

## 2. Learning-game mode

| ID | Feature | User outcome | Data contract | Traceable to |
| --- | --- | --- | --- | --- |
| L-01 | Guided quest through 적벽대전 evidence | User follows a short quest that requires opening both 정사 and 연의 evidence for at least one claim before it can complete | `QuestCard` states (`design/DESIGN.md`§6) | `_three_kingdoms_domain.md` 게이미피케이션 가드레일 |
| L-02 | Counter-evidence checkpoint | Quest cannot be marked complete by a single click; user must acknowledge at least one piece of evidence that complicates or contradicts their first impression | quest completion requires ≥1 "반대 근거 확인" event | same as above |
| L-03 | Score-formula reveal step | Before showing any score, the game shows the formula path (관측 근거 → 코드 → 하위 지표 → 정규화 → 가중치 → 표시 점수) as an explicit step, not a footnote | F-02 | `_three_kingdoms_domain.md` 점수와 비교 |
| L-04 | Evidence-based quiz (single event, single quiz) | User answers 2–4 questions whose correct answers are checkable against `evidence_id`s already shown in the quest, then sees which evidence supports the answer | evidence-linked quiz item schema `[TBD — R1/A1 to define exact item format in S1 if time allows; not blocking B1]` | `design/DESIGN.md`§5 |
| L-05 | Difficulty/learning-level presentation | **OPEN — Q-005 대기.** Whether this ships as a single fixed difficulty or a beginner/intermediate toggle depends on the human owner's answer to Q-005. Until answered, L-01–L-04 are specified at a single, unspecified difficulty level; do not build a difficulty selector speculatively. |

Explicit non-goals for this slice (do not build): a full curriculum beyond this one event, a second quest/event, adaptive difficulty, leaderboards, or any 8-bit battle rendering. The 8-bit visual motif is optional future decoration for L-01's "결과 확인" step, not a system to implement now (README.md's vertical-slice completion definition does not include it).

## 3. Cross-mode guardrails (apply to both E-* and L-*)

- 기본 점수 / 사용자 커스텀 점수 / 게임 수치(`GAME_DATA`, if ever introduced) are always three distinct labeled objects, never merged (`design/DESIGN.md`§4).
- No feature computes or displays a single "누가 최강인가" ranking; every score view leads with "어떤 기준에서 왜" (contribution breakdown) before any number (`agents/product_manager.md`).
- No feature treats missing annotation/evidence as a 0 score — insufficient-evidence and stale-result states (`design/DESIGN.md`§7) are used instead.
- No feature promises coverage the data doesn't have: annotation-dependent UI (F-00's 정사 주석 mode, E-02's three-way comparison) must degrade explicitly rather than silently showing only two layers as if that were complete.

## 4. Explicit non-scope for S1/S2 (do not implement yet)

- Full person database beyond the 3–5-person cast (PROJECT_BRIEF §4).
- Personality/mental-state diagnosis of any person.
- User-vs-user competition or leaderboards.
- Unreviewed auto-generated facts published to users.
- Production UI code, 8-bit battle system, full curriculum — gated behind B2 (`handoffs/CURRENT_TASK.md`).

## Open items carried from B0/S1

- Q-005 (learning-game difficulty level) — blocks finalizing L-05 only; does not block B1.
- Q-009 (primary user data-literacy assumption) — affects how much explanatory scaffolding E-01–E-04 need by default; until answered, all screens default to the more explanatory (lower-literacy-friendly) presentation per `design/DESIGN.md` information hierarchy, and this default is called out in `product/acceptance_criteria.md`.
