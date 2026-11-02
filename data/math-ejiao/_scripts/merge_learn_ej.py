#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版 · 学层合并：_learn_out/<id>.json → learn/<册>.json（按骨架顺序）

用法：python3 merge_learn_ej.py [--write]
缺失的课时会列出来（不中断），全部到齐才写整册文件。
"""
import json, os, sys

D = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-ejiao"
skel = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
OUT = os.path.join(D, "learn")
os.makedirs(OUT, exist_ok=True)


def main():
    write = "--write" in sys.argv
    total_have = 0
    for v in skel["volumes"]:
        book = v["book"]
        lessons, missing = [], []
        for u in v["units"]:
            for l in u["lessons"]:
                p = os.path.join(D, "_learn_out", f"{l['id']}.json")
                if not os.path.isfile(p):
                    missing.append(l["id"])
                    continue
                d = json.load(open(p, encoding="utf-8"))
                lessons.append({"topicId": l["id"], "title": d.get("title") or l["name"],
                                "markdown": d.get("markdown", ""), "words": d.get("words")})
        total_have += len(lessons)
        flag = "OK" if not missing else f"缺 {len(missing)}"
        print(f"{book}: {len(lessons)}/{len(lessons)+len(missing)} 篇 [{flag}]")
        if missing:
            print("   缺:", " ".join(missing[:8]) + (" …" if len(missing) > 8 else ""))
        if write and not missing:
            json.dump({"book": book, "lessons": lessons},
                      open(os.path.join(OUT, f"{book}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print(f"   → 已写 learn/{book}.json")
    print(f"\n合计已就绪 {total_have}/212")


if __name__ == "__main__":
    main()
