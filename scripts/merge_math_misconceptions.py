# -*- coding: utf-8 -*-
"""把 data/math/misconceptions/<册>.json 合并进 data/math/topics.json 的 `misconceptions` 字段。

幂等：重复跑结果一致。用法：python3 scripts/merge_math_misconceptions.py [--write]
"""
import glob
import json
import os
import sys

D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/math")
WRITE = "--write" in sys.argv


def main():
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    merged, unknown = 0, []
    for f in sorted(glob.glob(f"{D}/misconceptions/*.json")):
        book = os.path.basename(f)[:-5]
        data = json.load(open(f, encoding="utf-8"))
        for tid, arr in data.items():
            t = T.get(tid)
            if not t:
                unknown.append((book, tid))
                continue
            t["misconceptions"] = [x.strip() for x in arr if x and x.strip()]
            merged += 1
    ke = [t for t in topics if " · " in (t.get("chapter") or "")]
    covered = [t for t in ke if t.get("misconceptions")]
    print(f"合并 {merged} 个知识点；课时点覆盖 {len(covered)}/{len(ke)}")
    if unknown:
        print(f"⚠️ 有 {len(unknown)} 个 id 在 topics 里不存在：{unknown[:5]}")
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    json.dump(topics, open(f"{D}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(f"{D}/topics.json", "a").write("\n")
    print("✅ 已写回 topics.json")


if __name__ == "__main__":
    main()
