#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版数学合并后收口修复（幂等）：
 1 高中册 grade/semester 按仓库口径重排：必修一 10 / 必修二 11 / 必修三 12 / 选必一 13 / 选必二 14，semester 全「上」
 2 描述不足 40 汉字的点补足（按各点实际内容续写，不写套话）
 3 课标引文统一取仓库同一 id 的原句（同 id 只能有一套 quote）：按名称相似度在仓库同主线条目里挑最贴近的一条
用法：python3 /tmp/fix_hj_closeout.py [--write]
"""
import difflib
import json
import os
import re
import sys

D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data")
HJ = f"{D}/math-hujiao"

GRADE = {"沪教版必修第一册": 10, "沪教版必修第二册": 11, "沪教版必修第三册": 12,
         "沪教版选择性必修第一册": 13, "沪教版选择性必修第二册": 14}

DESC = {
    "mhj_h005": "统整函数的概念与两个要素、奇偶性与单调性、最值与零点、实际建模以及反函数的概念；"
                "能用定义判断函数是否相同，能借图像读出单调区间与最值，并把实际问题化成函数模型求解。",
    "mhj_h1020": "理解 y=A sin(ωx+φ) 中振幅、最小正周期、频率、相位与初始相位的含义，会用五点法作出它在一个周期上的图像；"
                 "能说明 A、ω、φ 各自改变图像的哪一处，并把简谐运动、交流电等情境翻译成该模型。",
    "mhj_h1030": "借助公理1、公理2及其三个推论判断点与直线共面，并用公理3确定两个相交平面的交线；"
                 "能画出斜二测直观图，会用反证法说明「三点共面」「四边共面」这类结论成立的理由。",
    "mhj_h1070": "掌握乘法原理与加法原理的适用条件，能按步骤或按类别完成计数，做到不重不漏；"
                 "能判断一个计数问题是分步还是分类，并写出完整的乘法或加法算式说明依据。",
    "mhj_h1071": "理解排列的定义与排列数公式，能用直接法、间接法、捆绑法处理带限制条件的排列问题；"
                 "能区分「排成一列」与「任取几个」两种问法，并把相邻、不相邻条件翻译成相应的处理方法。",
    "mhj_h1072": "理解组合的定义与组合数公式，能用组合数的两个性质化简计算并解决选取与分配问题；"
                 "能说明同一情境下何时用排列、何时用组合，并用对称性与递推性质检验计算结果是否合理。",
    "mhj_h1073": "能把古典概率问题归结为排列组合计数，用样本点数之比求随机事件的概率；"
                 "会先判断样本空间是否等可能，再决定用列举、排列还是组合来数样本点。",
    "mhj_h1074": "了解杨辉三角的构成规律与二项展开式的系数特征，能写出展开式并求指定项的系数；"
                 "知道展开式的项数、各项次数之和与系数和的关系，能用通项定位某一项的系数。",
}


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    write = "--write" in sys.argv
    T = json.load(open(f"{HJ}/topics.json", encoding="utf-8"))
    ref = {}
    for t in json.load(open(f"{D}/math/topics.json", encoding="utf-8")):
        for s in t.get("standards") or []:
            if s.get("id") and s.get("quote"):
                ref.setdefault(s["id"], []).append((t.get("name", ""), s["quote"]))

    n_grade = n_desc = n_std = 0
    for t in T:
        book = t["chapter"].split(" ")[0]
        if book in GRADE:
            g, sem = GRADE[book], "上"
            if (t.get("grade"), t.get("semester")) != (g, sem):
                t["grade"], t["semester"] = g, sem
                n_grade += 1
        if t["id"] in DESC and han(t.get("description")) < 40:
            t["description"] = DESC[t["id"]]
            n_desc += 1
        # 课标引文：同 id 的 quote 必须与仓库一致
        new = []
        for s in t.get("standards") or []:
            sid = s.get("id")
            if not sid or sid not in ref:
                new.append(s)
                continue
            quotes = ref[sid]
            if any(q == s.get("quote") for _, q in quotes):
                new.append(s)
                continue
            name = t.get("name", "")
            best = max(quotes, key=lambda nq: difflib.SequenceMatcher(None, name, nq[0]).ratio())
            s = dict(s, quote=best[1])
            n_std += 1
            new.append(s)
        t["standards"] = new

    print(f"grade/semester 修正 {n_grade} 点 · 描述补足 {n_desc} 点 · 引文对齐 {n_std} 条")
    if write:
        json.dump(T, open(f"{HJ}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        open(f"{HJ}/topics.json", "a", encoding="utf-8").write("\n")
        print("已写入 topics.json")
    else:
        print("干跑（加 --write 落盘）")


if __name__ == "__main__":
    main()
