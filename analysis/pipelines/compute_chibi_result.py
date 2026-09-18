#!/usr/bin/env python3
"""Reproducible A1 aggregation for the 적벽대전 (Battle of Red Cliffs) vertical slice.

Input: research/evidence_matrix.csv (committed, short-excerpt evidence rows only).
Output: analysis/outputs/result.json (conforms to analysis/schemas/result.schema.json)
        analysis/outputs/run_manifest.json (input hash, script version, timestamp).

This script only counts and classifies rows that already exist in evidence_matrix.csv.
It does not read raw corpus text and does not invent any value. Every number here must
be reproducible by re-running this script against the same evidence_matrix.csv.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_VERSION = "1.1.0"
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_CSV = ROOT / "research" / "evidence_matrix.csv"
RESULT_JSON = ROOT / "analysis" / "outputs" / "result.json"
MANIFEST_JSON = ROOT / "analysis" / "outputs" / "run_manifest.json"

# Display-name fallback for known PERSON-* IDs. This is NOT the cast list — the cast is
# derived dynamically below from whatever PERSON-* refs actually appear in
# evidence_matrix.csv, so adding a new person to the CSV (D-016 expansion or any future
# one) requires no code change here. This dict only supplies a readable Chinese name for
# metric labels; an ID missing from it still gets scored, just displayed by its raw ID.
KNOWN_DISPLAY_NAMES = {
    "PERSON-CAOCAO": "曹操",
    "PERSON-LIUBEI": "劉備",
    "PERSON-ZHUGELIANG": "諸葛亮",
    "PERSON-SUNQUAN": "孫權",
    "PERSON-ZHOUYU": "周瑜",
    "PERSON-HUANGGAI": "黃蓋",
    "PERSON-GUANYU": "關羽",
    "PERSON-LUSU": "魯肅",
    "PERSON-ZHAOYUN": "趙雲",
    "PERSON-GUOJIA": "郭嘉",
}
LAYERS = ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"]

# Canonical person_id per PERSON-* token, matching data/pipelines/build_curated_export.py's
# PERSON_TOKEN_TO_ID exactly (same 10 persons, same "person.xxx" convention) so this
# script's edges use the same node identity as the curated export / backend API.
# Duplicated rather than imported to avoid a cross-directory import between
# analysis/pipelines and data/pipelines for one small dict; keep the two in sync by hand
# if a future expansion pass adds a person to both.
PERSON_TOKEN_TO_CANONICAL_ID = {
    "PERSON-CAOCAO": "person.cao_cao",
    "PERSON-SUNQUAN": "person.sun_quan",
    "PERSON-LIUBEI": "person.liu_bei",
    "PERSON-ZHOUYU": "person.zhou_yu",
    "PERSON-ZHUGELIANG": "person.zhuge_liang",
    "PERSON-HUANGGAI": "person.huang_gai",
    "PERSON-GUANYU": "person.guan_yu",
    "PERSON-LUSU": "person.lu_su",
    "PERSON-ZHAOYUN": "person.zhao_yun",
    "PERSON-GUOJIA": "person.guo_jia",
}
# primary_actor/subject_of_claim in evidence_matrix.csv are free-text Chinese names
# (e.g. "曹操"), not PERSON-* tokens -- build the name -> canonical_id map from the two
# dicts above rather than hand-duplicating a third mapping.
NAME_ZH_TO_CANONICAL_ID = {
    name_zh: PERSON_TOKEN_TO_CANONICAL_ID[token]
    for token, name_zh in KNOWN_DISPLAY_NAMES.items()
}

# Meta actors that must never be treated as a network node or a scored cast member
# (commentators / cited works, not people who acted in the event).
META_ACTOR_MARKERS = ("(commentator)", "(source)")


def discover_cast(rows: list[dict]) -> dict[str, str]:
    """Every distinct real PERSON-* ref found in evidence_matrix.csv is scored — no
    hardcoded cast size or list. A person with only 1 evidence span is still scored
    (coverage=1), never excluded for having 'too little' data (agents/_three_kingdoms_domain.md:
    missing evidence is recorded as missing, not scored as 0, and a person is never
    dropped from scoring just because their coverage is thin)."""
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

    # --- 1. historical_narrative_weight: evidence-span coverage count per person x layer ---
    # Counts every row whose person_refs includes the cast member, regardless of
    # primary_actor/subject_of_claim role. This is a COVERAGE count, not a capability
    # score: a 0 here means "no coded span in this layer for this person in this slice",
    # never "this person scored zero on some trait." Cast is discovered dynamically
    # (see discover_cast) so this loop scores every person actually present in the CSV,
    # however many there are.
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
                        "Count of research/evidence_matrix.csv rows whose person_refs "
                        f"includes {pid} and source_layer == {layer}. Coverage/emphasis "
                        "fact only, per research/analysis_criteria.md 'historical_narrative_weight' "
                        "— not a capability or ability score, and not comparable across persons "
                        "as a ranking."
                    ),
                }
            )

    # --- 2. coding_label frequency (descriptive, exploratory) ---
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
                    "Count of research/evidence_matrix.csv rows with this coding_label. "
                    "Exploratory descriptive count only (N=22 total); not adjusted for "
                    "text length or narrative opportunity, per agents/_three_kingdoms_domain.md "
                    "'언급 빈도만으로 능력치를 만들지 않는다' — this is a label tally, not a trait score."
                ),
            }
        )

    # --- 3. Network edges: primary_actor -> subject_of_claim, real persons only ---
    # Kept as a real, structured edge list in the result (not just counts) -- see
    # analysis/network_analysis_plan.md's "적벽대전 vertical-slice application" section,
    # which previously flagged this as an open follow-up (edges were computed but
    # discarded, only network_edge_count.* survived). source/target are canonical
    # person_id (NAME_ZH_TO_CANONICAL_ID), matching the curated export/backend API's node
    # identity; *_name_zh kept alongside for human readability without a second lookup.
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
                    "Count of evidence_matrix.csv rows with both a real (non-commentator, "
                    "non-cited-source) primary_actor and subject_of_claim, grouped by "
                    "source_layer, per analysis/network_analysis_plan.md#적벽대전-slice-application "
                    "('create separate graphs by source layer before comparison')."
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

    # --- 3b. Descriptive network stats (no centrality -- N too small, per
    # analysis/network_analysis_plan.md's explicit decision and agents/_three_kingdoms_domain.md's
    # "centrality를 능력 또는 인기의 직접 척도로 이름 붙이지 않는다"). Only counts/density/overlap,
    # each with a caution in its own method field so a UI can't silently drop the caveat.
    #
    # Kept OUT of `metrics[]` deliberately: app/backend/api/db.py's GET
    # /v1/events/{id}/metrics query already filters to metric_id prefixes
    # {coverage, label_frequency, divergence} (excluding network_edge_count.* on purpose,
    # per its own comment -- network detail belongs with /relationships). Adding new
    # network_* prefixes to `metrics[]` would silently leak past that filter and break
    # tests/backend/test_api.py::test_metrics_default_kinds_only. A separate top-level
    # `network_summary` field avoids touching that contract (backend code is outside this
    # task's write scope) and is arguably the more correct home for this data anyway.
    network_summary_by_layer: dict[str, dict] = {}
    for layer in LAYERS:
        layer_edges = edges_by_layer[layer]
        nodes = {e["source"] for e in layer_edges} | {e["target"] for e in layer_edges}
        max_pairs = len(nodes) * (len(nodes) - 1)  # directed, no self-loops
        density = (len(layer_edges) / max_pairs) if max_pairs > 0 else None
        network_summary_by_layer[layer] = {
            "unique_node_count": len(nodes),
            "edge_count": len(layer_edges),
            "density": density,
            "density_caution": (
                f"edges / (nodes * (nodes-1)) for the {layer} graph only "
                f"(nodes={len(nodes)}, edges={len(layer_edges)}). At this N, density reflects "
                "which of the 30 evidence rows happened to name both an actor and a subject, "
                "not real social closeness or narrative centrality -- do not present as a "
                "sociability or importance score (agents/_three_kingdoms_domain.md). null when "
                "fewer than 2 nodes."
            ),
            "unique_node_count_note": (
                f"Distinct canonical person_ids appearing as source or target of a {layer} "
                f"edge -- smaller than the full {len(cast)}-person cast in most layers, since "
                "most evidence rows have no subject_of_claim (see network_edge_count.* "
                "warning). A person absent here may still have real coverage.* evidence in "
                "this layer, just not in actor-subject form."
            ),
        }

    # Cross-layer node-pair overlap: does the same (unordered) person pair appear as an
    # edge in more than one layer, and with what relation in each? This is a real,
    # interesting comparison point (does 정사/주석/연의 agree on WHO interacts, even if the
    # story of HOW differs) without needing any centrality computation.
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
            "relation labels are a real comparison point (do source layers agree on who "
            "interacts, even if the story of how differs); this is not a centrality or "
            "importance measure. An empty list means no pair currently shares an edge across "
            "layers in this slice -- itself informative, not an error."
        ),
    }

    # --- 4. Pre-registered source-layer divergence classifications ---
    # These 3 pairs were pre-registered in analysis/analysis_plan.md before this script
    # was run, based on which evidence rows describe the SAME person's claim/behavior at a
    # comparable moment across two layers. Cases where one layer is simply silent (no
    # coded claim at all) are NOT forced into this classification — see the
    # 'historical_narrative_weight' coverage metrics above instead.
    divergence_cases = [
        {
            "case_id": "divergence.caocao_selfreflection",
            "name": "Divergence: Cao Cao's self-reflection after the Red Cliffs defeat",
            "evidence_ids": ["HB-J54-P2", "RM-C050-P3"],
            "classification": "contradictory",
            "rationale": (
                "HB-J54-P2 (HISTORY_BASE): Cao Cao's own letter denies fault, attributes "
                "retreat to disease, and denies Zhou Yu deserved credit. RM-C050-P3 (ROMANCE): "
                "Cao Cao explicitly admits the defeat was his own strategic failure and blames "
                "Guo Jia's death for the lack of a check on his judgment. Same person, same "
                "general aftermath, opposite self-presentation."
            ),
        },
        {
            "case_id": "divergence.liubei_role_reliability",
            "name": "Divergence: reliability of Liu Bei's decisive-role account",
            "evidence_ids": ["HB-J32-P1", "HA-J32-P1"],
            "classification": "complementary",
            "rationale": (
                "HB-J32-P1 (HISTORY_BASE main biography) states Liu Bei's forces jointly "
                "broke Cao Cao's army and pursued to Nanjun, without qualification. "
                "HA-J32-P1 (HISTORY_ANNOTATION, 孫盛) does not deny this claim outright but "
                "flags the broader 江表傳 tradition behind such accounts as likely "
                "Wu-partisan self-flattery. This adds a reliability caveat rather than "
                "asserting the opposite fact, so it is classified complementary, not "
                "contradictory."
            ),
        },
        {
            "case_id": "divergence.fireattack_originator",
            "name": "Divergence: who is credited with originating the fire-attack idea",
            "evidence_ids": ["HB-J54-P1", "RM-C049-P2"],
            "classification": "contradictory",
            "rationale": (
                "Within this slice's coded rows only: HB-J54-P1 (HISTORY_BASE) credits the "
                "fire-attack idea to Huang Gai (subordinate), with Zhou Yu authorizing it. "
                "RM-C049-P2 (ROMANCE) instead shows Zhuge Liang independently advising Zhou "
                "Yu that a fire attack is needed. These are different originator "
                "attributions for the same tactical idea. Caveat: Romance's fuller "
                "narrative (回44-46, outside this slice's coded rows) also separately "
                "features Huang Gai's proposal; this classification is scoped strictly to "
                "the two coded rows compared, not the full novel."
            ),
        },
        # --- Added post-D-016 expansion (D-025 follow-up), covering the 5 newly-scored persons ---
        {
            "case_id": "divergence.lusu_origination_credit",
            "name": "Divergence: who first originated the plan to resist Cao Cao",
            "evidence_ids": ["HB-J47-P1", "HA-J54-P4"],
            "classification": "contradictory",
            "rationale": (
                "HB-J47-P1 (HISTORY_BASE, 孫權 biography, 卷47): '惟瑜、肅執拒之儀，意與權同' "
                "-- credits Zhou Yu and Lu Su jointly for holding the resistance position, "
                "without stating who proposed it first. HA-J54-P4 (HISTORY_ANNOTATION, 裴松之 "
                "commenting on 周瑜's own biography, 卷54): '臣松之以為建計拒曹公，實始魯肅……"
                "本傳直云，權延見群下，問以計策，瑜擺撥眾人之議，獨言抗拒之計，了不云肅先有謀' "
                "-- Pei Songzhi states the plan to resist actually originated with Lu Su first, "
                "and explicitly flags that Zhou Yu's own main-biography account omits Lu Su's "
                "origination role entirely, crediting Zhou Yu alone as having spoken the "
                "resistance plan. This is a direct dispute over origination credit between the "
                "base historical narrative (as the annotator characterizes it) and the "
                "annotator's own corrective claim -- reinforced by a second annotation row "
                "(HA-J54-P5, not counted in this pair) citing 吳書/江表傳 for the same claim. "
                "Not merely a coverage gap: HA-J54-P4 explicitly names and disputes the base "
                "account's specific claim, which is what makes this contradictory rather than "
                "complementary."
            ),
        },
        {
            "case_id": "divergence.huanggai_feigned_surrender",
            "name": "Divergence: the feigned-surrender deception against Cao Cao",
            "evidence_ids": ["HA-J54-P1", "RM-C049-P6"],
            "classification": "complementary",
            "rationale": (
                "HA-J54-P1 (HISTORY_ANNOTATION, 江表傳, Huang Gai's actual surrender letter): "
                "'蓋受孫氏厚恩，常為將帥，見遇不薄……今日歸命，是其實計' -- a written deception, "
                "no violence or public spectacle described. RM-C049-P6 (ROMANCE): '汝是何等人，"
                "敢來詐降！吾今缺少福物祭旗，願借你首級' -- Zhou Yu stages a mock execution of a "
                "spy (蔡和) to make the deception credible to Cao Cao's side. Both layers agree "
                "on the same underlying tactic (a feigned surrender to enable the fire attack) "
                "and the same actors (黃蓋's letter, 周瑜's orchestration); ROMANCE adds a "
                "dramatized, violent theatrical element with no counterpart or denial in the "
                "HISTORY_ANNOTATION account -- an elaboration, not a stated contradiction, so "
                "classified complementary rather than contradictory. Pre-flagged as a direct "
                "comparison candidate by both rows' own ambiguity notes before this case was "
                "added."
            ),
        },
        # --- Added in expansion pass 2 (data-analysis broadening, 2026-09-18) ---
        {
            "case_id": "divergence.huanggai_wound",
            "name": "Divergence: how Huang Gai was wounded during the fire attack",
            "evidence_ids": ["HA-J55-P1", "RM-C049-P8"],
            "classification": "complementary",
            "rationale": (
                "HA-J55-P1 (HISTORY_ANNOTATION, 吳書, quoted in 黃蓋's own biography): '蓋爲流矢"
                "所中，時寒墮水，爲吳軍人所得，不知其蓋也……蓋自彊以一聲呼韓當' -- Huang Gai is hit "
                "by a stray arrow amid the chaos, falls into cold water, and is nearly left for "
                "dead until he identifies himself by voice to a fellow officer (韓當) who "
                "recognizes him. RM-C049-P8 (ROMANCE): '黃蓋在火光中，高聲大叫……正中肩窩，翻身落"
                "水' -- Huang Gai is shot in the shoulder specifically while charging his fire "
                "ship into Cao Cao's fleet, shouting his own name. Both layers agree Huang Gai "
                "was wounded by an arrow and fell into the water during the attack -- the "
                "underlying event is the same. ROMANCE stages it as a heroic, self-announced "
                "charge; HISTORY_ANNOTATION describes an anonymous, near-fatal accident only "
                "resolved by chance recognition. Classified complementary (same core event, "
                "different emphasis/detail) rather than contradictory, since neither account "
                "denies the other's specific claims."
            ),
        },
        {
            "case_id": "divergence.zhouyu_lusu_succession",
            "name": "Divergence: Zhou Yu's deathbed recommendation of Lu Su as successor",
            "evidence_ids": ["HA-J54-P6", "RM-C057-P3"],
            "classification": "compatible",
            "rationale": (
                "HA-J54-P6 (HISTORY_ANNOTATION, 江表傳, Zhou Yu's own letter to Sun Quan while "
                "dying): '魯肅忠烈，臨事不苟，可以代瑜' -- explicitly recommends Lu Su as his "
                "successor. RM-C057-P3 (ROMANCE, Sun Quan reading Zhou Yu's deathbed letter): "
                "'既遺書特薦子敬，孤敢不從之？' -- Sun Quan confirms the letter recommends Lu Su "
                "(子敬), and follows it. Both layers agree on the same specific claim (Zhou Yu "
                "personally named Lu Su as his successor in a deathbed letter to Sun Quan) with "
                "no meaningful conflict in detail -- classified compatible, the strongest "
                "same-claim agreement case in this slice, unlike the mostly complementary or "
                "contradictory cases elsewhere."
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
            "Only HISTORY_BASE juan {01,32,35,47,54,55} and ROMANCE 回49,50,51,52,53,54,56,57 have been coded so far (research/analysis_criteria.md §Coverage); juan {10,31,48,56} (reviewed, judged not relevant to the 10-person cast) and 回55,58-61 remain uncoded, so any claim about 'the full battle' is out of scope for this result.",
            "This entire evidence set was coded by AI agents only (initial 22 rows by R1, +8 rows by the D-016 expansion pass, +18 rows by expansion pass 2), with an LLM-LLM double-coding check on the original 22 rows (Cohen's kappa=0.90, research/intercoder_reliability.md). The original 30 rows (through D-016) were subsequently reviewed and confirmed by the human project owner (D-024, coding_validation_status=human_validated in the curated export) -- but the 18 rows added in expansion pass 2 (2026-09-18) have NOT yet been human-reviewed. Do not treat expansion-pass-2 coding_label assignments as human-validated ground truth until a review pass covers them too.",
            "The 5 persons added in the D-016 expansion pass (Huang Gai, Guan Yu, Lu Su, Zhao Yun, Guo Jia) generally have thinner coverage per layer than the original 5 — thin coverage for a newly scored person reflects sampling choices made so far, not necessarily their true narrative weight in the full corpus.",
            "HISTORY_ANNOTATION boundaries were identified via a `〈...〉` bracket heuristic; data/quality_report.json flags one juan (56, not used as a source for any row in this evidence set) with an unbalanced bracket count (QC-D1-1).",
            "coding_label frequency counts are not adjusted for each person's total narrative length or number of narrative opportunities in the source texts; they must not be read as ability or trustworthiness scores (agents/_three_kingdoms_domain.md).",
        ]
    )
    warnings.extend(
        [
            "Do not compute or display a composite/weighted score or a 'strongest leader' ranking from this result — analysis/scoring_model.md explicitly requires research/evaluator-approved default weights, which do not exist yet, and N=22 is too small to support one regardless.",
            "coverage.* metrics with value=0 mean 'no coded evidence span in this layer for this person in this slice', not 'score of zero' — do not let downstream UI (ScoreCard) render a 0-count as a 0 ability score.",
            "network_edge_count.* covers only rows with a real named primary_actor AND subject_of_claim; rows with an empty subject_of_claim (most rows) are excluded from the graph, so these are not full interaction counts for each person.",
        ]
    )

    cast_display = "/".join(cast.values())
    result = {
        "analysis_id": "A1-chibi-vertical-slice-v1",
        "run_id": None,  # filled in by main() with a timestamp-based id
        "status": "partial",  # partial: only a fraction of the approved sample scope is coded so far (see limitations)
        "population": {
            "n": len(rows),
            "description": (
                f"{len(rows)} coded evidence spans (research/evidence_matrix.csv) covering "
                f"{len(cast)} named persons ({cast_display}) in the 적벽대전 (Battle of Red "
                "Cliffs) vertical slice, across HISTORY_BASE, HISTORY_ANNOTATION, and ROMANCE. "
                "Cast size is derived from the CSV at run time (see discover_cast), not fixed."
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
        "script": "analysis/pipelines/compute_chibi_result.py",
        "script_version": SCRIPT_VERSION,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "input_files": [
            {
                "path": "research/evidence_matrix.csv",
                "sha256": sha256_file(EVIDENCE_CSV),
                "row_count": len(rows),
            }
        ],
        "output_files": [
            {
                "path": "analysis/outputs/result.json",
                "sha256": sha256_file(RESULT_JSON),
            }
        ],
        "reproduce_command": "python analysis/pipelines/compute_chibi_result.py",
        "notes": (
            "Deterministic aggregation script: re-running against an unchanged "
            "research/evidence_matrix.csv reproduces identical metrics (run_id and "
            "executed_at will differ by design)."
        ),
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {RESULT_JSON} and {MANIFEST_JSON} (run_id={run_id})")


if __name__ == "__main__":
    main()
