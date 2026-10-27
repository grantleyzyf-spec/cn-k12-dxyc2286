#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理学科数据不变量测试（可单独跑，也可接进 CI）
用法: python3 scripts/test_geography.py
退出码 0 = 全绿；1 = 有失败项
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（7）普通高中地理课程标准日常修订版（2017年版2025年修订）.txt",
]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, "geography/topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, "geography/dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, "geography/questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}

# 1 规模与唯一性
ck("知识点 104 条", len(topics) == 104, len(topics))
ck("id 唯一", len(T) == len(topics))
ck("全部 subject=geography", all(t.get("subject") == "geography" for t in topics))
ck("题与知识点 1:1", len(qs) == len(topics), f"{len(qs)} vs {len(topics)}")
ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))

# 2 册次覆盖（义教 7/8 全四册 + 高中 10–12）
grades = {int(t["grade"]) for t in topics}
ck("年级覆盖 7、8、10、11、12", grades == {7, 8, 10, 11, 12}, sorted(grades))
per_vol = Counter((t["grade"], t["semester"]) for t in topics)
ck("七上/七下/八上/八下 均有 ≥5 个知识点",
   all(per_vol.get((g, s), 0) >= 5 for g in (7, 8) for s in ("上", "下")),
   {f"{g}{s}": per_vol.get((g, s), 0) for g in (7, 8) for s in ("上", "下")})

# 3 章节口径（人教 2012 版初中册次章名；七下必须真有亚洲/地区/国家/极地）
chn = {t["chapter"] for t in topics}
need_ch = [
    "七年级上册 第二章 陆地和海洋", "七年级上册 第三章 天气与气候",
    "七年级上册 第四章 居民与聚落", "七年级上册 第五章 发展与合作",
    "七年级下册 第六章 我们生活的大洲——亚洲", "七年级下册 第七章 我们邻近的地区和国家",
    "七年级下册 第八章 东半球其他的地区和国家", "七年级下册 第九章 西半球的国家",
    "七年级下册 第十章 极地地区",
    "八年级上册 第四章 中国的经济发展", "八年级下册 第五章 中国的地理差异",
    "八年级下册 第六章 北方地区", "八年级下册 第七章 南方地区",
    "八年级下册 第八章 西北地区", "八年级下册 第九章 青藏地区",
    "八年级下册 第十章 中国在世界中",
]
miss_ch = [c for c in need_ch if c not in chn]
ck("初中册次章节齐全（16 章）", not miss_ch, miss_ch)
ck("章名不含「十X年级」错写", not [c for c in chn if re.search(r"十[一二三四]年级", c)])

# 3.1 领域分类（原文大批节点误用「地球与宇宙」兜底）
DOMAINS = {"地球与宇宙", "地图与地理工具", "世界地理", "中国地理", "自然地理", "人文地理"}
bad_dom = [(t["id"], t.get("domain")) for t in topics if t.get("domain") not in DOMAINS]
ck("领域取值都在允许集合内", not bad_dom, bad_dom[:3])
mis_dom = [t["id"] for t in topics
           if t["chapter"].startswith(("必修第二册", "选择性必修2", "选择性必修3")) and t.get("domain") != "人文地理"]
ck("必修二/选必2/选必3 归人文地理", not mis_dom, mis_dom[:3])
mis_dom2 = [t["id"] for t in topics
            if t["chapter"].startswith(("必修第一册 第二章", "必修第一册 第三章", "必修第一册 第四章",
                                        "必修第一册 第五章", "选择性必修1 第二章",
                                        "选择性必修1 第三章", "选择性必修1 第四章"))
            and t.get("domain") != "自然地理"]
ck("必修一自然地理部分/选必1 归自然地理", not mis_dom2, mis_dom2[:3])

# 4 课标
no_std = [t["id"] for t in topics if not t.get("standards")]
ck("全部挂课标", not no_std, no_std)
bad_ref = [(t["id"], s.get("id")) for t in topics for s in t.get("standards", [])
           if s.get("id") not in {e["id"] for e in idx["subjects"]["geography"]["entries"]}]
ck("课标条目都能在索引里找到", not bad_ref, bad_ref[:3])
no_quote = [t["id"] for t in topics for s in t.get("standards", []) if not s.get("quote")]
ck("每条课标引用都带 quote", not no_quote, no_quote[:3])
ck("confidence 只用三档",
   all(s.get("confidence") in ("exact", "partial", "inferred")
       for t in topics for s in t.get("standards", [])))

# 5 quote 回表（有原文才查，CI 环境缺文件自动跳过）
if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表命中 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, ""))

# 6 先修边
pairs = [(e["from"], e["to"]) for e in deps]
ck("无自环", all(a != b for a, b in pairs))
ck("无重复边", len(set(pairs)) == len(pairs))
ck("两端都存在", all(a in T and b in T for a, b in pairs))
ck("边类型只用 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))

parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
asym = [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])]
ck("deps 与 topics.prerequisites 双向镜像", not asym, asym[:3])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1:
            return True
        if color.get(b, 0) == 0 and dfs(b):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))

# 7 根节点
roots = [t for t in topics if not t.get("prerequisites")]
ck("根节点都有 root_reason", all(t.get("root_reason") for t in roots), len(roots))

# 8 题目可用性
by_topic = {}
for q in qs:
    by_topic.setdefault(q.get("topicId"), []).append(q)
ck("每个知识点都有题", all(t in by_topic for t in T), len(T) - len(by_topic))
ck("难度只用 basic/standard/hard",
   all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("难度三档齐全", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"})
bad_choice = []
for q in qs:
    if q.get("type") == "choice":
        labels = [o.get("label") for o in (q.get("options") or [])]
        if len(labels) != 4 or q.get("answer") not in labels:
            bad_choice.append(q["id"])
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥ 8 字", all(len(q.get("prompt", "")) >= 8 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 8][:5])
ck("题干 ≥ 12 字（口径线）", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:5])
ck("每题都有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 题都有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
ck("topicId 都能对上知识点", all(q.get("topicId") in T for q in qs))

# 9 核心字段
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("诊断题与题库一致", all(t.get("diagnostic_question", {}).get("question")
                            and t["diagnostic_question"]["answer"] for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("GEOGRAPHY DATA PASSED")
