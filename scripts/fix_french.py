# -*- coding: utf-8 -*-
"""法语数据归一（幂等）。用法: python3 scripts/fix_french.py [--write]

修的是本批体检出来的五类缺口：
1. 难度别名 easy/medium → basic/standard（契约只认三档）。
2. 8 个根节点补 root_reason（逐条手写，不用模板串）。
3. 5 条 soft 边在 topics.prerequisites 里缺镜像 → 补齐。
4. 领域误分：h40–h42（口语）、h43–h46（写作）原写成「语音」。
5. 高三册次口径：grade 12 原借「选择性必修IV下册」册名（与高二册名重复），
   统一为「高三复习」（高三无新册，同 english 的「高考复习」口径）。
另修题库：重复选项、题干与答案不一致、解析笔误、难度分档、答案字母分布。
"""
import json, os, re, sys

WRITE = "--write" in sys.argv
D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data")
S = "french"
tp, qp, dp = f"{D}/{S}/topics.json", f"{D}/{S}/questions.json", f"{D}/{S}/dependencies.json"
topics = json.load(open(tp, encoding="utf-8"))
qs = json.load(open(qp, encoding="utf-8"))
deps = json.load(open(dp, encoding="utf-8"))
T = {x["id"]: x for x in topics}

# ---------- 1. 难度别名 ----------
DIFF = {"easy": "basic", "medium": "standard"}
n_diff = 0
for q in qs:
    if q.get("difficulty") in DIFF:
        q["difficulty"] = DIFF[q["difficulty"]]
        n_diff += 1

# ---------- 2. 根节点 root_reason（逐条手写） ----------
ROOT_REASON = {
    "fre_h01": "起始知识点：必修III上册语音基础第 1 课，法语学习的最早一环，语音层面无更早前置",
    "fre_h02": "起始知识点：必修III上册语音基础辅音部分，与元音发音并列入门，故无先修",
    "fre_h06": "起始知识点：必修III上册 Unité1 词汇入口，高一入门词汇，之前无词汇单元",
    "fre_h07": "起始知识点：必修III上册 Unité2 主题词汇，属入门主题词，与其它主题词并列不连边（跨主题词汇互不为前置）",
    "fre_h08": "起始知识点：必修III上册 Unité3 主题词汇，入门主题词，跨主题词汇不连边",
    "fre_h09": "起始知识点：必修III上册 Unité4 主题词汇，入门主题词，跨主题词汇不连边",
    "fre_h15": "起始知识点：必修III上册语法首项（名词短语的基础规则），语法层无更早前置",
    "fre_h17": "起始知识点：人称代词体系的第一项，不依赖名词性数即可先学，与冠词/性数并列（不连边）",
}
n_root = 0
for t in topics:
    if not t.get("prerequisites") and not t.get("root_reason") and t["id"] in ROOT_REASON:
        t["root_reason"] = ROOT_REASON[t["id"]]
        n_root += 1

# ---------- 3. deps → prerequisites 镜像 ----------
n_mirror = 0
for e in deps:
    a, b = e["from"], e["to"]
    if a in T and b in T and a not in T[b].setdefault("prerequisites", []):
        T[b]["prerequisites"].append(a)
        n_mirror += 1
for t in topics:
    t["prerequisites"] = sorted(set(t.get("prerequisites") or []))

# ---------- 4. 领域误分 ----------
DOMAIN_FIX = {}
for i in ("fre_h40", "fre_h41", "fre_h42"):
    DOMAIN_FIX[i] = "口语"
for i in ("fre_h43", "fre_h44", "fre_h45", "fre_h46"):
    DOMAIN_FIX[i] = "写作"
n_dom = 0
for t in topics:
    if t["id"] in DOMAIN_FIX and t.get("domain") != DOMAIN_FIX[t["id"]]:
        t["domain"] = DOMAIN_FIX[t["id"]]
        n_dom += 1

# ---------- 5. 高三册次口径 ----------
n_book = 0
for t in topics:
    if int(t.get("grade") or 0) < 12:
        continue
    ch = t.get("chapter") or ""
    if ch.startswith("选择性必修"):
        tail = ch.split(" ", 1)[1] if " " in ch else ""
        t["chapter"] = ("高三复习 " + tail).strip()
        n_book += 1
    elif re.match(r"^高三复习(\S)", ch):          # 修早期漏空格的「高三复习写作」
        t["chapter"] = re.sub(r"^高三复习(\S+)", r"高三复习 \1", ch)
        n_book += 1

