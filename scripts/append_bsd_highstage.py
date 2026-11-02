#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把初中 / 高中骨架（课时级知识点 + 先修边）并入 math-bsd 的 topics.json / dependencies.json。

只做「缺失补齐」，不删不改已有条目 —— 小学 12 册由并行工位维护，本脚本不碰它们的字段。

用法:
  python3 scripts/append_bsd_highstage.py            # 预览（不写盘）
  python3 scripts/append_bsd_highstage.py --write
"""
import argparse, json, collections

ROOT = "data/math-bsd"
SK = [f"{ROOT}/_skeleton_初中.json", f"{ROOT}/_skeleton_高中.json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    topics = json.load(open(f"{a.root}/topics.json", encoding="utf-8"))
    deps = json.load(open(f"{a.root}/dependencies.json", encoding="utf-8"))
    tid = {t["id"] for t in topics}
    have = {(d["from"], d["to"]) for d in deps}

    add_t, add_d = [], []
    for path in [f"{a.root}/_skeleton_初中.json", f"{a.root}/_skeleton_高中.json"]:
        sk = json.load(open(path, encoding="utf-8"))
        for t in sk["topics"]:
            if t["id"] in tid:
                continue
            t = dict(t)
            t.setdefault("subject", "math-bsd")
            t.setdefault("level", "lesson")
            t.setdefault("type", "procedural")
            t.setdefault("external", False)
            t.setdefault("verified", False)
            t.setdefault("tags", [t.get("domain")])
            t.setdefault("standards", [])
            t.setdefault("prerequisites", [])
            add_t.append(t)
            tid.add(t["id"])
        for d in sk["deps"]:
            key = (d["from"], d["to"])
            if key in have:
                continue
            add_d.append(dict(d))
            have.add(key)

    # tags 首位必须＝领域（门禁 test_math_bsd 的口径）；对全库统一校正，幂等
    fixed_tags = 0
    for t in topics + add_t:
        tg = [x for x in (t.get("tags") or []) if x != t.get("domain")]
        if (t.get("tags") or [None])[0] != t.get("domain"):
            t["tags"] = [t.get("domain")] + tg
            fixed_tags += 1
    if fixed_tags:
        print(f"tags 首位校正 {fixed_tags} 点")

    print(f"topics.json 现有 {len(topics)} 点 → 新增 {len(add_t)} 点（初中+高中课时点）")
    print(f"dependencies.json 现有 {len(deps)} 边 → 新增 {len(add_d)} 边")
    print("新增点按册分布:", dict(collections.Counter(t["chapter"].split(" ")[0] for t in add_t)))
    print("新增点按领域分布:", dict(collections.Counter(t["domain"] for t in add_t)))
    if len(add_t) != 617:
        print(f"⚠ 预期新增 617 点（396+221），实际 {len(add_t)} —— 若已部分并入可忽略")

    if a.write:
        all_t = topics + add_t
        json.dump(all_t, open(f"{a.root}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(f"{a.root}/topics.json", "a", encoding="utf-8").write("\n")
        json.dump(deps + add_d, open(f"{a.root}/dependencies.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        open(f"{a.root}/dependencies.json", "a", encoding="utf-8").write("\n")
        print(f"written: topics {len(all_t)} 点 / deps {len(deps) + len(add_d)} 边")


if __name__ == "__main__":
    main()
