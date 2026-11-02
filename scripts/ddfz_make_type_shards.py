#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 politics 题型改造分片：每个课时点把 8 道选择题中的 2 道改造成 1 填空 + 1 简答。

（单元/课点保持 5 道选择题；题量 8/5 不变，只改题型构成）
用法: python3 scripts/ddfz_make_type_shards.py [--max 40]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
OUT = os.path.join(SUB, "_batch", "type")

RULES = """# {tag} · 题型改造派单（{book}）

本片 {n} 个课时点，每个点把 8 道选择题中的 **2 道**改造为 **1 填空 + 1 简答**（题量仍 8，不许增删题）。

## 改造要求

1. **填空（type=fill）**：把指定题重写成情境化填空题，题干里用 `____` 标出空位；
   - `options` 必须写 `[]`（没有选项），`answer` 写**要填的文本**（多个空用「；」分隔，每空一个答案）；
   - 不能是选择题换个说法（不许出现「A/B/C/D」字样）。
2. **简答（type=short-answer）**：把指定题重写成简答题；
   - `answer` 写参考答案（一条完整表述，可用「；」分点）；
   - `keypoints` 写 **2–4 条**要点，每条 ≥4 个汉字，是判分要点而不是整句重复；
   - `options` 同样写 `[]`。
3. 两题都必须**保留原题的 topicId 与 id**（只换题面与字段），`prompt` 与 `question` 同值，≥12 个汉字，情境化，禁止「关于「X」，下列说法正确的是」模板；
4. `explanation` ≥15 个汉字，说明答案依据；
5. 术语准确（权利/权力、法治/法制、人大/政府/法院/政协 不得混用），不编造法条与数字。

## 产出格式

写到 `{out_path}`，顶层数组，每题一个对象：

```json
[{{"id": "polq_qS010002", "topicId": "pol_p002", "prompt": "…____…", "question": "…____…",
   "answer": "…", "type": "fill", "difficulty": "standard", "explanation": "…", "options": []}},
 {{"id": "polq_qS010007", "topicId": "pol_p002", "prompt": "…", "question": "…",
   "answer": "…", "type": "short-answer", "difficulty": "hard", "explanation": "…",
   "keypoints": ["…", "…"], "options": []}}]
```

## 自检（必须到末行 PASS）

```bash
python3 {root}/scripts/ddfz_check_type.py {out_path} --shard={tag}
```
"""


def main():
    mx = 40
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])
    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    qs = json.load(open(os.path.join(SUB, "questions.json"), encoding="utf-8"))
    by = {}
    for q in qs:
        by.setdefault(q["topicId"], []).append(q)
    lessons = [t for t in topics if t["level"] == "lesson"]
    os.makedirs(OUT, exist_ok=True)
    shards, cur, book = [], [], None
    for t in lessons:
        b = t["chapter"].split(" ")[0]
        if cur and (len(cur) >= mx or (book != b and len(cur) >= 20)):
            shards.append((book, cur))
            cur = []
        book = b
        cur.append(t)
    if cur:
        shards.append((book, cur))

    for i, (b, pts) in enumerate(shards, 1):
        tag = "T%02d" % i
        d = os.path.join(OUT, tag)
        os.makedirs(d, exist_ok=True)
        out_path = os.path.join(OUT, tag + ".json")
        lines = [RULES.format(tag=tag, book=b, n=len(pts), out_path=out_path, root=ROOT), "",
                 "## 本片改造清单", "",
                 "| topicId | 名称 | 教材位置 | 改成填空的题 | 改成简答的题 |", "| --- | --- | --- | --- | --- |"]
        for t in pts:
            ids = sorted(x["id"] for x in by.get(t["id"], []))
            fill_id = ids[2] if len(ids) > 2 else ids[0]
            short_id = ids[6] if len(ids) > 6 else ids[-1]
            lines.append("| %s | %s | %s | %s | %s |" % (t["id"], t["name"], t["chapter"],
                                                         fill_id, short_id))
        # 把原题内容贴出来，便于改造（只贴被改造的两题）
        lines += ["", "## 原题（改造参考）", ""]
        for t in pts:
            ids = sorted(x["id"] for x in by.get(t["id"], []))
            for qid in (ids[2] if len(ids) > 2 else ids[0], ids[6] if len(ids) > 6 else ids[-1]):
                q = next(x for x in by[t["id"]] if x["id"] == qid)
                lines.append("### %s（%s）" % (qid, t["name"]))
                lines.append("- 题干：" + q["prompt"])
                for o in q.get("options") or []:
                    lines.append("  - %s. %s" % (o["label"], o["text"]))
                lines.append("- 答案：%s" % q["answer"])
                lines.append("- 解析：" + q["explanation"])
                lines.append("")
        open(os.path.join(d, "WORKER.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("%s %-26s %d 点（%d 题）" % (tag, b, len(pts), len(pts) * 2))
    print("分片 %d 个 / 点 %d" % (len(shards), sum(len(p) for _, p in shards)))


if __name__ == "__main__":
    main()
