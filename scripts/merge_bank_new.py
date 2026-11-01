#!/usr/bin/env python3
"""把 data/math/_bank_new/S*.json 合并进 data/math/questions.json。

用法：
  python3 scripts/merge_bank_new.py            # 预演（只报告，不落盘）
  python3 scripts/merge_bank_new.py --write    # 真正合并

规则：
- 先按 check_bank_new.py 的判据逐文件校验（有不合格则整批拒绝合并）
- id 已存在 → 跳过并计数（不覆盖既有题）
- 题干（去空白）与既有题重复 → 跳过并报错（禁止重题入库）
- 合并后按 topicId 排序，写回 questions.json（indent=2 / ensure_ascii=False）
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "math")
QJSON = os.path.join(DATA, "questions.json")

sys.path.insert(0, HERE)
from check_bank_new import check_file  # noqa: E402


def main():
    write = "--write" in sys.argv
    files = sorted(glob.glob(os.path.join(DATA, "_bank_new", "S*.json")))
    if not files:
        print("没有找到 data/math/_bank_new/S*.json，什么都没做")
        return 1

    errs = []
    total = 0
    for p in files:
        total += check_file(p, errs)
    if errs:
        print(f"❌ 分片校验未通过（{len(errs)} 项），拒绝合并：")
        for e in errs[:30]:
            print("  -", e)
        return 1
    print(f"✅ 分片校验通过：{len(files)} 个文件 · {total} 题")

    qs = json.load(open(QJSON, encoding="utf-8"))
    have_ids = {q["id"] for q in qs}
    have_prompts = {re.sub(r"\s+", "", q.get("prompt") or ""): q["id"] for q in qs}

    added, skip_id, dup_prompt = [], [], []
    for p in files:
        for it in json.load(open(p, encoding="utf-8")):
            key = re.sub(r"\s+", "", it.get("prompt") or "")
            if it["id"] in have_ids:
                skip_id.append(it["id"])
                continue
            if key in have_prompts:
                dup_prompt.append((it["id"], have_prompts[key]))
                continue
            added.append(it)
            have_ids.add(it["id"])
            have_prompts[key] = it["id"]

    print(f"新增 {len(added)} 题 | 已存在跳过 {len(skip_id)} | 题干重复跳过 {len(dup_prompt)}")
    if dup_prompt:
        print("  题干重复示例：", dup_prompt[:5])
    if not write:
        print("（预演结束，未落盘；加 --write 才真正写入）")
        return 0

    merged = qs + added
    order = {t["id"]: i for i, t in enumerate(json.load(open(os.path.join(DATA, "topics.json"), encoding="utf-8")))}
    merged.sort(key=lambda q: (order.get(q.get("topicId"), 10 ** 6), q["id"]))
    with open(QJSON, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"✅ 已写入 questions.json：{len(qs)} → {len(merged)} 题")
    return 0


if __name__ == "__main__":
    sys.exit(main())
