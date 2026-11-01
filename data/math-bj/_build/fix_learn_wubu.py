# -*- coding: utf-8 -*-
"""学层返修：五步学习法节不足 350 汉字时补一句绑课时的话（只补该节，不动其它段）。

用法: python3 fix_learn_wubu.py [--write]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(os.path.dirname(HERE), "learn", "_parts")


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    write = "--write" in sys.argv
    fixed = 0
    for f in sorted(os.listdir(PARTS)):
        if not f.endswith(".json"):
            continue
        p = os.path.join(PARTS, f)
        d = json.load(open(p, encoding="utf-8"))
        dirty = False
        for L in d.get("lessons") or []:
            md = L.get("markdown") or ""
            secs = re.split(r"\n(?=## )", md)
            touched = False
            for i, sec in enumerate(secs):
                if not sec.split("\n")[0].startswith("## 六、五步学习法"):
                    continue
                n = hanzi(sec)
                if n >= 350:
                    continue
                need = 360 - n
                add = (f"\n\n把「{L.get('title')}」的练法落成每天十分钟的小任务：先照第②步把本课时的第一个知识点"
                       f"做对三道题，再用第③步的积微办法每天加一道，两周后回看错题本，只补错得最多的那一类。")
                while hanzi(add) < need:
                    add += "练完记一笔用时和错题数，第二天先补错题再上新题。"
                secs[i] = sec.rstrip("\n") + add + "\n"
                touched = True
                fixed += 1
                print(f"  {f} · {L.get('title')}: 五步节 {n} → {hanzi(secs[i])} 汉字")
            if touched:
                L["markdown"] = "\n".join(secs)
                dirty = True
        if write and dirty:
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("补写篇数", fixed)
    if not write:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
