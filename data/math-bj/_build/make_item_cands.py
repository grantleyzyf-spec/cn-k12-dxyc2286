# -*- coding: utf-8 -*-
"""为 math-bj 仍未挂标的点，从「课标原文条目池」（items.json，新命名空间 mat-2022n:*）
生成封闭候选（每点 top-5），供工位挑选。

与 make_std_cands.py 的区别：候选来自**课标原文重切条目**，一 id 一义；
匹配以 2-gram IDF 为主，点名权重加倍。

用法：python3 make_item_cands.py [--write]
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(HERE, "_std_work")


def norm(s):
    return re.sub(r"[\s　，。、；：？！“”‘’（）()《》〈〉·—…\-~,.;:?!\"'/\\|\[\]【】]+", "", s or "")


def stage(g):
    return 1 if g <= 2 else 2 if g <= 4 else 3 if g <= 6 else 4


def bigrams(s):
    s = norm(s)
    return [s[i:i + 2] for i in range(len(s) - 1)]


def main():
    write = "--write" in sys.argv
    items = json.load(open(os.path.join(WORK, "items.json"), encoding="utf-8"))["items"]
    n = len(items)
    df = collections.Counter()
    for it in items:
        for g in set(bigrams(it["text"])):
            df[g] += 1
    idf = {g: math.log(1 + n / (1 + v)) for g, v in df.items()}

    topics = json.load(open(os.path.join(DATA, "math-bj", "topics.json"), encoding="utf-8"))
    gaps = [t for t in topics if not t.get("standards")]
    out = []
    for t in gaps:
        sg = stage(t["grade"])
        name_bg = set(bigrams(t["name"]))
        chap_bg = set(bigrams(t["chapter"].split(" ")[-1]))
        scored = []
        for it in items:
            if it["stage"] != sg:
                continue
            ib = set(bigrams(it["text"]))
            sc = (2.0 * sum(idf.get(g, 1.0) for g in name_bg & ib)
                  + 1.0 * sum(idf.get(g, 1.0) for g in chap_bg & ib))
            sc /= 1 + math.log(1 + len(name_bg) + len(chap_bg))
            if sc > 0:
                scored.append((sc, it))
        scored.sort(key=lambda x: -x[0])
        out.append({"pid": t["id"], "name": t["name"], "chapter": t["chapter"],
                    "grade": t["grade"], "domain": t.get("domain"),
                    "cands": [{"n": i + 1, "id": it["item_id"], "stage": it["stage"],
                               "domain": it["domain"], "topic": it["topic"],
                               "quote": it["text"], "score": round(s, 2)}
                              for i, (s, it) in enumerate(scored[:5])]})

    shards, buf, idx = [], [], 0
    for row in out:
        buf.append(row)
        if len(buf) >= 22:
            idx += 1
            shards.append((f"G{idx:02d}", buf))
            buf = []
    if buf:
        idx += 1
        shards.append((f"G{idx:02d}", buf))

    print(f"空缺点 {len(gaps)} | 条目池 {n} | 分片 {len(shards)}")
    for name, rows in shards:
        hi = sum(1 for r in rows if r["cands"] and r["cands"][0]["score"] >= 6)
        print(f"  {name}: {len(rows)} 点，其中高分候选(≥6) {hi} 点")
        if write:
            json.dump({"shard": name, "points": rows},
                      open(os.path.join(WORK, f"gap_cands_{name}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    if write:
        print("已写", WORK)


if __name__ == "__main__":
    main()
