# -*- coding: utf-8 -*-
"""初中小节级核对后发现的 2 个真缺知识点 + 1 处章归属修正。

教材依据（人教 2024 新版，目录页逐节核对）：
  八年级上册 18.4 整数指数幂          （图谱第十八章「分式」原有 5 点，缺该小节）
  八年级下册 24.3 数据的四分位数      （图谱第二十四章「数据的分析」原有 4 点，缺该小节）
章归属修正：
  「一次函数的概念」原挂在第二十二章 函数 → 教材在第二十三章 一次函数（23.1）

用法：python3 fix_chuzhong_sections.py [--write]
"""
import json
import os
import sys
from collections import Counter, defaultdict

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, DP, QP = (f"{REPO}/data/math/topics.json", f"{REPO}/data/math/dependencies.json",
              f"{REPO}/data/math/questions.json")
WRITE = "--write" in sys.argv
RANK = {"basic": 0, "standard": 1, "hard": 2}

STD = {
    "zg": ("会用科学记数法表示数", "partial"),
    "sf": ("知道百分位数和四分位数，能计算一组数据的四分位数，知道箱线图可以直观反映数据分布的信息", "exact"),
}
SID = {"zg": "mat-2022:4.NR.63", "sf": "mat-2022:4.TS.12"}

UNITS = [
    dict(id="mat_p951", name="整数指数幂与科学记数法", grade=8, semester="上",
         chapter="八年级上册 第十八章 分式", domain="数与代数", type="procedural",
         desc="理解负整数指数幂的意义 a^(-n)=1/a^n（a≠0），会把整数指数幂写成不含分母的形式，并会用 10 的负整数次幂表示很小的数",
         mastery=["能把 a^(-n) 化为 1/a^n 并正确计算", "会用科学记数法表示绝对值小于 1 的数"],
         tags=["数与代数", "分式", "整数指数幂"], pre=["mat_p824"], std=["zg"]),
    dict(id="mat_p952", name="数据的四分位数", grade=8, semester="下",
         chapter="八年级下册 第二十四章 数据的分析", domain="统计与概率", type="procedural",
         desc="知道四分位数的含义，会把一组数据按从小到大排列后找出下四分位数、中位数与上四分位数，并能用箱线结构判断数据的分布特征",
         mastery=["能给一组数据求三个四分位数", "能说明四分位数与中位数在刻画离散程度上的区别"],
         tags=["统计与概率", "数据的分析", "四分位数"], pre=["mat_p849"], std=["sf"]),
]

QS = {
 "mat_p951": [
  ("choice", "basic", "下列各式正确的是哪一个？",
   [("2^(-3)=1/8", 1), ("2^(-3)=-8", 0), ("2^(-3)=-1/8", 0), ("2^(-3)=0", 0)], "",
   "负整数指数幂 a^(-n)=1/a^n（a≠0），所以 2^(-3)=1/2³=1/8。-8 是把负指数当成负的幂，0 混淆了底数为 0。"),
  ("choice", "basic", "把 0.000 031 用科学记数法表示，正确的是哪一个？",
   [("3.1×10^(-5)", 1), ("3.1×10^5", 0), ("31×10^(-6)", 0), ("0.31×10^(-4)", 0)], "",
   "0.000 031 = 3.1×10^(-5)：小数点后到 3 之间有 5 位，指数取 -5。3.1×10^5 把它放大成 310000；31×10^(-6) 与 0.31×10^(-4) 都不满足 1≤|a|<10。"),
  ("fill", "basic", "计算：5^(-2) = ___（填分数，如 1/25）。", [], "1/25",
   "5^(-2)=1/5²=1/25。易错：写成 -25 或 -1/25，把负指数误当成取相反数。"),
  ("numeric", "standard", "计算 (1/3)^(-2) 的值是多少？只填数字。", [], "9",
   "(1/3)^(-2)=1/(1/3)²=1/(1/9)=9（即 3**2）。易错：算成 1/9 或 -9。"),
  ("short-answer", "hard", "请说明负整数指数幂的意义，以及整数指数幂的三条运算性质在负指数时是否仍然适用。", [],
   "a^(-n)=1/a^n（a≠0），即负指数表示取倒数后取正指数幂；同底数幂相乘、幂的乘方、积的乘方三条性质对整数指数（含负数）仍然成立，如 a^m·a^n=a^(m+n) 在 m、n 为负整数时也成立",
   "负指数不是「负的幂」而是「倒数」：a^(-n)=1/a^n。正因为这样定义，整数指数幂的运算性质才能统一到负数指数上，幂的运算法则在整数范围内保持形式不变，这也是把分式运算化为整式指数运算的依据。"),
 ],
 "mat_p952": [
  ("choice", "basic", "把 7 个数从小到大排列后，中位数是第几个数？",
   [("第 3 个", 0), ("第 4 个", 1), ("第 5 个", 0), ("第 1 个", 0)], "",
   "7 个数据的中位数是第 4 个（正中间那个）。(7+1)/2=4，所以取第 4 个。"),
  ("choice", "basic", "四分位数把一组从小到大排列的数据大致分成几部分？",
   [("两部分", 0), ("三部分", 0), ("四部分", 1), ("五部分", 0)], "",
   "下四分位数 Q1、中位数 Q2、上四分位数 Q3 把数据分成四部分，每部分约含 1/4 的数据，这正是「四分位数」名称的由来。"),
  ("fill", "basic", "已知一组数据的中位数是 12，下四分位数是 8，上四分位数是 20，则四分位距（Q3−Q1）= ___（只填数字）。", [], "12",
   "四分位距 IQR=Q3−Q1=20-8=12。它只用到中间 50% 的数据，因此不受极端值影响。"),
  ("numeric", "standard", "数据 2, 4, 4, 6, 8, 10, 12, 12 共 8 个，中位数是多少？只填数字。", [], "7",
   "8 个数据的中位数取第 4、5 个的平均：(6+8)/2=7。易错：直接取第 4 个 6。"),
  ("short-answer", "hard", "请说明四分位数的作用，以及为什么它比平均数更能反映「中间部分」的分布。", [],
   "四分位数把排列好的数据分成四段，Q1、Q2（中位数）、Q3 分别对应 25%、50%、75% 位置；四分位距 IQR=Q3−Q1 只反映中间 50% 数据的集中程度，不受极端值影响，而平均数会被极端值拉偏",
   "四分位数是「位置统计量」，只看数据排在第几成，不用算总和，因此对极端值稳健。比较两组数据时，IQR 小说明中间一半更集中；看 Q1/Q3 还能发现偏态。平均数的缺点正是会被离群值拉走，这也是要用中位数与四分位数补充的原因。"),
 ],
}

