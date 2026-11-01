# -*- coding: utf-8 -*-
"""组装 out_parts：python3 build.py part1 part2 ..."""
import importlib.util
import json
import os
import re
import sys

W = os.path.dirname(os.path.abspath(__file__))
OUT = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/learn/_parts/六年级上册__L30.json"


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def load(p):
    spec = importlib.util.spec_from_file_location(p, os.path.join(W, p + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.LESSONS


def main():
    parts = sys.argv[1:]
    lessons = []
    for p in parts:
        lessons.extend(load(p))
    out = {"book": "六年级上册", "shard": "L30",
           "lessons": [{"topicId": L["topicId"], "title": L["title"],
                        "markdown": L["markdown"], "words": hanzi(L["markdown"])}
                       for L in lessons]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"写出 {len(lessons)} 篇 → {OUT}")
    print("汉字合计", sum(x["words"] for x in out["lessons"]))


if __name__ == "__main__":
    main()
