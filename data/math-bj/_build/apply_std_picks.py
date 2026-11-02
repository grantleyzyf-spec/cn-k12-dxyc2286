# -*- coding: utf-8 -*-
"""把工位挑出的课标候选落到 data/math-bj/topics.json。

纪律：
- 只接受「候选集里真实存在的 (id, quote) 对」，且 quote 必须在课标 TXT 里逐字命中
  （norm 去空白/标点后子串判定）—— 与 scripts/test_math_bj.py 的回表口径一致。
- 不改写 quote、不新造 id、不动已挂标的点。
- 干跑打印明细，--write 才落盘。

用法：python3 apply_std_picks.py [--write]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(HERE, "_std_work")
TXT = os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt")


def norm(s):
    return re.sub(r"[\s，。、；：？！“”‘’（）()《》〈〉·—…\-~,.;:?!\"'/\\|\[\]【】]+", "", s or "")


def main():
    write = "--write" in sys.argv
    src = norm(open(TXT, encoding="utf-8", errors="ignore").read())
    bj_path = os.path.join(DATA, "math-bj", "topics.json")
    topics = json.load(open(bj_path, encoding="utf-8"))
    by_id = {t["id"]: t for t in topics}

    ov_path = os.path.join(WORK, "overrides.json")
    ov = json.load(open(ov_path, encoding="utf-8"))["overrides"] if os.path.exists(ov_path) else {}

    applied, skipped, bad, missing = [], [], [], []
    for cf in sorted(glob.glob(os.path.join(WORK, "cands_C*.json"))):
        shard = os.path.basename(cf).replace("cands_", "").replace(".json", "")
        pf = os.path.join(WORK, f"pick_{shard}.json")
        if not os.path.exists(pf):
            missing.append(shard)
            continue
        cands = {p["pid"]: p for p in json.load(open(cf, encoding="utf-8"))["points"]}
        picks = json.load(open(pf, encoding="utf-8"))["picks"]
        for pid, pick in picks.items():
            t = by_id.get(pid)
            if not t:
                bad.append((shard, pid, "点不存在"))
                continue
            if t.get("standards"):
                skipped.append((pid, "已挂标"))
                continue
            n = pick.get("n") if isinstance(pick, dict) else None
            conf_over = None
            if pid in ov:  # 父代裁定优先
                n = ov[pid].get("n")
                conf_over = (pick.get("confidence") if n else None)
            if not n:
                skipped.append((pid, "工位判 null"))
                continue
            pool = {c["n"]: c for c in cands[pid]["cands"]}
            c = pool.get(n)
            if not c:
                bad.append((shard, pid, f"候选 n={n} 不存在"))
                continue
            if norm(c["quote"]) not in src:
                bad.append((shard, pid, "quote 未在课标 TXT 逐字命中"))
                continue
            conf = conf_over if conf_over else pick.get("confidence")
            if conf not in ("exact", "partial", "inferred"):
                conf = "partial"
            t["standards"] = [{"id": c["id"], "confidence": conf, "quote": c["quote"]}]
            t["curriculumRef"] = c["id"]
            applied.append((pid, t["name"], c["id"], conf, c["quote"][:24]))

    print(f"落标 {len(applied)} 点 | 跳过 {len(skipped)} | 异常 {len(bad)} | 缺片 {missing}")
    for a in applied:
        print("  ✓", a[0], a[1], "→", a[2], f"[{a[3]}]", a[4])
    if bad:
        print("异常明细：")
        for b in bad:
            print("  ⚠", b)
    tot = len(topics)
    n = sum(1 for t in topics if t.get("standards"))
    print(f"挂标率：{n}/{tot} = {n / tot * 100:.1f}%")
    if write:
        json.dump(topics, open(bj_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写", bj_path)
    else:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
