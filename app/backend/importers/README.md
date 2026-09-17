# Curated Export Importers

Importers may read only an approved package from the private curated app-export zone. They must:

- validate `app_export_manifest.schema.json`
- verify every file checksum
- validate record schemas and source-layer values
- run atomically/idempotently
- record export/schema/pipeline versions
- preserve evidence and score provenance
- reject packages without an approval reference
- leave the previous serving version intact on failure

Importers must never crawl sources, normalize raw text, run exploratory analysis, or read the private analysis workspace.

