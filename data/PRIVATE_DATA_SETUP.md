# Private Data Setup

## Recommended: keep actual data outside the repository

Create a sibling directory manually or with the provided helper.

```bash
python scripts/init_private_data.py ../tkaf-private-data
```

Set the local-only `.env` file:

```text
TKAF_PRIVATE_DATA_ROOT=../tkaf-private-data
TKAF_APP_DATABASE_URL=sqlite:///data/runtime/tkaf.local.sqlite3
```

Suggested private directory:

```text
tkaf-private-data/
├── raw/inbox/
│   ├── history_base_zh/
│   ├── history_annotations_zh/
│   ├── romance_zh/
│   └── unclassified/
├── analysis/
│   ├── normalized/
│   ├── tables/
│   ├── notebooks_output/
│   └── results/
└── curated/app_export/
```

## Alternative: local private data under the repository

If convenience matters more, use `data/private/`. The `.gitignore` excludes all contents except directory placeholders. Still verify before every commit:

```bash
python scripts/check_data_boundaries.py
git status --short
```

## First operation must be read-only inventory

The Data Engineer must not reorganize the raw folder. It creates file/hash/encoding/duplicate/source-layer/rights inventories and a proposed normalization pipeline.

Only after B0 approval may a small sample be copied into the analysis zone and normalized.

## Chinese text rules

- Preserve original bytes and original relative paths.
- Convert to UTF-8 only in the analysis zone.
- Preserve original text beside any simplified/traditional derivative.
- Record the conversion tool and version; never silently replace characters.
- Separate HISTORY_BASE, HISTORY_ANNOTATION, and ROMANCE.
- Stable locators include source ID, volume/chapter, paragraph, offsets, and text hash.

