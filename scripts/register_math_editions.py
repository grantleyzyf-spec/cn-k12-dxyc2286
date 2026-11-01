#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把若干「数学版本桶」登记进 data/subjects.json 与 data/subject-groups.json（幂等）。

为什么单独成脚本：`build_subjects_registry.py` 只统计 **git 已跟踪** 的目录，
在途（未提交）的版本桶会被静默剔除；而 `subjects.json` 是首页学科卡与旧内联下拉的数据源，
少一条就是「站点上看不到这个版本」。所以新版本上线前用它显式 upsert 一次。

用法：
  python3 scripts/register_math_editions.py                # 按内置表 upsert 全部数学版本
  python3 scripts/register_math_editions.py math-sujiao    # 只登记一个
  python3 scripts/register_math_editions.py --check        # 只报告差异，不写盘
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# 桶 → (版本显示名, 版本 icon)
EDITIONS = {
    "math": "人教版",
    "math-bj": "北京版",
    "math-bsd": "北师大版",
    "math-ejiao": "鄂教版",
    "math-hebei": "冀教版",
    "math-hujiao": "沪教版",
    "math-qd": "青岛版",
    "math-sujiao": "苏教版",
    "math-suke": "苏科版",
    "math-xiangjiao": "湘教版",
}
ICON = "📐"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def counts(bucket):
    tp = os.path.join(DATA, bucket, "topics.json")
    qp = os.path.join(DATA, bucket, "questions.json")
    n_t = len(load(tp)) if os.path.exists(tp) else 0
    n_q = len(load(qp)) if os.path.exists(qp) else 0
    return n_t, n_q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("buckets", nargs="*")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    want = a.buckets or [b for b in EDITIONS if os.path.exists(os.path.join(DATA, b, "topics.json"))]

    # ---------- subjects.json（平铺）----------
    sp = os.path.join(DATA, "subjects.json")
    subj = load(sp)
    lst = subj["subjects"]
    changed = []
    for b in want:
        n_t, _ = counts(b)
        if not n_t:
            print(f"  跳过 {b}：没有 topics.json")
            continue
        entry = next((x for x in lst if x.get("id") == b), None)
        name = EDITIONS.get(b, b)
        label = "数学" if b == "math" else f"数学（{name}）"
        if entry is None:
            lst.append({"id": b, "name": label, "icon": ICON, "count": n_t})
            changed.append(f"subjects.json + {b}（{n_t}）")
        elif entry.get("count") != n_t:
            changed.append(f"subjects.json ~ {b}：{entry.get('count')} → {n_t}")
            entry["count"] = n_t
    subj["total_topics"] = sum(x.get("count", 0) for x in lst)
    subj["total_subjects"] = len(lst)

    # ---------- subject-groups.json（学科→版本）----------
    gp = os.path.join(DATA, "subject-groups.json")
    grp = load(gp)
    math = next((s for s in grp["subjects"] if s.get("id") == "math"), None)
    if math is not None:
        eds = math.setdefault("editions", [])
        for b in want:
            n_t, n_q = counts(b)
            if not n_t:
                continue
            e = next((x for x in eds if x.get("id") == b), None)
            if e is None:
                eds.append({"id": b, "name": EDITIONS.get(b, b), "icon": ICON,
                            "topics": n_t, "questions": n_q})
                changed.append(f"subject-groups + {b}（{n_t}/{n_q}）")
            elif (e.get("topics"), e.get("questions")) != (n_t, n_q):
                changed.append(f"subject-groups ~ {b}：{e.get('topics')}/{e.get('questions')} → {n_t}/{n_q}")
                e["topics"], e["questions"] = n_t, n_q
        # 人教排第一，其余按显示名排序
        eds.sort(key=lambda x: (x["id"] != "math", x.get("name", "")))
        math["topics"] = sum(x.get("topics", 0) for x in eds)
        math["questions"] = sum(x.get("questions", 0) for x in eds)

    if not changed:
        print("已是最新，无需改动")
        return 0
    for c in changed:
        print(" ", c)
    if a.check:
        print("（--check：未写盘）")
        return 1
    dump(sp, subj)
    dump(gp, grp)
    print(f"已写盘：subjects {subj['total_subjects']} 条 / {subj['total_topics']} 点；数学 {math['topics']} 点 {len(math['editions'])} 版")
    return 0


if __name__ == "__main__":
    sys.exit(main())
