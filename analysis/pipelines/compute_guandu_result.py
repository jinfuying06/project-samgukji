#!/usr/bin/env python3
"""Reproducible A1 aggregation for the 관도대전 (Battle of Guandu) vertical slice --
second event in the per-battle expansion (handoffs/DECISIONS.md#D-036), mirroring
analysis/pipelines/compute_chibi_result.py's exact method for 적벽대전.

Input: research/evidence_matrix_guandu.csv (committed, short-excerpt evidence rows only).
Output: analysis/outputs/guandu_result.json (conforms to analysis/schemas/result.schema.json)
        analysis/outputs/guandu_run_manifest.json (input hash, script version, timestamp).

This script only counts and classifies rows that already exist in
evidence_matrix_guandu.csv. It does not read raw corpus text and does not invent any
value. Every number here must be reproducible by re-running this script against the
same evidence_matrix_guandu.csv.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_CSV = ROOT / "research" / "evidence_matrix_guandu.csv"
RESULT_JSON = ROOT / "analysis" / "outputs" / "guandu_result.json"
MANIFEST_JSON = ROOT / "analysis" / "outputs" / "guandu_run_manifest.json"

# Display-name fallback for known PERSON-* IDs -- see compute_chibi_result.py's identical
# comment: this is NOT the cast list, just a readable-name lookup. Cast is derived
# dynamically from whatever PERSON-* refs actually appear in the CSV.
KNOWN_DISPLAY_NAMES = {
    "PERSON-CAOCAO": "曹操",       # shared with 적벽대전 cast
    "PERSON-GUOJIA": "郭嘉",       # shared with 적벽대전 cast
    "PERSON-GUANYU": "關羽",       # shared with 적벽대전 cast
    "PERSON-YUANSHAO": "袁紹",
    "PERSON-XUNYU": "荀彧",
    "PERSON-XUYOU": "許攸",
    "PERSON-ZHANGHE": "張郃",
    "PERSON-JUSHOU": "沮授",
    "PERSON-TIANFENG": "田豐",
}
LAYERS = ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"]

# Matches data/pipelines/build_guandu_sample.py's CANONICAL_PERSONS ids exactly (same
# convention as compute_chibi_result.py's PERSON_TOKEN_TO_CANONICAL_ID -- duplicated
# rather than imported across the data/analysis pipeline boundary, kept in sync by hand).
PERSON_TOKEN_TO_CANONICAL_ID = {
    "PERSON-CAOCAO": "person.cao_cao",
    "PERSON-GUOJIA": "person.guo_jia",
    "PERSON-GUANYU": "person.guan_yu",
    "PERSON-YUANSHAO": "person.yuan_shao",
    "PERSON-XUNYU": "person.xun_yu",
    "PERSON-XUYOU": "person.xu_you",
    "PERSON-ZHANGHE": "person.zhang_he",
    "PERSON-JUSHOU": "person.ju_shou",
    "PERSON-TIANFENG": "person.tian_feng",
}
NAME_ZH_TO_CANONICAL_ID = {
    name_zh: PERSON_TOKEN_TO_CANONICAL_ID[token]
    for token, name_zh in KNOWN_DISPLAY_NAMES.items()
}

META_ACTOR_MARKERS = ("(commentator)", "(source)", "(annotator)")


def discover_cast(rows: list[dict]) -> dict[str, str]:
    ids: set[str] = set()
    for row in rows:
        for ref in (r.strip() for r in row["person_refs"].split(";")):
            if ref.startswith("PERSON-") and is_real_person(ref):
                ids.add(ref)
    return {pid: KNOWN_DISPLAY_NAMES.get(pid, pid) for pid in sorted(ids)}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def is_real_person(name: str) -> bool:
    if not name:
        return False
    return not any(marker in name for marker in META_ACTOR_MARKERS)


def load_rows() -> list[dict]:
    with EVIDENCE_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def compute(rows: list[dict]) -> dict:
    metrics: list[dict] = []
    warnings: list[str] = []
    limitations: list[str] = []

    cast = discover_cast(rows)
    coverage = {pid: {layer: 0 for layer in LAYERS} for pid in cast}
    for row in rows:
        refs = [r.strip() for r in row["person_refs"].split(";") if r.strip()]
        layer = row["source_layer"]
        for ref in refs:
            if ref in coverage:
                coverage[ref][layer] += 1

    for pid, display in cast.items():
        for layer in LAYERS:
            metrics.append(
                {
                    "metric_id": f"coverage.{pid}.{layer}",
                    "name": f"Evidence-span coverage count: {display} ({layer})",
                    "value": coverage[pid][layer],
                    "unit": "evidence_span_count",
                    "interval_low": None,
                    "interval_high": None,
                    "method": (
                        "Count of research/evidence_matrix_guandu.csv rows whose person_refs "
                        f"includes {pid} and source_layer == {layer}. Coverage/emphasis "
                        "fact only, not a capability or ability score, and not comparable "
                        "across persons as a ranking."
                    ),
                }
            )

    label_counts: dict[str, int] = {}
    for row in rows:
        label = row["coding_label"]
        label_counts[label] = label_counts.get(label, 0) + 1
    for label, count in sorted(label_counts.items()):
        metrics.append(
            {
                "metric_id": f"label_frequency.{label}",
                "name": f"Coding-label frequency: {label}",
                "value": count,
                "unit": "evidence_span_count",
                "interval_low": None,
                "interval_high": None,
                "method": (
                    "Count of research/evidence_matrix_guandu.csv rows with this coding_label. "
                    f"Exploratory descriptive count only (N={len(rows)} total); not adjusted "
                    "for text length or narrative opportunity -- a label tally, not a trait score."
                ),
            }
        )

    edges: list[dict] = []
    for row in rows:
        actor = row["primary_actor"].strip()
        subject = row["subject_of_claim"].strip()
        if is_real_person(actor) and is_real_person(subject) and subject:
            edges.append(
                {
                    "source": NAME_ZH_TO_CANONICAL_ID.get(actor, actor),
                    "source_name_zh": actor,
                    "target": NAME_ZH_TO_CANONICAL_ID.get(subject, subject),
                    "target_name_zh": subject,
                    "relation": row["coding_label"],
                    "source_layer": row["source_layer"],
                    "evidence_id": row["evidence_id"],
                    "confidence": row["confidence"],
                }
            )

    edges_by_layer: dict[str, list[dict]] = {layer: [] for layer in LAYERS}
    for e in edges:
        edges_by_layer[e["source_layer"]].append(e)

    for layer in LAYERS:
        metrics.append(
            {
                "metric_id": f"network_edge_count.{layer}",
                "name": f"Person-to-person network edges ({layer})",
                "value": len(edges_by_layer[layer]),
                "unit": "edge_count",
                "interval_low": None,
                "interval_high": None,
                "method": (
                    "Count of evidence_matrix_guandu.csv rows with both a real "
                    "(non-commentator, non-annotator) primary_actor and subject_of_claim, "
                    "grouped by source_layer. Layers are never merged into one graph."
                ),
            }
        )
    metrics.append(
        {
            "metric_id": "network_edge_count.total",
            "name": "Person-to-person network edges (all layers, unmerged list)",
            "value": len(edges),
            "unit": "edge_count",
            "interval_low": None,
            "interval_high": None,
            "method": "Sum of the three per-layer edge counts above. Layers are never merged into one graph.",
        }
    )

    network_summary_by_layer: dict[str, dict] = {}
    for layer in LAYERS:
        layer_edges = edges_by_layer[layer]
        nodes = {e["source"] for e in layer_edges} | {e["target"] for e in layer_edges}
        max_pairs = len(nodes) * (len(nodes) - 1)
        density = (len(layer_edges) / max_pairs) if max_pairs > 0 else None
        network_summary_by_layer[layer] = {
            "unique_node_count": len(nodes),
            "edge_count": len(layer_edges),
            "density": density,
            "density_caution": (
                f"edges / (nodes * (nodes-1)) for the {layer} graph only "
                f"(nodes={len(nodes)}, edges={len(layer_edges)}). At this N, density reflects "
                "which evidence rows happened to name both an actor and a subject, not real "
                "social closeness or narrative centrality -- do not present as a sociability "
                "or importance score. null when fewer than 2 nodes."
            ),
            "unique_node_count_note": (
                f"Distinct canonical person_ids appearing as source or target of a {layer} "
                f"edge -- smaller than the full {len(cast)}-person cast in most layers, since "
                "most evidence rows have no subject_of_claim. A person absent here may still "
                "have real coverage.* evidence in this layer, just not in actor-subject form."
            ),
        }

    pair_layers: dict[tuple[str, str], dict[str, list[dict]]] = {}
    for e in edges:
        pair = tuple(sorted((e["source"], e["target"])))
        pair_layers.setdefault(pair, {}).setdefault(e["source_layer"], []).append(e)
    shared_pairs = {pair: by_layer for pair, by_layer in pair_layers.items() if len(by_layer) > 1}
    network_summary = {
        "by_layer": network_summary_by_layer,
        "cross_layer_shared_pair_count": len(shared_pairs),
        "cross_layer_shared_pairs": [
            {
                "person_a": a,
                "person_b": b,
                "relations_by_layer": {layer: [e["relation"] for e in es] for layer, es in by_layer.items()},
            }
            for (a, b), by_layer in shared_pairs.items()
        ],
        "cross_layer_note": (
            "Count/list of unordered (person_a, person_b) pairs with at least one edge in 2+ "
            "of {HISTORY_BASE, HISTORY_ANNOTATION, ROMANCE}. Same-pair-different-layer "
            "relation labels are a real comparison point, not a centrality or importance "
            "measure. An empty list means no pair currently shares an edge across layers in "
            "this slice -- itself informative, not an error."
        ),
    }

    # Pre-registered source-layer divergence classifications -- see
    # research/coding_manual_guandu.md's "Ambiguity handling" section for the full
    # reasoning behind each; this is the same qualitative-classification mechanism as
    # compute_chibi_result.py's divergence_cases (compatible/complementary/contradictory),
    # scoped strictly to the coded rows compared, not the full novel/history.
    divergence_cases = [
        {
            "case_id": "divergence.zhanghe_defection_cause",
            "name": "Divergence: why 張郃 defected to 曹操",
            "evidence_ids": ["HB-J01-P5", "HA-J17-P1"],
            "classification": "contradictory",
            "rationale": (
                "HB-J01-P5 (武帝紀): frames 張郃's defection as opportunistic, immediately "
                "after hearing the Wuchao raid succeeded. HA-J17-P1 (裴松之 annotation on "
                "張郃's own biography) explicitly names this as a discrepancy: 張郃's own "
                "biography instead attributes the defection to fear of 郭圖's false "
                "accusation after the defeat, not to the Wuchao news itself. This is the "
                "one case in this event's coding where an annotation itself flags the "
                "conflict (coded coding_label=source_conflict_note at HA-J17-P1), unlike "
                "許攸's defection (HB-J01-P4 vs HB-J10-P2), where two HISTORY_BASE passages "
                "disagree with no annotation flagging it -- see the coding manual's "
                "ambiguity-handling note for why that pair was not registered as a "
                "divergence case here."
            ),
        },
        {
            "case_id": "divergence.guanyu_yanliang_credit",
            "name": "Divergence: who is credited with killing 顏良",
            "evidence_ids": ["HB-J01-P2", "RM-C025-P1"],
            "classification": "contradictory",
            "rationale": (
                "HB-J01-P2 (武帝紀): credits 張遼 and 關羽 jointly ('使張遼、關羽前登，擊破，斬"
                "良'), in one plain sentence with no combat detail. RM-C025-P1 (ROMANCE): a "
                "full combat set-piece crediting 關羽 alone, with 張遼 present only as an "
                "onlooker who explicitly warns him not to make an idle boast. Same "
                "underlying event (顏良's death at the 白馬 relief), different credit "
                "attribution and dramatically different narrative weight."
            ),
        },
        {
            "case_id": "divergence.jushou_imprisonment",
            "name": "Divergence: whether 沮授 was imprisoned before the battle",
            "evidence_ids": ["HB-J06-P4", "RM-C030-P2"],
            "classification": "contradictory",
            "rationale": (
                "HB-J06-P4 (袁紹傳): 沮授 loses part of his command (reassigned to 郭圖) "
                "before the battle, but is not imprisoned -- he is only captured later, "
                "during the retreat across the river, and killed afterward for trying to "
                "return to 袁紹's side. RM-C030-P2 (ROMANCE): 袁紹 explicitly has 沮授 "
                "'鎖禁軍中' (locked in custody within the army) alongside 田豐, before the "
                "battle even starts. ROMANCE escalates a real documented event (loss of "
                "command) into a stronger, undocumented claim (imprisonment) -- a genuine "
                "contradiction, not merely a coverage gap."
            ),
        },
        {
            "case_id": "divergence.xunyu_character_assessment",
            "name": "Divergence: 荀彧's character assessment of 袁紹's staff",
            "evidence_ids": ["HB-J10-P1", "RM-C022-P1"],
            "classification": "compatible",
            "rationale": (
                "HB-J10-P1 (荀彧傳, a memorial to 曹操) and RM-C022-P1 (ROMANCE, staged as "
                "dialogue with 孔融) give essentially the same character assessment of each "
                "named advisor on 袁紹's side (田豐/許攸/審配/逢紀/顏良/文醜), down to nearly "
                "identical phrasing for several of them. ROMANCE changes the delivery "
                "context (a conversation rather than a private memorial) but not the "
                "assessment's content -- classified compatible, the strongest same-claim "
                "agreement case in this event's coded rows, unlike the mostly contradictory "
                "cases above."
            ),
        },
    ]
    for case in divergence_cases:
        metrics.append(
            {
                "metric_id": case["case_id"],
                "name": case["name"],
                "value": None,
                "unit": "categorical_classification",
                "interval_low": None,
                "interval_high": None,
                "method": (
                    f"classification={case['classification']}; evidence_ids="
                    f"{','.join(case['evidence_ids'])}; rationale: {case['rationale']}"
                ),
            }
        )

    limitations.extend(
        [
            f"N={len(rows)} evidence spans total across {len(cast)} persons and 3 source layers — far too small for any inferential statistic; all metrics here are descriptive counts or single-case qualitative classifications, not estimates with sampling uncertainty.",
            "This is a first-pass coding scoped to HISTORY_BASE juan {01,06,10,14,17} and ROMANCE 回{22,25,26,30}, out of a larger extracted candidate pool (866 paragraphs, 205 keyword-matched) covering juan {01,06,9,10,14,17} and 回{22,25,26,30,31,32} -- see research/coding_manual_guandu.md's Scope section for exactly what remains uncoded.",
            "This entire evidence set was coded by a single pass (R1-equivalent, no independent second coder yet) -- unlike 적벽대전, there is no LLM-LLM double-coding check and no human review for this event yet. Treat every coding_label assignment here as provisional until a second, independent pass is run.",
            "3 of 9 scored persons (曹操/郭嘉/關羽) are shared person_ids with the 적벽대전 cast; their coverage.* counts here reflect ONLY this event's evidence, not a combined cross-battle total.",
            "HISTORY_ANNOTATION coverage (4 of 25 rows) is proportionally thinner than 적벽대전's -- see the coding manual's Coverage note for why.",
            "coding_label frequency counts are not adjusted for each person's total narrative length or number of narrative opportunities in the source texts; they must not be read as ability or trustworthiness scores.",
        ]
    )
    warnings.extend(
        [
            "Do not compute or display a composite/weighted score or a 'strongest leader' ranking from this result -- no approved default weights exist for this event either, and N is too small regardless.",
            "coverage.* metrics with value=0 mean 'no coded evidence span in this layer for this person in this slice', not 'score of zero'.",
            "network_edge_count.* covers only rows with a real named primary_actor AND subject_of_claim; most rows are excluded from the graph, so these are not full interaction counts.",
        ]
    )

    cast_display = "/".join(cast.values())
    result = {
        "analysis_id": "A1-guandu-vertical-slice-v1",
        "run_id": None,
        "status": "partial",
        "population": {
            "n": len(rows),
            "description": (
                f"{len(rows)} coded evidence spans (research/evidence_matrix_guandu.csv) "
                f"covering {len(cast)} named persons ({cast_display}) in the 관도대전 "
                "(Battle of Guandu) vertical slice, across HISTORY_BASE, HISTORY_ANNOTATION, "
                "and ROMANCE. Cast size is derived from the CSV at run time, not fixed."
            ),
        },
        "metrics": metrics,
        "edges": edges,
        "network_summary": network_summary,
        "limitations": limitations,
        "warnings": warnings,
    }
    return result


def main() -> None:
    rows = load_rows()
    result = compute(rows)
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    result["run_id"] = run_id

    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "run_id": run_id,
        "script": "analysis/pipelines/compute_guandu_result.py",
        "script_version": SCRIPT_VERSION,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "input_files": [
            {
                "path": "research/evidence_matrix_guandu.csv",
                "sha256": sha256_file(EVIDENCE_CSV),
                "row_count": len(rows),
            }
        ],
        "output_files": [
            {
                "path": "analysis/outputs/guandu_result.json",
                "sha256": sha256_file(RESULT_JSON),
            }
        ],
        "reproduce_command": "python analysis/pipelines/compute_guandu_result.py",
        "notes": (
            "Deterministic aggregation script: re-running against an unchanged "
            "research/evidence_matrix_guandu.csv reproduces identical metrics (run_id and "
            "executed_at will differ by design)."
        ),
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {RESULT_JSON} and {MANIFEST_JSON} (run_id={run_id})")


if __name__ == "__main__":
    main()
