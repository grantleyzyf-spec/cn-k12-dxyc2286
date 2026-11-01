# -*- coding: utf-8 -*-
"""检查学层精讲分片：python3 check_learn.py L001"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(os.path.dirname(BASE), "_bank")
TITLES = ["## 一、先说生活里的一件事", "## 二、课标和课本怎么说", "## 三、用大白话讲清楚",
          "## 四、两个情境演练", "## 五、容易踩的坑", "## 六、五步学习法",
          "## 七、方法锚与自查"]
FIVE = ["每天锻炼一个小时", "扎实掌握第一个知识点", "能积微者速成",
        "运用对标思维突破学习困境", "运用杠铃法则缓解学习疲劳"]
MED_RE = re.compile(r"抑郁|诊断|治疗|药物|症(?!状)")
SUYANG = ["自我意识", "情绪管理", "人际交往", "学会学习", "生命与社会适应"]

if len(sys.argv) < 2:
    sys.exit("用法: python3 check_learn.py L001")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    sh = json.load(open(os.path.join(BASE, sys.argv[1] + ".json"), encoding="utf-8"))
    p = os.path.join(BANK, sh["shard"] + ".json")
    if not os.path.exists(p):
        sys.exit(f"FAIL 缺文件 {p}")
    b = json.load(open(p, encoding="utf-8"))
    got = {i.get("topicId"): i for i in b.get("items", [])}
    want = {i["topicId"]: i for i in sh["items"]}
    fails = []

    def ck(name, ok, detail=""):
        if not ok:
            fails.append(f"{name} {detail}")

    ck("篇目覆盖完整", set(got) == set(want),
       {"多": sorted(set(got) - set(want))[:3], "缺": sorted(set(want) - set(got))[:3]})

    counts = []
    for tid, meta in want.items():
        it = got.get(tid) or {}
        md = it.get("md") or ""
        n = han(md)
        counts.append(n)
        ck(f"{tid} 汉字数 1200–2600", 1200 <= n <= 2600, n)
        pos = [md.find(t) for t in TITLES]
        ck(f"{tid} 七段标题齐全", all(x >= 0 for x in pos),
           [TITLES[i] for i, x in enumerate(pos) if x < 0])
        ck(f"{tid} 七段顺序正确", pos == sorted(pos) if all(x >= 0 for x in pos) else False)
        ck(f"{tid} quote 逐字命中", norm(meta["quote"]) in norm(md), meta["quote"][:18])
        ck(f"{tid} 五步五条逐字", all(f in md for f in FIVE),
           [f for f in FIVE if f not in md])
        ck(f"{tid} ❌ 至少 2 处", md.count("❌") >= 2, md.count("❌"))
        ck(f"{tid} ✅ 至少 2 处", md.count("✅") >= 2, md.count("✅"))
        ck(f"{tid} 自查 ≥3 条", md.count("- [ ]") >= 3, md.count("- [ ]"))
        bad = sorted({m.group(0) for m in MED_RE.finditer(md)})
        ck(f"{tid} 无医学诊断词", not bad, bad)
        ck(f"{tid} 素养词合法", any(s in md for s in SUYANG) and meta["domain"] in md,
           meta["domain"])

    print(f"{sh['shard']} {sh['book']}：{len(want)} 篇 | 汉字 {counts}")
    if fails:
        print(f"\n❌ {len(fails)} 项未通过（前 20）:")
        for f in fails[:20]:
            print("  -", f)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
