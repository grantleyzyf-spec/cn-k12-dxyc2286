# -*- coding: utf-8 -*-
"""为 math-bj 未挂课标的点生成「封闭候选集」（每点 top-5），供工位挑选。

思路：仓库里 mat-2022 的 id→quote 映射由各版本桶各自分配、并不自洽
（同一 id 在不同桶挂着完全不同的句子），所以**只以 quote 文本为准**，
id 只作为该句的代表 id 沿用 —— 不新造 id、不改写 quote。

产出：_build/_std_work/cands_<shard>.json（每片 ≤25 点）
用法：python3 make_std_cands.py [--write]
"""
import collections
import glob
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(ROOT, "data")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_std_work")
TXT = os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt")
NOISE = re.compile(r"学段|教学|整合|分析主题|核心素养主要|引导|课时|学期|年级为|评价|教师|教材|单元")
# OCR 噪声：@ * 之类符号、小标题序号、举例标记、"加诚/图掌握"这类错字
DIRTY = re.compile(r"[@*]|加诚|图掌握|^\s*\(?\d+\)|例如[:：]|D 。|\.\s*$|^\s*[，。;；]")


def norm(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()《》〈〉·—…\-~,.;:?!\"'/\\|\[\]【】]+", "", s or "")


def stage(g):
    return 1 if g <= 2 else 2 if g <= 4 else 3 if g <= 6 else 4


def build_pool():
    """quote → 代表 id（同句取出现最多的 id）"""
    seen = collections.defaultdict(collections.Counter)
    for f in glob.glob(os.path.join(DATA, "*", "topics.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        pts = d["topics"] if isinstance(d, dict) else d
        if not isinstance(pts, list):
            continue
        for p in pts:
            for s in p.get("standards") or []:
                if isinstance(s, dict) and s.get("id", "").startswith("mat-2022") and s.get("quote"):
                    seen[s["quote"]][s["id"]] += 1
    pool = []
    for q, ids in seen.items():
        if not (12 <= len(q) <= 70) or NOISE.search(q):
            continue
        pool.append({"quote": q, "id": ids.most_common(1)[0][0]})
    return pool


def bigrams(s):
    s = norm(s)
    return [s[i:i + 2] for i in range(len(s) - 1)]


def main():
    write = "--write" in sys.argv
    pool = build_pool()
    n = len(pool)
    df = collections.Counter()
    for c in pool:
        for g in set(bigrams(c["quote"])):
            df[g] += 1
    idf = {g: math.log(1 + n / (1 + v)) for g, v in df.items()}

    bj = json.load(open(os.path.join(DATA, "math-bj", "topics.json"), encoding="utf-8"))
    un = [p for p in bj if not p.get("standards")]
    out = collections.defaultdict(list)
    for p in un:
        sg = stage(p["grade"])
        key = norm(p["name"] + p["chapter"].split(" ")[-1] * 2)  # 点名+单元名，点名加权
        bg = set(bigrams(key))
        scored = []
        for c in pool:
            if int(c["id"].split(":")[1].split(".")[0]) != sg:
                continue
            cg = set(bigrams(c["quote"]))
            hit = bg & cg
            sc = sum(idf.get(g, 1.0) for g in hit) / (1 + math.log(1 + len(bg)))
            if sc > 0:
                scored.append((sc + (1.5 if not DIRTY.search(c["quote"]) else 0), c))
        scored.sort(key=lambda x: -x[0])
        top = [{"n": i + 1, "id": c["id"], "quote": c["quote"], "score": round(s, 2),
                "clean": (not DIRTY.search(c["quote"]))}
               for i, (s, c) in enumerate(scored[:5])]
        book = p["chapter"].split(" ")[0]
        out[book].append({"pid": p["id"], "name": p["name"], "chapter": p["chapter"],
                          "grade": p["grade"], "domain": p.get("domain"), "cands": top})

    # 按册分片，每片 ≤25 点
    shards, buf, idx = [], [], 0
    for book in sorted(out):
        for item in out[book]:
            buf.append(item)
            if len(buf) >= 25:
                idx += 1
                shards.append((f"C{idx:02d}", buf))
                buf = []
    if buf:
        idx += 1
        shards.append((f"C{idx:02d}", buf))

    print(f"未挂点 {len(un)} | 池 quote {n} 条 | 分片 {len(shards)} 片")
    for name, items in shards:
        nz = sum(1 for it in items if it["cands"] and it["cands"][0]["score"] >= 4)
        print(f"  {name}: {len(items)} 点，其中「高置信候选(score≥4)」 {nz} 点")
        if write:
            os.makedirs(OUT, exist_ok=True)
            json.dump({"shard": name, "points": items},
                      open(os.path.join(OUT, f"cands_{name}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    if write:
        json.dump({"pool": pool, "txt": TXT},
                  open(os.path.join(OUT, "_pool.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写", OUT)


if __name__ == "__main__":
    main()
