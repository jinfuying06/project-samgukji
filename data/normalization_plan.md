# Normalization Plan

Status: `DRAFT — execution requires B0 approval`

## Non-destructive contract

- Raw bytes and paths remain unchanged.
- All transforms write to the private analysis zone.
- Every output records input checksum, pipeline version, parameters, and timestamp.

## Planned steps

1. Decode with recorded source encoding.
2. Preserve original Unicode text.
3. Create optional normalized Unicode derivative.
4. Create optional simplified/traditional mapping as a separate field.
5. Remove crawler/HTML artifacts with logged rules.
6. Segment work/volume/chapter/paragraph without discarding original locators.
7. Assign source, evidence, entity, and event candidate IDs.
8. Validate counts, hashes, round-trip locators, and source-layer separation.

## Decisions required before execution

- **Edition mapping**: single edition per work confirmed by inventory — `history_base_zh` = 陳壽《三國志》 65 卷 (`zh.wikisource.org`), `romance_zh` = 羅貫中《三國演義》 120 回 (`zh.wikisource.org`). No competing editions were found in this raw drop, so no edition-conflict resolution is needed for this sample; if a second edition is added later, it must get its own `edition_ref` and never overwrite this one.
- **Script conversion policy (proposed)**: corpus is traditional-Chinese-dominant (154/185 files by heuristic). Proposal: keep original traditional text as the authoritative field; generate a simplified-Chinese derivative as a separate, clearly labeled field using a vetted converter (e.g. OpenCC) with tool/version recorded, never overwriting the original. The 11 files flagged `mixed_or_uncertain`/`simplified_dominant` in `data/ingestion_report.md` must be manually spot-checked before this rule is applied to them.
- **Annotation separation**: moot for this raw drop — `history_annotations_zh` has 0 files, so there is currently no `HISTORY_ANNOTATION` material to separate. Proposal: proceed to S1 without this layer, record it as an explicit scope exclusion in `product/concepts` and `research/protocol.md`, and open a follow-up task to source 裴松之注 (or equivalent) before any release that claims annotation-layer coverage.
- **Permitted excerpt storage**: proposal — store full original `body_text` only in the private analysis zone (`data/private/analysis` or `${TKAF_PRIVATE_DATA_ROOT}/analysis`), never in the repository. Any user-facing or committed artifact may only carry short evidence excerpts (a sentence or two) plus a stable locator (juan/回 + paragraph/offset), consistent with `research/source_policy.md`. Since both texts trace to the same public-Wikisource domain and are historical/imperial-era works, excerpt risk is lower than for modern translations, but this is not a substitute for the B-D0-2 rights review in `data/ingestion_report.md`.
- **First sample scope (proposed)**: 赤壁大戰 (Battle of Red Cliffs) — `history_base_zh` juan {01,10,31,32,35,47,48,54,55,56} and `romance_zh` 回 49–61, narrowed at S1 kickoff to the 3–5 people / 20–40 evidence-span target from `PROJECT_BRIEF.md`. See `data/ingestion_report.md` "Recommended sample" for the keyword-hit evidence and the 官渡 (Guandu) alternative. This is a recommendation for the B0 human decision, not a preselection.

