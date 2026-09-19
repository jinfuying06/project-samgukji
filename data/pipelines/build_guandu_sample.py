#!/usr/bin/env python3
"""Build the 관도대전 (Battle of Guandu) sample -- second event in the
per-battle expansion (handoffs/DECISIONS.md#D-036), following the exact same
non-destructive extraction method already validated for 적벽대전
(data/pipelines/build_chibi_sample.py).

Non-destructive: reads raw JSON from ${TKAF_PRIVATE_DATA_ROOT}/raw/inbox only,
never writes there. All row-level output (including any original body text or
excerpts) is written under ${TKAF_PRIVATE_DATA_ROOT}/analysis, which is outside
this Git repository and must never be committed. Only this script, the schemas
under data/schemas/, data/data_dictionary.csv are committed to the repo.

Source-layer split for HISTORY_BASE: same 〈...〉 (U+3008/U+3009) bracket
convention as build_chibi_sample.py -- see that module's docstring.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
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

# Sample scope, frozen by a keyword scan (官渡/烏巢/袁紹) over the full raw
# corpus (all 65 history_base juan, all 120 romance hui) -- see
# handoffs/DECISIONS.md#D-036 for the scan method and juan-by-juan hit counts.
# Juan selected: those with at least one *battle-specific* hit (官渡 or 烏巢),
# not merely a passing 袁紹 mention (many biographies name him without
# discussing the battle) -- narrower and more precise than "any juan that
# mentions Yuan Shao," matching Chibi's own precedent of a tight first slice.
HISTORY_JUAN = [1, 6, 9, 10, 14, 17]
# 01 武帝紀 (Cao Cao's own annals -- the campaign's primary account)
# 06 (袁紹 biography juan -- the opposing commander's own account)
# 09 (諸夏侯曹傳 family -- Cao's inner circle during the campaign)
# 10 (荀彧荀攸賈詡傳 -- Xun Yu's advice to hold the line is the campaign's most-cited strategic turning point)
# 14 (程昱郭嘉... -- Guo Jia's biography; Guo Jia is already in the 적벽대전 cast, a real cross-battle link)
# 17 (張樂于張徐傳 -- Zhang He's mid-battle defection to Cao Cao)

# Core battle arc only (mobilization -> Wuchao raid -> Yuan's collapse), not
# the wider Yuan-family succession war that follows in hui 33+ -- same
# "tight first slice" discipline as Chibi's hui 49-57 narrowing.
ROMANCE_HUI = [22, 25, 26, 30, 31, 32]
# 22 袁曹各起馬步三軍 (both sides mobilize)
# 25 屯土山關公約三事 救白馬曹操解重圍 (White Horse -- opening engagement of the campaign)
# 26 袁本初敗兵折將 關雲長掛印封金 (further prelude skirmishes)
# 30 戰官渡本初敗績 劫烏巢孟德燒糧 (the battle itself: Guandu stand + Wuchao raid -- the climax)
# 31 曹操倉亭破本初 (Cangting -- final pursuit/rout)
# 32 奪冀州袁尚爭鋒 (immediate aftermath: Yuan Shao's death, succession dispute begins)

# Canonical persons confirmed present in this sample's actual text (checked
# directly against the extracted paragraphs, not invented). Persons already
# known from 적벽대전 keep the SAME person_id so cross-battle evidence for the
# same real person can be queried together later -- a new event does not
# fork a person's identity. Aliases kept minimal/conservative: only forms
# actually observed while coding this sample, not assumed from general
# knowledge of the text.
CANONICAL_PERSONS = {
    "person.cao_cao": {  # already in 적벽대전 cast -- SAME id, reused on purpose
        "canonical_name_zh": "曹操",
        "aliases": [
            {"alias": "曹操", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "孟德", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "曹公", "type": "honorific", "observed_in": ["HISTORY_BASE"]},
        ],
    },
    "person.yuan_shao": {  # new: this battle's opposing commander
        "canonical_name_zh": "袁紹",
        "aliases": [
            {"alias": "袁紹", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
            {"alias": "本初", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
            {"alias": "袁本初", "type": "courtesy_name(字)+name", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.guo_jia": {  # already in 적벽대전 cast -- SAME id
        "canonical_name_zh": "郭嘉",
        "aliases": [
            {"alias": "郭嘉", "type": "name", "observed_in": ["HISTORY_BASE"]},
        ],
    },
    "person.xun_yu": {  # new
        "canonical_name_zh": "荀彧",
        "aliases": [
            {"alias": "荀彧", "type": "name", "observed_in": ["HISTORY_BASE"]},
        ],
    },
    "person.xu_you": {  # new: defector whose intelligence enabled the Wuchao raid
        "canonical_name_zh": "許攸",
        "aliases": [
            {"alias": "許攸", "type": "name", "observed_in": ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"]},
        ],
    },
    "person.ju_shou": {  # new: 袁紹's advisor, repeatedly correct and repeatedly ignored
        "canonical_name_zh": "沮授",
        "aliases": [
            {"alias": "沮授", "type": "name", "observed_in": ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"]},
        ],
    },
    "person.tian_feng": {  # new: 袁紹's advisor, imprisoned then executed for being right
        "canonical_name_zh": "田豐",
        "aliases": [
            {"alias": "田豐", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
        ],
    },
    "person.zhang_he": {  # new: mid-battle defector
        "canonical_name_zh": "張郃",
        "aliases": [
            {"alias": "張郃", "type": "name", "observed_in": ["HISTORY_BASE", "ROMANCE"]},
        ],
    },
    "person.liu_bei": {  # already in 적벽대전 cast -- SAME id; allied with Yuan Shao at this point
        "canonical_name_zh": "劉備",
        "aliases": [
            {"alias": "劉備", "type": "name", "observed_in": ["ROMANCE"]},
            {"alias": "玄德", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
        ],
    },
    "person.guan_yu": {  # already in 적벽대전 cast -- SAME id; White Horse episode
        "canonical_name_zh": "關羽",
        "aliases": [
            {"alias": "關羽", "type": "name", "observed_in": ["ROMANCE"]},
            {"alias": "關公", "type": "honorific", "observed_in": ["ROMANCE"]},
            {"alias": "雲長", "type": "courtesy_name(字)", "observed_in": ["ROMANCE"]},
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
                    "evidence_id": f"ev.guandu.hist.{juan:02d}.{p_idx}.base",
                    "source_layer": "HISTORY_BASE",
                    "work_id": "sanguozhi",
                    "work_title": doc.get("work_title", "三國志"),
                    "unit": "卷",
                    "num": juan,
                    "chapter_title": title,
                    "paragraph_index": p_idx,
                    "text_hash": h,
                    "text_len": len(split.base_text),
                    "crawled_at": doc.get("crawled_at"),
                })
                layer_counts["HISTORY_BASE"] += 1
            for a_idx, ann in enumerate(split.annotation_spans):
                if not ann.strip():
                    continue
                h = sha256(ann)
                rows.append({
                    "evidence_id": f"ev.guandu.hist.{juan:02d}.{p_idx}.ann.{a_idx}",
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
                "evidence_id": f"ev.guandu.rom.{hui:03d}.{p_idx}",
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

    with (OUT_TABLES / "guandu_evidence_candidates.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT_NORMALIZED / "guandu_paragraphs.jsonl").open("w", encoding="utf-8") as f:
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
                        "evidence_id": f"ev.guandu.hist.{juan:02d}.{p_idx}.base",
                        "source_layer": "HISTORY_BASE",
                        "text": split.base_text,
                    }, ensure_ascii=False) + "\n")
                for a_idx, ann in enumerate(split.annotation_spans):
                    if ann.strip():
                        f.write(json.dumps({
                            "evidence_id": f"ev.guandu.hist.{juan:02d}.{p_idx}.ann.{a_idx}",
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
                        "evidence_id": f"ev.guandu.rom.{hui:03d}.{p_idx}",
                        "source_layer": "ROMANCE",
                        "text": para,
                    }, ensure_ascii=False) + "\n")

    with (OUT_TABLES / "guandu_person_registry.json").open("w", encoding="utf-8") as f:
        json.dump(CANONICAL_PERSONS, f, ensure_ascii=False, indent=2)

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
            "event": "관도대전 (Battle of Guandu)",
            "history_juan": HISTORY_JUAN,
            "romance_hui": ROMANCE_HUI,
        },
        "input_file_hashes": input_hashes,
        "files_missing": files_missing,
        "row_counts_by_layer": layer_counts,
        "duplicate_text_hash_rows_by_layer": duplicates,
        "annotation_bracket_check": bracket_report,
    }
    with (OUT_TABLES / "guandu_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({k: v for k, v in result.items() if k != "input_file_hashes"}, ensure_ascii=False, indent=2))