# ---------- 题库 ----------
OPTION_FIX = {
    # (id, label, 原文本) → 新文本 —— 原 A/C、A/D、B/D 文本完全重复，实为废干扰项。
    # 按「标签+原文本」双条件命中，脚本次次幂等（轮转后标签下的文本已换，不会再被改一次）。
    ("fre_q16", "C", "les belles filles"): "les belle filles",
    ("fre_q19", "D", "nous sommes"): "nous est",
    ("fre_q20", "D", "ils finent"): "ils finis",
    ("fre_q30", "D", "Je veux un café."): "Je voudrai un café.",
    # B「Où tu vas ?」在口语里其实也说，留着会让「A和C都对」出错 → 换成明确错误的代词形式
    ("fre_q22", "B", "Où tu vas ?"): "Où vas-toi ?",
}
PROMPT_FIX = {
    # 原题干限「主谓倒装」，但 A(倒装) 与 C(est-ce que) 都正确 → 改题干为准
    "fre_q22": "「你去哪里？」下面哪种法语说法是正确的？",
}
EXPL_FIX = {
    "fre_q25": "'venir'是表示移动的动词，复合过去时用'être'作助动词：elle est venue。",
    "fre_q22": "'Où vas-tu ?'（主谓倒装）与'Où est-ce que tu vas ?'都是正确的疑问句形式；'Où vas-toi ?'的倒装代词用错（应为 toi→tu 倒装成 -tu）。",
}
DIFF_PROMOTE = {"fre_q31": "hard", "fre_q32": "hard", "fre_q33": "hard"}

n_opt = n_prompt = n_expl = n_prom = 0
for q in qs:
    for (qid, lab, old_txt), new_txt in OPTION_FIX.items():
        if qid != q["id"]:
            continue
        for o in q["options"]:
            if o["label"] == lab and o["text"] == old_txt:
                o["text"] = new_txt
                n_opt += 1
    if q["id"] in PROMPT_FIX and q.get("prompt") != PROMPT_FIX[q["id"]]:
        q["prompt"] = q["question"] = PROMPT_FIX[q["id"]]
        n_prompt += 1
    if q["id"] in EXPL_FIX and q.get("explanation") != EXPL_FIX[q["id"]]:
        q["explanation"] = EXPL_FIX[q["id"]]
        n_expl += 1
    if q["id"] in DIFF_PROMOTE and q.get("difficulty") != DIFF_PROMOTE[q["id"]]:
        q["difficulty"] = DIFF_PROMOTE[q["id"]]
        n_prom += 1

# 答案字母分布：B 占 28/46（61%），可被「猜 B」套利。
# 对「非自指选项」的题做循环轮转（含『A和C都对』之类自指选项的不动），
# 让答案字母落在 A/B/C/D 轮转位上；选项文本与解析一律不动。
SELFREF = re.compile(r"A和|都对|都需要|都可以")
LETTERS = ["A", "B", "C", "D"]
n_rot = 0
idx = 0
for q in qs:
    if q.get("type") != "choice" or len(q.get("options") or []) != 4:
        continue
    if any(SELFREF.search(o.get("text", "")) for o in q["options"]):
        continue
    target = LETTERS[idx % 4]
    idx += 1
    cur = q["answer"]
    if cur == target:
        continue
    shift = (LETTERS.index(target) - LETTERS.index(cur)) % 4
    lab2opt = {o["label"]: o for o in q["options"]}
    texts = [lab2opt[l]["text"] for l in LETTERS]
    rotated = texts[-shift:] + texts[:-shift] if shift else texts
    for l, txt in zip(LETTERS, rotated):
        lab2opt[l]["text"] = txt
    q["answer"] = target
    n_rot += 1

# ---------- 自检 ----------
dup = [(q["id"]) for q in qs if len({o["text"] for o in q["options"]}) != len(q["options"])]
from collections import Counter
print(f"难度归一 {n_diff} | 根节点 reason {n_root} | 镜像边 {n_mirror} | 领域修正 {n_dom} | 册次修正 {n_book}")
print(f"题库：选项去重 {n_opt} | 题干订正 {n_prompt} | 解析订正 {n_expl} | 难度上调 {n_prom} | 答案轮转 {n_rot}")
print("难度:", Counter(q["difficulty"] for q in qs))
print("答案分布:", Counter(q["answer"] for q in qs))
print("剩余重复选项题:", dup)
print("仍无 root_reason 的根节点:", [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")])
print("prerequisites 与 deps 不镜像:", sum(1 for e in deps if e["from"] not in T[e["to"]].get("prerequisites", [])))

if WRITE:
    json.dump(topics, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(tp, "a", encoding="utf-8").write("\n")
    json.dump(qs, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(qp, "a", encoding="utf-8").write("\n")
    print("written:", tp, qp)
