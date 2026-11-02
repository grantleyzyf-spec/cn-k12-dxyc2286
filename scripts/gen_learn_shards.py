#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为某版本桶生成「学层精讲」派单（learn/_shards/L*.json）。

每片 = 同一册的若干课时点（默认 4 篇），派单给出：
  lessons[]：topicId / name / chapter / page / misconceptions / 教材 TXT 路径（若提供 --txt-root）
  out：本片落盘路径（learn/_parts/<LID>.json）

为什么不用手写：单册口径是硬约束（checker 与合并器都按 book 归属），一本册的课时点
跨片就会整片不合格；按册切、按页给 TXT 路径，工人不需要自己去数页码。

用法：
  python3 scripts/gen_learn_shards.py math-hujiao --per-shard 4 \
      --booktag 沪教版必修第一册=h1 沪教版必修第二册=h2 沪教版必修第三册=h3 \
                沪教版选择性必修第一册=x1 沪教版选择性必修第二册=x2 --txt-root /tmp/mhj

注意：`--txt-root` 指向「逐页 TXT 目录」（<root>/<tag>/pNNN.txt）。教材是单一整册 TXT 时
不要传它，让写手自己按 book 找；两种形态下 check_<桶>_learn.py 的回表源不同。
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket")
    ap.add_argument("--per-shard", type=int, default=4)
    ap.add_argument("--booktag", nargs="*", default=[], help="册名=教材tag（如 沪教版必修第一册=h1）")
    ap.add_argument("--txt-root", default="", help="逐页 TXT 根目录（<root>/<tag>/pNNN.txt）")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    base = os.path.join(ROOT, "data", a.bucket)
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))
    tag_of = dict(x.split("=", 1) for x in a.booktag)

    # 只取课时点（level==lesson）；没有 level 的桶先用 page / chapter 里的「 · 」兜底
    lessons = [t for t in topics if t.get("level") == "lesson"]
    if not lessons:
        lessons = [t for t in topics if t.get("page") is not None]
    lessons.sort(key=lambda t: (t["chapter"].split(" ")[0], t.get("page") or 0, t["id"]))
    by_book = {}
    for t in lessons:
        by_book.setdefault(t["chapter"].split(" ")[0], []).append(t)

    out_dir = os.path.join(base, "learn", "_shards")
    parts_dir = os.path.join(base, "learn", "_parts")
    if not a.dry:
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(parts_dir, exist_ok=True)

    n = 0
    for book, items in by_book.items():
        tag = tag_of.get(book)
        for i in range(0, len(items), a.per_shard):
            n += 1
            lid = f"L{n:02d}"
            chunk = items[i:i + a.per_shard]
            payload = {
                "shard": lid, "bucket": a.bucket, "book": book,
                "grade": chunk[0].get("grade"), "semester": chunk[0].get("semester"),
                "txt_tag": tag, "out": f"data/{a.bucket}/learn/_parts/{lid}.json",
                "lessons": [{
                    "topicId": t["id"], "name": t["name"], "chapter": t["chapter"],
                    "page": t.get("page"),
                    "misconceptions": t.get("misconceptions") or [],
                    "txt": (f"{a.txt_root}/{tag}/p{int(t['page']):03d}.txt"
                            if (a.txt_root and tag and t.get("page")) else ""),
                } for t in chunk],
            }
            if not a.dry:
                json.dump(payload, open(os.path.join(out_dir, lid + ".json"), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
    print(f"{a.bucket}: 课时点 {len(lessons)} · 册 {len(by_book)} · 分片 {n}"
          f"{'（干跑）' if a.dry else ' → ' + out_dir}")


if __name__ == "__main__":
    main()
