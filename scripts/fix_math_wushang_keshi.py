# -*- coding: utf-8 -*-
"""五年级上册课时级核对（读人工《每节内容对应页码》TXT）后的收口：

① 补 3 个真缺知识点（教材有独立课时、图谱无对应点）
   第四单元 设计图案            → mat_p962 图形的运动的应用（设计图案）
   第六单元 组合图形的面积      → mat_p961 组合图形的面积
   第七单元 初步认识可能性      → mat_p963 随机现象与可能性（初步认识）
② 修 2 处章号/编号口径（据教材目录：有趣的密铺是不编号的综合实践，可能性才是第七单元）
   「五年级上册 第七单元 有趣的密铺」→「五年级上册 综合与实践 有趣的密铺」
   「五年级上册 第八单元 可能性」    →「五年级上册 第七单元 可能性」

用法：python3 fix_wushang_keshi.py [--write]
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
    "tu": ("对给定的简单图形，能用平移、旋转和轴对称的方法，在方格纸上设计图案，并能说出设计图案与简单图形的关系", "exact"),
    "zh": ("引导学生运用转化的思想，推导平行四边形、三角形、梯形、圆等平面图形的面积公式，形成空间观念和推理意识", "partial"),
    "kn": ("能列举生活中的随机现象，列出简单随机现象中所有可能发生的结果，判断简单随机现象发生可能性的大小", "exact"),
}
SID = {"tu": "mat-2022:3.XY.24", "zh": "mat-2022:3.TS.32", "kn": "mat-2022:3.TS.33"}

UNITS = [
    dict(id="mat_p961", name="组合图形的面积", grade=5, semester="上",
         chapter="五年级上册 第六单元 多边形的面积", domain="图形与几何", type="procedural",
         desc="会把组合图形分割或补全成学过的基本图形（长方形、平行四边形、三角形、梯形），先分别求面积再求和或求差，能根据图形特点选择合适的分割方法",
         mastery=["能把组合图形分成学过的基本图形并算出总面积", "能说出分割法与补法的适用情形"],
         tags=["图形与几何", "多边形的面积", "组合图形"], pre=["mat_p304", "mat_p305"], std=["zh"]),
    dict(id="mat_p962", name="图形的运动的应用（设计图案）", grade=5, semester="上",
         chapter="五年级上册 第四单元 图形的运动", domain="图形与几何", type="application",
         desc="能用平移、旋转和轴对称在方格纸上设计简单图案，能说出设计出的图案与基本图形之间的关系，能欣赏生活中的对称与旋转图案",
         mastery=["能用轴对称或旋转变换在方格纸上复制并拼出图案", "能说出图案由哪个基本图形经过什么变换得到"],
         tags=["图形与几何", "图形的运动", "图案设计"], pre=["mat_p219", "mat_p220"], std=["tu"]),
    dict(id="mat_p963", name="随机现象与可能性（初步认识）", grade=5, semester="上",
         chapter="五年级上册 第七单元 可能性", domain="统计与概率", type="conceptual",
         desc="知道生活中有确定现象与随机现象，能用「一定」「可能」「不可能」描述事件，能列出简单随机现象所有可能发生的结果，并对可能性大小作定性判断",
         mastery=["能用一定/可能/不可能描述事件", "能列举简单随机现象的全部可能结果并比较可能性大小"],
         tags=["统计与概率", "可能性", "随机现象"], pre=[], std=["kn"],
         root="起始知识点：小学阶段「随机现象发生的可能性」主题的入口，图谱内更早没有概率类知识点"),
]

QS = {
 "mat_p961": [
  ("choice", "basic", "求组合图形的面积，常用的两种方法是？",
   [("分割法和补全法", 1), ("加减法和乘除法", 0), ("平移法和旋转法", 0), ("估算法和测量法", 0)], "",
   "组合图形由几个基本图形拼成：把它分成几块（分割法）分别求面积再相加，或补成一个大图形再减去多补的部分（补全法）。"),
  ("choice", "basic", "一个长方形里去掉一个三角形（如图阴影部分），求阴影面积的正确做法是？",
   [("长方形面积 − 三角形面积", 1), ("长方形面积 + 三角形面积", 0), ("长方形周长 − 三角形周长", 0), ("三角形面积 × 2", 0)], "",
   "从整体里挖去一块，用「整体减部分」：阴影面积 = 长方形面积 − 三角形面积。混淆成加法是常见错误。"),
  ("fill", "basic", "把组合图形分割成两个长方形，一个面积 24 平方厘米，另一个 18 平方厘米，组合图形面积是___平方厘米（只填数字）。", [], "42",
   "分割法把面积相加：24+18 = 42（平方厘米）。易错：把两块相减得 6。"),
  ("numeric", "standard", "一个正方形边长 6 厘米，在其中一角剪去一个直角边为 2 厘米的等腰直角三角形，剩下部分的面积是多少平方厘米？只填数字。", [], "34",
   "正方形面积 6×6=36，三角形面积 2×2÷2=2，剩余 36-2=34（平方厘米），即 6*6-2*2/2=34。"),
  ("short-answer", "hard", "请说明分割法与补全法各自的适用情形，并各举一例。", [],
   "分割法适用于图形能干净地分成几个学过的基本图形（如 L 形分成两个长方形）；补全法适用于图形缺一块、补成大图形后更容易算（如从长方形中挖去三角形）；两种方法都要先看清边界再动笔，算完检查单位",
   "选法看「哪条辅助线最短、切出的图形是否有现成公式」。分割法：切口不穿越未知区域；补全法：补出的整体是标准图形、多补部分好算。两种方法可互相验算，结果应一致。"),
 ],
 "mat_p962": [
  ("choice", "basic", "用图形的运动设计图案，主要用到哪三种变换？",
   [("平移、旋转、轴对称", 1), ("加、减、乘", 0), ("测量、画图、裁剪", 0), ("估算、验算、比较", 0)], "",
   "图案设计的三把工具就是平移、旋转（含绕点旋转）与轴对称（翻折），它们都不改变图形的形状和大小。"),
  ("choice", "basic", "把一个基本图形沿某条直线翻折得到另一个图形，这种变换是？",
   [("轴对称（翻折）", 1), ("平移", 0), ("旋转", 0), ("放大", 0)], "",
   "沿直线翻折得到的是轴对称图形，这条直线就是对称轴。平移是沿方向直移、旋转是绕点转动，都不产生镜像。"),
  ("fill", "basic", "把图形向右平移 4 格、再向右平移 3 格，相当于向右平移___格（只填数字）。", [], "7",
   "同方向两次平移可合并：4+3 = 7（格）。这与旋转不能简单相加不同。"),
  ("numeric", "standard", "把一个图案绕它的中心顺时针旋转 90°，连续旋转 4 次回到原样。每次旋转多少度、共转多少度？请填 4 次累计的度数。", [], "360",
   "每次 90°，4 次共 90×4=360（度），正好回到原来方向，即 90*4=360。"),
  ("short-answer", "hard", "请说明怎样用轴对称与旋转设计一个花边图案。", [],
   "先选定一个基本图形，画一条对称轴，用轴对称得到相邻的镜像图形；再选一个旋转中心，把基本图形绕它按固定角度重复旋转，得到环绕的图案；最后检查各处变换是否一致，整幅图案就由这两种运动组合而成",
   "设计思路是「以一个基本图形为单位，用变换批量复制」。轴对称负责镜像（左右/上下成对），旋转负责环绕（绕中心等角度重复），平移负责成排。三种配合可做出花边、瓷砖纹样等。"),
 ],
 "mat_p963": [
  ("choice", "basic", "「太阳从东方升起」这件事属于？",
   [("一定发生", 1), ("可能发生", 0), ("不可能发生", 0), ("无法判断", 0)], "",
   "这是确定现象，必然发生，用「一定」描述。可能性只用于随机现象，如「明天下雨」。"),
  ("choice", "basic", "袋子里有 3 个红球、1 个白球（除颜色外都相同），任意摸一个，摸到哪种球的可能性大？",
   [("红球", 1), ("白球", 0), ("一样大", 0), ("无法比较", 0)], "",
   "球除颜色外完全相同，个数多的那种被摸到的可能性更大：红球 3 个多于白球 1 个，所以摸到红球的可能性大。"),
  ("fill", "basic", "一个正方体骰子，任意掷一次，出现的点数有___种可能（只填数字）。", [], "6",
   "骰子六个面分别是 1~6，共有 6 种可能结果，且每个结果出现的可能性相同。"),
  ("numeric", "standard", "袋子里有 2 个红球和 6 个白球，任意摸一个，可能的颜色共有几种？只填数字。", [], "2",
   "只按颜色分类，可能结果只有「红」或「白」2 种，即 2 种可能结果（球的总数 8 个不决定结果种数）。易错：答 8。"),
  ("short-answer", "hard", "请说明怎样判断一件事件是「一定」「可能」还是「不可能」发生，并各举一例。", [],
   "看条件是否允许：在给定条件下必然发生的用「一定」（如太阳东升）；必然不发生的用「不可能」（如袋子里只有红球却摸出蓝球）；可能发生也可能不发生的用「可能」（如掷骰子得到 6），这就是随机现象",
   "判断三步：①列出所有可能结果；②看目标事件是否一定在结果里（一定）、一定不在（不可能）、或部分在（可能）；③对「可能」事件，再用结果个数或面积比较可能性大小。"),
 ],
}

VERIFY = {"mat_p961": "6*6-2*2/2", "mat_p962": "90*4", "mat_p963": "2"}

topics = json.load(open(TP, encoding="utf-8"))
deps = json.load(open(DP, encoding="utf-8"))
qs = json.load(open(QP, encoding="utf-8"))
T = {t["id"]: t for t in topics}

# ① 章号/编号修正
fix = 0
for t in topics:
    if t["chapter"] == "五年级上册 第七单元 有趣的密铺":
        t["chapter"] = "五年级上册 综合与实践 有趣的密铺"
        fix += 1
    elif t["chapter"] == "五年级上册 第八单元 可能性":
        t["chapter"] = "五年级上册 第七单元 可能性"
        fix += 1

# ② 新增知识点
LBL = "ABCD"
added_t, added_e, added_q = [], 0, 0
for u in UNITS:
    if u["id"] in T:
        continue
    stds = [{"id": SID[c], "confidence": STD[c][1], "quote": STD[c][0]} for c in u["std"]]
    node = {
        "id": u["id"], "name": u["name"], "subject": "math", "domain": u["domain"],
        "grade": u["grade"], "semester": u["semester"], "chapter": u["chapter"], "type": u["type"],
        "description": u["desc"], "mastery_criteria": u["mastery"],
        "diagnostic_question": {"question": "", "answer": ""}, "external": False,
        "standards": stds, "tags": u["tags"], "prerequisites": u["pre"],
        "curriculumRef": stds[0]["id"], "verified": False,
    }
    if u.get("root"):
        node["root_reason"] = u["root"]
    topics.append(node)
    T[u["id"]] = node
    added_t.append(u["id"])

pairs = {(e["from"], e["to"]) for e in deps}
for u in UNITS:
    for p in u["pre"]:
        if p not in T:
            print(f"⚠ 先修点不存在：{p}")
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

print(f"章号/编号修正 {fix} 处 · 新增 {len(added_t)}：{added_t} · 边 +{added_e} · 题 +{added_q}")
print(f"规模：点 {len(topics)} · 边 {len(deps)} · 题 {len(qs)}")
print("每点题数", dict(Counter(Counter(q['topicId'] for q in qs).values())))

if WRITE:
    for path, obj in ((TP, topics), (DP, deps), (QP, qs)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("✅ 已写入")
