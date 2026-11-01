# -*- coding: utf-8 -*-
"""politics 题库分片 + 派单（W=单元5／课时8，每片 ≤70 题）。

产出 data/politics/_shards/S{NN}/WORKER.md；题目落 data/politics/_bank/S{NN}.json（数组）。
幂等：已在 _bank 出现的 topicId 自动跳过。
用法: python3 scripts/ddfz_make_shards.py [--max 70] [--write]
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
W = {"unit": 5, "lesson": 8}


def main():
    mx = 70
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])
    write = "--write" in sys.argv

    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    done = set()
    for f in glob.glob(os.path.join(SUB, "_bank", "*.json")):
        data = json.load(open(f, encoding="utf-8"))
        items = data.get("questions", []) if isinstance(data, dict) else data
        done |= {q["topicId"] for q in items}

    order = []
    for t in topics:
        if t["id"] in done:
            continue
        book = t["chapter"].split(" ")[0]
        if not order or order[-1][0] != book:
            order.append((book, []))
        order[-1][1].append(t)

    used = [int(os.path.basename(p)[1:3]) for p in glob.glob(os.path.join(SUB, "_bank", "S*.json"))]
    used += [int(os.path.basename(p)[1:]) for p in glob.glob(os.path.join(SUB, "_shards", "S*"))]
    nxt = (max(used) + 1) if used else 1

    shards = []
    for book, pts in order:
        cur, wsum = [], 0
        for t in pts:
            w = W[t["level"]]
            if cur and wsum + w > mx:
                shards.append((book, cur, wsum))
                cur, wsum = [], 0
            cur.append(t)
            wsum += w
        if cur:
            shards.append((book, cur, wsum))

    print("待补知识点 %d | 分片 %d | 题量合计 %d"
          % (sum(len(p) for _, p in order), len(shards), sum(w for _, _, w in shards)))
    for i, (book, pts, w) in enumerate(shards, nxt):
        tag = "S%02d" % i
        print("  %s %-28s 点=%d 题=%d" % (tag, book, len(pts), w))
        if not write:
            continue
        d = os.path.join(SUB, "_shards", tag)
        os.makedirs(d, exist_ok=True)
        bank = os.path.join(SUB, "_bank", tag + ".json")
        ids = ",".join(t["id"] for t in pts)
        lines = ["# %s · %s 题库分片派单" % (tag, book), "",
                 "本片知识点 %d 个，需写 **%d 道题**（课时点每点 8 题、单元点每点 5 题）。" % (len(pts), w), "",
                 "| topicId | level | 名称 | 教材位置 | 题数 |", "| --- | --- | --- | --- | --- |"]
        for t in pts:
            lines.append("| %s | %s | %s | %s | %d |"
                         % (t["id"], t["level"], t["name"], t["chapter"], W[t["level"]]))
        lines += ["", "## 题目要求", "",
                  "1. 全部 `choice`，4 个选项，字段：`{\"id\",\"topicId\",\"prompt\",\"question\",\"answer\",\"type\":\"choice\",\"difficulty\",\"explanation\",\"options\":[{\"label\":\"A\",\"text\":\"…\"},…]}`。",
                  "2. `prompt` 与 `question` 同值；≥12 个汉字；必须是**情境化题干**（给具体场景/材料/对话/做法，再问判断或选择），⛔ 禁「关于「X」，下列说法正确的是」这类模板题干。",
                  "3. 4 个选项都要实质内容；3 个错项必须是学生真实错法：概念混淆（如「权利/义务」「法治/法制」「道德/法律」）、以偏概全、绝对化表述（「一切」「完全」「只要…就」）、主体错位（人大/政府/法院/政协职责互串）、张冠李戴（史实或制度对应错）。⛔ 禁「与本题无关」「不知道」「以上都不是」「仅在大学学习」。",
                  "4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。",
                  "5. 难度三档齐全：basic（识记再现、单点判断）/ standard（一步情境辨析）/ hard（多主体、多概念交叉或易错边界）。",
                  "6. `explanation` ≥15 个汉字，写清「为什么对」并点出错项错在哪一类。",
                  "7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。",
                  "8. 内容必须与该点所属册次、学段一致（义教用学生身边情境，高中可用时政材料）；不编造条文、数字、人名与文件名。",
                  "9. `id` 用 `polq_q%s` + 4 位流水（如 `polq_q%s0001`）；`topicId` 只能取本片清单内的 id。" % (tag, tag),
                  "", "## 产出与自检（必须跑到末行 PASS）", "",
                  "把题目数组写到 `%s`（顶层就是数组），然后运行：" % bank, "",
                  "```bash",
                  "python3 %s/scripts/qd_check_bank.py %s --allow=%s" % (ROOT, bank, ids),
                  "```", "",
                  "有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。", "",
                  "## 汇报（一句话）", "",
                  "分片 %s / 题数 / 难度分布 / 答案位分布 / checker 末行。" % tag]
        open(os.path.join(d, "WORKER.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    if write:
        print("WRITTEN", os.path.join(SUB, "_shards"))


if __name__ == "__main__":
    main()
