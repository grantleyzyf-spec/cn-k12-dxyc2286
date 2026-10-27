#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只重建 data/ 汇总三件套（topics/questions/dependencies），⛔ 不改各学科分片文件。

用途：某学科分片被就地修正后，汇总文件会过期（build_stats / validate --all 读汇总）。
与 normalize_to_ref_schema.py --write 的区别：本脚本不写回各学科分片，避免卷进并行会话的改动。
用法：python3 scripts/rebuild_aggregates_only.py
"""
import importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

spec = importlib.util.spec_from_file_location("nz", os.path.join(ROOT, "scripts", "normalize_to_ref_schema.py"))
nz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nz)

all_t, all_q, all_d = [], [], []
for sub in sorted(d for d in os.listdir(DATA) if os.path.isdir(os.path.join(DATA, d))):
    tp = os.path.join(DATA, sub, "topics.json")
    if not os.path.exists(tp):
        continue
    topics = nz.load(tp)
    qpath = os.path.join(DATA, sub, "questions.json")
    dpath = os.path.join(DATA, sub, "dependencies.json")
    qs = nz.load(qpath) if os.path.exists(qpath) else []
    deps = nz.load(dpath) if os.path.exists(dpath) else []
    qmap = {}
    nq = [nz.norm_question(q, sub) for q in qs]
    for q in nq:
        qmap.setdefault(q["topicId"], q)
    nt = [nz.norm_topic(t, sub, qmap) for t in topics]
    ids = {t["id"] for t in nt}
    nd = []
    for d in deps:
        if d.get("from") not in ids or d.get("to") not in ids:
            continue
        ty = (d.get("type") or "hard").strip().lower()
        nd.append({"from": d["from"], "to": d["to"], "type": ty if ty in ("hard", "soft") else "hard"})
    all_t += nt
    all_q += nq
    all_d += nd

nz.dump(os.path.join(DATA, "topics.json"), all_t)
nz.dump(os.path.join(DATA, "questions.json"), all_q)
nz.dump(os.path.join(DATA, "dependencies.json"), all_d)
print("汇总已重建：topics %d / questions %d / dependencies %d" % (len(all_t), len(all_q), len(all_d)))
