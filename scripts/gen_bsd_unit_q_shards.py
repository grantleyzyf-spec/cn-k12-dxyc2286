#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单元点 5 题派单：把 `_unit_specs/*.json` 每 3 个单元打一片 → `_unit_shards/U###.json`。

工人按片写 `_unit_parts/U###.json`：
  {"units": [{"unitId": "mbs_u085", "questions": [ <5 题> ]}, …]}
父代用 `make_bsd_unit_specs.py --apply data/math-bsd/_unit_parts/*.json` 合并入库
（该脚本也负责建单元点本身与依赖边）。

用法：python3 scripts/gen_bsd_unit_q_shards.py --per-shard 3
"""
import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "data", "math-bsd")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-shard", type=int, default=3)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    specs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(B, "_unit_specs", "*.json")))]
    out_dir = os.path.join(B, "_unit_shards")
    if not a.dry:
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(os.path.join(B, "_unit_parts"), exist_ok=True)

    n = 0
    for i in range(0, len(specs), a.per_shard):
        chunk = specs[i:i + a.per_shard]
        # 一片不得跨册：按册重切
        books = {c["book"] for c in chunk}
        if len(books) > 1:
            chunk = [c for c in chunk if c["book"] == chunk[0]["book"]]
        n += 1
        uid = f"U{n:03d}"
        payload = {"shard": uid, "bucket": "math-bsd", "book": chunk[0]["book"],
                   "out": f"data/math-bsd/_unit_parts/{uid}.json",
                   "units": chunk}
        if not a.dry:
            json.dump(payload, open(os.path.join(out_dir, f"{uid}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
    print(f"单元题派单 {n} 片（单元 {len(specs)} 个，每片 {a.per_shard}）"
          f"{'（干跑）' if a.dry else ' → ' + out_dir}")


if __name__ == "__main__":
    main()
