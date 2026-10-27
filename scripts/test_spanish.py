# -*- coding: utf-8 -*-
"""西班牙语学科不变量自检（收口用）。用法: python3 scripts/test_spanish.py

口径（与 docs/spanish.md 一致）：
- grade 1–9 = 义教年级（七/八/九年级）；10–16 = 高中册次（必修四第一~三册=10/11/12，选必第一~四册=13/14/15/16）
- 册名一律从 chapter 前缀派生；chapter = "<册名> Unidad N <教材单元标题>"
- 课标权威源 = 必修Ⅰ~Ⅳ/选择性必修/选修（《普通高中西班牙语课程标准（2017年版2020年修订）》）
  本库把义教七/八/九年级分别对齐必修Ⅰ/Ⅱ/Ⅲ（1/2/3级），高中必修Ⅳ=4级，选必=5级
- 每条 quote 必须与 data/spanish-standards-entries.json 的目录条目逐字一致（课标 PDF 不在时也能校验）
"""
import json, os, re, sys

SUBJECT = "spanish"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

VOLUMES = {   # 册名 -> (grade, semester, 课标 level)
    "七年级上册": (7, "上", 1), "七年级下册": (7, "下", 1),
    "八年级上册": (8, "上", 2), "八年级下册": (8, "下", 2),
    "九年级上册": (9, "上", 3),
    "必修四第一册": (10, "上", 4), "必修四第二册": (11, "上", 4), "必修四第三册": (12, "上", 4),
    "选择性必修第一册": (13, "上", 5), "选择性必修第二册": (14, "上", 5),
    "选择性必修第三册": (15, "上", 5), "选择性必修第四册": (16, "上", 5),
}
DOMAINS = {"语音", "词汇", "语法", "交际", "文化", "读写"}
TYPES = {"conceptual", "procedural", "reasoning", "modeling", "application"}
fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


topics = load(os.path.join(D, SUBJECT, "topics.json"))
deps = load(os.path.join(D, SUBJECT, "dependencies.json"))
qs = load(os.path.join(D, SUBJECT, "questions.json"))
idx = load(os.path.join(D, "cn-curriculum-standards.json"))
cat = load(os.path.join(D, "spanish-standards-entries.json"))["entries"]
CQ = {e["id"]: e for e in cat}
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

ck("id 唯一", len(T) == len(topics))
ck("规模 ≥ 100 知识点", len(topics) >= 100, len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("id 段位（义教 p / 高中 h）",
   all(re.match(r"^spa_[ph]\d{3}$", t["id"]) and
       (t["id"].startswith("spa_p") == (t["grade"] <= 9)) for t in topics))
ck("册次集合完整（12 册）", {vol_of for vol_of in
   [((t.get("chapter") or "").split(" ")[0]) for t in topics]} == set(VOLUMES),
   sorted({((t.get("chapter") or "").split(" ")[0]) for t in topics} - set(VOLUMES)))
ck("chapter 前缀册名合法", all((t.get("chapter") or "").split(" ")[0] in VOLUMES for t in topics))
ck("chapter 带 Unidad 单元", all(re.search(r"Unidad\s*\d+", t.get("chapter") or "", re.I) for t in topics))
bad_vol = [t["id"] for t in topics
           if (t.get("grade"), t.get("semester")) != VOLUMES[(t.get("chapter") or "").split(" ")[0]][:2]]
ck("grade/semester 与册名一一对应", not bad_vol, bad_vol[:5])
ck("domain 六类词表", all(t.get("domain") in DOMAINS for t in topics),
   sorted({t.get("domain") for t in topics} - DOMAINS))
ck("type 枚举合规", all(t.get("type") in TYPES for t in topics),
   sorted({t.get("type") for t in topics} - TYPES))
ck("名称 ≤50 字", all(len(t.get("name") or "") <= 50 for t in topics))
ck("名称无重复", len({t.get("name") for t in topics}) == len(topics))
ck("描述 ≥60 字", all(len(t.get("description") or "") >= 60 for t in topics),
   [t["id"] for t in topics if len(t.get("description") or "") < 60][:5])
ck("掌握标准 2–3 条", all(2 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("掌握标准每条 ≥8 字", all(len(m) >= 8 for t in topics for m in (t.get("mastery_criteria") or [])))
ck("诊断题完整", all((t.get("diagnostic_question") or {}).get("question") and
               (t.get("diagnostic_question") or {}).get("answer") for t in topics))
# 课标
ck("课标 id 均在目录", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in CQ])
ck("课标 id 均在索引", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("quote 与课标目录逐字一致",
   not [(t["id"], s["id"]) for t in topics for s in t.get("standards", [])
        if s.get("id") in CQ and s.get("quote") != CQ[s["id"]]["quote"]],
   [(t["id"], s["id"]) for t in topics for s in t.get("standards", [])
    if s.get("id") in CQ and s.get("quote") != CQ[s["id"]]["quote"]][:3])
ck("confidence 二档", all(s.get("confidence") in ("exact", "partial", "inferred")
                       for t in topics for s in t.get("standards", [])))
bad_lv = [(t["id"], s["id"]) for t in topics for s in t.get("standards", [])
          if s.get("id") in CQ
          and CQ[s["id"]]["level"] != VOLUMES[(t["chapter"] or "").split(" ")[0]][2]
          and not (s.get("confidence") == "partial"
                   and CQ[s["id"]]["level"] == VOLUMES[(t["chapter"] or "").split(" ")[0]][2] - 1)]
ck("课标 level 与册 level 匹配", not bad_lv, bad_lv[:3])
ck("standards 无越界字段",
   not [1 for t in topics for s in t.get("standards", [])
        if set(s) - {"id", "confidence", "quote", "sourceLine"}])
# 边
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
ck("topics 先修都有边",
   not [(p, t["id"]) for t in topics for p in (t.get("prerequisites") or []) if (p, t["id"]) not in set(pairs)])
color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason", all(t.get("root_reason") for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")][:5])
# 题
ck("题数 = 知识点数", len(qs) == len(topics), f"{len(qs)} vs {len(topics)}")
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("题 topicId 均可对", all(q.get("topicId") in T for q in qs))
ck("难度三档", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("难度三档均有覆盖", {"basic", "standard", "hard"} <= {q.get("difficulty") for q in qs},
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥12 字", all(len(q.get("prompt") or "") >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt") or "") < 12][:5])
ck("每题有解析 ≥10 字", all(len(q.get("explanation") or "") >= 10 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
ck("题目 subject 标注", all(q.get("subject") == SUBJECT for q in qs))
# 分册规模
per_vol = {}
for t in topics:
    per_vol.setdefault((t.get("chapter") or "").split(" ")[0], []).append(t["id"])
ck("每册知识点 6–14", all(6 <= len(v) <= 14 for v in per_vol.values()),
   {k: len(v) for k, v in per_vol.items() if not 6 <= len(v) <= 14})

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("SPANISH DATA PASSED")
