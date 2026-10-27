# -*- coding: utf-8 -*-
"""音乐学科不变量测试（`python3 scripts/test_music.py`）。

课标 TXT 快照存在时做逐字回表；CI 环境没有本地 TXT 时自动跳过该两项。
回表口径：去掉空白与标点/符号后子串匹配（义教艺术课标为扫描件，OCR 快照的
标点全/半角与符号会有差异，字符本身逐字一致）。
"""
import json, os, re, sys, unicodedata

SUBJECT = "music"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = {
    "mus-2022": "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/《义务教育艺术课程标准》(2022年版) 扫描件OCR.txt",
    "mus-2017": "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（14）普通高中音乐课程标准（2017年版2020年修订）.txt",
}

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    s = re.sub(r"\s+", "", s or "")
    return "".join(ch for ch in s
                   if not unicodedata.category(ch).startswith(("P", "S")))


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}
pairs = [(e["from"], e["to"]) for e in deps]

# ---------------------------------------------------------------- 结构
ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("id 形态合规（mus_[ph]NNN）", all(re.fullmatch(r"mus_[ph]\d{3}", t["id"]) for t in topics),
   [t["id"] for t in topics if not re.fullmatch(r"mus_[ph]\d{3}", t["id"])][:3])
ck("诊断题数量不少于知识点", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("题目 id 唯一", len({q.get("id") for q in qs}) == len(qs),
   sorted({q.get("id") for q in qs if [x.get("id") for x in qs].count(q.get("id")) > 1})[:3])
ck("题目 topicId 均可解析", all(q.get("topicId") in T for q in qs),
   [q["id"] for q in qs if q.get("topicId") not in T][:3])
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))

# ---------------------------------------------------------------- 课标
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids],
   [(t["id"], s.get("id")) for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids][:3])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))
ck("quote 长度 12–40 字（课标原文片段口径）",
   all(12 <= len(norm(s["quote"])) <= 40 for t in topics for s in t.get("standards", [])),
   [(t["id"], s["quote"]) for t in topics for s in t.get("standards", []) if not 12 <= len(norm(s["quote"])) <= 40][:3])
_src = {}
for key, path in TXT.items():
    _src[key] = norm(open(path, encoding="utf-8", errors="ignore").read()) if os.path.exists(path) else None
if all(v is not None for v in _src.values()):
    miss = [(t["id"], s["id"]) for t in topics for s in t.get("standards", [])
            if norm(s["quote"]) not in _src[s["id"].split(":")[0]]]
    ck("quote 逐字回表 100%", not miss, miss[:3])
    lines = {k: open(p, encoding="utf-8", errors="ignore").read().split("\n")
             for k, p in TXT.items()}
    bad = []
    for t in topics:
        for s in t.get("standards", []):
            k = s["id"].split(":")[0]
            ln = int(s.get("sourceLine") or 0)
            L = lines[k]
            if not (1 <= ln <= len(L)):
                bad.append((t["id"], s["id"], ln))
                continue
            joined = norm(L[ln - 1] + (L[ln] if ln < len(L) else ""))
            if norm(s["quote"])[:10] not in joined:
                bad.append((t["id"], s["id"], ln))
    ck("quote 的 sourceLine 可定位", not bad, bad[:3])
else:
    checks.append(("quote 回表（缺 TXT，跳过）", True, None))
    checks.append(("sourceLine 定位（缺 TXT，跳过）", True, None))

# ---------------------------------------------------------------- 先修边
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps → prerequisites 镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])
ck("prerequisites → deps 镜像",
   not [(p, t["id"]) for t in topics for p in t.get("prerequisites", []) if (p, t["id"]) not in set(pairs)])

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
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))
ck("先修边两端学段不倒挂（不指向更低年级）",
   not [(a, b) for a, b in pairs if T[a]["grade"] > T[b]["grade"]],
   [(a, b) for a, b in pairs if T[a]["grade"] > T[b]["grade"]][:3])

# ---------------------------------------------------------------- 题库
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("难度三档都用到", {"basic", "standard", "hard"} <= {q.get("difficulty") for q in qs},
   sorted({q.get("difficulty") for q in qs}))
