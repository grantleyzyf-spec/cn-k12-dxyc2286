#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""晋教版地理：学层（L）与讲解（K）派单分片生成器。

学层：一片＝一个主题（8 篇），16 片；分片自带教材全文绝对路径（工人不许自己猜路径）。
讲解：一片＝4 卷（一册一片），8 片；覆盖 32 卷。

⛔ 本脚本只写 `_learn_shards/`、`_lecture_shards/` 两个目录里**自己的** L/K 文件，
   不删除任何既有分片（不像仓内 gen_lecture_shards.py 会先清空目录）。
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-jin")
TXT_ROOT = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中")
LSH = os.path.join(D, "_learn_shards")
KSH = os.path.join(D, "_lecture_shards")


def main() -> int:
    os.makedirs(LSH, exist_ok=True)
    os.makedirs(KSH, exist_ok=True)
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    units = [t for t in topics if t["level"] == "unit"]

    # ---- 学层：一主题一片 ----
    li = 0
    for u in sorted(units, key=lambda t: t["id"]):
        li += 1
        book = u["chapter"].split(" ")[0]
        txt = os.path.join(TXT_ROOT, book, "整册全文.txt")
        if not os.path.exists(txt):
            print(f"❌ {book} 缺教材全文：{txt}")
            return 1
        lessons = [t for t in topics if t.get("prereqUpper") == u["id"]]
        lessons.sort(key=lambda t: t["id"])
        shard = dict(
            shard=f"L{li:02d}",
            book=book, unitPoint=u["id"], unitLabel=u["name"], chapter=u["chapter"],
            txt=txt,
            out=f"data/geography-jin/learn/_parts/L{li:02d}_{book}.json",
            lessons=[dict(topicId=t["id"], title=t["name"], chapter=t["chapter"],
                          grade=t["grade"], domain=t["domain"],
                          standards=t.get("standards") or []) for t in lessons],
        )
        json.dump(shard, open(os.path.join(LSH, f"L{li:02d}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    # ---- 讲解：一册一片，4 卷 ----
    ki = 0
    shards = []
    for book in ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]:
        exams = sorted(glob.glob(os.path.join(D, "exams", book, "*.json")))
        if len(exams) != 8:
            print(f"⚠️ {book} 现有 {len(exams)} 卷（应为 8），讲解派单按实际卷数生成")
        ki += 1
        papers = []
        for p in exams:
            d = json.load(open(p, encoding="utf-8"))
            papers.append(dict(examId=d["examId"], paper=d["paper"], kind=d["kind"],
                               examPath=os.path.relpath(p, ROOT),
                               out=f"data/geography-jin/exam_lectures/{book}/{d['paper']}.json"))
        shard = dict(shard=f"K{ki:02d}", book=book, outDir=f"data/geography-jin/exam_lectures/{book}",
                     papers=papers)
        json.dump(shard, open(os.path.join(KSH, f"K{ki:02d}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        shards.append((f"K{ki:02d}", book, len(papers)))

    print(f"学层派单 {li} 片（{sum(len(json.load(open(os.path.join(LSH, f)))['lessons']) for f in sorted(os.listdir(LSH)))} 篇）")
    for s, b, n in shards:
        print(f"  讲解派单 {s} {b}: {n} 卷")
    return 0


if __name__ == "__main__":
    sys.exit(main())
