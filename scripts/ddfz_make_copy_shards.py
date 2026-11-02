#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 politics「文案改写」批次分片（description + mastery_criteria）。

每个分片：data/politics/_batch/wen/S{NN}/WORKER.md（派单）+ _batch/wen/S{NN}.json（产出）
用法: python3 scripts/ddfz_make_copy_shards.py [--max 40]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
OUT = os.path.join(SUB, "_batch", "wen")

RULES = """# {tag} · 文案改写派单（{book}）

本片 {n} 个知识点，需要为**每一个**点重写 `description` 与 `mastery_criteria`。

## 写作要求

1. `description`（40–90 个汉字，写「学到什么 + 核心概念/价值取向」）：
   - 必须落到本点**具体内容**（看着教材位置与课标引文写），不许写成「本课讲了…」的套话；
   - ⛔ 不得等于 `name`，不得出现「核心观点并联系生活实例说明」这类模板句；
   - 义教用学生能懂的话（举身边场景），高中用学科语域（概念、制度、原理表述准确）。
2. `mastery_criteria`（2–3 条，每条 15–50 个汉字）：
   - 每条以**行为动词**开头：能说出／能举例／能辨别／能说明／能运用／懂得／知道／理解；
   - 必须**可观察、可判定**（写「能举例说明××与××的区别」，不写「深刻理解××」）；
   - 同一段里不要重复上一句的措辞。
3. 术语准确：权利/权力、法治/法制、道德/法律、人大/政府/法院/政协 不得混用；
   法条、制度名称、史实年代不确定就不写细节。
4. ⛔ 禁 AI 腔：不用「总之／综上所述／不仅…而且…／赋能／抓手／闭环／维度／赋能」，
   不用排比堆叠，不用「随着…的发展」开头。
5. 每条 `mastery_criteria` 用中文标点，句末不加句号也可以，但整段不要出现 Markdown 记号。

## 产出格式

写到 `{out_path}`，顶层数组：

```json
[{{"id": "pol_p001", "description": "…", "mastery_criteria": ["…", "…"]}}]
```

本片 {n} 个点**必须全部出现**，id 原样照抄，顺序不限。

## 自检（必须跑到末行 PASS）

```bash
python3 {root}/scripts/ddfz_check_copy.py {out_path} --shard={tag}
```
"""


def main():
    mx = 40
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])
    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    order = []
    for t in topics:
        book = t["chapter"].split(" ")[0]
        if not order or order[-1][0] != book:
            order.append((book, []))
        order[-1][1].append(t)

    shards, cur, curbook = [], [], None
    for book, pts in order:
        if cur and (len(cur) + len(pts) > mx or len(cur) >= mx - 8):
            shards.append((curbook, cur))
            cur, curbook = [], None
        if curbook is None:
            curbook = book
        elif curbook != book and len(cur) >= 28:
            shards.append((curbook, cur))
            cur, curbook = [], book
        cur += pts
        curbook = book if curbook is None else curbook
    if cur:
        shards.append((curbook, cur))

    os.makedirs(OUT, exist_ok=True)
    for i, (book, pts) in enumerate(shards, 1):
        tag = "W%02d" % i
        d = os.path.join(OUT, tag)
        os.makedirs(d, exist_ok=True)
        out_path = os.path.join(OUT, tag + ".json")
        lines = [RULES.format(tag=tag, book=book, n=len(pts), out_path=out_path, root=ROOT), "",
                 "## 本片知识点", "", "| id | level | 名称 | 教材位置 | 课标引文 |", "| --- | --- | --- | --- | --- |"]
        for t in pts:
            q = "；".join(s["quote"] for s in t["standards"][:2]).replace("|", "／")
            lines.append("| %s | %s | %s | %s | %s |" % (t["id"], t["level"], t["name"],
                                                         t["chapter"], q[:120]))
        open(os.path.join(d, "WORKER.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("%s %-26s %d 点" % (tag, book, len(pts)))
    print("分片 %d 个 / 点 %d" % (len(shards), sum(len(p) for _, p in shards)))


if __name__ == "__main__":
    main()
