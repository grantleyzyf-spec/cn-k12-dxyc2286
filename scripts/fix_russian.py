# -*- coding: utf-8 -*-
"""俄语（russian）学科数据归一：幂等、按序、只改本学科文件。

用法：
    python3 scripts/fix_russian.py           # 干跑，打印将要改的内容
    python3 scripts/fix_russian.py --write   # 落盘

做六件事：
 1. 难度别名归一：easy→basic、medium→standard（契约只允许 basic/standard/hard）。
 2. 根节点补 root_reason（唯一根 rus_p001）。
 3. dependencies 与 topics.prerequisites 双向镜像（补 topics 缺失的一侧）。
 4. 题干不足 12 字者补足（rus_q011）。
 5. diagnostic_question 空答案的 40 个知识点，按知识点语义补题补答。
 6. 课标 quote 逐字回表校正：6 条非原文引文改为原文片段；随后按重建的
    俄语课标 OCR TXT 重算 standards[].sourceLine。
 7. 选择题答案分布拉平：正确答案按 A/B/C/D 轮转落到四个位置（选项文本不
    改，只换顺序并同步 answer），消除「一半答案都是 B」的可猜测偏差。
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SUBJ = "russian"
STD_TXT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
           "《义务教育俄语课程标准》(2022年版) 扫描件OCR.txt")

DIFF_FIX = {"easy": "basic", "medium": "standard"}

ROOT_REASON = {
    "rus_p001": "起始知识点：七年级上册第一单元 Урок 1 从 33 个字母入门，"
                "此前无俄语先修内容（义务教育俄语零起点）。",
}

PROMPT_FIX = {
    "rus_q011": "元音字母я在词首读作哪个音？",
}

# 非原文引文 → 课标原文片段（逐字，见 docs/russian.md「课标回表」一节）
QUOTE_FIX = {
    "语音知识内容要求1. 掌握 33 个字母读音": "1. 掌握 33 个字母读音。",
    "1. 能正确书写 33 个大小写字母": "能正确书写 33 个大小写字母",
    "2. 初步掌握俄语书写规范。": "初步掌握俄语书写规范",
    "1. 能正确认读 33 个字母。": "能正确认读 33 个字母",
    "7. 前置词， 掌握前置词的意义和用法": "掌握前置词的意义和用法",
    "前置词， 掌握前置词的意义和用法": "掌握前置词的意义和用法",
    # 原稿「括问句」为「疑问句」之误（第 23 页高清行级重识别已确认）
    "陈述句、括问句和祈使句的意义和用法": "陈述句、疑问句和祈使句的意义和用法",
    # 原文该条用两个分号（第 21 页高清裁切已核），原稿写成逗号
    "感知词的音节和重音，了解单音节、双音节和多音节，读准重音，了解重音移动":
        "感知词的音节和重音；了解单音节、双音节和多音节；读准重音，了解重音移动",
}

# 40 个 diagnostic_question 缺答的知识点：问题 + 短答（答案给内容词，不给选项字母）
DIAG_FILL = {
    "rus_p017": ("俄语字母 ш、ж、ц 属于硬辅音还是软辅音？",
                 "ш、ж、ц 是硬辅音（ч、щ 是软辅音）"),
    "rus_p018": ("硬音符号 ъ 本身是否发音？它的作用是什么？",
                 "ъ 不发音，作用是使前面的辅音保持硬音"),
    "rus_p019": ("词末的浊辅音 г 要读成什么音？",
                 "清化为 [к]"),
    "rus_p020": ("陈述句通常使用哪种语调调型？",
                 "调型 1（ИК-1），句末语调下降"),
    "rus_p021": ("不带疑问词的一般疑问句使用哪种调型？",
                 "调型 2（ИК-2），疑问中心词上语调加强"),
    "rus_p022": ("带疑问词的特殊疑问句使用哪种调型？",
                 "调型 3（ИК-3）"),
    "rus_p023": ("俄语单词书写时，字母在四线三格中按什么原则占位？",
                 "按字母形态分别占中格，大写与上行字母再占上格，下行字母再占下格"),
    "rus_p024": ("俄语 33 个字母中元音字母、辅音字母和无音字母各多少个？",
                 "10 个元音、21 个辅音、2 个无音字母"),
    "rus_p043": ("идти 和 ходить 的主要区别是什么？",
                 "идти 表示一次性的定向运动，ходить 表示往返、经常性的不定向运动"),
    "rus_p044": ("表示乘坐某种交通工具，名词用什么格？",
                 "用 на + 名词第五格，如 на автобусе"),
    "rus_p045": ("俄语动词现在时变位有几种类型？",
                 "两种：第一变位法和第二变位法"),
    "rus_p051": ("完成体动词过去时表示什么样的动作？",
                 "表示已经完成、结果保留到现在的动作"),
    "rus_p052": ("阳性名词单数第三格通常加什么词尾？",
                 "加 -у 或 -ю"),
    "rus_p053": ("动词 дать（给）后面的接受者用什么格？",
                 "第三格，如 дать брату"),
    "rus_p054": ("表达“我感到冷”时，人称代词 я 用什么格？",
                 "第三格 мне，如 Мне холодно"),
    "rus_p055": ("阴性名词单数第五格通常加什么词尾？",
                 "加 -ой 或 -ей"),
    "rus_p056": ("表示“用钢笔写”时，ручка 用什么格？",
                 "第五格 ручкой"),
    "rus_p057": ("表达“我将成为医生”时，врач 用什么格？",
                 "第五格，如 Я буду врачом"),
    "rus_p058": ("动词 интересоваться 后面的名词用什么格？",
                 "第五格，如 интересоваться музыкой"),
    "rus_p059": ("句型 Мне нравится... 中，мне 为什么用第三格？",
                 "第三格表示喜欢的感受者，即“谁喜欢”"),
    "rus_p060": ("молоко（牛奶）属于可数名词还是不可数名词？",
                 "不可数名词，一般不用复数形式"),
    "rus_p061": ("动词 дать 表示“给一点水”时，вода 用什么格？",
                 "第二格 воды，表示部分概念"),
    "rus_p062": ("俄语名词单数第三格和第五格分别表示什么基本意义？",
                 "第三格表示间接客体，第五格表示工具、方式或身份"),
    "rus_p068": ("运动动词 идти 的完成体对应形式是什么？",
                 "пойти"),
    "rus_p069": ("形容词阳性单数第五格加什么词尾？",
                 "加 -ым 或 -им"),
    "rus_p070": ("购物时询问价格常用哪个疑问句？",
                 "Сколько стоит ...?（多少钱）"),
    "rus_p071": ("名词复数第三格通常加什么词尾？",
                 "加 -ам 或 -ям"),
    "rus_p072": ("形容词和代词复数第三格加什么词尾？",
                 "加 -ым 或 -им"),
    "rus_p073": ("名词复数第六格通常加什么词尾？",
                 "加 -ах 或 -ях"),
    "rus_p074": ("形容词和代词复数第六格加什么词尾？",
                 "加 -ых 或 -их"),
    "rus_p075": ("动物名词复数第四格与哪一格形式相同？",
                 "与第二格形式相同"),
    "rus_p076": ("非动物名词复数第四格与哪一格形式相同？",
                 "与第一格形式相同"),
    "rus_p077": ("反身代词 свой 表示什么意思？",
                 "表示“自己的”，随所修饰名词的性、数、格变化"),
    "rus_p078": ("名词复数第三格、第四格、第六格分别对应哪些词尾？",
                 "第三格 -ам/-ям，第六格 -ах/-ях，第四格动物同第二格、非动物同第一格"),
    "rus_p091": ("表示“在星期一”时，понедельник 用什么格？",
                 "第四格，如 в понедельник"),
    "rus_p092": ("“在空闲时间”用俄语怎么表达？",
                 "в свободное время"),
    "rus_p093": ("动词第二人称命令式常用的词尾有哪些？",
                 "-и 或 -й，如 пиши、читай"),
    "rus_p094": ("Купите мне, пожалуйста 表达的是什么语气？",
                 "礼貌的请求"),
    "rus_p095": ("购物时想比较两件商品的贵贱，常用哪两个词？",
                 "дешевле / дороже（更便宜 / 更贵）"),
    "rus_p096": ("九年级上册重点复习了哪两类语法内容？",
                 "名词复数各格变化与动词命令式"),
}

PUNCT = "，。；：、！？（）()“”\"'‘’《》〈〉…—－-.,;:!?·"


def norm(s):
    return re.sub(r"\s+", "", s or "")


def norm_loose(s):
    return "".join(ch for ch in norm(s) if ch not in PUNCT)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def quote_positions():
    """课标 OCR 源 → (去空白去标点文本, 下标→原文件行号)。"""
    text = open(STD_TXT, encoding="utf-8", errors="ignore").read()
    chars, lines, line = [], [], 1
    for ch in text:
        if ch == "\n":
            line += 1
            continue
        if ch.isspace() or ch in PUNCT:
            continue
        chars.append(ch)
        lines.append(line)
    return "".join(chars), lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    tp = os.path.join(DATA, SUBJ, "topics.json")
    dp = os.path.join(DATA, SUBJ, "dependencies.json")
    qp = os.path.join(DATA, SUBJ, "questions.json")
    topics, deps, qs = load(tp), load(dp), load(qp)
    T = {t["id"]: t for t in topics}
    Q = {q["id"]: q for q in qs}
    changes = []

    # 1. 难度别名
    for q in qs:
        if q.get("difficulty") in DIFF_FIX:
            changes.append(f"难度 {q['id']}: {q['difficulty']} → {DIFF_FIX[q['difficulty']]}")
            q["difficulty"] = DIFF_FIX[q["difficulty"]]

    # 2. 根节点 root_reason
    for tid, reason in ROOT_REASON.items():
        if not T[tid].get("root_reason"):
            changes.append(f"root_reason {tid}")
            T[tid]["root_reason"] = reason

    # 3. 双向镜像
    for e in deps:
        a, b = e["from"], e["to"]
        pre = T[b].setdefault("prerequisites", [])
        if a not in pre:
            pre.append(a)
            pre.sort()
            changes.append(f"先修镜像 {b} += {a}")

    # 4. 题干补足
    for qid, prompt in PROMPT_FIX.items():
        if len(Q[qid]["prompt"]) < 12:
            changes.append(f"题干 {qid}: {Q[qid]['prompt']} → {prompt}")
            Q[qid]["prompt"] = prompt
            Q[qid]["question"] = prompt

    # 5. diagnostic_question 补题补答
    for tid, (ask, ans) in DIAG_FILL.items():
        dq = T[tid].setdefault("diagnostic_question", {})
        if not (dq.get("question") or "").strip() or not (dq.get("answer") or "").strip():
            changes.append(f"诊断题 {tid}")
            dq["question"], dq["answer"] = ask, ans

    # 6. quote 校正 + sourceLine 重算
    src, linemap = quote_positions()
    for t in topics:
        for s in t.get("standards", []):
            q = s.get("quote", "")
            if q in QUOTE_FIX:
                changes.append(f"引文 {t['id']} {s['id']}: {q} → {QUOTE_FIX[q]}")
                s["quote"] = QUOTE_FIX[q]
            pos = src.find(norm_loose(s["quote"]))
            line = linemap[pos] if pos >= 0 else None
            if line and s.get("sourceLine") != line:
                changes.append(f"sourceLine {t['id']} {s['id']}: {s.get('sourceLine')} → {line}")
                s["sourceLine"] = line
            if pos < 0:
                print(f"⚠️ 回表失败 {t['id']} {s['id']}: {s['quote']}")

    # 7. 选择题答案位置轮转（幂等：已在目标位置的题不动）
    cycle = ["A", "B", "C", "D"]
    for i, q in enumerate(sorted((x for x in qs if x.get("type") == "choice"),
                                 key=lambda x: x["id"])):
        target = cycle[i % 4]
        if q.get("answer") == target:
            continue
        labels = [o["label"] for o in q["options"]]
        cur = labels.index(q["answer"]) if q.get("answer") in labels else 0
        tgt = labels.index(target)
        opts = q["options"]
        opts[cur], opts[tgt] = opts[tgt], opts[cur]
        for j, o in enumerate(opts):
            o["label"] = cycle[j]
        q["answer"] = target
        changes.append(f"答案位置 {q['id']}: → {target}")

    print(f"共 {len(changes)} 处变更" + ("" if args.write else "（干跑）"))
    for c in changes[:400]:
        print("  ·", c)
    if len(changes) > 40:
        print(f"  … 另 {len(changes) - 40} 处")
    if args.write:
        dump(tp, topics)
        dump(dp, deps)
        dump(qp, qs)
        print("已写入 topics.json / dependencies.json / questions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
