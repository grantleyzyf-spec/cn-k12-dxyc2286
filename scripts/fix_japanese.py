# -*- coding: utf-8 -*-
"""日语学科数据归一（收口用）。用法: python3 scripts/fix_japanese.py [--write]

幂等。做六件事：
1. 难度归一：easy→basic / medium→standard；再把 4 道真正高级的题标 hard（三档齐备）；
2. 领域归一：语音 / 词汇 / 语法 / 听力 / 阅读 / 写作 / 文化（对齐课标「语言知识＋语言技能＋文化」）；
3. 题干 <12 字的补足上下文（原题干像残句）；
4. 修掉题目硬伤：同题多个选项文本相同（等于没有干扰项）、双正解题；
5. 根节点补 root_reason；
6. 边双向镜像（deps 有 / topics.prerequisites 缺）+ sourceLine 按课标 TXT 首现行号重算。
"""
import json
import os
import re
import sys

S = "japanese"
WRITE = "--write" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（17）普通高中日语课程标准（2017年版2020年修订）.txt"

tp, qp = f"{D}/{S}/topics.json", f"{D}/{S}/questions.json"
topics = json.load(open(tp, encoding="utf-8"))
qs = json.load(open(qp, encoding="utf-8"))
deps = json.load(open(f"{D}/{S}/dependencies.json", encoding="utf-8"))

# ---------- 1. 难度 ----------
DIFF = {"easy": "basic", "medium": "standard"}
HARD = {"jpn_q023", "jpn_q024", "jpn_q032", "jpn_q034"}  # 被动/使役、敬语、推测样态、语法综合

# ---------- 2. 领域 ----------
DOMAIN = {
    "jpn_h001": "语音", "jpn_h002": "语音", "jpn_h003": "语音", "jpn_h004": "语音",
    "jpn_h005": "词汇", "jpn_h006": "词汇", "jpn_h026": "词汇", "jpn_h033": "词汇",
    "jpn_h007": "语法", "jpn_h008": "语法", "jpn_h009": "语法", "jpn_h010": "语法",
    "jpn_h011": "语法", "jpn_h012": "语法", "jpn_h018": "语法", "jpn_h019": "语法",
    "jpn_h020": "语法", "jpn_h021": "语法", "jpn_h022": "语法", "jpn_h023": "语法",
    "jpn_h024": "语法", "jpn_h025": "语法", "jpn_h031": "语法", "jpn_h032": "语法",
    "jpn_h034": "语法",
    "jpn_h013": "听力", "jpn_h027": "听力", "jpn_h036": "听力",
    "jpn_h014": "阅读", "jpn_h028": "阅读", "jpn_h035": "阅读",
    "jpn_h015": "写作", "jpn_h029": "写作", "jpn_h037": "写作",
    "jpn_h016": "文化", "jpn_h017": "文化", "jpn_h030": "文化", "jpn_h038": "文化", "jpn_h039": "文化",
}

# ---------- 3. 题干补足（原 <12 字，补上下文，答案不变） ----------
PROMPT_FIX = {
    "jpn_q003": "下列日语单词中，哪一个含有促音（小写「っ」）？",
    "jpn_q005": "汉字「水」对应的日语读法（假名）是哪一项？",
    "jpn_q006": "日语动词「食べる」的中文意思是什么？",
    "jpn_q011": "下列日语词中属于形容动词（な形容词）的是哪一个？",
    "jpn_q012": "い形容词「暑い」的过去式（た形）是哪一项？",
    "jpn_q017": "日本人开始吃饭前通常会说的寒暄语是哪一句？",
    "jpn_q018": "一类动词「書く」的て形（连用形音便）是哪一项？",
    "jpn_q021": "动词可能形「書ける」表示的中文意思是什么？",
    "jpn_q026": "日语副词「やはり」在句中的意思是什么？",
    "jpn_q030": "日本传统的七夕节（たなばた）是几月几日？",
    "jpn_q033": "日语汉字词「努力」的音读（假名）是哪一项？",
}

# ---------- 4. 题目硬伤 ----------
# q010: A/B 选项文本完全相同（都是「かきます」）；q018: A/C/D 三选项全同；
# q015: A「私は王です。」本身也正确，属双正解；q031: 「降れば」与「降ったら」都成立，属双正解。
OPTION_FIX = {
    "jpn_q010": {
        "prompt": "一类动词「書く」的ます形（礼貌体）是哪一项？",
        "options": [
            {"label": "A", "text": "かきます"},
            {"label": "B", "text": "かくます"},
            {"label": "C", "text": "かきります"},
            {"label": "D", "text": "かきました"},
        ],
        "answer": "A",
        "explanation": "一类动词「書く」把词尾「く」改成「き」再加「ます」→「かきます」。「かくます」是把辞书形直接加ます的错形。",
    },
    "jpn_q018": {
        "prompt": "一类动词「書く」的て形（连用形音便）是哪一项？",
        "options": [
            {"label": "A", "text": "かいて"},
            {"label": "B", "text": "かっで"},
            {"label": "C", "text": "かきて"},
            {"label": "D", "text": "かくて"},
        ],
        "answer": "A",
        "explanation": "「く」结尾的一类动词て形发生イ音便：「書く」→「かいて」。「かっで」是「ぐ」结尾（如「泳ぐ→泳いで」）的连浊形。",
    },
    "jpn_q015": {
        "prompt": "下列哪一句是完整的日文自我介绍开头（姓名＋寒暄结语）？",
        "options": [
            {"label": "A", "text": "私が王さんです。"},
            {"label": "B", "text": "私は王と申します。どうぞよろしくお願いします。"},
            {"label": "C", "text": "王は私。"},
            {"label": "D", "text": "王です私。"},
        ],
        "answer": "B",
        "explanation": "自我介绍用「私は〜と申します／〜です」＋「どうぞよろしくお願いします」；A 用「が」且自称加「さん」，C、D 语序残缺。",
    },
    "jpn_q031": {
        "prompt": "「〜たら」（假定条件）的接续形式，下列哪一项正确？",
        "options": [
            {"label": "A", "text": "降るたら"},
            {"label": "B", "text": "降ったら"},
            {"label": "C", "text": "降りたら"},
            {"label": "D", "text": "降れたら"},
        ],
        "answer": "B",
        "explanation": "「〜たら」由动词た形＋「ら」构成，「降る」的た形是「降った」，故为「降ったら」；接辞书形或ます形词干都错。",
    },
}

