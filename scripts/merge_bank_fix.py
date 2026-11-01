#!/usr/bin/env python3
"""把 data/math/_bank_fix/<册>.json 的改写结果合并回 data/math/questions.json。

用法：
  python3 scripts/merge_bank_fix.py            # 预演
  python3 scripts/merge_bank_fix.py --write    # 真正写入

规则：
- 先按 check_bank_fix.py 逐文件校验，有不合格则整批拒绝
- 按 id 就地替换（题量、topicId、题型、难度不变）
- 写入后按 topics.json 的次序排序，indent=2 / ensure_ascii=False
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "math")
QJSON = os.path.join(DATA, "questions.json")

sys.path.insert(0, HERE)
from check_bank_fix import check_file  # noqa: E402


def main():
    write = "--write" in sys.argv
    files = sorted(glob.glob(os.path.join(DATA, "_bank_fix", "*.json")))
    if not files:
        print("没有 data/math/_bank_fix/*.json")
        return 1
    errs, total = [], 0
    for p in files:
        total += check_file(p, errs)
    if errs:
        print(f"❌ 校验未通过（{len(errs)} 项），拒绝合并：")
        for e in errs[:30]:
            print("  -", e)
        return 1
    print(f"✅ 校验通过：{len(files)} 个文件 · {total} 题")

    qs = json.load(open(QJSON, encoding="utf-8"))
    patch = {}
    for p in files:
        for it in json.load(open(p, encoding="utf-8")):
            patch[it["id"]] = it
    hit = 0
    for i, q in enumerate(qs):
        if q["id"] in patch:
            new = dict(q)
            new.update(patch[q["id"]])
            qs[i] = new
            hit += 1
    missing = sorted(set(patch) - {q["id"] for q in qs})
    print(f"就地替换 {hit} 题" + (f" | 未命中 {len(missing)}: {missing[:5]}" if missing else ""))
    if not write:
        print("（预演结束，加 --write 才写入）")
        return 0
    order = {t["id"]: i for i, t in enumerate(json.load(open(os.path.join(DATA, "topics.json"), encoding="utf-8")))}
    qs.sort(key=lambda q: (order.get(q.get("topicId"), 10 ** 6), q["id"]))
    with open(QJSON, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)
    print(f"✅ 已写入 questions.json：共 {len(qs)} 题")
    return 0


if __name__ == "__main__":
    sys.exit(main())
