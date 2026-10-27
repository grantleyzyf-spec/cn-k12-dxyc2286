#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生物学数据归一（幂等）。用法: python3 scripts/fix_biology.py [--write]

修正项：
 1) 两处缺失课标回表（bio_p040／bio_p041）：以课标「学业要求」原文回表，confidence=inferred
 2) 根节点 bio_p001 补 root_reason
 3) dependencies 去重（保留首条，硬边优先）
 4) deps → topics.prerequisites 双向镜像补齐
 5) 知识点 type 细分（conceptual/procedural/reasoning/application）
 6) 题目 difficulty 归一（easy→basic、medium→standard）并按题干关键词分三档
 7) 题干 <12 字补上下文
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "biology")
WRITE = "--write" in sys.argv

STD_QUOTE = "运用进化与适应观和生态观分析生物在形态结构和行为等方面与环境相适应的特征"
STD = {"id": "bio-2022:4.XY.05", "confidence": "inferred", "quote": STD_QUOTE, "sourceLine": 1433}
ROOT_REASON = "七年级上册开篇知识点：生物的基本特征是全部后续内容的起点，无更早先修；与小学科学「生物的特征」衔接。"


def load(n):
    return json.load(open(os.path.join(D, n), encoding="utf-8"))


def save(n, o):
    p = os.path.join(D, n)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)
        f.write("\n")


topics = load("topics.json")
deps = load("dependencies.json")
qs = load("questions.json")

log = {}

# ---- 1) 课标回表 ----
for t in topics:
    if t["id"] in ("bio_p040", "bio_p041") and not t.get("standards"):
        t["standards"] = [dict(STD)]
        t["curriculumRef"] = STD["id"]
log["课标补录"] = [t["id"] for t in topics if t.get("curriculumRef") == STD["id"]]

# ---- 2) 根节点 ----
for t in topics:
    if not t.get("prerequisites") and not t.get("root_reason"):
        t["root_reason"] = ROOT_REASON
log["root_reason"] = sum(1 for t in topics if t.get("root_reason"))

# ---- 3) 去重 ----
seen, uniq = set(), []
for e in deps:
    k = (e["from"], e["to"])
    if k in seen:
        continue
    seen.add(k)
    uniq.append({"from": e["from"], "to": e["to"], "type": e.get("type", "hard")})
for e in deps:
    k = (e["from"], e["to"])
    for u in uniq:
        if (u["from"], u["to"]) == k and e.get("type") == "hard":
            u["type"] = "hard"
log["边去重"] = len(deps) - len(uniq)
deps = uniq

# ---- 4) 镜像 ----
T = {t["id"]: t for t in topics}
mirror = 0
for e in deps:
    b = T.get(e["to"])
    if b is None:
        continue
    pre = b.setdefault("prerequisites", [])
    if e["from"] not in pre:
        pre.append(e["from"])
        mirror += 1
log["镜像补齐"] = mirror

# ---- 5) type 细分 ----
PROC = re.compile(r"实验|观察|制作|使用|测量|调查|练习|培养|解剖|探究|装片|显微镜|检索表")
REAS = re.compile(r"推理|分析|判断|规律|遗传规律|概率|论证|计算")
APPL = re.compile(r"应用|防治|育种|健康|保护|利用|生活|生产|疾病")
tc = Counter()
for t in topics:
    blob = (t["name"] + " " + t.get("description", ""))
    if PROC.search(blob):
        t["type"] = "procedural"
    elif REAS.search(blob):
        t["type"] = "reasoning"
    elif APPL.search(blob):
        t["type"] = "application"
    else:
        t["type"] = "conceptual"
    tc[t["type"]] += 1
log["知识点 type"] = dict(tc)

# ---- 6) 难度 ----
HARD = re.compile(r"分析|推理|推导|推断|为什么|原因|说明理由|设计|探究|评价|方案|解释原因")
STD_W = re.compile(r"比较|区别|过程|作用|影响|判断|描述|解释|实验|结构|功能|说明|意义")
dc = Counter()
for q in qs:
    d = q.get("difficulty")
    if d == "easy":
        d = "basic"
    elif d == "medium":
        d = "standard"
    if d not in ("basic", "standard", "hard"):
        d = "basic"
    p = q.get("prompt", "")
    if HARD.search(p):
        d = "hard"
    elif STD_W.search(p) or len(p) >= 16:
        d = "standard"
    else:
        d = "basic"
    q["difficulty"] = d
    dc[d] += 1
log["题目难度"] = dict(dc)

# ---- 7) 题干补上下文（<12 字）----
fill = 0
for q in qs:
    p = q.get("prompt", "")
    if len(p) < 12:
        tail = "请选出正确的一项。"
        if p.endswith(("？", "?")):
            q["prompt"] = p + tail
        elif p.endswith(("。", "．", ".")):
            q["prompt"] = p + tail
        else:
            q["prompt"] = p + "？" + tail
        fill += 1
log["题干补上下文"] = fill

print(json.dumps(log, ensure_ascii=False, indent=1))
if WRITE:
    save("topics.json", topics)
    save("dependencies.json", deps)
    save("questions.json", qs)
    print("\n✅ 已写入 data/biology/{topics,dependencies,questions}.json")
else:
    print("\n（dry-run，未写盘；加 --write 生效）")
