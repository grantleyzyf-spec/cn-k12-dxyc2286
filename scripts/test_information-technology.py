#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""信息科技 / 信息技术学科不变量测试（义教 3–9 年级 + 高中 10–12 年级册次）。

用法：python3 scripts/test_information-technology.py
课标原文不在（CI 环境）时，对应学段的「quote 逐字回表」自动跳过，其余 25 项照跑。
课标来源：
  义教 —— 《义务教育信息科技课程标准·日常修订版》(2022年版2025年修订).txt（本地有空格目录）
  高中 —— 《普通高中信息技术课程标准（2017年版2020年修订）》.docx（stdlib 解压读 XML，不依赖 python-docx）
"""
import json, os, re, sys, zipfile

SUBJECT = "information-technology"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

YJ_TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/9.《义务教育信息科技课程标准·日常修订版》(2022年版2025年修订).txt"
GZ_DOCX = "/Users/a627692/Desktop/中小学教材/中小学教材/2025修订课程标准/普通高中课程方案及20科课程标准（2017年版2020年修订)/11.普通高中信息技术课程标准（2017年版2020年修订）.docx"

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def src_yj():
    if not os.path.exists(YJ_TXT):
        return None
    return norm(open(YJ_TXT, encoding="utf-8", errors="ignore").read())


def src_gz():
    if not os.path.exists(GZ_DOCX):
        return None
    try:
        with zipfile.ZipFile(GZ_DOCX) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        txt = re.sub(r"<[^>]+>", "", xml)
        # 课标页眉会切断正文（6.6「…实现」+页眉+「作品的各种功能模块。」），去掉页眉再比对
        txt = txt.replace("普通高中信息技术课程标准（2017年版2020年修订）", "")
        return norm(txt)
    except Exception:
        return None


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

# ---------- 结构 ----------
ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("题量 ≥ 知识点数", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档",
   all(s.get("confidence") in ("exact", "partial", "inferred") for t in topics for s in t.get("standards", [])))

# ---------- 课标回表（按学段分源） ----------
yj, gz = src_yj(), src_gz()
if yj is None and gz is None:
    checks.append(("quote 回表（缺课标原文，跳过）", True, None))
else:
    miss = []
    for t in topics:
        for s in t.get("standards", []):
            q = s.get("quote")
            if not q:
                continue
            sid = s.get("id", "")
            src = gz if sid.startswith("ith-") else yj
            if src is None:
                continue                      # 该学段原文缺失，跳过该条
            if norm(q) not in src:
                miss.append((t["id"], sid, q[:14]))
    ck("quote 逐字回表 100%", not miss, miss[:3])

# ---------- 图 ----------
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


sys.setrecursionlimit(10000)
ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))

# ---------- 题库 ----------
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("难度三档齐备", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"},
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥8 字", all(len(q.get("prompt", "")) >= 8 for q in qs))
ck("每题有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))

# ---------- 字段 / 掌握标准 ----------
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("知识点名 ≤20 汉字", all(han(t.get("name")) <= 20 for t in topics),
   [(t["id"], han(t.get("name"))) for t in topics if han(t.get("name")) > 20][:5])

# ---------- 学段/册次口径 ----------
yj_topics = [t for t in topics if int(t["grade"]) <= 9]
gz_topics = [t for t in topics if int(t["grade"]) >= 10]
ck("义教 3–9 年级均有知识点", {int(t["grade"]) for t in yj_topics} >= {3, 4, 5, 6, 7, 8, 9},
   sorted({int(t["grade"]) for t in yj_topics}))
ck("高中 10–12 册次均有知识点", {int(t["grade"]) for t in gz_topics} == {10, 11, 12},
   sorted({int(t["grade"]) for t in gz_topics}))
BOOK = re.compile(r"^(选择性必修|必修)(第?[一二三四五六七八九十]册|上册|下册|中册)\b|^选修\b")
bad_book = [t["id"] for t in gz_topics if not BOOK.match(t.get("chapter") or "")]
ck("高中册名可从 chapter 派生", not bad_book, bad_book[:5])
ck("义教章节以「X年级上/下册」开头",
   all(re.match(r"^[一二三四五六七八九]年级[上下]册", t.get("chapter") or "") for t in yj_topics),
   [t["chapter"] for t in yj_topics if not re.match(r"^[一二三四五六七八九]年级[上下]册", t.get("chapter") or "")][:3])
ck("高中章节与 grade 对应（10 必修 / 11–12 选必或选修）",
   all((int(t["grade"]) == 10) == (t["chapter"].startswith("必修")) for t in gz_topics),
   [(t["id"], t["grade"], t["chapter"][:8]) for t in gz_topics
    if (int(t["grade"]) == 10) != (t["chapter"].startswith("必修"))][:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过  （义教 {len(yj_topics)} 点 / 高中 {len(gz_topics)} 点）")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
