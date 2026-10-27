# -*- coding: utf-8 -*-
"""艺术（美术，art）学科不变量测试。用法: python3 scripts/test_art.py

28 项不变量：规模 / 唯一 / subject / 课标可解析 / quote 逐字回表 / confidence /
先修图（无环·无重·无自环·双端存在·镜像） / 根节点 reason / 每题齐备 /
选择 4 选项且答案在选项内 / 题干长度 / 解析 / 答案分布 / 选项无占位干扰项 /
domain 属四类艺术实践 / 年级覆盖 / 课标条目无孤儿 / 题号与知识点前缀一致。

课标底本（见 scripts/ocr_art_standards.py）：
- 义务教育艺术课标为**扫描版**，回表底本是 OCR 文本 /tmp/art_yijiao_ocr.txt，
  4 处 OCR 误识登记在 OCR_FIX（把 OCR 文本改回正确字后再比）。
- 高中美术课标有文字层，TXT 为 GB18030 编码，转存为 /tmp/gaozhong_meishu.txt。
底本缺失时跳过回表（CI 同款约定，不会红）。
"""
import json
import os
import re
import sys

SUBJECT = "art"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

YIJIAO_OCR = "/tmp/art_yijiao_ocr.txt"
GAOZHONG_TXT = "/tmp/gaozhong_meishu.txt"

# 义教扫描件 OCR 误识 → 正确字（登记项；只要新增一条就必须同步写进 docs/art.md）
OCR_FIX = {
    "折和县揉搓压": "折剪揉搓压",          # 1.T2.04「折、剪、揉、搓、压」
    "书法繁刻": "书法篆刻",                # 2.T1.01
    "运用线条有形状": "运用线条形状",        # 4.T1.04（OCR 多出一字）
    "形式原理汰析": "形式原理分析",          # 4.T1.04
    "情况感情继承": "情况感悟继承",          # 4.T4.01
}

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + ("：" + str(detail) if detail else ""))


def norm(s):
    """回表归一：只保留汉字与字母数字（去空白与全部标点，含 PDF 抽取产生的杂符）。"""
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s or "")


def read_text(path):
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8", errors="ignore").read()
    if txt.count("美术") < 10:  # 万一拿到的是乱码底本
        txt = open(path, "rb").read().decode("gb18030", errors="ignore")
    return txt


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids],
   sorted({s["id"] for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids})[:3])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))

yj, gz = read_text(YIJIAO_OCR), read_text(GAOZHONG_TXT)
if yj and gz:
    src_y = norm(yj)
    for bad, good in OCR_FIX.items():
        src_y = src_y.replace(bad, good)
    src_g = norm(gz)
    miss = []
    for t in topics:
        for s in t.get("standards", []):
            q = norm(s.get("quote"))
            src = src_g if s["id"].startswith("art-2017") else src_y
            if q not in src:
                miss.append((t["id"], s["id"], s["quote"][:16]))
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺 OCR/TXT 底本，跳过；跑 scripts/ocr_art_standards.py 可补齐）", True, None))

pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])],
   [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])][:3])
ck("prerequisites 都在 topics",
   not [(p, t["id"]) for t in topics for p in t.get("prerequisites", []) if p not in T])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")])
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T),
   [tid for tid in T if not any(q.get("topicId") == tid for q in qs)])
ck("题号与知识点前缀一致", all(q["id"].startswith("art_q") for q in qs))

ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("难度三档都有", len({q.get("difficulty") for q in qs}) == 3, sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [(q["id"], len(q.get("prompt", ""))) for q in qs if len(q.get("prompt", "")) < 12][:3])
ck("每题解析 ≥10 字", all(len(q.get("explanation", "")) >= 10 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 10][:3])
ck("prompt 与 question 同值", all(q.get("question") == q.get("prompt") for q in qs),
   [q["id"] for q in qs if q.get("question") != q.get("prompt")][:3])
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))

# —— 艺术学科专属：答案分布、干扰项质量、领域口径、年级覆盖、课标孤儿 ——
dist = {k: sum(1 for q in qs if q.get("answer") == k) for k in "ABCD"}
ck("答案分布不单一（≥3 个标签，单标签 ≤50%）",
   sum(1 for v in dist.values() if v) >= 3 and max(dist.values()) <= len(qs) * 0.5, dist)

PLACEHOLDER = ("仅在大学", "不属于美术", "无关", "不知道", "以上都不是", "...", "…")
bad_opt = [(q["id"], o["text"]) for q in qs for o in q.get("options") or []
           if any(p in o["text"] for p in PLACEHOLDER) or len(o["text"]) < 2]
ck("选项无占位/玩笑干扰项、无截断省略号", not bad_opt, bad_opt[:3])

DOMAINS = ("造型表现", "设计应用", "欣赏评述", "综合探索")
ck("domain 属课标四类艺术实践", all(t.get("domain") in DOMAINS for t in topics),
   sorted({t.get("domain") for t in topics} - set(DOMAINS)))
ck("年级覆盖 1–12 全学段", {t.get("grade") for t in topics} == set(range(1, 13)),
   sorted(set(range(1, 13)) - {t.get("grade") for t in topics}))
ck("课标条目每条至少挂 1 个知识点", idx["subjects"][SUBJECT]["entries"]
   and all(e.get("topicCount", 0) >= 1 for e in idx["subjects"][SUBJECT]["entries"]))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics),
   [t["id"] for t in topics if not all(t.get(k) for k in need)][:3])
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
