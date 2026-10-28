# -*- coding: utf-8 -*-
"""数学学科收口第二批：
1) domain 统一为课标四领域（细分沉到 tags）；
2) 照人教版一年级下册补「认识图形（二）」「分类与整理」两单元（6 个知识点 + 30 道题）；
3) 纠正一下章号错位（20 以内退位减法 = 第二单元）。
用法：python3 math_closeout2.py [--write]
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
WRITE = "--write" in sys.argv
TP = f"{REPO}/data/math/topics.json"
DP = f"{REPO}/data/math/dependencies.json"
QP = f"{REPO}/data/math/questions.json"
RANK = {"basic": 0, "standard": 1, "hard": 2}

DOMAIN_MAP = {
    "数与运算": "数与代数", "函数": "数与代数", "导数": "数与代数", "不等式": "数与代数",
    "指数": "数与代数", "对数": "数与代数", "数列": "数与代数", "集合": "数与代数",
    "逻辑": "数与代数", "计数": "数与代数", "复数": "数与代数", "三角函数": "数与代数",
    "向量": "图形与几何", "解析几何": "图形与几何", "立体几何": "图形与几何",
    "统计": "统计与概率", "概率": "统计与概率",
}
FOUR = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}

topics = json.load(open(TP, encoding="utf-8"))
deps = json.load(open(DP, encoding="utf-8"))
qs = json.load(open(QP, encoding="utf-8"))
T = {t["id"]: t for t in topics}

# ---------- 1. domain 归一 ----------
n_dom = 0
for t in topics:
    old = t.get("domain")
    new = DOMAIN_MAP.get(old, old)
    if new != old:
        n_dom += 1
    t["domain"] = new
    tags = [x for x in (t.get("tags") or []) if x]
    t["tags"] = [new] + [x for x in tags if x != new]
print(f"domain 归一 {n_dom} 个点 →", {k: sum(1 for t in topics if t['domain'] == k) for k in FOUR})

# ---------- 2. 一下章号纠错 ----------
if T["mat_p101"]["chapter"].startswith("一年级下册 第一单元"):
    T["mat_p101"]["chapter"] = T["mat_p101"]["chapter"].replace("第一单元", "第二单元")
    print("已纠正 mat_p101 章号：第一单元 → 第二单元（人教版一下第二单元为 20 以内退位减法）")

# ---------- 3. 补 6 个知识点 ----------
STD = {  # id → (quote, confidence)
    "XY.09": ("能直观描述这些平面图形的特征", "partial"),
    "XY.10": ("能根据描述的特征对图形进行简单分类", "partial"),
    "XY.11": ("能说出立体图形中某一个面对应的平面图形", "partial"),
    "NR.13": ("会用简单图形拼图", "exact"),
    "XY.12": ("能在组合图形中说出各组成部分图形的名称", "partial"),
    "NR.14": ("会对物体、图形或数据进行分类，初步了解分类与分类标准的关系，形成初步的数据意识", "partial"),
    "XY.13": ("能发现事物的特征并制订分类标准，依据标准对物体分类", "exact"),
    "XY.14": ("能用语言简单描述分类的过程", "inferred"),
}

NEW = [
    dict(id="mat_p107", name="认识长方形、正方形、三角形和圆", domain="图形与几何", type="conceptual",
         chapter="一年级下册 第一单元 认识图形（二）",
         description="能辨认长方形、正方形、三角形和圆，能用自己的话说出这几种平面图形的样子（边的条数、角的个数）",
         mastery=["能在一堆图形中找出长方形、正方形、三角形和圆",
                  "能说出三角形有 3 条边、3 个角，长方形和正方形都有 4 条边、4 个角"],
         tags=["图形与几何", "平面图形"],
         pre=["mat_p017"], std=[("XY.09", None), ("XY.10", None)], root=None),
    dict(id="mat_p108", name="从立体图形上找到平面图形", domain="图形与几何", type="conceptual",
         chapter="一年级下册 第一单元 认识图形（二）",
         description="能从长方体、正方体、圆柱等立体图形的面上找到并描出平面图形，知道立体图形的一个面可以是长方形、正方形或圆",
         mastery=["能说出正方体的面是正方形、圆柱的底面是圆",
                  "能照着立体图形的一个面在纸上描出相应的平面图形"],
         tags=["图形与几何", "平面图形", "立体与平面"],
         pre=["mat_p017", "mat_p107"], std=[("XY.11", None)], root=None),
    dict(id="mat_p109", name="平面图形的拼组与分割", domain="图形与几何", type="procedural",
         chapter="一年级下册 第一单元 认识图形（二）",
         description="能用同样大小的平面图形拼出新的图形（如两个三角形拼成正方形、四个小正方形拼成大正方形），也能把一个图形分成几个小图形",
         mastery=["能用两个完全一样的三角形拼成长方形、正方形或大三角形",
                  "能用 4 个相同的小正方形拼成一个大正方形"],
         tags=["图形与几何", "图形的拼组"],
         pre=["mat_p107"], std=[("NR.13", None), ("XY.12", None)], root=None),
    dict(id="mat_p110", name="按单一标准分类与整理", domain="统计与概率", type="conceptual",
         chapter="一年级下册 第三单元 分类与整理",
         description="知道什么是分类，能按一个给定的标准（如颜色、种类、大小）把物品分成几组，做到每件物品只放进一组",
         mastery=["能按给定标准把物品分组，做到不重不漏",
                  "能说出自己分类用的是什么标准"],
         tags=["统计与概率", "数据分类"],
         pre=[], std=[("NR.14", None)], root="起始知识点：分类与整理是人教版一年级下册第三单元的入门内容，图谱内无更早前置（幼儿园阶段经验不单独建点）"),
    dict(id="mat_p111", name="按不同标准分类", domain="统计与概率", type="reasoning",
         chapter="一年级下册 第三单元 分类与整理",
         description="知道同一堆物品可以按不同标准分类（颜色、形状、大小等），标准不同分出的组数和结果可能不同",
         mastery=["能对同一堆物品换一个标准再分一次，并说出两次结果哪里不同",
                  "能说出分类结果不同是因为标准不同"],
         tags=["统计与概率", "数据分类", "分类标准"],
         pre=["mat_p110"], std=[("XY.13", None)], root=None),
    dict(id="mat_p112", name="用象形统计图整理分类结果", domain="统计与概率", type="procedural",
         chapter="一年级下册 第三单元 分类与整理",
         description="能把分类的结果整理成象形统计图（一个物品画一个图形、从下往上对齐摆），并能从图上直接看出哪类最多、哪类最少",
         mastery=["能把分类结果一个一个画成象形统计图，各列对齐",
                  "能看着象形统计图说出最多的和最少的类别"],
         tags=["统计与概率", "象形统计图", "数据整理"],
         pre=["mat_p110"], std=[("XY.14", None)], root=None),
]

added = []
for n in NEW:
    if n["id"] in T:
        continue
    ids = {"XY.09": "mat-2022:1.XY.09", "XY.10": "mat-2022:1.XY.10", "XY.11": "mat-2022:1.XY.11",
           "XY.12": "mat-2022:1.XY.12", "XY.13": "mat-2022:1.XY.13", "XY.14": "mat-2022:1.XY.14",
           "NR.13": "mat-2022:1.NR.13", "NR.14": "mat-2022:1.NR.14"}
    stds = [{"id": ids[c], "confidence": STD[c][1], "quote": STD[c][0]} for c, _ in n["std"]]
    tp = {
        "id": n["id"], "name": n["name"], "subject": "math", "domain": n["domain"],
        "grade": 1, "semester": "下", "chapter": n["chapter"], "type": n["type"],
        "description": n["description"], "mastery_criteria": n["mastery"],
        "diagnostic_question": {"question": "", "answer": ""},
        "external": False, "standards": stds, "tags": n["tags"],
        "prerequisites": n["pre"], "curriculumRef": stds[0]["id"], "verified": False,
    }
    if n["root"]:
        tp["root_reason"] = n["root"]
    topics.append(tp)
    T[n["id"]] = tp
    added.append(n["id"])
print("新增知识点", added)

# ---------- 4. 先修边 ----------
pairs = {(e["from"], e["to"]) for e in deps}
n_edge = 0
for tid, t in T.items():
    for p in t.get("prerequisites") or []:
        if (p, tid) not in pairs:
            deps.append({"from": p, "to": tid, "type": "hard"})
            pairs.add((p, tid))
            n_edge += 1
print("补先修边", n_edge)

# ---------- 5. 新点的 5 题 ----------
D = "basic"
NEWQ = {
 "mat_p107": [
  ("choice", "basic", "下面哪种图形的边是弯曲的、一个角也没有？",
   [("长方形", 0), ("正方形", 0), ("圆", 1), ("三角形", 0)], "C",
   "圆没有直直的边，也没有角；长方形、正方形、三角形都有直边和角。"),
  ("choice", "basic", "一个图形有 4 条边、4 个角，而且 4 条边一样长，它是什么图形？",
   [("长方形", 0), ("正方形", 1), ("三角形", 0), ("圆", 0)], "B",
   "有 4 条边、4 个角，并且 4 条边都一样长，就是正方形；长方形的 4 条边只有对边相等。"),
  ("fill", "basic", "一个三角形有几条边？只填数字。", [], "3",
   "三角形由 3 条边围成，所以有 3 条边、3 个角；数的时候要一条一条数，别把顶点当边。"),
  ("numeric", "standard", "用小棒摆 2 个分开的三角形，每个三角形用 3 根小棒，一共要用多少根小棒？只填数字。",
   [], "6", "每个三角形用 3 根，摆 2 个就是 2 个 3，3+3=6（也就是 2*3=6）根；易错：只算一个三角形得 3 根。"),
  ("short-answer", "hard", "说一说长方形和正方形有什么相同的地方，又有什么不同的地方。",
   [], "都有 4 条边和 4 个角；4 个角都是直角；正方形的 4 条边一样长，长方形只有对着的两条边相等",
   "长方形和正方形都属于四边形：相同点是都有 4 条边、4 个角且 4 个角都是直角；不同点在边的长度——正方形 4 条边全部相等，长方形只是对边相等。易错：把正方形说成「边长的长方形」而忽略它 4 边相等这一关键特征。"),
 ],
 "mat_p108": [
  ("choice", "basic", "照着正方体的一个面在纸上描一描，描出来的图形是什么？",
   [("圆", 0), ("三角形", 0), ("正方形", 1), ("长方形", 0)], "C",
   "正方体的每个面都是正方形，所以描出来的图形是正方形；易错：以为描出来是长方形。"),
  ("choice", "basic", "照着圆柱的底面描一描，描出来的图形是什么？",
   [("正方形", 0), ("圆", 1), ("三角形", 0), ("长方形", 0)], "B",
   "圆柱的上下两个底面都是圆，所以描出来是圆；圆柱的侧面是弯的，描不出平平的图形。"),
  ("fill", "basic", "长方体一共有几个面？只填数字。", [], "6",
   "长方体有 6 个面：上面、下面、前面、后面、左面、右面各 1 个；易错：只数看得见的 3 个面。"),
  ("numeric", "standard", "一个正方体有 6 个面，每个面上都描出一个正方形，一共可以描出多少个正方形？只填数字。",
   [], "6", "正方体每个面都是正方形，6 个面就能描出 6 个正方形，6*1=6；易错：以为描出来都一样，只算 1 个。"),
  ("short-answer", "hard", "说一说圆柱和球有什么不同，为什么从球上描不出一个平平的图形。",
   [], "圆柱上下两个面是平平的圆；球的表面到处都是弯的，没有平平的面；所以球上描不出平面图形",
   "圆柱的底面、上面是平平的圆形面，可以贴着纸描出圆；球的表面处处弯曲、没有平面，所以贴着纸也描不出图形。易错：把球的「圆」和平面上的圆混为一谈。"),
 ],
 "mat_p109": [
  ("choice", "basic", "用两个完全一样的三角形，可以拼成下面哪种图形？",
   [("圆", 0), ("正方形或长方形", 1), ("球", 0), ("圆柱", 0)], "B",
   "两个完全一样的直角三角形可以拼成长方形，等腰直角三角形还能拼成正方形；圆、球、圆柱是弯的，拼不出来。"),
  ("choice", "basic", "把一张长方形纸沿着中间的折痕剪开，可以得到两个完全一样的什么图形？",
   [("圆", 0), ("长方形", 1), ("三角形", 0), ("正方形", 0)], "B",
   "沿中间横（竖）着剪开，得到两个完全一样的长方形；只有沿对角线剪才得到两个三角形。"),
  ("fill", "basic", "用 4 个完全一样的小正方形，可以拼成一个大 ___ 形（填图形名称）。", [], "正方形",
   "4 个同样的小正方形摆成 2 行 2 列，就拼成一个大正方形；易错：写成「长方形」（摆成 1 行 4 列才是长方形）。"),
  ("numeric", "standard", "用 6 个完全一样的小三角形拼图，每 3 个拼成 1 个大三角形，一共可以拼成几个大三角形？只填数字。",
   [], "2", "3 个拼 1 个，6 个里有 2 个 3：6/3=2，所以能拼成 2 个大三角形；易错：用减法算成 3 个。"),
  ("short-answer", "hard", "请说明怎样用 4 个完全相同的小正方形拼成一个大正方形，并说一拼成的图形为什么也是正方形。",
   [], "把 4 个小正方形摆成 2 行 2 列；大图形的每条边都由 2 条小边接成，四条边一样长；四个角都是直角，所以是正方形",
   "拼法：上面 2 个、下面 2 个，对齐摆成 2 行 2 列。理由：每条边都由 2 条小正方形边接成，故四条边相等；每个角仍是小正方形的直角，故四个角都是直角，所以拼成大正方形。易错：把 4 个排成 1 行，得到的是长方形。"),
 ],
 "mat_p110": [
  ("choice", "basic", "把一些扣子按「颜色」分类，下面哪种做法是对的？",
   [("把大的放一起、小的放一起", 0), ("把红色的放一堆、蓝色的放一堆", 1), ("随便分成两堆", 0), ("按形状分成三堆", 0)], "B",
   "按颜色分类，就要把同样颜色的扣子放在一起；按大小、按形状分都不是颜色这个标准。"),
  ("choice", "basic", "分类的时候，每一件物品应该放进几组里？",
   [("只放进一组", 1), ("放进两组", 0), ("放进三组", 0), ("放哪组都行", 0)], "A",
   "分类要求不重不漏：每件物品只能属于一组，否则数出来的结果会重复。易错：把两件物品同时放进两组。"),
  ("fill", "basic", "把 9 个苹果和 6 个梨按种类分开放，苹果一堆、梨一堆，一共分成几堆？只填数字。",
   [], "2", "按种类只有苹果和梨两类，所以分成 2 堆；注意问的是「几堆」不是「一共有几个」。"),
  ("numeric", "standard", "桌上有 5 个红球和 7 个白球，按颜色分类放好，红球比白球少几个？只填数字。",
   [], "2", "分类后数一数：红球 5 个、白球 7 个，7-5=2，所以红球比白球少 2 个；易错：用加法算成 12。"),
  ("short-answer", "hard", "说一说「分类」是什么意思，再举例说明怎样按同一个标准把文具分类。",
   [], "分类就是把有相同特点的物品放在一起；比如按种类分：铅笔放一起、橡皮放一起、尺子放一起；每件文具只能放进一组",
   "分类是按某个共同特点把物品分组，同一个标准要一直用到底。例如按种类分文具：铅笔、橡皮、尺子各成一组，每件只进一组，这样分组不重不漏。易错：中途换标准，或一件文具放进两组。"),
 ],
 "mat_p111": [
  ("choice", "basic", "同一堆图形，既可以按颜色分，还可以按什么分？",
   [("按大小", 0), ("按形状", 1), ("按个数", 0), ("按摆放的左右", 0)], "B",
   "形状是物品本身的特征，可以作为分类标准；个数是数出来的结果，不是物品的特征。"),
  ("choice", "basic", "同样的 8 个图形，按颜色分成 2 组，按形状分成 4 组，这说明了什么？",
   [("分类结果一定是固定的", 0), ("分类标准不同，分出的组数可能不同", 1), ("只能按颜色分", 0), ("按形状分错了", 0)], "B",
   "同一堆物品换一个标准再分，结果可以不一样：按颜色 2 组、按形状 4 组，两个结果都对。易错：认为只有一个正确答案。"),
  ("fill", "basic", "把 6 个气球按颜色分是 3 组，按大小分是 2 组，那么按大小分类一共分成几组？只填数字。",
   [], "2", "题目已经说明按大小分是 2 组，问的正是这个数；易错：把两种标准的组数相加得 5。"),
  ("numeric", "standard", "12 个图形按形状分成 3 组，平均每组有多少个？只填数字。",
   [], "4", "12 个平均分成 3 组：12/3=4，每组 4 个；易错：用减法算成 9。"),
  ("short-answer", "hard", "同一堆物品为什么可以有不同的分法？请举例说明。",
   [], "因为物品有不同的特征，比如颜色、形状、大小；选不同特征作标准，分组结果就不同；例如 6 个扣子按颜色可以分 2 组，按大小可以分 3 组",
   "分类标准取自物品的特征，特征不止一个，所以标准可以换。以 6 个扣子为例：按颜色分（红/蓝）得 2 组，按大小分（大/中/小）得 3 组，都对。易错：以为「分法不同」就说明有一次分错了。"),
 ],
 "mat_p112": [
  ("choice", "basic", "把分类的结果一个物品画一个图形、一列一列摞起来表示，这种图叫什么？",
   [("象形统计图", 1), ("线段图", 0), ("立体图", 0), ("示意图", 0)], "A",
   "一个物品用一个图形表示、一列一列摆齐，这种图叫象形统计图；它让人一眼看出谁多谁少。"),
  ("choice", "basic", "用象形统计图表示分类结果时，哪一类的图形摞得最高，说明什么？",
   [("那一类最少", 0), ("那一类最多", 1), ("每一类都一样多", 0), ("看不出来", 0)], "B",
   "象形统计图一个图形代表一个物品，摞得高说明个数多；最矮的那一列就是最少的。"),
  ("fill", "basic", "分类后苹果有 5 个、梨有 3 个，画象形统计图时，苹果那一列要比梨那一列多画几个图形？只填数字。",
   [], "2", "苹果 5 个、梨 3 个，5-3=2，苹果那一列多 2 个图形；易错：用加法算成 8。"),
  ("numeric", "standard", "统计结果：红气球 4 个、黄气球 6 个、蓝气球 2 个。画成象形统计图后，最高的一列有多少个图形？只填数字。",
   [], "6", "三列分别画 4 个、6 个、2 个图形，最高的那一列是黄气球，有 6 个；6>4>2。"),
  ("short-answer", "hard", "说一说用象形统计图整理分类结果的步骤，以及从图上能直接看出什么。",
   [], "先分类，再数出每一类有几个；每一类画一列，一个物品画一个图形，从下往上对齐摆；从图上能直接看出哪类最多、哪类最少",
   "步骤：①按标准分类并数出各类个数；②每类画一列，一个物品对应一个图形，各列底部对齐、从下往上摞；③标出类别。作用：图形高低直接反映数量多少，最多、最少一目了然。易错：不数就随手画，或各列不对齐导致看不出多少。"),
 ],
}

ex_ids = {q["id"] for q in qs}
added_q = 0
for tid, items in NEWQ.items():
    if any(q["topicId"] == tid for q in qs):
        continue
    for k, (typ, diff, prompt, opts, ans, expl) in enumerate(items):
        qid = f"{tid}_q{k+1}" if k else f"{tid}_q2"   # 槽1 用 _q2 起（与原批次命名一致）
        qid = f"{tid}_q{k+2}"
        assert qid not in ex_ids, qid
        choices = [{"label": "ABCD"[i], "text": t} for i, (t, _c) in enumerate(opts)] if typ == "choice" else []
        q = {"id": qid, "topicId": tid, "prompt": prompt, "question": prompt,
             "choices": choices, "options": [dict(c) for c in choices],
             "type": typ, "difficulty": diff, "explanation": expl, "subject": "math"}
        if typ == "choice":
            idx = [i for i, (_t, c) in enumerate(opts) if c == 1]
            assert len(idx) == 1
            q["answer"] = "ABCD"[idx[0]]
        else:
            q["answer"] = ans
        if typ == "numeric":
            # verify 用题面算式（能 eval 且等于 answer）
            q["verify"] = {"mat_p107": "2*3", "mat_p108": "6*1", "mat_p109": "6/3",
                           "mat_p110": "7-5", "mat_p111": "12/3", "mat_p112": "6"}[tid]
            assert abs(eval(q["verify"]) - float(q["answer"])) < 1e-9
        qs.append(q)
        ex_ids.add(qid)
        added_q += 1
        if k == 0:      # 首个槽位同时作为该点的 diagnostic_question
            T[tid]["diagnostic_question"] = {"question": prompt, "answer": q["answer"]}
print("新增题", added_q)

# 每点按难度升序重排
from collections import defaultdict
by = defaultdict(list)
for q in qs:
    by[q["topicId"]].append(q)
qs = [q for tid in [t["id"] for t in topics] for q in sorted(by[tid], key=lambda z: RANK[z["difficulty"]])]

print("规模：知识点", len(topics), "| 边", len(deps), "| 题", len(qs))
print("每点题数", {k: v for k, v in __import__("collections").Counter(
    __import__("collections").Counter(q["topicId"] for q in qs).values()).items()})

if WRITE:
    for path, obj in ((TP, topics), (DP, deps), (QP, qs)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("✅ 已写入", TP, DP, QP)
