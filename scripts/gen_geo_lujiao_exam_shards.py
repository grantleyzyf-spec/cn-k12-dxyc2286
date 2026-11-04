#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_geo_lujiao_exam_shards.py —— 鲁教版高中地理 39 卷派单生成器。

卷制（对齐 data/geography 高中卷）：150 分 / 150 分钟 / 24 题
  一、选择题 18×3＝54   二、综合题 6×16＝96
每册 4 卷：期中 A/B（前一半单元）、期末 A/B（全册）；每单元 1 卷 ⇒ 19+20＝39 卷。

产出：
  data/geography-lujiao/_exam_parts/_CONTRACT.md
  data/geography-lujiao/_exam_parts/E01…E39.json   （作业单：含 scope 单元、可用点、卷名、落盘路径）
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-lujiao")
OUT = os.path.join(D, "_exam_parts")
sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
TOPICS = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))

CODE = {"必修第一册": "bx1", "必修第二册": "bx2",
        "选择性必修1": "xx1", "选择性必修2": "xx2", "选择性必修3": "xx3"}
MIDN = {"必修第一册": 2, "必修第二册": 2, "选择性必修1": 3, "选择性必修2": 2, "选择性必修3": 1}

CONTRACT = """# 合同 · 鲁教版高中地理「单元/期中/期末卷」工位

## 0. 你只写一个文件
`data/geography-lujiao/_exam_parts/<EID>_out.json`（UTF-8，**对象**，不是数组）。

## 1. 卷面结构（硬口径，⛔ 不许改）
- 合计 **150 分 / 150 分钟 / 24 题**，`sections` 恰两段：
  1. `title="一、选择题（每小题 3 分，共 54 分）"`, `rule="每小题 3 分，共 54 分"`，**18 题**，每题 `score=3`, `type="choice"`；
  2. `title="二、综合题（每小题 16 分，共 96 分）"`, `rule="每小题 16 分，共 96 分"`，**6 题**，每题 `score=16`, `type="short"`。
- `no` 全卷连续 1…24（选择题 1–18，综合题 19–24）。
- 顶层字段：`book/kind/term/grade/stage/paper/duration/fullScore/examId/scope/sections`
  （`kind`：unit/mid/fin；`term` 用作业单里的值；`stage="高中"`）。
- 单元卷 `paper` 必须逐字＝`<第N单元 单元名> 测试卷`（**用「单元」不用「章」**）；期中/期末＝`期中测试卷A/B`、`期末测试卷A/B`。

## 2. 每题字段
```json
{"no":1,"type":"choice","difficulty":"basic","topicIds":["glj_p001"],"score":3,
 "stem":"材料：……（　）","options":[{"label":"A","text":"…"},…4项],
 "answer":"A","analysis":"…（≥40 汉字，逐项辨析并以「故选 X。」收束）","itemId":"<examId>_01"}
```
- 选择题：4 选项互异、`answer ∈ A–D`、**全卷 A/B/C/D 各 ≥15%**（18 题即每字母 ≥3 题）。
- 综合题：`type="short"`，**必须给 `scoreRule`**：`"scoreRule":[{"step":"…","score":4},…]`，各步之和 = 16；
  `answer` 用 ①②③ 分条；`options` 省略。
- 每题 `topicIds` **必须非空且只取作业单给出的本卷点**；难度 `basic/standard/hard` 三档都要有。
- `stem` ≥12 字；`analysis` ≥40 汉字。

## 3. 覆盖硬要求
- **单元卷**：`scope` 内**每个课时点至少被 1 题引用**（单元上位点可引用也可不引用）。
- **期中/期末**：`scope` 内每个单元至少 2 题；全卷至少覆盖 scope 内 80% 的课时点。
- ⛔ 不得与题库原文重复：`stem` 与 `data/geography-lujiao/questions.json` 任一 `prompt` 的相似度 <0.85
  （要改写情境与设问，不要抄题干）。

## 4. 素材与口径
- 教材全文：`data/geography-lujiao/_text/<册>.txt`（带 `===== PDF第N页 =====`；`grep -n "<节名>"` 定位后 `sed -n` 读段）。
- 只考 `scope` 内单元；术语按教材（鲁教版用「单元/节」，课标用高中地理四领域）。
- ⛔ 禁 Markdown、禁凑数选项、禁跨册串题。

## 5. 自检（写完必跑）
```bash
/usr/bin/python3 - <<'PY'
import json,re,sys
d=json.load(open("data/geography-lujiao/_exam_parts/<EID>_out.json",encoding="utf-8"))
sec=d["sections"]; bad=[]
if [len(s["items"]) for s in sec]!=[18,6]: bad.append("题数")
if sum(i["score"] for s in sec for i in s["items"])!=150: bad.append("总分")
nos=[i["no"] for s in sec for i in s["items"]]
if nos!=list(range(1,25)): bad.append("题号")
from collections import Counter
ans=Counter(i["answer"] for i in sec[0]["items"])
if min(ans.values())<3: bad.append(("答案位",dict(ans)))
for s in sec:
    for i in s["items"]:
        if not i.get("topicIds"): bad.append(("无点",i["no"]))
        if len(i["stem"])<12: bad.append(("题干短",i["no"]))
        if len(re.findall(r"[\\u4e00-\\u9fa5]",i["analysis"]))<40: bad.append(("解析短",i["no"]))
        if i["type"]=="choice" and (len(i.get("options") or [])!=4 or i["answer"] not in [o["label"] for o in i["options"]]): bad.append(("选项",i["no"]))
        if i["type"]=="short" and sum(x["score"] for x in i.get("scoreRule") or [])!=i["score"]: bad.append(("scoreRule",i["no"]))
print("题数",len(nos),"问题",bad[:6],"OK" if not bad else "FAIL")
PY
```
回报一行：`<EID> <卷名> ｜ 24 题 ｜ A/B/C/D=a/b/c/d ｜ 覆盖 x/y 点 ｜ 自检 OK/FAIL`。
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "_CONTRACT.md"), "w", encoding="utf-8").write(CONTRACT)
    books = {}
    for u in sk["units"]:
        books.setdefault(u["chapter"].split(" ")[0], []).append(u)
    pts_of_unit = {u["id"]: [t for t in TOPICS if t.get("unitId") == u["id"]] for u in sk["units"]}
    cards, n = [], 0
    for book, units in books.items():
        code = CODE[book]
        for ui, u in enumerate(units, 1):
            n += 1
            eid = "E%02d" % n
            card = {"eid": eid, "kind": "unit", "book": book, "grade": u["grade"], "term": u["semester"],
                    "paper": "%s 测试卷" % u["chapter"], "examId": "geo_exam_%s_u%02d" % (code, ui),
                    "scope": [u["chapter"]],
                    "points": [t["id"] for t in pts_of_unit[u["id"]]],
                    "out": os.path.join(ROOT, "data", "geography-lujiao", "_exam_parts", eid + "_out.json")}
            cards.append(card)
        # 期中 A/B（前一半单元）、期末 A/B（全册）
        half = MIDN[book]
        mid_units = units[:half]
        for kind, us, names in (("mid", mid_units, ("期中测试卷A", "期中测试卷B")),
                                ("fin", units, ("期末测试卷A", "期末测试卷B"))):
            for pname in names:
                n += 1
                eid = "E%02d" % n
                suf = "mid_a" if pname.endswith("A") and kind == "mid" else \
                      "mid_b" if kind == "mid" else ("final_a" if pname.endswith("A") else "final_b")
                cards.append({"eid": eid, "kind": kind, "book": book, "grade": us[0]["grade"],
                              "term": us[0]["semester"], "paper": pname,
                              "examId": "geo_exam_%s_%s" % (code, suf),
                              "scope": [x["chapter"] for x in us],
                              "points": [t["id"] for x in us for t in pts_of_unit[x["id"]]],
                              "out": os.path.join(ROOT, "data", "geography-lujiao", "_exam_parts", eid + "_out.json")})
    for c in cards:
        json.dump(c, open(os.path.join(OUT, c["eid"] + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print("派单 %d 卷" % len(cards))
    for c in cards:
        print("  %s %-6s %-28s 点 %2d" % (c["eid"], c["kind"], c["paper"][:26], len(c["points"])))
    assert len(cards) == 39


if __name__ == "__main__":
    main()
