#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版化学九年级：从 10 个「大单元」docx 重新抽取课时（**保留破折号后的限定语**，避免同名）。

产物 /tmp/chem_kepu_units.json：{book, unit, unitName, lessons:[{no,name}]}
与首版差异：name 不再截到「——」之前；若仍重名，由 build_chem_kepu 加「（第N单元）」消歧。
"""
import glob
import json
import re

import docx

BASE = "/Users/a627692/Desktop/中小学教材/中小学教材/化学/初中/科普版"
PAT = re.compile(r"^（[一二三四五六七八九十]+）第(\d+)课时\s*(.+)$")


def main():
    out = []
    for f in sorted(glob.glob(BASE + "/*大单元*.docx")):
        m = re.search(r"(九年级[上下]册)第([一二三四五六七八九十\d]+)单元\s*(.+?)\s*大单元", f)
        d = docx.Document(f)
        lessons = []
        for p in d.paragraphs:
            s = p.text.strip()
            mm = PAT.match(s)
            if mm:
                name = re.sub(r"[（(]\d+课时[）)]", "", mm.group(2)).strip()
                lessons.append({"no": int(mm.group(1)), "name": name})
        out.append({"book": m.group(1), "unit": m.group(2), "unitName": m.group(3).strip(),
                    "lessons": lessons})
    json.dump(out, open("/tmp/chem_kepu_units.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = sum(len(o["lessons"]) for o in out)
    names = [l["name"] for o in out for l in o["lessons"]]
    from collections import Counter
    dup = {k: v for k, v in Counter(names).items() if v > 1}
    print("单元 %d ｜课时 %d ｜重名 %d 种 %s" % (len(out), tot, len(dup), list(dup)[:6]))
    print("样例：", names[:3], "｜长名样例：", max(names, key=len)[:40])


if __name__ == "__main__":
    main()
