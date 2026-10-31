# -*- coding: utf-8 -*-
"""错因标签（misconceptions）机检。

输入：data/math/misconceptions/<册>.json —— { "mat_p1234": ["错因1", "错因2", ...], ... }

规则：
1 覆盖：该册**每个课时点**都必须有标签（chapter 含「 · 」且以本册名开头）
2 条数：3–5 条
3 每条 ≥8 字（「粗心」「不认真」这类空话会被拦）
4 禁止空话词：粗心 / 不认真 / 马虎 / 计算错误（单独成条时）
5 点内不重复；标签要指向**具体的概念或操作误判**，如
  「把 −a 一定当成负数，忽略 a 可以为 0」
6 id 必须存在且属于本册

用法：python3 scripts/check_math_misconceptions.py <册>.json
"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
EMPTY = re.compile(r"^(粗心|不认真|马虎|计算错误|审题不清|不会做|基础差)$")
errs = []


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_misconceptions.py data/math/misconceptions/<册>.json")
        sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    book = os.path.basename(sys.argv[1])[:-5]
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    ke = [t for t in topics if " · " in (t.get("chapter") or "") and (t.get("chapter") or "").startswith(f"{book} ")]
    if not ke:
        print(f"❌ 找不到本册课时点：{book}")
        sys.exit(1)
    ids = {t["id"] for t in ke}
    names = {t["id"]: t["name"] for t in ke}
    miss = sorted(ids - set(data))
    extra = sorted(set(data) - ids)
    if miss:
        errs.append(f"未覆盖 {len(miss)} 个课时点：" + "、".join(names[i] for i in miss[:8]))
    if extra:
        errs.append(f"有 {len(extra)} 个 id 不属于本册：{extra[:5]}")
    for tid, arr in data.items():
        nm = names.get(tid, tid)
        if not isinstance(arr, list):
            errs.append(f"{nm}: 应为字符串数组")
            continue
        if not (3 <= len(arr) <= 5):
            errs.append(f"{nm}: 应有 3–5 条，实为 {len(arr)}")
        seen = set()
        for x in arr:
            s = (x or "").strip()
            if len(s) < 8:
                errs.append(f"{nm}: 错因太短（{s}）")
            if EMPTY.match(s):
                errs.append(f"{nm}: 空话错因（{s}）")
            if s in seen:
                errs.append(f"{nm}: 点内重复（{s}）")
            seen.add(s)
    print(f"册：{book} · 课时点 {len(ke)} · 已标 {len(data)}")
    if errs:
        print(f"\n❌ {len(errs)} 条问题：")
        for e in errs[:30]:
            print("  -", e)
        sys.exit(1)
    print("✅ 自检通过")


if __name__ == "__main__":
    main()
