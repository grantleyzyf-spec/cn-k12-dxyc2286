#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给北师大版数学知识点挂课标（引文取自 docx 版课标的干净原文，逐字回表）。

为什么不用 OCR 版 TXT：OCR 版把「减法」写成「袜法」、「熟练」写成「郊练」，
引文会带错字。这里改用
`…/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订)（docx转换）.txt`
（由官方 docx 直接转换，100 684 字符，无 OCR 噪声）。

引文库按「学段 × 领域」人工裁定（每条都要能在干净原文里逐字命中，脚本自检）；
知识点按「课时名+单元名」正则归到某一条，命中强判 partial、弱判 inferred。
`standards.id` = `mbs-2022:<学段码>.<领域码>.<条内序号>`。

用法: python3 scripts/attach_bsd_std.py [--root data/math-bsd] [--write]
"""
import argparse, json, os, re

TXT = os.path.expanduser("~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
                         "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订)（docx转换）.txt")
DOM_CODE = {"数与代数": "SD", "图形与几何": "TX", "统计与概率": "TJ", "综合与实践": "ZH"}
STAGE_OF_GRADE = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 4}

# 引文库：每条 (学段, 领域, 序号, 正则, 引文)。引文必须能在干净课标原文里逐字命中。
POOL = [
    (1, "数与代数", "01", r"数一数|认[识读]|书写|序数|几和第几|认识0|6到10|10$|数的认识|大数",
     "在实际情境中感悟并理解万以内数的意义，理解数位的含义，知道用算盘可以表示多位数"),
    (1, "数与代数", "02", r"比较多少|大于号|小于号|等于号|比大小|比较",
     "了解符号<,=,>的含义，会比较万以内数的大小；通过数的大小比较，感悟相等和不等关系"),
    (1, "数与代数", "03", r"加减|加法|减法|运算|0的加减|四则",
     "在具体情境中，了解四则运算的意义，感悟运算之间的关系"),
    (1, "数与代数", "04", r"综合练习|算理|算法|口算",
     "探索加法和减法的算理与算法，会整数加减法"),
    (1, "数与代数", "05", r"解决问题|应用|数量关系|规律",
     "在简单的生活情境中，运用数和数的运算解决问题，能解释结果的实际意义，形成初步的应用意识"),
    (1, "图形与几何", "01", r"图形|立体|搭|拼|我说你做|观察物体|分类", 
     "通过实物和模型辨认简单的立体图形和平面图形，能对图形分类，会用简单图形拼图"),
    (1, "图形与几何", "02", r"测量|长度|米|厘米|量一量",
     "结合生活实际，体会建立统一度量单位的重要性，认识长度单位米、厘米"),
    (1, "统计与概率", "01", r"分类|整理",
     "会对物体、图形或数据进行分类，初步了解分类与分类标准的关系，形成初步的数据意识"),
    (1, "综合与实践", "01", r"游戏|拓展|实践|活动|数学好玩",
     "在具体情境中，回顾自己在学前阶段经历的与数学学习相关的活动"),
]


def norm(s):
    return re.sub(r"\s+", "", s or "")


RULES = [
    # 顺序＝优先级（越具体越前）。sid → 引文库里的 (学段,领域,序号) 三元组
    (r"游戏|拓展|实践", "1.ZH.01"),
    (r"分类|整理", "1.TJ.01"),
    (r"测量|米|厘米|量一量", "1.TX.02"),
    (r"图形|立体|搭|拼|我说你做|观察物体", "1.TX.01"),
    (r"大于号|小于号|等于号|比大小|比较多少|比较", "1.SD.02"),
    (r"综合练习|算理|算法|口算", "1.SD.04"),
    (r"加减|加法|减法|运算|0的", "1.SD.03"),
    (r"规律|解决问题|应用", "1.SD.05"),
    (r"数一数|几和第几|认识|书写|序数|大数|10", "1.SD.01"),
]
DEFAULT_SID = {"数与代数": "1.SD.01", "图形与几何": "1.TX.01",
               "统计与概率": "1.TJ.01", "综合与实践": "1.ZH.01"}
SEG2DOM = {"SD": "数与代数", "TX": "图形与几何", "TJ": "统计与概率", "ZH": "综合与实践"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/math-bsd")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    raw = open(TXT, encoding="utf-8", errors="ignore").read()
    N = norm(raw)
    lines = raw.split("\n")

    bad = [(q[:12]) for _, _, _, _, q in POOL if norm(q) not in N]
    if bad:
        raise SystemExit(f"引文未在课标原文命中：{bad}")
    print(f"引文库 {len(POOL)} 条，全部逐字回表命中 ✅")
    QUOTE = {f"{st}.{DOM_CODE[dom]}.{no}": q for st, dom, no, _, q in POOL}

    topics = json.load(open(f"{a.root}/topics.json", encoding="utf-8"))
    for t in topics:
        key = t["name"] + " " + t.get("chapter", "")
        sid = None
        for pat, cand in RULES:
            if re.search(pat, key):
                # 领域要对得上（分类不能挂到图形，图形不能挂到数代数）
                if SEG2DOM[cand.split(".")[1]] == t["domain"] or cand.endswith("ZH.01"):
                    sid = cand
                    break
        if not sid:
            sid = DEFAULT_SID[t["domain"]]
        quote = QUOTE[sid]
        conf = "partial" if SEG2DOM[sid.split(".")[1]] == t["domain"] else "inferred"
        line = next((i + 1 for i, l in enumerate(lines) if norm(quote)[:10] in norm(l)), 0)
        t["standards"] = [{"id": f"mbs-2022:{sid}", "confidence": conf,
                           "quote": quote, "sourceLine": line}]
        t["curriculumRef"] = f"mbs-2022:{sid}"

    for t in topics:
        if not t.get("prerequisites") and not t.get("root_reason"):
            head = t["chapter"].split(" ", 1)
            t["root_reason"] = (f"起始知识点：《{head[0]}》{head[1] if len(head) > 1 else ''}的第 1 课时，"
                                "本单元无更早的校内先修；跨册衔接以 soft 边表示")

    from collections import Counter
    print(f"挂课标 {sum(1 for t in topics if t.get('standards'))}/{len(topics)} | confidence:",
          dict(Counter(t['standards'][0]['confidence'] for t in topics)))
    print("条目复用:", dict(Counter(t['standards'][0]['id'] for t in topics)))
    if a.write:
        json.dump(topics, open(f"{a.root}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(f"{a.root}/topics.json", "a", encoding="utf-8").write("\n")
        print("written", f"{a.root}/topics.json")


if __name__ == "__main__":
    main()
