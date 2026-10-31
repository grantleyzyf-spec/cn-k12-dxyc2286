# -*- coding: utf-8 -*-
"""修正「课时点」的先修模型（数据层，一次性 + 幂等）。

问题：课时级建点时，合并器把「同 chapter 的单元级点」当成课时点的**硬前置**连了边。
但数学的单元级点其实是按**知识点**命名的（如「科学记数法」挂在「七年级上册 第一章 有理数」），
于是出现「1.1 正数和负数」的前置是「科学记数法」这种语义错乱的边——
拿它做自适应诊断，会把「上位概念没掌握」误报成「前置知识缺口」。

正确模型：
- 课时点的学习顺序前置 = **同单元上一课时**（课时点→课时点）；
- 单元级点与课时点是「上位/下位」关系，不是学习顺序，**不进 prerequisites**。

本脚本：
1) 从每个课时点的 prerequisites 里剔除 chapter 不含「 · 」的单元级点；
2) 保留的「课时点→课时点」边由 soft 提升为 hard（它就是真正的学习前置）；
3) 同步重建 dependencies.json 里对应边（删除被剔除的、把保留的 soft 改 hard）。

用法：python3 scripts/fix_math_ke_prereq_model.py [--write]
"""
import json
import os
import sys

D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/math")
WRITE = "--write" in sys.argv


def main():
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    deps = json.load(open(f"{D}/dependencies.json", encoding="utf-8"))
    T = {t["id"]: t for t in topics}

    def is_ke(tid):
        return " · " in (T.get(tid, {}).get("chapter") or "")

    ke_ids = {t["id"] for t in topics if is_ke(t["id"])}
    removed = promoted = 0
    for t in topics:
        if t["id"] not in ke_ids:
            continue
        keep = [p for p in (t.get("prerequisites") or []) if is_ke(p)]
        removed += len(t.get("prerequisites") or []) - len(keep)
        t["prerequisites"] = keep

    # 剔除后变成根节点的课时点必须补 root_reason（门禁 test_math 要求根节点有理由）
    added_root = 0
    for t in topics:
        if t["id"] in ke_ids and not t["prerequisites"] and not t.get("root_reason"):
            t["root_reason"] = (f"起始课时：{t['chapter']} 是本单元的第一课时，"
                                f"单元内无更早的课时可作为前置（上位概念单独记在上位关系里，不连先修边）")
            added_root += 1

    new_deps, seen = [], set()
    for e in deps:
        a, b = e["from"], e["to"]
        if b in ke_ids and a not in ke_ids:
            continue                      # 单元点 → 课时点：上位关系，不是先修，丢弃
        ty = e.get("type")
        if b in ke_ids and a in ke_ids and ty == "soft":
            ty = "hard"                   # 课时→课时就是学习顺序前置
            promoted += 1
        if (a, b) in seen:
            continue
        seen.add((a, b))
        new_deps.append({"from": a, "to": b, "type": ty})

    # 兜底：topics.prerequisites 与 deps 双向镜像
    have = {(e["from"], e["to"]) for e in new_deps}
    for t in topics:
        for p in t.get("prerequisites") or []:
            if (p, t["id"]) not in have:
                new_deps.append({"from": p, "to": t["id"], "type": "hard"})
                have.add((p, t["id"]))

    print(f"剔除单元级前置 {removed} 条；课时→课时升为 hard {promoted} 条；"
          f"边数 {len(deps)} → {len(new_deps)}")
    print(f"仍带前置的课时点：{sum(1 for t in topics if t['id'] in ke_ids and t['prerequisites'])}/{len(ke_ids)}"
          f"；补 root_reason {added_root} 条")
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    for name, obj in (("topics", topics), ("dependencies", new_deps)):
        with open(f"{D}/{name}.json", "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    print("✅ 已写回 topics.json / dependencies.json")


if __name__ == "__main__":
    main()