EXPL_FIX = {
    "jpn_q016": "早上见面用「おはようございます」，是礼貌体的早安问候；「こんばんは」用于晚上，「おやすみなさい」是睡前道别。",
}

# ---------- 执行 ----------
n_diff = n_domain = n_prompt = n_opt = n_expl = n_root = n_edge = n_line = 0

for t in topics:
    want = DOMAIN.get(t["id"])
    if want and t.get("domain") != want:
        t["domain"] = want
        n_domain += 1

for q in qs:
    if q.get("difficulty") in DIFF:
        q["difficulty"] = DIFF[q["difficulty"]]
        n_diff += 1
    if q["id"] in HARD and q.get("difficulty") != "hard":
        q["difficulty"] = "hard"
    fix = OPTION_FIX.get(q["id"])
    if fix:
        q["prompt"] = q["question"] = fix["prompt"]
        q["options"] = fix["options"]
        q["answer"] = fix["answer"]
        q["explanation"] = fix["explanation"]
        n_opt += 1
    elif q["id"] in PROMPT_FIX and len(q.get("prompt", "")) < 12:
        q["prompt"] = q["question"] = PROMPT_FIX[q["id"]]
        n_prompt += 1
    if q["id"] in EXPL_FIX:
        q["explanation"] = EXPL_FIX[q["id"]]
        n_expl += 1

# 根节点 root_reason
for t in topics:
    if not t.get("prerequisites") and not t.get("root_reason"):
        t["root_reason"] = (
            f"起始知识点：{(t.get('chapter') or '')[:24]} 是高中日语的入门内容，"
            "图谱内无更早前置（义务段日语未建点，跨学段前置不单独连边）"
        )
        n_root += 1

# 边双向镜像：以 dependencies.json 为准
T = {t["id"]: t for t in topics}
for e in deps:
    a, b = e["from"], e["to"]
    if a in T and b in T and a not in T[b].setdefault("prerequisites", []):
        T[b]["prerequisites"].append(a)
        n_edge += 1
for t in topics:
    t["prerequisites"] = sorted(set(t.get("prerequisites") or []))

# sourceLine 重算（去空白全文的字符位置 → 行号）
if os.path.exists(TXT):
    raw = open(TXT, encoding="utf-8").read().split("\n")
    starts, acc = [], 0
    for i, line in enumerate(raw, 1):
        starts.append((acc, i))
        acc += len(re.sub(r"\s+", "", line))
    full = re.sub(r"\s+", "", "".join(raw))
    import bisect
    offs = [s[0] for s in starts]

    def line_of(ch):
        i = bisect.bisect_right(offs, ch) - 1
        return starts[max(i, 0)][1]

    for t in topics:
        for s in t.get("standards", []):
            qq = re.sub(r"\s+", "", s.get("quote") or "")
            pos = full.find(qq) if qq else -1
            if pos >= 0 and s.get("sourceLine") != line_of(pos):
                s["sourceLine"] = line_of(pos)
                n_line += 1
else:
    print("!! 课标 TXT 不存在，跳过 sourceLine 重算：", TXT)

print(f"领域归一 {n_domain} | 难度归一 {n_diff} | 题干补足 {n_prompt} | 重写选项/题 {n_opt} "
      f"| 解析改写 {n_expl} | 根节点 reason {n_root} | 补镜像边 {n_edge} | sourceLine 修正 {n_line}")
print("领域:", {k: sum(1 for t in topics if t["domain"] == k) for k in
               ("语音", "词汇", "语法", "听力", "阅读", "写作", "文化")})
print("难度:", {k: sum(1 for q in qs if q["difficulty"] == k) for k in ("basic", "standard", "hard")})
print("题型:", {k: sum(1 for t in topics if t["type"] == k) for k in
               ("conceptual", "procedural", "reasoning", "modeling", "application")})
print("仍 <12 字题干:", [q["id"] for q in qs if len(q["prompt"]) < 12])
dup = [q["id"] for q in qs if len({o["text"] for o in q["options"]}) != len(q["options"])]
print("仍有重复选项文本:", dup)
print("仍缺 root_reason 的根节点:", [t["id"] for t in topics if not t["prerequisites"] and not t.get("root_reason")])

if WRITE:
    for path, obj in ((tp, topics), (qp, qs)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("written:", tp, qp)
