#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版初中化学桶（chemistry-kepu）建库：结构 → _structure.json ＋ topics/dependencies/_skeleton。

结构源：**大单元 docx 的「（N）第K课时 <名>」标题**（10 个单元 docx，九年级上下册），
        比 PDF 目录更细，直接给到课时级；已由 /tmp/chem_kepu_units.json 抽取（见 scripts/probe_chem_kepu_docx.py）。
课标：借 `data/_chem_std_pool.json` 的 che-2022（义教 2022）条目，quote 逐字不动，只挂 confidence。
字段形状与 chemistry-sujiao / chemistry-lujiao 完全同构（同 build_chem_editions.build）。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-kepu")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

POOL = json.load(open(os.path.join(ROOT, "data", "_chem_std_pool.json"), encoding="utf-8"))
PREFIX, SUBJECT = "ckp", "chemistry-kepu"
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

# 内容域（义教化学课标五域：物质的性质与应用 / 物质的组成与结构 / 物质的化学变化 /
#         科学探究与化学实验 / 化学与社会·跨学科实践）
DOMAIN_RULES = [
    ("化学与社会·跨学科实践", r"生活|社会|健康|营养|环境|材料|能源|资源|跨学科|湿地|社区"),
    ("科学探究与化学实验", r"实验|探究|仪器|操作|测量|制取|检验|观察|方法|安全"),
    ("物质的组成与结构", r"构成|微粒|分子|原子|离子|元素|化学式|化合价|相对|结构|模型"),
    ("物质的化学变化", r"反应|燃烧|条件|质量守恒|方程式|速率|能量|变化|氧化|还原|催化|配平"),
    ("物质的性质与应用", r"空气|氧气|水|溶液|碳|金属|酸碱|盐|性质|用途|材料|燃料|化肥"),
]
# 单元 → 义教课标学习主题号（1 科学探究与化学实验 / 2 物质的性质与应用 /
# 3 物质的组成与结构 / 4 物质的化学变化 / 5 化学与社会·跨学科实践）
UNIT_THEME = {
    "走进化学世界": 1, "探析空气之谜": 2, "初探物质构成": 3, "再探燃烧与燃料": 4,
    "表征化学反应": 4, "探秘碳的世界": 2, "探究水和溶液": 2, "再识金属与金属材料": 2,
    "认识酸、碱和盐": 2, "体悟化学与生活、社会": 5,
}
ITEMS = json.load(open(os.path.join(ROOT, "data", "_chem2022_items.json"), encoding="utf-8"))


def pick_std(name, unit_name=""):
    """在**同一学习主题**的课标条目里，按「课时名 + 单元名」与条目标题/正文的字符重合度取值。

    只从已抽取的 31 条 che-2022 条目里取，quote 逐字可回表；同主题内取不到高分时
    退到本主题第一条（保证语义仍在同一学习主题内，不跨主题乱挂）。
    """
    theme = UNIT_THEME.get(unit_name, 0)
    cand = [x for x in ITEMS if x["theme"] == theme] or ITEMS
    probe = set(name) | set(unit_name)

    def sc(x):
        return 2 * len(probe & set(x["title"])) + len(probe & set(x["quote"][:120]))

    ranked = sorted(cand, key=sc, reverse=True)
    best = ranked[0]
    out = [{"id": best["id"], "confidence": "partial" if sc(best) >= 8 else "inferred",
            "quote": best["quote"], "sourceLine": best["sourceLine"]}]
    if len(ranked) > 1 and sc(ranked[1]) >= 8:
        second = ranked[1]
        out.append({"id": second["id"], "confidence": "partial",
                    "quote": second["quote"], "sourceLine": second["sourceLine"]})
    return out


def domain_of(name):
    for d, pat in DOMAIN_RULES:
        if re.search(pat, name):
            return d
    return "物质的性质与应用"


