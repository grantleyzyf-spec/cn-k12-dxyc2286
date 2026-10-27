#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把分模块撰写稿（/tmp/it_mods/out/mK.json）装配进 information-technology 数据。

知识点口径：高中信息技术课标「内容要求」一条 = 1 个知识点（共 75 条 / 10 模块）。
quote 一律取**课标 docx 原文**（不经撰写稿转手），保证逐字回表 100%。

用法：python3 scripts/build_it_highschool.py [--write]
"""
import json, os, re, sys, zipfile

WRITE = "--write" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
S = "information-technology"
GZ = ("/Users/a627692/Desktop/中小学教材/中小学教材/2025修订课程标准/"
      "普通高中课程方案及20科课程标准（2017年版2020年修订)/11.普通高中信息技术课程标准（2017年版2020年修订）.docx")
MODS = "/tmp/it_mods"

MODCODES = ["BX1", "BX2", "XX1", "XX2", "XX3", "XX4", "XX5", "XX6", "XU1", "XU2"]

META = [
    ("必修第一册 数据与计算", 10, "上", ["数据与信息", "数据处理与应用", "算法与程序实现"]),
    ("必修第二册 信息系统与社会", 10, "下", ["信息社会特征", "信息系统组成与应用", "信息安全与信息社会责任"]),
    ("选择性必修第一册 数据与数据结构", 11, "上", ["数据及其价值", "数据结构", "数据结构应用"]),
    ("选择性必修第二册 网络基础", 11, "下", ["网络基本概念", "网络协议与安全", "物联网"]),
    ("选择性必修第三册 数据管理与分析", 11, "下", ["数据需求分析", "数据管理", "数据分析"]),
    ("选择性必修第四册 人工智能初步", 12, "上", ["人工智能基础", "简单人工智能应用模块开发", "人工智能技术的发展与应用"]),
    ("选择性必修第五册 三维设计与创意", 12, "上", ["三维设计对社会的影响", "三维作品设计与创意", "三维作品发布"]),
    ("选择性必修第六册 开源硬件项目设计", 12, "下", ["开源硬件的特征", "开源硬件项目流程", "基于开源硬件的作品设计与制作"]),
    ("选修 算法初步", 12, "下", ["算法基础", "常见算法及程序实现", "算法应用"]),
    ("选修 移动应用设计", 12, "下", ["移动技术对社会的影响", "移动应用功能设计与开发", "移动应用中的信息安全"]),
]
# 跨模块承接（soft）：(前置 模块号, 前置 code, 后置 模块号, 后置 code)
CROSS = [(0, "1.1", 2, "1.1"), (0, "1.4", 4, "3.1"), (0, "1.6", 8, "1.1"), (0, "1.8", 5, "4.1"),
         (1, "2.4", 3, "2.1"), (1, "2.5", 9, "2.1")]

PROC = re.compile(r"(编程|程序|开发|搭建|调试|制作|设计|发布)")
norm = lambda s: re.sub(r"\s+", "", s or "")
han = lambda s: len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def gz_items():
    """从课标 docx 抽 10 个【内容要求】块 → [[(code, body), ...], ...]

    课标 docx 里偶有正文被页眉切断（如 6.6「…实现」+ 页眉 +「作品的各种功能模块。」），
    故遇到不以编号/【 开头的续行要并回上一条，并丢掉重复的页眉行。
    """
    with zipfile.ZipFile(GZ) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    paras = [re.sub(r"<[^>]+>", "", p) for p in re.split(r"</w:p>", xml)]
    paras = [p.strip() for p in paras if p.strip()]
    blocks, i = [], 0
    while i < len(paras):
        if paras[i].startswith("【内容要求】"):
            j, items = i + 1, []
            while j < len(paras) and not paras[j].startswith("【"):
                line = paras[j]
                m = re.match(r"^(\d+\.\d+)\s*(.*)$", line)
                if m:
                    items.append([m.group(1), m.group(2).strip()])
                elif items and not re.match(r"^【", line) and not re.match(r"^普通高中信息技术课程标准", line) \
                        and not re.match(r"^[│|]", line):
                    items[-1][1] += line          # 被页眉切断的续行，并回上一条
                j += 1
            blocks.append([(c, b) for c, b in items])
            i = j
        else:
            i += 1
    return blocks[:10]


src_items = gz_items()
assert len(src_items) == 10 and all(len(b) > 0 for b in src_items), [len(b) for b in src_items]

topics, questions, deps = [], [], []
problems = []
code2tid = {}

ti = qi = 0
for k, (chap, grade, sem, parts) in enumerate(META):
    fp = f"{MODS}/out/m{k}.json"
    if not os.path.exists(fp):
        problems.append(f"缺 {fp}")
        continue
    data = json.load(open(fp, encoding="utf-8"))
    got = data.get("topics", [])
    want = src_items[k]
    if len(got) != len(want):
        problems.append(f"m{k} 条目数 {len(got)} ≠ 课标 {len(want)}")
    for (code, body), tp in zip(want, got):
        if tp.get("code") != code:
            problems.append(f"m{k} 编号错位：撰写稿 {tp.get('code')} ≠ 课标 {code}")
            continue
        ti += 1
        tid = "it_h%03d" % ti
        code2tid[(k, code)] = tid
        q = tp.get("question") or {}
        if han(tp.get("name")) > 20:
            problems.append(f"{tid} name 过长 {han(tp.get('name'))}")
        if not (40 <= han(tp.get("description")) <= 90):
            problems.append(f"{tid} description {han(tp.get('description'))} 汉字（要求 40-90）")
        if not (1 <= len(tp.get("mastery_criteria") or []) <= 3):
            problems.append(f"{tid} mastery_criteria 条数异常")
        opts = q.get("options") or []
        if len(opts) != 4 or q.get("answer") not in [o.get("label") for o in opts]:
            problems.append(f"{tid} 选择题不合规")
        if q.get("difficulty") not in ("basic", "standard", "hard"):
            problems.append(f"{tid} difficulty={q.get('difficulty')}")
        if han(q.get("explanation")) < 30:
            problems.append(f"{tid} explanation {han(q.get('explanation'))} 汉字(<30)")
        if tp.get("domain") not in parts:
            problems.append(f"{tid} domain={tp.get('domain')} 不在 {parts}")
        ttype = "procedural" if PROC.search(tp.get("name", "")) else "conceptual"
        topics.append({
            "id": tid, "name": tp["name"], "subject": S,
            "domain": tp.get("domain") or parts[0], "grade": grade, "semester": sem,
            "chapter": chap, "type": ttype,
            "description": tp["description"],
            "mastery_criteria": tp.get("mastery_criteria") or [tp["description"]],
            "diagnostic_question": {"question": q.get("prompt", ""), "answer": q.get("answer", "")},
            "external": False,
            "standards": [{"id": "ith-2017:%s-%s" % (MODCODES[k], code), "confidence": "exact",
                           "quote": body, "sourceLine": 0}],
            "tags": [tp.get("domain") or parts[0], chap.split(" ")[0]],
            "prerequisites": [],
            "curriculumRef": "ith-2017:%s-%s" % (MODCODES[k], code),
            "verified": True,
        })
        qi += 1
        questions.append({
            "id": "it_hq%03d" % qi, "topicId": tid,
            "prompt": q.get("prompt", ""), "question": q.get("prompt", ""),
            "options": opts, "answer": q.get("answer", ""), "type": "choice",
            "difficulty": q.get("difficulty", "standard"), "explanation": q.get("explanation", ""),
        })
        for pc in tp.get("prereq_codes") or []:
            deps.append({"from": code2tid.get((k, pc), ""), "to": tid, "type": "hard"})

# 模块内前置解析（写入 prerequisites，跳过解析失败的）
dep_out = []
bytid = {t["id"]: t for t in topics}
for e in deps:
    if not e["from"]:
        continue
    bytid[e["to"]]["prerequisites"].append(e["from"])
    dep_out.append(e)

# 跨模块承接 soft 边
for (pk, pc, nk, nc) in CROSS:
    a, b = code2tid.get((pk, pc)), code2tid.get((nk, nc))
    if a and b and a not in bytid[b]["prerequisites"]:
        bytid[b]["prerequisites"].append(a)
        dep_out.append({"from": a, "to": b, "type": "soft"})

# 根节点 reason（模块首条 + 模块内另起一条内容主线的节点）
for k, (chap, grade, sem, parts) in enumerate(META):
    for t in topics:
        if t["chapter"] == chap and not t["prerequisites"] and not t.get("root_reason"):
            first = code2tid.get((k, src_items[k][0][0])) if k < len(src_items) else None
            t["root_reason"] = (
                ("起始知识点：%s 首条内容要求，高中信息技术课标该模块的入门节点；跨学段（义教信息科技）前置不单独连边"
                 % chap) if t["id"] == first else
                ("主线起点：%s「%s」部分的首个节点，课标该部分自成一脉，模块内无更早前置"
                 % (chap, t.get("domain") or parts[0])))

print("装配：知识点 %d / 题 %d / 边 %d（soft %d）"
      % (len(topics), len(questions), len(dep_out), sum(1 for e in dep_out if e["type"] == "soft")))
from collections import Counter
print("grade:", dict(sorted(Counter(t["grade"] for t in topics).items())))
print("难度:", dict(Counter(q["difficulty"] for q in questions)))
print("题型:", dict(Counter(t["type"] for t in topics)))
print("根节点:", [(t["id"], t["chapter"]) for t in topics
                if not t["prerequisites"] and not t.get("root_reason")])
if problems:
    print("问题 %d 条：" % len(problems))
    for p in problems[:40]:
        print("  -", p)
else:
    print("校验：撰写稿全部合规 ✅")

if WRITE and not problems:
    tp = os.path.join(D, S, "topics.json")
    qp = os.path.join(D, S, "questions.json")
    dp = os.path.join(D, S, "dependencies.json")
    old_t = json.load(open(tp, encoding="utf-8"))
    old_q = json.load(open(qp, encoding="utf-8"))
    old_d = json.load(open(dp, encoding="utf-8"))
    keep_t = [t for t in old_t if not t["id"].startswith("it_h")]
    keep_q = [q for q in old_q if not q["topicId"].startswith("it_h")]
    keep_d = [e for e in old_d if not (e["from"].startswith("it_h") or e["to"].startswith("it_h"))]
    json.dump(keep_t + topics, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(keep_q + questions, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(keep_d + dep_out, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written:", tp, qp, dp)
elif problems:
    print("⛔ 有不合规项，未写盘")
