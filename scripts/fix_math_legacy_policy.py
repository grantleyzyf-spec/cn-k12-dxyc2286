# -*- coding: utf-8 -*-
"""执行口径：新版同册目录没有、且该册全文关键词 0 命中的旧单元 ⇒
按「旧版延伸内容」保留，标签写「旧版·新版未设」，册次照旧。

做法：
  ① chapter 由 `<册> 附：<名>（新版教材未设独立单元，待核）`
     改为 `<册> 附：<名>（旧版延伸内容·新版未设）`（册次 grade/semester 不动）
  ② 该点 tags 第 2 位插入「旧版·新版未设」（首位仍是课标领域，保持既有不变量）
  ③ description 末尾补一句说明（幂等）

依据（本机新版 PDF 全文检索，均 0 命中）：
  一下「找规律」、二上「搭配」、二下「推理」、四上「数学广角（优化）」、
  四上「除数是两位数的除法（含试商）」、六上「比（意义/基本性质/按比分配）」、五上「简易方程」

用法：python3 apply_legacy_policy.py [--write]
"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/math/topics.json"
WRITE = "--write" in sys.argv
TAG = "旧版·新版未设"
NOTE = "（旧版延伸内容：新版教材同册目录未设该单元、该册全文关键词 0 命中；册次照旧，等缺失的新版教材到齐再判是否后移）"

CLEAN = re.compile(r"（新版教材未设独立单元[^）]*）|（旧版延伸内容·新版未设）")


topics = json.load(open(TP, encoding="utf-8"))
changed = 0
for t in topics:
    if "附：" not in t["chapter"]:
        continue
    new = CLEAN.sub("", t["chapter"]).rstrip() + "（旧版延伸内容·新版未设）"
    if new != t["chapter"]:
        t["chapter"] = new
        changed += 1
    tags = t.get("tags") or []
    if TAG not in tags:
        tags.insert(min(1, len(tags)), TAG)
        t["tags"] = tags
    if NOTE not in t["description"]:
        t["description"] = t["description"].rstrip("。") + "。" + NOTE

print(f"改 chapter 并打标 {changed} 条；带「附：」知识共 "
      f"{sum(1 for t in topics if '附：' in t['chapter'])} 个")
for c in sorted({t["chapter"] for t in topics if "附：" in t["chapter"]}):
    pts = [t["name"] for t in topics if t["chapter"] == c]
    print(f"   · {c} → {len(pts)} 点：{'、'.join(pts)}")

if WRITE:
    with open(TP, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("✅ 已写入", TP)
