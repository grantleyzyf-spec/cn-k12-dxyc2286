# -*- coding: utf-8 -*-
"""把 528 篇学层的七段小标题统一成规范写法（各写手写法不一致：有的加「（开场）」、有的「开场·」）。

规范（checker 关键词全部命中）：
  一、开场：先说生活里的一件事 / 二、课本原文说了什么 / 三、费曼翻译一遍 /
  四、例题精讲 / 五、易错点拨 / 六、五步学习法 / 七、方法锚与自查

用法: python3 normalize_learn_titles.py [--write]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS = os.path.join(ROOT, "learn", "_parts")
CANON = {
    1: "开场：先说生活里的一件事",
    2: "课本原文说了什么",
    3: "费曼翻译一遍",
    4: "例题精讲",
    5: "易错点拨",
    6: "五步学习法",
    7: "方法锚与自查",
}
CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七"}


def fix(md):
    changed = 0
    out = []
    for ln in md.split("\n"):
        m = re.match(r"^##\s*([一二三四五六七])、\s*(.+?)\s*$", ln)
        if m:
            no = "一二三四五六七".index(m.group(1)) + 1
            want = f"## {CN[no]}、{CANON[no]}"
            if ln != want:
                changed += 1
            out.append(want)
            continue
        out.append(ln)
    return "\n".join(out), changed


def main():
    write = "--write" in sys.argv
    tot = nf = 0
    for f in sorted(os.listdir(PARTS)):
        if not f.endswith(".json"):
            continue
        p = os.path.join(PARTS, f)
        d = json.load(open(p, encoding="utf-8"))
        c_all = 0
        for L in d.get("lessons") or []:
            new, c = fix(L.get("markdown") or "")
            if c:
                L["markdown"] = new
                c_all += c
                nf += 1
            tot += 1
        if write and c_all:
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if c_all:
            print(f"  {f}: 改 {c_all} 处标题")
    print(f"篇数 {tot} | 有改动篇数 {nf}")
    if not write:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