def main(write=False):
    src = json.load(open("/tmp/chem_kepu_units.json", encoding="utf-8"))
    struct = {"九年级上册": [], "九年级下册": []}
    for o in src:
        struct[o["book"]].append({
            "no": CN.get(o["unit"], 0) if not str(o["unit"]).isdigit() else int(o["unit"]),
            "name": o["unitName"],
            "lessons": sorted([{"no": l["no"], "name": l["name"]} for l in o["lessons"]], key=lambda x: x["no"]),
        })
    for b in struct:
        struct[b].sort(key=lambda x: x["no"])

    topics, deps, skeleton = [], [], []
    uid = lid = 0
    prev = None
    for book, grade, sem in (("九年级上册", 9, "上"), ("九年级下册", 9, "下")):
        sk = {"book": book, "grade": grade, "semester": sem, "units": []}
        for u in struct[book]:
            uid += 1
            unit_id = "%s_u%03d" % (PREFIX, uid)
            dom = domain_of(u["name"])
            chapter = "%s 第%d单元 %s" % (book, u["no"], u["name"])
            topics.append({
                "id": unit_id, "name": u["name"], "subject": SUBJECT, "domain": dom,
                "grade": grade, "semester": sem, "chapter": chapter, "level": "unit",
                "type": "conceptual",
                "description": "%s第%d单元围绕「%s」组织，含 %d 个课时，覆盖%s领域的主要概念、实验与思维方法。"
                               % (book, u["no"], u["name"], len(u["lessons"]), dom),
                "mastery_criteria": ["能说出「%s」的主线与各课时之间的关系" % u["name"],
                                     "能综合运用本单元知识解释一个真实情境中的化学问题"],
                "diagnostic_question": {"question": "本单元《%s》的核心内容是？" % u["name"], "answer": "B"},
                "tags": [dom, u["name"]], "standards": pick_std(u["name"], u["name"]),
                "prerequisites": [], "root_reason": "单元上位点，不设先修", "verified": False,
            })
            sk["units"].append({"no": u["no"], "name": u["name"], "unitId": unit_id,
                                "lessons": [l["name"] for l in u["lessons"]]})
            for l in u["lessons"]:
                lid += 1
                tid = "%s_j%03d" % (PREFIX, lid)
                ldom = domain_of(l["name"]) if domain_of(l["name"]) != "物质的性质与应用" else dom
                st = pick_std(l["name"], u["name"])
                topics.append({
                    "id": tid, "name": l["name"], "subject": SUBJECT, "domain": ldom,
                    "grade": grade, "semester": sem,
                    "chapter": "%s · %s" % (chapter, l["name"]), "level": "lesson",
                    "type": "procedural" if re.search(r"实验|探究|测定|制取|检验|配制|计算", l["name"]) else "conceptual",
                    "description": "本课时学习「%s」，属%s，侧重%s领域的核心知识与方法。" % (l["name"], chapter, ldom),
                    "mastery_criteria": ["能说出「%s」的基本内容与关键实验现象" % l["name"],
                                          "能在新情境中运用本课时方法解释或解决一个问题"],
                    "diagnostic_question": {"question": "关于「%s」，下列说法正确的是？" % l["name"], "answer": "B"},
                    "tags": [ldom, l["name"]], "standards": st,
                    "prerequisites": [prev] if prev else [], "prereqUpper": [unit_id], "verified": False,
                })
                if prev:
                    deps.append({"from": prev, "to": tid, "type": "hard"})
                else:
                    topics[-1]["root_reason"] = "本教材第一节，作为先修链起点"
                prev = tid
        skeleton.append(sk)

    n_u = sum(1 for t in topics if t["level"] == "unit")
    n_l = sum(1 for t in topics if t["level"] == "lesson")
    st = sum(1 for t in topics if t["standards"])
    near = sum(1 for t in topics for s in t["standards"] if s["confidence"] == "inferred")
    print("%s：单元 %d ＋ 课时 %d ＝ %d 点｜边 %d｜挂课标 %d（%.0f%%）｜其中 inferred %d"
          % (SUBJECT, n_u, n_l, len(topics), len(deps), st, 100.0 * st / len(topics), near))
    from collections import Counter
    print("领域", dict(Counter(t["domain"] for t in topics)), "｜类型", dict(Counter(t["type"] for t in topics)))
    if write:
        os.makedirs(D, exist_ok=True)
        json.dump(struct, open(os.path.join(D, "_structure.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(skeleton, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写入 _structure.json / topics.json / dependencies.json / _skeleton.json")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
