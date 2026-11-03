# -*- coding: utf-8 -*-
"""历史「补点 + 补题」缺口计划（只读，产工单数据）。

用法：
  python3 scripts/plan_history_gap.py                 # 打印计划
  python3 scripts/plan_history_gap.py --write         # 落 data/history/_toc/_gap_plan.json

两步：
  ① 补点：`_skeleton.json` 的课 − `topics.json` 已有点（按「册+单元」内课名近似匹配，ratio ≥ 0.55 记为已覆盖）
  ② 补题：每个已有点 8 题目标 − 现有题数（同点题量不足即补）
"""
import argparse
import difflib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "history")
TARGET_Q = 8
RATIO = 0.55


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def norm(s):
    return re.sub(r"[\s·、，。：（）()「」《》“”\"'—-]", "", s or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    topics = load(os.path.join(D, "topics.json"))
    qs = load(os.path.join(D, "questions.json"))
    sk = load(os.path.join(D, "_skeleton.json"))["points"]
    qcnt = Counter(q["topicId"] for q in qs)

    by_chapter = defaultdict(list)
    for t in topics:
        by_chapter[t["chapter"]].append(t)

    # 逐单元按「课数 vs 点数」定缺口（历史库内点名是主题式、教材课名是叙事式，按名匹配必然假缺口：
    # 实测逐名匹配会报 132 个「新点」而单元课数只缺 52）。
    new_points, covered, unmatched, surplus = [], [], [], []
    sk_by_chapter = defaultdict(list)
    for p in sk:
        sk_by_chapter[p["chapter"]].append(p)
    for chap, sk_list in sk_by_chapter.items():
        ex_list = by_chapter.get(chap, [])
        # 先贪心配对（只为报告「哪个骨架点已被哪个库内点代表」）
        pairs, used = [], set()
        for p in sk_list:
            best, score = None, 0.0
            for t in ex_list:
                if t["id"] in used:
                    continue
                r = difflib.SequenceMatcher(None, norm(p["name"]), norm(t["name"])).ratio()
                if r > score:
                    best, score = t, r
            if best and score >= RATIO:
                pairs.append((p, best, score))
                used.add(best["id"])
        for p, t, score in pairs:
            covered.append({"skeleton": p["id"], "existing": t["id"], "ratio": round(score, 2)})
            t["_used"] = True
        need = len(sk_list) - len(ex_list)
        if need > 0:
            rest = [p for p in sk_list if not any(p["id"] == c["skeleton"] for c in covered)]
            for p in rest[:need]:
                new_points.append(p)
        elif need < 0:
            surplus.append({"chapter": chap, "lessons": len(sk_list), "points": len(ex_list)})

    # 已有点里没被任何骨架点认领的（说明库内多出/错册）
    orphan = [t for t in topics if not t.get("_used")]
    for t in topics:
        t.pop("_used", None)

    # 补题计划（只针对库里已有的点）
    need_q = []
    for t in topics:
        n = qcnt.get(t["id"], 0)
        if n < TARGET_Q:
            need_q.append({"topicId": t["id"], "name": t["name"], "chapter": t["chapter"],
                           "have": n, "need": TARGET_Q - n})
    # 题型补位：已有点现有题全 choice ⇒ 每点至少要 1 fill / 1 short-answer / 1 numeric 视内容而定
    type_gap = {}
    for t in topics:
        types = {q["type"] for q in qs if q["topicId"] == t["id"]}
        type_gap[t["id"]] = sorted(types)

    print(f"骨架点 {len(sk)}｜库内点 {len(topics)}")
    print(f"① 补点：新增 {len(new_points)} 点／已覆盖 {len(covered)} 点／库内无人认领 {len(orphan)} 点"
          f"／库内多于课数的单元 {len(surplus)} 个")
    per_book = Counter(p["book"] for p in new_points)
    for b, n in per_book.items():
        print(f"    {b:16s} +{n}")
    if orphan:
        print(f"   库内未认领：{[t['id'] + ' ' + t['name'][:12] for t in orphan][:12]}")
    print(f"② 补题：{len(need_q)} 点不足 {TARGET_Q} 题，合计需补 {sum(x['need'] for x in need_q)} 题"
          f"；新点还需 {len(new_points) * TARGET_Q} 题 ⇒ 本轮共写 "
          f"{sum(x['need'] for x in need_q) + len(new_points) * TARGET_Q} 题")
    print(f"   现有题型集合：{sorted({tp for v in type_gap.values() for tp in v})}")

    if a.write:
        out = {"target": {"questionsPerPoint": TARGET_Q, "matchRatio": RATIO},
               "summary": {"skeletonPoints": len(sk), "existingPoints": len(topics),
                           "newPoints": len(new_points), "covered": len(covered),
                           "orphanPoints": len(orphan),
                           "pointsNeedingQuestions": len(need_q),
                           "questionsToWrite": sum(x["need"] for x in need_q)},
               "newPoints": new_points, "needQuestions": need_q, "surplusUnits": surplus,
               "orphanPoints": [t["id"] for t in orphan]}
        path = os.path.join(D, "_toc", "_gap_plan.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        print(f"\n✅ 计划已落盘：{path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