VERIFY = {"mat_p951": "3**2", "mat_p952": "(6+8)/2"}

topics = json.load(open(TP, encoding="utf-8"))
deps = json.load(open(DP, encoding="utf-8"))
qs = json.load(open(QP, encoding="utf-8"))
T = {t["id"]: t for t in topics}

# ① 章归属修正：一次函数的概念 → 第二十三章
fix = 0
for t in topics:
    if t["name"] == "一次函数的概念" and t["chapter"] == "八年级下册 第二十二章 函数":
        t["chapter"] = "八年级下册 第二十三章 一次函数"
        fix += 1

# ② 新增 2 个知识点
LBL = "ABCD"
added_t, added_e, added_q = [], 0, 0
for u in UNITS:
    if u["id"] in T:
        continue
    stds = [{"id": SID[c], "confidence": STD[c][1], "quote": STD[c][0]} for c in u["std"]]
    topics.append({
        "id": u["id"], "name": u["name"], "subject": "math", "domain": u["domain"],
        "grade": u["grade"], "semester": u["semester"], "chapter": u["chapter"], "type": u["type"],
        "description": u["desc"], "mastery_criteria": u["mastery"],
        "diagnostic_question": {"question": "", "answer": ""}, "external": False,
        "standards": stds, "tags": u["tags"], "prerequisites": u["pre"],
        "curriculumRef": stds[0]["id"], "verified": False,
    })
    T[u["id"]] = topics[-1]
    added_t.append(u["id"])

pairs = {(e["from"], e["to"]) for e in deps}
for u in UNITS:
    for p in u["pre"]:
        if p not in T:
            print(f"⚠ 先修点不存在，跳过：{p} → {u['id']}")
            continue
        if (p, u["id"]) not in pairs:
            deps.append({"from": p, "to": u["id"], "type": "hard"})
            pairs.add((p, u["id"]))
            added_e += 1

for tid, items in QS.items():
    if any(q["topicId"] == tid for q in qs):
        continue
    for k, (typ, diff, prompt, opts, _ans, expl) in enumerate(items, start=2):
        qid = f"{tid}_q{k}"
        if typ == "choice":
            choices = [{"label": LBL[i], "text": t} for i, (t, _c) in enumerate(opts)]
            idx = [i for i, (_t, c) in enumerate(opts) if c == 1]
            assert len(idx) == 1, (tid, prompt)
            q = {"id": qid, "topicId": tid, "prompt": prompt, "question": prompt,
                 "choices": choices, "options": [dict(c) for c in choices],
                 "answer": LBL[idx[0]], "type": typ, "difficulty": diff,
                 "explanation": expl, "subject": "math"}
        else:
            q = {"id": qid, "topicId": tid, "prompt": prompt, "question": prompt,
                 "choices": [], "options": [], "answer": _ans, "type": typ,
                 "difficulty": diff, "explanation": expl, "subject": "math"}
        if typ == "numeric":
            q["verify"] = VERIFY[tid]
            assert abs(eval(q["verify"]) - float(q["answer"])) < 1e-9, (tid, q["verify"], q["answer"])
        qs.append(q)
        added_q += 1
        if k == 2:
            T[tid]["diagnostic_question"] = {"question": prompt, "answer": q["answer"]}

by = defaultdict(list)
for q in qs:
    by[q["topicId"]].append(q)
qs = [q for t in topics for q in sorted(by[t["id"]], key=lambda z: RANK[z["difficulty"]])]

print(f"章归属修正 {fix} 处 · 新增知识点 {len(added_t)}：{added_t} · 边 +{added_e} · 题 +{added_q}")
print(f"规模：点 {len(topics)} · 边 {len(deps)} · 题 {len(qs)}")
print("每点题数", dict(Counter(Counter(q['topicId'] for q in qs).values())))

if WRITE:
    for path, obj in ((TP, topics), (DP, deps), (QP, qs)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("✅ 已写入")
