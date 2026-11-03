# -*- coding: utf-8 -*-
"""生成历史「补点 + 补题」分片作业单（父代预分配 id 与答案位）。

用法：
  python3 scripts/gen_history_bank_shards.py                  # 生成到 data/history/_bank_shards/
  python3 scripts/gen_history_bank_shards.py --per-shard 8    # 每片最多几个点（默认 8）

口径：
  · 目标 8 题/点（一课一点）；存量点只补差额，新点写「内容 + 8 题」
  · 题目 id 父代预分配（his_qNNNN 续 max+1）——⛔ 工人不得自行续号
  · 答案位父代按 A/B/C/D 轮转预分配（test_history.py 有「答案分布最多–最少 ≤8」硬断言，
    1632 道全靠轮转才守得住）；工人必须把正确项放在指定 label 上
  · 历史本轮只出选择题（test 的答案分布判据按单选字母统计，填空/简答会把它打散）
"""
import argparse
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "history")
OUT = os.path.join(D, "_bank_shards")
TARGET_Q = 8
LABELS = "ABCD"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-shard", type=int, default=8)
    a = ap.parse_args()

    topics = load(os.path.join(D, "topics.json"))
    qs = load(os.path.join(D, "questions.json"))
    sk = load(os.path.join(D, "_skeleton.json"))["points"]
    plan = load(os.path.join(D, "_toc", "_gap_plan.json"))

    have = defaultdict(int)
    for q in qs:
        have[q["topicId"]] += 1
    qmax = max(int(re.search(r"(\d+)$", q["id"]).group(1)) for q in qs)

    new_ids = {p["id"] for p in plan["newPoints"]}
    sk_by_id = {p["id"]: p for p in sk}

    # 工作项：先按「册 + 单元号」排序，保证同片同册、顺序与教材一致
    order_key = {}
    for p in sk:
        order_key[p["id"]] = (p["book"], p["unitNo"], p["lessonNo"])
    existing_order = {}
    for i, t in enumerate(topics):
        existing_order[t["id"]] = i

    items = []
    for t in topics:                       # 存量点：补差额
        need = TARGET_Q - have.get(t["id"], 0)
        if need > 0:
            items.append({"topicId": t["id"], "name": t["name"], "chapter": t["chapter"],
                          "isNew": False, "need": need, "have": have.get(t["id"], 0)})
    for pid in sorted(new_ids, key=lambda i: order_key.get(i, ("", 0, 0))):
        p = sk_by_id[pid]
        items.append({"topicId": pid, "name": p["name"], "chapter": p["chapter"],
                      "isNew": True, "need": TARGET_Q, "have": 0,
                      "book": p["book"], "domain": p["domain"],
                      "grade": p["grade"], "semester": p["semester"]})

    def book_of(it):
        if it.get("book"):
            return it["book"]
        return it["chapter"].split(" ")[0]

    # 按册 → 单元 → 教材课序 归组
    def sort_key(it):
        pid = it["topicId"]
        return (book_of(it), order_key.get(pid, ("", 99, 99)), existing_order.get(pid, 999))

    items.sort(key=sort_key)

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith("H") and f.endswith(".json"):
            os.remove(os.path.join(OUT, f))     # 只清本目录的 H*.json（显式前缀，不碰别处）

    shards, cur = [], []
    for it in items:
        if cur and (book_of(it) != book_of(cur[0]) or len(cur) >= a.per_shard):
            shards.append(cur)
            cur = []
        cur.append(it)
    if cur:
        shards.append(cur)

    qn = qmax
    ans_i = 0
    manifest = []
    for n, group in enumerate(shards, 1):
        sid = f"H{n:02d}"
        pts = []
        for it in group:
            labels = []
            for k in range(it["need"]):
                qn += 1
                labels.append({"qid": f"his_q{qn:04d}", "label": LABELS[ans_i % 4]})
                ans_i += 1
            pts.append({**it, "questions": labels})
        shard = {"shard": sid, "book": book_of(group[0]),
                 "out": os.path.join(OUT, f"{sid}_out.json"), "points": pts,
                 "questionCount": sum(len(p["questions"]) for p in pts)}
        with open(shard["out"], "w", encoding="utf-8") as f:
            json.dump(shard, f, ensure_ascii=False, indent=2)
        manifest.append({"shard": sid, "book": shard["book"], "points": len(pts),
                         "questions": shard["questionCount"],
                         "newPoints": sum(1 for p in pts if p["isNew"])})
        print(f"{sid} {shard['book']:16s} 点{len(pts):2d}（新{sum(1 for p in pts if p['isNew']):2d}） 题{shard['questionCount']:3d}")

    with open(os.path.join(OUT, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"target": TARGET_Q, "shards": manifest,
                   "totalPoints": len(items), "totalQuestions": ans_i}, f, ensure_ascii=False, indent=2)
    print(f"\n合计 {len(shards)} 片｜{len(items)} 点｜{ans_i} 题（答案位轮转 ABCD）")
    print(f"作业单目录：{OUT}")


if __name__ == "__main__":
    main()
