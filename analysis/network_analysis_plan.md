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

