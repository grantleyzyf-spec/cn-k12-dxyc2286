#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 politics 补挂「义教课标里原先无点引用」的条目（人工定标表见 extra_citations.json）。

幂等：已挂过的条目跳过。只往 topics[].standards 追加，不改 id/题/边。
用法: python3 scripts/ddfz_extra_citations.py [--write]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import ddfz_standards as S  # noqa: E402

SUB = os.path.join(ROOT, "data", "politics")
MAP = os.path.join(SUB, "_standards_src", "extra_citations.json")


def quote_for(entry, limit=90):
    """补挂引文取整条原文（≤60 字），超长时取首句／首个 60 字内在标点处收口。"""
    text = entry["quote"]
    if len(text) <= limit:
        return text
    head = re.split(r"(?<=[。；])", text)[0]
    if 12 <= len(head) <= 90:
        return head
    cut = text[:limit]
    i = max(cut.rfind("，"), cut.rfind("；"), cut.rfind("。"))
    return cut[:i] if i >= 12 else cut


def main():
    write = "--write" in sys.argv
    cfg = json.load(open(MAP, encoding="utf-8"))
    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    entries = json.load(open(S.ENTRIES, encoding="utf-8"))
    by_id = {e["id"]: e for e in entries}
    T = {t["id"]: t for t in topics}
    scorer = S.Scorer(entries)

    added, skipped, bad = [], [], []
    for eid, (pid, conf) in cfg["map"].items():
        if eid not in by_id:
            bad.append(("条目不存在", eid))
            continue
        if pid not in T:
            bad.append(("点不存在", pid))
            continue
        t = T[pid]
        e = by_id[eid]
        rec = {"id": eid, "confidence": conf, "quote": quote_for(e),
               "sourceLine": e["line"]}
        exist = next((x for x in t["standards"] if x["id"] == eid), None)
        if exist:
            if exist != rec:
                exist.update(rec)
            skipped.append(eid)
            continue
        t["standards"].append(rec)
        added.append((eid, pid, t["name"]))

    used = {s["id"] for t in topics for s in t["standards"]}
    ec = [e for e in entries if e["id"].startswith("ddf")]
    print("本次补挂 %d 条（已存在跳过 %d）" % (len(added), len(skipped)))
    for a in added:
        print("   %-20s → %-9s %s" % a)
    if bad:
        print("!! 异常:", bad)
    print("义教条目覆盖：%d/%d；全科唯一条目 %d/%d"
          % (sum(1 for e in ec if e["id"] in used), len(ec), len(used), len(entries)))
    print("未覆盖：", [e["id"] for e in ec if e["id"] not in used])
    print("引文总条数：", sum(len(t["standards"]) for t in topics))
    if write:
        json.dump(topics, open(os.path.join(SUB, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写回 data/politics/topics.json")
    else:
        print("（dry-run，加 --write 落盘）")


if __name__ == "__main__":
    main()
