#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""physics-hkjy 学层精讲 checker：一篇一检或 --all 全量。

用法：check_phys_hkjy_learn.py <_out.json ...> | --all
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
HAN = re.compile(r"[\u4e00-\u9fa5]")
SEC = ["## 一、开场", "## 二、课本原文", "## 三、费曼翻译", "## 四、例题精讲",
       "## 五、易错点拨", "## 六、五步学习法", "## 七、自查清单"]
STEP = ["每天锻炼一个小时", "扎实掌握第一个知识点", "能积微者速成",
        "运用对标思维突破学习困境", "运用杠铃法则缓解学习疲劳"]
BAN = ["首先", "其次", "综上所述", "总而言之", "由此可见", "赋能", "抓手", "闭环", "值得注意的是"]


def han(s):
    return len(HAN.findall(s or ""))


def check_one(les):
    E = []
    md = les.get("markdown") or ""
    n = han(md)
    if not 1200 <= n <= 2800:
        E.append("字数 %d ∉[1200,2800]" % n)
    if abs(int(les.get("words") or 0) - n) > 10:
        E.append("words 字段 %s ≠ 实测 %d" % (les.get("words"), n))
    pos = []
    for s in SEC:
        i = md.find(s)
        if i < 0:
            E.append("缺段 " + s)
        pos.append(i)
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        E.append("七段顺序错")
    if md.count("> ") + md.count(">\n") < 2:
        E.append("引文 <2")
    if "这句话的意思是" not in md:
        E.append("引文缺解释句")
    if "❌" not in md or "✅" not in md:
        E.append("缺 ❌/✅")
    if md.count("- [ ]") < 3:
        E.append("自查 <3")
    for w in BAN:
        if w in md:
            E.append("禁词 " + w)
    for m in re.findall(r"^#{1,6}\s.*$", md, re.M):
        if m.strip() not in SEC:
            E.append("多出标题 " + m.strip()[:16])
    if "**" in md:
        E.append("有 ** 加粗")
    if "$" in md or "\\frac" in md:
        E.append("有 LaTeX")
    # 第六段字数
    try:
        s6 = md.split("## 六、五步学习法")[1].split("## 七、")[0]
        if not 350 <= han(s6) <= 900:
            E.append("五步段 %d ∉[350,900]" % han(s6))
        for st in STEP:
            if st not in s6:
                E.append("五步缺 " + st)
    except IndexError:
        pass
    return E


def main():
    args = sys.argv[1:]
    files = sorted(glob.glob(os.path.join(D, "_learn_parts", "L*_out.json"))) if args[:1] == ["--all"] else args
    bad = 0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print("❌", os.path.basename(f), "解析失败", e)
            bad += 1
            continue
        rows = d.get("lessons") if isinstance(d, dict) else d
        E = []
        for les in rows:
            e = check_one(les)
            if e:
                E.append("%s（%s）：%s" % (les.get("topicId"), les.get("title"), "；".join(e)))
        if E:
            bad += 1
            print("❌", os.path.basename(f))
            for x in E[:6]:
                print("   -", x)
        else:
            print("✅", os.path.basename(f), "/".join(str(han(l["markdown"])) for l in rows))
    print("\n共 %d 份 · 不合格 %d" % (len(files), bad))
    print("RESULT: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
