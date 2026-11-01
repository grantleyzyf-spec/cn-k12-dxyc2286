# -*- coding: utf-8 -*-
"""把青岛版数学剩余册次切成题库分片，并生成每片的 WORKER.md（派单）。

分片规则：按「单元 → 其课时」顺序装箱，权重 单元点=5 题、课时点=8 题，每片 ≤SHARD_MAX 题。
已交题库的知识点（_bank 里已有的 topicId）自动跳过，可反复运行（幂等）。

产出：
  data/math-qd/_shards/S{NN}/WORKER.md   派单（绝对路径、题量、格式、自检命令）
用法: python3 scripts/qd_make_shards.py [--max 70] [--write]
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QD = os.path.join(ROOT, "data", "math-qd")
W = {"unit": 5, "lesson": 8}


def main():
    mx = 70
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])
    write = "--write" in sys.argv

    topics = json.load(open(os.path.join(QD, "topics.json"), encoding="utf-8"))
    done = set()
    for f in glob.glob(os.path.join(QD, "_bank", "*.json")):
        data = json.load(open(f, encoding="utf-8"))
        items = data.get("questions", []) if isinstance(data, dict) else data
        done |= {q["topicId"] for q in items}

    # 按册分组，保持 topics 顺序（册 → 单元 → 课时）
    order = []
    for t in topics:
        if t["id"] in done:
            continue
        book = t["chapter"].split(" ")[0]
        if not order or order[-1][0] != book:
            order.append((book, []))
        order[-1][1].append(t)

    used = [int(os.path.basename(p)[1:3]) for p in glob.glob(os.path.join(QD, "_bank", "S*.json"))]
    used += [int(os.path.basename(p)[1:]) for p in glob.glob(os.path.join(QD, "_shards", "S*"))]
    nxt = (max(used) + 1) if used else 1
    shards = []
    for book, pts in order:
        cur, wsum = [], 0
        for t in pts:
            w = W[t["level"]]
            if cur and wsum + w > mx:
                shards.append((book, cur, wsum)); cur, wsum = [], 0
            cur.append(t); wsum += w
        if cur:
            shards.append((book, cur, wsum))

    print(f"待补知识点 {sum(len(p) for _, p in order)} | 分片 {len(shards)} | 题量合计 {sum(w for _, _, w in shards)}")
    for i, (book, pts, w) in enumerate(shards, nxt):
        tag = f"S{i:02d}"
        print(f"  {tag} {book:<8} 点={len(pts):<3} 题={w}")
        if not write:
            continue
        d = os.path.join(QD, "_shards", tag)
        os.makedirs(d, exist_ok=True)
        lines = [f"# {tag} · {book} 题库分片派单", "",
                 f"本片知识点 {len(pts)} 个，需写 **{w} 道题**（课时点每点 8 题、单元点每点 5 题）。", "",
                 "| topicId | level | 名称 | 教材位置 | 题数 |", "| --- | --- | --- | --- | --- |"]
        for t in pts:
            lines.append(f"| {t['id']} | {t['level']} | {t['name']} | {t['chapter']} | {W[t['level']]} |")
        ids = ",".join(t["id"] for t in pts)
        lines += ["", "## 题目要求", "",
                  "1. 全部 `choice`，4 个选项，字段：`{\"id\",\"topicId\",\"prompt\",\"question\",\"answer\",\"type\":\"choice\",\"difficulty\",\"explanation\",\"options\":[{\"label\":\"A\",\"text\":\"…\"},…]}`。",
                  "2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。",
                  "3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。",
                  "4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。",
                  "5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。",
                  "6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。",
                  "7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。",
                  "8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。",
                  f"9. `id` 用 `qdm_q{tag}` + 4 位流水（如 `qdm_q{tag}0001`）；`topicId` 只能取本片清单内的 id。",
                  "", "## 产出与自检（必须跑到末行 PASS）", "",
                  f"把题目数组写到 `{os.path.join(QD, '_bank', tag + '.json')}`（顶层就是数组），然后运行：", "",
                  "```bash", f"python3 {ROOT}/scripts/qd_check_bank.py {os.path.join(QD, '_bank', tag + '.json')} --allow={ids}", "```", "",
                  "有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。", "",
                  "## 汇报（一句话）", "", f"分片 {tag} / 题数 / 难度分布 / 答案位分布 / checker 末行。"]
        open(os.path.join(d, "WORKER.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    if write:
        print("WRITTEN", os.path.join(QD, "_shards"))


if __name__ == "__main__":
    main()
