#!/usr/bin/env python3
"""Build the S1 적벽대전 (Battle of Red Cliffs) sample.

Non-destructive: reads raw JSON from ${TKAF_PRIVATE_DATA_ROOT}/raw/inbox only,
never writes there. All row-level output (including any original body text or
excerpts) is written under ${TKAF_PRIVATE_DATA_ROOT}/analysis, which is outside
this Git repository and must never be committed. Only this script, the schemas
under data/schemas/, data/data_dictionary.csv, and data/quality_report.json are
committed to the repo.

Source-layer split for HISTORY_BASE:
  Chinese Wikisource marks Pei Songzhi (裴松之) commentary inline inside the
  base text of each 三國志 juan using angle brackets U+3008/U+3009 (〈 〉).
  Everything inside a top-level 〈...〉 span is HISTORY_ANNOTATION; everything
  outside is HISTORY_BASE. This was verified empirically (see
  data/quality_report.json "annotation_bracket_check") to be balanced and
  non-nested for 9 of the 10 sample juan; juan 56 has one unmatched opening
  bracket and is flagged rather than silently repaired.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

OPEN, CLOSE = "〈", "〉"  # 〈 〉

REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_ROOT = Path(os.environ.get("TKAF_PRIVATE_DATA_ROOT", "../tkaf-private-data"))
if not PRIVATE_ROOT.is_absolute():
    PRIVATE_ROOT = (REPO_ROOT / PRIVATE_ROOT).resolve()

RAW_HIST_DIR = PRIVATE_ROOT / "raw" / "inbox" / "history_base_zh"
RAW_ROM_DIR = PRIVATE_ROOT / "raw" / "inbox" / "romance_zh"

OUT_NORMALIZED = PRIVATE_ROOT / "analysis" / "normalized"
OUT_TABLES = PRIVATE_ROOT / "analysis" / "tables"

PIPELINE_VERSION = "1.0.0"

# Sample scope frozen in handoffs/CURRENT_TASK.md.
# Romance narrowed from the D0-proposed 49-61 to 49-57: chapters 58-61 pivot to
# the unrelated Ma Chao/Han Sui campaign and had 0-1 Chibi keyword hits each
# (see orchestrator's keyword scan); this is a minor, reversible D1 scoping
# decision, logged in the completion report, not a silent change.
HISTORY_JUAN = [1, 10, 31, 32, 35, 47, 48, 54, 55, 56]
ROMANCE_HUI = list(range(49, 58))  # 49..57 inclusive

# Canonical persons confirmed present in this sample's actual text (listed_persons
# fields and/or chapter titles/body text), not invented. Alias lists are only the
# forms actually observed; do not add unobserved honorifics.
CANONICAL_PERSONS = {
    "person.cao_cao": {
        "canonical_name_zh": "曹操",
        "aliases": [
            {"alias": "曹操", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "孟德", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "曹阿瞞", "type": "nickname", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.sun_quan": {
        "canonical_name_zh": "孫權",
        "aliases": [
            {"alias": "孫權", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "孫仲謀", "type": "courtesy_name(字)+name", "observed_in": ["ROMANCE"]},
            {"alias": "仲謀", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.liu_bei": {
        "canonical_name_zh": "劉備",
        "aliases": [
            {"alias": "劉備", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "玄德", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "劉皇叔", "type": "honorific", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.zhou_yu": {
        "canonical_name_zh": "周瑜",
        "aliases": [
            {"alias": "周瑜", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "公瑾", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "周郎", "type": "nickname", "observed_in": ["ROMANCE"]},
            {"alias": "周公瑾", "type": "courtesy_name(字)+name", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.zhuge_liang": {
        "canonical_name_zh": "諸葛亮",
        "aliases": [
            {"alias": "諸葛亮", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "孔明", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "臥龍", "type": "nickname", "observed_in": ["ROMANCE"]},
        ],
    },
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class BracketSplit:
    base_text: str
    annotation_spans: list[str]
    open_count: int
    close_count: int
    balanced: bool
    end_depth: int


def split_annotation(body: str) -> BracketSplit:
    """Split one paragraph into (base_text_outside_brackets, [annotation_runs])."""
    base_parts: list[str] = []
    ann_parts: list[str] = []
    depth = 0
    open_count = 0
    close_count = 0
    buf: list[str] = []

    def flush():
        text = "".join(buf)
        buf.clear()
        if not text:
            return
        if depth > 0:
            ann_parts.append(text)
        else:
            base_parts.append(text)

    for ch in body:
        if ch == OPEN:
            flush()
            depth += 1
            open_count += 1
            continue
        if ch == CLOSE:
            flush()
            depth = max(0, depth - 1)
            close_count += 1
            continue
        buf.append(ch)
    flush()

    return BracketSplit(
        base_text="".join(base_parts),
        annotation_spans=ann_parts,
        open_count=open_count,
        close_count=close_count,
        balanced=(open_count == close_count),
        end_depth=depth,
    )


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def paragraphs(body_text: str) -> list[str]:
    return [p for p in (seg.strip() for seg in body_text.split("\n")) if p]


def build() -> dict:
    OUT_NORMALIZED.mkdir(parents=True, exist_ok=True)
    OUT_TABLES.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    bracket_report: list[dict] = []
    input_hashes: dict[str, str] = {}
    layer_counts = {"HISTORY_BASE": 0, "HISTORY_ANNOTATION": 0, "ROMANCE": 0}
    files_missing = []

    for juan in HISTORY_JUAN:
        path = RAW_HIST_DIR / f"{juan:02d}.json"
        if not path.exists():
            files_missing.append(str(path))
            continue
        raw_bytes = path.read_bytes()
        input_hashes[f"history_base_zh/{juan:02d}.json"] = hashlib.sha256(raw_bytes).hexdigest()
        doc = json.loads(raw_bytes.decode("utf-8"))
        body = doc.get("body_text", "")
        title = doc.get("title", "")

        file_open = file_close = 0
        for p_idx, para in enumerate(paragraphs(body)):
            split = split_annotation(para)
            file_open += split.open_count
            file_close += split.close_count
            if split.base_text:
                h = sha256(split.base_text)
                rows.append({
                    "evidence_id": f"ev.hist.{juan:02d}.{p_idx}.base",
                    "source_layer": "HISTORY_BASE",
                    "work_id": "sanguozhi",
                    "work_title": doc.get("work_title", "三國志"),
                    "unit": "卷",
                    "num": juan,
                    "chapter_title": title,
                    "paragraph_index": p_idx,
                    "text_hash": h,
                    "text_len": len(split.base_text),
                    "source_url_domain": (doc.get("source") or doc.get("url") or "").split("/")[2]
                        if "://" in (doc.get("source") or doc.get("url") or "") else None,
                    "crawled_at": doc.get("crawled_at"),
                })
                layer_counts["HISTORY_BASE"] += 1
            for a_idx, ann in enumerate(split.annotation_spans):
                if not ann.strip():
                    continue
                h = sha256(ann)
                rows.append({
                    "evidence_id": f"ev.hist.{juan:02d}.{p_idx}.ann.{a_idx}",
                    "source_layer": "HISTORY_ANNOTATION",
                    "work_id": "sanguozhi",
                    "work_title": doc.get("work_title", "三國志"),
                    "unit": "卷",
                    "num": juan,
                    "chapter_title": title,
                    "paragraph_index": p_idx,
                    "annotation_index": a_idx,
                    "text_hash": h,
                    "text_len": len(ann),
                    "crawled_at": doc.get("crawled_at"),
                })
                layer_counts["HISTORY_ANNOTATION"] += 1

        bracket_report.append({
            "juan": juan,
            "open": file_open,
            "close": file_close,
            "balanced": file_open == file_close,
        })

    for hui in ROMANCE_HUI:
        path = RAW_ROM_DIR / f"{hui:03d}.json"
        if not path.exists():
            files_missing.append(str(path))
            continue
        raw_bytes = path.read_bytes()
        input_hashes[f"romance_zh/{hui:03d}.json"] = hashlib.sha256(raw_bytes).hexdigest()
        doc = json.loads(raw_bytes.decode("utf-8"))
        body = doc.get("body_text", "")
        chapter_title = doc.get("chapter_title", "")

        for p_idx, para in enumerate(paragraphs(body)):
            if not para.strip():
                continue
            h = sha256(para)
            rows.append({
                "evidence_id": f"ev.rom.{hui:03d}.{p_idx}",
                "source_layer": "ROMANCE",
                "work_id": "sanguoyanyi",
                "work_title": doc.get("work_title", "三國演義"),
                "unit": "回",
                "num": hui,
                "chapter_title": chapter_title,
                "paragraph_index": p_idx,
                "text_hash": h,
                "text_len": len(para),
                "crawled_at": doc.get("crawled_at"),
            })
            layer_counts["ROMANCE"] += 1

    # Write private, non-committed row-level table (metadata only here; full text
    # written separately to normalized/ so tables/ stays small and inspectable).
    with (OUT_TABLES / "chibi_evidence_candidates.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Write the actual paragraph text (base/annotation/romance) separately, private-only.
    with (OUT_NORMALIZED / "chibi_paragraphs.jsonl").open("w", encoding="utf-8") as f:
        for juan in HISTORY_JUAN:
            path = RAW_HIST_DIR / f"{juan:02d}.json"
            if not path.exists():
                continue
            doc = load_json(path)
            body = doc.get("body_text", "")
            for p_idx, para in enumerate(paragraphs(body)):
                split = split_annotation(para)
                if split.base_text:
                    f.write(json.dumps({
                        "evidence_id": f"ev.hist.{juan:02d}.{p_idx}.base",
                        "source_layer": "HISTORY_BASE",
                        "text": split.base_text,
                    }, ensure_ascii=False) + "\n")
                for a_idx, ann in enumerate(split.annotation_spans):
                    if ann.strip():
                        f.write(json.dumps({
                            "evidence_id": f"ev.hist.{juan:02d}.{p_idx}.ann.{a_idx}",
                            "source_layer": "HISTORY_ANNOTATION",
                            "text": ann,
                        }, ensure_ascii=False) + "\n")
        for hui in ROMANCE_HUI:
            path = RAW_ROM_DIR / f"{hui:03d}.json"
            if not path.exists():
                continue
            doc = load_json(path)
            body = doc.get("body_text", "")
            for p_idx, para in enumerate(paragraphs(body)):
                if para.strip():
                    f.write(json.dumps({
                        "evidence_id": f"ev.rom.{hui:03d}.{p_idx}",
                        "source_layer": "ROMANCE",
                        "text": para,
                    }, ensure_ascii=False) + "\n")

    with (OUT_TABLES / "person_registry.json").open("w", encoding="utf-8") as f:
        json.dump(CANONICAL_PERSONS, f, ensure_ascii=False, indent=2)

    # Duplicate-hash check within each layer.
    hash_by_layer: dict[str, dict[str, int]] = {"HISTORY_BASE": {}, "HISTORY_ANNOTATION": {}, "ROMANCE": {}}
    for row in rows:
        d = hash_by_layer[row["source_layer"]]
        d[row["text_hash"]] = d.get(row["text_hash"], 0) + 1
    duplicates = {
        layer: sum(1 for c in counts.values() if c > 1)
        for layer, counts in hash_by_layer.items()
    }

    manifest = {
        "pipeline_version": PIPELINE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_scope": {
            "event": "적벽대전 (Battle of Red Cliffs)",
            "history_juan": HISTORY_JUAN,
            "romance_hui": ROMANCE_HUI,
            "romance_hui_narrowed_from": list(range(49, 62)),
            "narrowing_reason": "hui 58-61 pivot to the Ma Chao/Han Sui campaign; 0-1 Chibi keyword hits each in the D0 keyword scan",
        },
        "input_file_hashes": input_hashes,
        "files_missing": files_missing,
        "row_counts_by_layer": layer_counts,
        "duplicate_text_hash_rows_by_layer": duplicates,
        "annotation_bracket_check": bracket_report,
    }
    with (OUT_TABLES / "run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({k: v for k, v in result.items() if k != "input_file_hashes"}, ensure_ascii=False, indent=2))
