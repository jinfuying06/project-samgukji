# Raw Data Ingestion Report

Status: `READ_ONLY_INVENTORY_COMPLETE`

Produced during S0/D0 after a read-only inventory. Do not paste corpus text into this committed report.

## Inventory summary

- Private data root reference: `${TKAF_PRIVATE_DATA_ROOT}/raw/inbox` (sibling directory outside the Git repository; local `.env` sets `TKAF_PRIVATE_DATA_ROOT=../tkaf-private-data`).
- Read-only confirmed: yes. No file under `raw/inbox` was moved, renamed, overwritten, or converted in place. Full per-file evidence (path, size, SHA-256) is recorded in `${TKAF_PRIVATE_DATA_ROOT}/manifests/raw_file_inventory.full.csv` (outside the repo, not committed) and a domain-redacted copy is committed at `data/manifests/raw_file_inventory.template.csv`.
- Files/bytes: 185 files total, all `.json`, all parse as valid JSON.
  - `history_base_zh/`: 65 files, ~2.15 MB (2,247,464 bytes)
  - `history_annotations_zh/`: 0 files, 0 bytes
  - `romance_zh/`: 120 files, ~1.67 MB (1,746,765 bytes)
- Formats/encodings: 100% `.json`, 100% decode cleanly as UTF-8. No non-UTF-8 files found.
- Script type (traditional vs. simplified, heuristic character-pair count over `body_text`):
  - `traditional_dominant`: 154 files
  - `traditional` (no simplified-only markers found): 20 files
  - `mixed_or_uncertain`: 10 files
  - `simplified_dominant`: 1 file
  - Net: the corpus is overwhelmingly Traditional Chinese. The 1 simplified-leaning and 10 mixed files should be re-checked file-by-file before normalization (heuristic is a character-pair count, not a certified script detector).
- Source-layer classification: derived directly from folder name, matches each file's internal structure.
  - `history_base_zh` → `HISTORY_BASE` (65 files, `work_title` = 三國志, `unit`/`num`/`label` = 卷 1–65)
  - `romance_zh` → `ROMANCE` (120 files, `work_title` = 三國演義, `label` = 回 1–120, i.e. the full 120-chapter novel)
  - `history_annotations_zh` → `HISTORY_ANNOTATION`: **0 files present**. No 裴松之注 (Pei Songzhi commentary) or other annotation-layer material exists in this raw drop.
- Duplicate/damage findings: 0 duplicate files (by SHA-256), 0 corrupt/unparseable files, 0 files with empty `body_text`. The corpus is structurally clean.
- Metadata completeness: every file carries `work_title`, `author`, `unit`, `num`, `label`, `title`, `url`, `source`, `crawled_at`, `body_text`, and a layer-specific field (`listed_persons` for history, `chapter_title` for romance). `crawled_at` for the sampled files is `2026-08-06`.
- Source/domain: both `history_base_zh` and `romance_zh` files' `source`/`url` fields resolve to the single domain `zh.wikisource.org` (Chinese Wikisource). Full URLs are kept only in the non-committed full manifest; only the domain is in the committed template per `data/manifests/README.md`.
- Rights status: `[TBD — legal review needed]`. Non-binding note for the reviewer: both 陳壽《三國志》 and 羅貫中《三國演義》 are historical/imperial-era works whose original Chinese text is in the public domain; Wikisource itself publishes such texts under an open license. This is a favorable signal, not a legal conclusion — the crawl may still carry site-specific formatting/derivative-work considerations, and this finding does not cover any future annotation or translation layer. Formal confirmation is still required before any public-facing use.

## Blockers and questions

- **B-D0-1 (material):** `history_annotations_zh` is empty. The domain model (`agents/_three_kingdoms_domain.md`) treats `HISTORY_ANNOTATION` (裴注 etc.) as a required, distinct evidence layer for comparison and for resolving `HISTORY_BASE` vs `ROMANCE` conflicts. With zero annotation files, S1's evidence matrix cannot include this layer unless (a) it is explicitly scoped out for S1 and revisited later, or (b) additional raw data is sourced. This should go to `handoffs/OPEN_QUESTIONS.md` for the B0 decision.
- **B-D0-2:** Rights status is not legally confirmed. Recommend proceeding with the S1 *sample-scale, non-public* analysis while treating any public/user-facing release of excerpts as blocked pending real legal review (see `research/source_policy.md` translation/excerpt rules).
- **B-D0-3 (minor):** 11 files show `mixed_or_uncertain` or `simplified_dominant` script-type by the heuristic; recommend the Data Engineer re-verify these specific files with a proper OpenCC-based detector before any script normalization step, rather than trusting the lightweight character-pair heuristic used here.

## Recommended sample

Both 官渡 (Guandu) and 赤壁 (Chibi/Red Cliffs) are attested in **both** source layers (see keyword-hit detail in `data/normalization_plan.md`), so either is viable for S1. Recommendation: **赤壁大戰 (Battle of Red Cliffs)**.

- Romance hits form one tight, contiguous block: 回 49–61 (13 of 120 chapters), matching the well-known Red Cliffs narrative arc — easy to bound a small evidence set.
- History hits span 10 of 65 juan, a manageable read for double-coding.
- The event naturally involves a small, clear cast (曹操, 孫權, 劉備, 周瑜, 諸葛亮) that fits the S1 target of 3–5 people / 20–40 evidence spans without extra scoping work.
- Guandu is a reasonable alternative: its Romance hits (回 22,24,26,30,31,32,40) are also fairly contiguous, but its History hits are spread across 17 of 65 juan (many biographies mention it only in passing), which would take more effort to bound tightly for a first vertical slice. It may be a better candidate later for network-analysis breadth.

Final selection is a B0 decision, not preselected here.
