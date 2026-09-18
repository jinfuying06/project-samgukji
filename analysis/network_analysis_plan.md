# Source-Aware Network Analysis Plan

## Graph definitions

Create separate graphs by source layer before comparison.

- Nodes: people, factions, events, places
- Edges: typed, directed where appropriate, temporal, evidence-backed
- `co_occurrence` is never silently treated as alliance or interaction

## Candidate metrics

| Metric | Possible interpretation | Required caution |
| --- | --- | --- |
| Degree | number of modeled ties | coverage and text-length dependent |
| Betweenness | brokerage in this graph | not innate political skill |
| Closeness | modeled reachability | unstable for disconnected graphs |
| Community | structural grouping | algorithm/resolution dependent |

## Comparison

- Use the same node/edge definition where possible.
- Report unmatched entities/relations separately.
- Normalize or stratify for corpus length and source coverage.
- Inspect whether key differences come from one passage or broad patterns.
- Always provide event/evidence drill-down for highlighted edges.

## 적벽대전 vertical-slice application (S1/A1, 2026-09-17; updated S3, 2026-09-18 per D-026)

- Edge definition used: a directed edge exists when a `research/evidence_matrix.csv` row has both a real, named `primary_actor` and `subject_of_claim` (commentators like `孫盛(commentator)` and cited works like `江表傳(source)` are excluded as nodes — they are sources commenting on the event, not participants in it). `relation` = the row's `coding_label`; every edge carries its `evidence_id`, `source_layer`, and `confidence` for drill-down. `source`/`target` are canonical `person.xxx` IDs, matching the curated export/backend API's node identity (`NAME_ZH_TO_CANONICAL_ID` in `analysis/pipelines/compute_chibi_result.py`).
- **Resolved open follow-up:** `analysis/outputs/result.json` now carries the actual `edges` array (not just counts), and `analysis/schemas/result.schema.json` was extended with a typed `edges` field to match — validated with `jsonschema` against a real `result.json` run. UI/graph views no longer need to parse `metrics[].method` strings for edge data.
- Current counts (post D-016 expansion, 10 persons / 30 evidence rows): **HISTORY_BASE 2 edges / HISTORY_ANNOTATION 5 edges / ROMANCE 3 edges** (10 total, never merged into one graph) — up from the original 5-person slice's 2/3/3.
- **New descriptive stats added** (`network_unique_nodes.*`, `network_density.*`, `network_cross_layer_shared_pairs` metrics): unique node count and edge density are now reported per layer, each with an explicit caution in its `method` field that density reflects which rows happened to name both an actor and a subject, not real social closeness. **No centrality metric (degree/betweenness/closeness/community) is computed or reported anywhere** — still correctly withheld at this N per the original decision below.
- **Cross-layer finding (real, not fabricated):** `network_cross_layer_shared_pairs` = **0** in the current 30-row set — no unordered person-pair currently has an edge in more than one source layer. This is itself informative: it means the "same two people, different story" comparison this metric was designed to surface doesn't yet have a case to show, not that source layers agree or disagree on any specific relationship. Revisit once more evidence rows are coded (particularly rows with a non-empty `subject_of_claim`, which most rows still lack).
- At this N, **no centrality metric (degree/betweenness/closeness/community) is computed or reported.** With 2-5 edges per layer, any such metric would be an artifact of which spans happened to get coded first, not a structural signal — this is the "coverage and text-length dependent" caution the table above already flags, taken to its practical conclusion at this sample size.
- Most evidence rows (23 of 30) have no `subject_of_claim` at all (the person is the sole actor/subject of the passage, e.g. `minimal_narrative_role`, `psychosomatic_strategic_anxiety`), so this is a sparse, partial interaction graph, not a full social network of the battle — do not present it as one.
- **Known duplication, not resolved here:** `data/pipelines/build_curated_export.py` independently computes its own relationship edges for the backend's `/v1/events/{id}/relationships` endpoint (via `name_to_person_id` resolution against the person registry), separate from this script's `edges` computation. Both should produce the same edges given the same input, but there is currently no single shared source of truth between the two pipelines — flagged for whoever next touches either script, not fixed in this pass (out of this task's write scope).

