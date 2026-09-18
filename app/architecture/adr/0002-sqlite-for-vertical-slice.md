# ADR 0002: SQLite Runtime DB, No Graph Database, for the 적벽대전 Vertical Slice

- Status: Accepted
- Date: 2026-09-17

## Context

The runtime DB must serve `/v1/events`, `/v1/people/*/evidence`, `/v1/events/*/metrics`, and `/v1/events/*/relationships` for one event, 5(+) persons (D-016 expansion pending), and dozens of evidence rows. `.env` already anticipates `TKAF_APP_DATABASE_URL=sqlite:///data/runtime/tkaf.local.sqlite3`. `agents/architect.md` prohibits unjustified decomposition/complexity.

## Decision

Use a single relational SQLite database for this slice. Network edges (`relationship.schema.json`) are stored as a typed table (`from_person_id`, `to_person_id`, `relation_type`, `source_layer`, `evidence_refs`), queried directly — no graph database, no in-memory graph library, no centrality computation (matches `analysis/network_analysis_plan.md`'s explicit decision not to compute centrality at this N).

## Consequences

- Simple deployment: one file-based DB, no separate graph service to run/monitor.
- Relationship queries (list edges for an event, filter by source_layer) are simple `WHERE` queries; if centrality/graph-traversal analysis is ever added, it would run offline in the analysis pipeline (producing more `Metric` rows), not as a live graph-database query.
- Revisit if the corpus scales toward the full 65-juan/120-回 dataset (post D-016 full-expansion) and centrality/traversal queries become a real product feature — that would justify a graph store or a graph-query extension, but not before there's an actual feature requiring it.