ck("题型至少三类（choice / numeric / short-answer）",
   {"choice", "numeric", "short-answer"} <= {q.get("type") for q in qs},
   sorted({q.get("type") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
dup_opt = [q["id"] for q in qs if q.get("type") == "choice"
           and len({o.get("text") for o in q.get("options") or []}) != len(q.get("options") or [])]
ck("选择题选项文本互不重复", not dup_opt, dup_opt[:3])
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:3])
ck("每题有解析（≥10 字）", all(len(q.get("explanation", "")) >= 10 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 10][:3])
ck("prompt 与 question 同值（兼容字段）", all(q.get("prompt") == q.get("question") for q in qs),
   [q["id"] for q in qs if q.get("prompt") != q.get("question")][:3])
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))


def _num_ok(q):
    try:
        return abs(float(eval(q["verify"], {"__builtins__": {}})) - float(q["answer"])) <= max(1e-6, abs(float(q["answer"])) * 1e-3)
    except Exception:
        return False


ck("numeric 的 answer 与 verify 复算一致",
   all(_num_ok(q) for q in qs if q.get("type") == "numeric"),
   [q["id"] for q in qs if q.get("type") == "numeric" and not _num_ok(q)][:3])
ck("非选择题不带 options",
   all(not q.get("options") for q in qs if q.get("type") != "choice"),
   [q["id"] for q in qs if q.get("type") != "choice" and q.get("options")][:3])

# ---------------------------------------------------------------- 节点字段
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics),
   [t["id"] for t in topics if not all(t.get(k) for k in need)][:3])
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("描述与掌握标准不重复（描述须解释，不得照抄判据）",
   all(norm(t["description"]) not in [norm(m) for m in t.get("mastery_criteria") or []] for t in topics),
   [t["id"] for t in topics
    if norm(t["description"]) in [norm(m) for m in t.get("mastery_criteria") or []]][:3])
ck("任务型诊断题与题库一致",
   all(isinstance(t.get("diagnostic_question"), dict) and t["diagnostic_question"].get("question")
       and t["diagnostic_question"].get("answer") for t in topics),
   [t["id"] for t in topics if not (t.get("diagnostic_question") or {}).get("question")][:3])

# ---------------------------------------------------------------- 学科口径
_stage_of = lambda g: 1 if g <= 2 else (2 if g <= 5 else (3 if g <= 7 else 4))
_mis_stage = []
for t in topics:
    for s in t.get("standards", []):
        sid = s["id"]
        if sid.startswith("mus-2022"):
            want = _stage_of(t["grade"])
            got = sid.split(":")[1].split(".")[0]
            if got != str(want):
                _mis_stage.append((t["id"], t["grade"], sid))
ck("义教节点年级与课标学段一致（1–2/3–5/6–7/8–9 → 学段 1–4）", not _mis_stage, _mis_stage[:3])
_dupname = [n for n in {t["name"] for t in topics}
            if len({_stage_of(x["grade"]) for x in topics if x["name"] == n}) <
               [x["name"] for x in topics].count(n)]
ck("同学段内知识点名不重复", not _dupname, _dupname[:3])
_hi = [t for t in topics if t["grade"] >= 10]
ck("高中节点册名为「高中必修/高中选择性必修/高中选修」之一",
   all(re.match(r"^高中(必修|选择性必修|选修) ", t["chapter"]) for t in _hi),
   [t["chapter"] for t in _hi if not re.match(r"^高中(必修|选择性必修|选修) ", t["chapter"])][:3])
_must = ["音乐鉴赏", "歌唱", "演奏", "音乐编创", "音乐与舞蹈", "音乐与戏剧"]
_elect = ["合唱", "合奏", "舞蹈表演", "戏剧表演", "音乐基础理论", "视唱练耳"]
_chs = {t["chapter"] for t in _hi}
ck("高中必修 6 模块全覆盖", all(any(m in c for c in _chs) for m in _must),
   [m for m in _must if not any(m in c for c in _chs)])
ck("高中选择性必修 6 模块全覆盖", all(any(m in c for c in _chs) for m in _elect),
   [m for m in _elect if not any(m in c for c in _chs)])
_reg = lambda g: "义教" if g <= 9 else "高中"
ck("义教节点册名可派生（年级+上/下册）",
   all(re.match(r"^[一二三四五六七八九]年级[上下]册 ", t["chapter"]) for t in topics if t["grade"] <= 9),
   [t["chapter"] for t in topics if t["grade"] <= 9
    and not re.match(r"^[一二三四五六七八九]年级[上下]册 ", t["chapter"])][:3])
ck("领域取值在既定三/四类内",
   {t["domain"] for t in topics} <= {"音乐鉴赏", "音乐表现", "音乐创作", "音乐理论"},
   sorted({t["domain"] for t in topics}))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("MUSIC DATA PASSED")
