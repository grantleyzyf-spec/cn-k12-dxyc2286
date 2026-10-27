#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把分册片段（/tmp/spa_build/<volkey>.json）合并为 data/spanish 三件套。

- 片段来源：每册一个 {volume, book, topics[], questions[]}，由分册工位产出（契约见 docs/spanish.md）
- 跨册先修：片段里 `prereq_names` 写中文知识点名，本脚本按全库 name 索引解析成边
- 兜底衔接：某册若没有任何跨册入边，用上一册「末个语法/交际知识点」接本册首个根知识点，避免册间断链
- 环检测：任何会成环的边一律丢弃并报告

用法：python3 scripts/merge_spanish_volumes.py --fragments /tmp/spa_build [--write]
"""
import argparse, difflib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ORDER = ["g7a", "g7b", "g8a", "g8b", "g9a", "b4a", "b4b", "b4c", "x1", "x2", "x3", "x4"]
KEEP = {"id", "name", "subject", "domain", "grade", "semester", "chapter", "type", "description",
        "mastery_criteria", "diagnostic_question", "standards", "tags", "prerequisites",
        "curriculumRef", "textbookRef", "verified", "root_reason"}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def renumber(frags):
    """分册工位各自从 001 编起，合并时按册序统一重编：
    义教（g7a..g9a）→ spa_p001…；高中（b4a..x4）→ spa_h001…
    同步重写 questions.id/topicId 与 prerequisites（册内先修）。"""
    counters = {"p": 0, "h": 0}
    maps = {}
    for vk, d in frags:
        side = "p" if d["book"].startswith(("七年级", "八年级", "九年级", "一", "二", "三")) and "必修四" not in d["book"] and "选择性" not in d["book"] else "h"
        m = {}
        for t in d["topics"]:
            counters[side] += 1
            m[t["id"]] = "spa_%s%03d" % (side, counters[side])
        maps[vk] = m
        for t in d["topics"]:
            t["id"] = m[t["id"]]
            t["prerequisites"] = [m[p] for p in (t.get("prerequisites") or []) if p in m]
        for q in d["questions"]:
            old = q.get("topicId")
            if old in m:
                q["topicId"] = m[old]
                q["id"] = "q_" + m[old]
    return maps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fragments", default="/tmp/spa_build")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    topics, qs, report = [], [], []
    per_vol = {}
    loaded = []
    for vk in ORDER:
        p = os.path.join(a.fragments, vk + ".json")
        if not os.path.exists(p):
            print("!! 缺片段", p)
            continue
        loaded.append((vk, load(p)))
    renumber(loaded)
    for vk, d in loaded:
        book = d["book"]
        ts = d["topics"]
        for t in ts:
            t = {k: v for k, v in t.items() if k in KEEP}
            t["subject"] = "spanish"
            topics.append(t)
        qs += d["questions"]
        per_vol[vk] = {"book": book, "topicIds": [t["id"] for t in ts],
                       "topics": ts, "prereq_names": {t["id"]: t.get("prereq_names") or [] for t in ts}}
        report.append(f"{vk} {book}: {len(ts)} 知识点 / {len(d['questions'])} 题")

    ids = {t["id"] for t in topics}
    by_name = {}
    for t in topics:
        by_name.setdefault(t["name"].strip(), t["id"])

    def nkey(s):
        """归一化：去括号注释、标点、空格、西里尔/拉丁字母大小写，只留中文与字母数字"""
        s = re.sub(r"[（(][^）)]*[）)]", "", s or "")
        s = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", s)
        return s.lower()

    by_nkey = {}
    for t in topics:
        by_nkey.setdefault(nkey(t["name"]), t["id"])

    def resolve(nm):
        nm = (nm or "").strip()
        if not nm:
            return None
        if nm in by_name:
            return by_name[nm]
        k = nkey(nm)
        if k and len(k) >= 4 and k in by_nkey:
            return by_nkey[k]
        cands = [i for n, i in by_nkey.items() if k and len(k) >= 4 and (k in n or n in k)]
        if len(cands) == 1:
            return cands[0]
        # 末招：相似度唯一最高且 ≥0.72
        scored = sorted(((difflib.SequenceMatcher(None, k, n).ratio(), i) for n, i in by_nkey.items()),
                        reverse=True)
        if scored and scored[0][0] >= 0.72 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.05):
            return scored[0][1]
        return None

    # 1) 跨册先修：prereq_names -> 边
    edges = set()
    unresolved = []
    for vk, v in per_vol.items():
        for tid, names in v["prereq_names"].items():
            for nm in names:
                nm = (nm or "").strip()
                if not nm:
                    continue
                target = resolve(nm)
                if not target or target == tid:
                    unresolved.append((tid, nm))
                    continue
                edges.add((target, tid))
    # 2) 册内先修
    for t in topics:
        for p in t.get("prerequisites") or []:
            if p in ids and p != t["id"]:
                edges.add((p, t["id"]))

    # 3) 兜底衔接：册间无入边则接上一册骨架末点
    def spine_tail(ts):
        pick = None
        for t in ts:
            if t.get("domain") in ("语法", "交际"):
                pick = t["id"]
        return pick or ts[-1]["id"]

    prev_tail = None
    for vk in ORDER:
        v = per_vol.get(vk)
        if not v:
            continue
        first_root = None
        for t in v["topics"]:
            if not (t.get("prerequisites") or []):
                first_root = t["id"]
                break
        first_root = first_root or v["topicIds"][0]
        has_in = any(b in v["topicIds"] for _, b in edges)
        if prev_tail and not has_in:
            edges.add((prev_tail, first_root))
            report.append(f"   ↳ 兜底衔接 {prev_tail} → {first_root}")
        prev_tail = spine_tail(v["topics"])

    # 4) 环检测：逐条加入，成环则丢弃
    parent = {}


    def creates_cycle(a, b):
        stack, seen = [a], set()
        while stack:
            u = stack.pop()
            if u == b:
                return True
            if u in seen:
                continue
            seen.add(u)
            stack.extend(parent.get(u, ()))
        return False


    kept, dropped = [], []
    for a_, b_ in sorted(edges):
        if a_ not in ids or b_ not in ids:
            continue
        if creates_cycle(a_, b_):
            dropped.append((a_, b_))
            continue
        parent.setdefault(b_, []).append(a_)
        kept.append({"from": a_, "to": b_, "type": "hard"})

    # 5) prerequisites 与边镜像一致
    premap = {}
    for e in kept:
        premap.setdefault(e["to"], []).append(e["from"])
    for t in topics:
        t["prerequisites"] = sorted(premap.get(t["id"], []))
    for t in topics:
        if not t["prerequisites"] and not t.get("root_reason"):
            t["root_reason"] = "该册起始知识点，教材此前无同域先修内容（跨册未连边）"

    report.append(f"边 {len(kept)} 条（丢弃成环 {len(dropped)}，跨册名未解析 {len(unresolved)}）")
    for u in unresolved[:12]:
        report.append(f"   · 未解析先修名 {u[0]} ← {u[1]}")
    print("\n".join(report))
    print(f"合计 topics {len(topics)} / questions {len(qs)}")

    if a.write:
        dump(os.path.join(DATA, "spanish", "topics.json"), topics)
        dump(os.path.join(DATA, "spanish", "questions.json"), qs)
        dump(os.path.join(DATA, "spanish", "dependencies.json"), kept)
        print("已写入 data/spanish/{topics,questions,dependencies}.json")


if __name__ == "__main__":
    main()
