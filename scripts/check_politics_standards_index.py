#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""politics 课标索引桶新鲜度检查（CI 用，只查本学科，不碰全局索引）。

为什么要单独一个检查：`build_standards_index.py` 是全库重生成，而本仓并行会话
会让某些学科「分学科文件」与「已提交的聚合文件」暂时不一致（实测 math-bsd 聚合 562 点、
分学科文件 31 点）⇒ 全局 freshness 步永远红，且与本学科无关。
本脚本只按 politics 的 topics.json 重算它自己的桶，与 data/cn-curriculum-standards.json
里的 politics 桶逐字段比对；桶不一致才红。

用法: python3 scripts/check_politics_standards_index.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_standards_index as B  # noqa: E402  复用 std_ids / volume_of

SUB = "politics"
topics = json.load(open(os.path.join(ROOT, "data", SUB, "topics.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(ROOT, "data", "cn-curriculum-standards.json"), encoding="utf-8"))
vol_map = json.load(open(os.path.join(ROOT, "data", "mappings", "volume-map.json"), encoding="utf-8"))

by_std = defaultdict(lambda: {"topicIds": [], "grades": set(), "confidence": Counter()})
by_vol = defaultdict(lambda: {"topicCount": 0, "grades": set(), "chapters": set()})
covered = 0
for t in topics:
    ids = B.std_ids(t)
    if ids:
        covered += 1
    for sid, conf in ids:
        e = by_std[sid]
        e["topicIds"].append(t["id"])
        e["grades"].add(t.get("grade"))
        e["confidence"][conf] += 1
    v = B.volume_of(t.get("chapter"))
    b = by_vol[v]
    b["topicCount"] += 1
    b["grades"].add(t.get("grade"))
    ch = (t.get("chapter") or "").strip()
    if ch:
        b["chapters"].add(ch)

entries = [{"id": sid, "topicCount": len(e["topicIds"]),
            "topicIds": sorted(e["topicIds"]),
            "grades": sorted(g for g in e["grades"] if g is not None),
            "confidence": dict(e["confidence"])}
           for sid, e in sorted(by_std.items())]
want = {"entryCount": len(entries), "topicsWithStandard": covered,
        "topicsTotal": len(topics), "entries": entries}
want_vol = {v: {"topicCount": b["topicCount"],
                "grades": sorted(g for g in b["grades"] if g is not None),
                "chapterCount": len(b["chapters"])} for v, b in sorted(by_vol.items())}

got = idx.get("subjects", {}).get(SUB)
got_vol = vol_map.get("subjects", {}).get(SUB)
fails = []
if got != want:
    fails.append("cn-curriculum-standards.json 的 politics 桶已过期"
                 "（索引 entryCount=%s / 现算=%s，topicsTotal=%s / %s）"
                 % ((got or {}).get("entryCount"), want["entryCount"],
                    (got or {}).get("topicsTotal"), want["topicsTotal"]))
if got_vol != want_vol:
    fails.append("volume-map.json 的 politics 册次桶已过期（索引 %d 册 / 现算 %d 册）"
                 % (len(got_vol or {}), len(want_vol)))

print("politics 索引桶：条目 %d / 覆盖 %d/%d 知识点 / 册次 %d"
      % (want["entryCount"], covered, len(topics), len(want_vol)))
if fails:
    for f in fails:
        print("  ❌ " + f)
    sys.exit(1)
print("  ✅ 与 data/politics/topics.json 一致")
