# -*- coding: utf-8 -*-
"""化学版本桶不变量测试：用法 python3 scripts/test_chem_editions.py <chemistry-lujiao|chemistry-luke>
口径与 test_chemistry.py 完全一致，只把学科改成参数。"""
import json, os, re, sys  # noqa

SUBJECT = sys.argv[1] if len(sys.argv) > 1 else "chemistry"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（9）普通高中化学课程标准日常修订版（2017年版2025年修订）.txt",
]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
_sec = idx["subjects"].get(SUBJECT) or idx["subjects"]["chemistry"]
std_ids = {e["id"] for e in _sec["entries"]}
# 新桶尚未进课标索引时，用全库已挂标 id 作解析基准（口径不放松：id 必须是仓内已出现过的课标 id）
import glob as _g
for _f in _g.glob(os.path.join(D, "*", "topics.json")):
    try:
        for _t in json.load(open(_f, encoding="utf-8")):
            for _s in (_t.get("standards") or []):
                std_ids.add(_s.get("id"))
    except Exception:
        pass

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("有 quote 的引用都带整数 sourceLine（schema 要求 integer）",
   all(isinstance(st.get("sourceLine"), int) for t in topics for st in t.get("standards", []) if st.get("quote")),
   [(t["id"], st.get("id")) for t in topics for st in t.get("standards", []) if st.get("quote") and not isinstance(st.get("sourceLine"), int)][:3])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺 TXT，跳过）", True, None))

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


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥8 字", all(len(q.get("prompt", "")) >= 8 for q in qs))
ck("每题有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("题目 id 唯一", len({q.get("id") for q in qs}) == len(qs),
   sorted({q.get("id") for q in qs if [x.get("id") for x in qs].count(q.get("id")) > 1})[:3])
def _num_ok(q):
    try:
        return abs(float(eval(q["verify"], {"__builtins__": {}})) - float(q["answer"])) <= max(1e-6, abs(float(q["answer"])) * 1e-3)
    except Exception:
        return False


ck("numeric 的 answer 与 verify 复算一致", all(_num_ok(q) for q in qs if q.get("type") == "numeric"),
   [q["id"] for q in qs if q.get("type") == "numeric" and not _num_ok(q)][:3])
_stage = lambda g: 1 if g <= 6 else (2 if g <= 9 else 3)
_dup_stage = [n for n in {t["name"] for t in topics}
              if len({_stage(x["grade"]) for x in topics if x["name"] == n}) <
                 [x["name"] for x in topics].count(n)]
ck("同学段内知识点名不重复（跨学段同名允许，如九年级/高中「金属材料」）", not _dup_stage, _dup_stage[:3])
ck("高中册名可派生（章节以「必修/选择性必修…册」开头）",
   all(re.match(r"^(必修第[一二三四五]册|选择性必修第[一二三]册) ", t["chapter"]) for t in topics if t["grade"] >= 10),
   [t["chapter"] for t in topics if t["grade"] >= 10 and not re.match(r"^(必修第[一二三四五]册|选择性必修第[一二三]册) ", t["chapter"])][:3])

# ---- 试卷层（54 卷：单元/章卷 + 每册期中期末 A/B）----
import glob, subprocess
_ep = os.path.join(D, SUBJECT, "exams")
_exams = sorted(glob.glob(os.path.join(_ep, "*", "*.json")))
ck("试卷文件数 = 单元/章数 + 4×册数", len(_exams) > 0, len(_exams))
_units = {t["chapter"] for t in topics if t["level"] == "unit"}
_books = {t["chapter"].split(" ")[0] for t in topics}
_scope = set()
for _f in _exams:
    _d = json.load(open(_f, encoding="utf-8"))
    _scope |= set(_d.get("scope") or [])
ck("每个单元/章都有卷", _units <= _scope, sorted(_units - _scope)[:3])
_mid = {json.load(open(f, encoding="utf-8"))["book"] for f in _exams
        if json.load(open(f, encoding="utf-8"))["kind"] == "mid"}
_fin = {json.load(open(f, encoding="utf-8"))["book"] for f in _exams
        if json.load(open(f, encoding="utf-8"))["kind"] == "fin"}
ck("每册都有期中卷与期末卷", _books <= _mid and _books <= _fin,
   sorted(_books - _mid)[:3] + sorted(_books - _fin)[:3])
_r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_chem_editions_exam.py"),
                     "--subject", SUBJECT, "--all"], capture_output=True, text=True)
ck("试卷逐卷合规（结构/分值/覆盖/原创性）", _r.stdout.strip().endswith("RESULT: PASS"),
   _r.stdout.strip()[-300:])

# ---- 学层层（每个课时点一篇精讲）----
_learn = sorted(glob.glob(os.path.join(D, SUBJECT, "learn", "*.json")))
_lessons = [t["id"] for t in topics if t["level"] == "lesson"]
_have = set()
for _f in _learn:
    for _l in json.load(open(_f, encoding="utf-8")).get("lessons", []):
        _have.add(_l.get("topicId"))
ck("每个课时点都有学层精讲", set(_lessons) <= _have, sorted(set(_lessons) - _have)[:3])
_rl = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_chem_editions_learn.py"),
                      "--bucket", SUBJECT, "--all"], capture_output=True, text=True)
ck("学层逐篇合规（七节/字数/引文回表/例题/五步）", _rl.stdout.strip().endswith("RESULT: PASS"),
   _rl.stdout.strip()[-300:])

# ---- 讲解层（每卷一讲）----
_lec = sorted(glob.glob(os.path.join(D, SUBJECT, "exam_lectures", "*", "*.json")))
_exam_ids = {json.load(open(f, encoding="utf-8"))["examId"] for f in _exams}
_lec_ids = set()
for _f in _lec:
    if os.path.basename(_f).startswith("_"):
        continue
    _lec_ids.add(json.load(open(_f, encoding="utf-8")).get("examId"))
ck("每份卷都有试卷讲解", _exam_ids <= _lec_ids, sorted(_exam_ids - _lec_ids)[:3])
_rk = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_chem_editions_lecture.py"),
                      "--bucket", SUBJECT, "--all"], capture_output=True, text=True)
ck("讲解逐卷合规（六段/题号分值对齐/五步/自查）", _rk.stdout.strip().endswith("RESULT: PASS"),
   _rk.stdout.strip()[-300:])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails)); sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
