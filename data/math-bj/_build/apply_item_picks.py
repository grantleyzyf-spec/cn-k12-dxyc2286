# -*- coding: utf-8 -*-
"""把「课标原文条目池」挑出的结果落到 data/math-bj/topics.json（第二轮补挂）。

纪律（同第一轮）：
- 只接受候选集里真实存在的条目，`quote` 必须逐字命中课标 TXT（norm 去空白/标点后子串）；
- 不改写 quote、不新造 id、不动已挂标的点；
- 父代可用 _std_work/overrides_items.json（{"<pid>": {"n": 1-5|null}}）覆盖工位判定；
- 干跑打印明细，--write 才落盘。

用法：python3 apply_item_picks.py [--write]
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
NOISE = re.compile(r"^=+\s*$|^page \d+ / \d+$|^\d{1,3}$")


def norm(s):
    return re.sub(r"[\s　，。、；：？！“”‘’（）()《》〈〉·—…\-~,.;:?!\"'/\\|\[\]【】]+", "", s or "")


def main():
    write = "--write" in sys.argv
    raw = open(TXT, encoding="utf-8", errors="ignore").read().split("\n")
    src = norm("".join("" if (NOISE.match(x.strip()) or x.strip().startswith("====")) else x for x in raw))

    topics = json.load(open(os.path.join(DATA, "math-bj", "topics.json"), encoding="utf-8"))
    by_id = {t["id"]: t for t in topics}
    ov_path = os.path.join(WORK, "overrides_items.json")
    ov = json.load(open(ov_path, encoding="utf-8"))["overrides"] if os.path.exists(ov_path) else {}
    # 父代直接判读（id + quote 显式给出，建表时已逐字校验）
    dp_path = os.path.join(WORK, "overrides_items_direct.json")
    direct = json.load(open(dp_path, encoding="utf-8"))["overrides"] if os.path.exists(dp_path) else {}

    applied, skipped, bad, missing = [], [], [], []
    for cf in sorted(glob.glob(os.path.join(WORK, "gap_cands_G*.json"))):
        shard = os.path.basename(cf).replace("gap_cands_", "").replace(".json", "")
        pf = os.path.join(WORK, f"pick_{shard}.json")
        if not os.path.exists(pf):
            missing.append(shard)
            continue
        cands = {p["pid"]: p for p in json.load(open(cf, encoding="utf-8"))["points"]}
        picks = json.load(open(pf, encoding="utf-8"))["picks"]
        picks = {**{k: v for k, v in direct.items()}, **picks}  # 父代直接判读优先
        for pid, pick in picks.items():
            t = by_id.get(pid)
            if not t:
                bad.append((shard, pid, "点不存在"))
                continue
            if t.get("standards"):
                skipped.append((pid, "已挂标"))
                continue
            if isinstance(pick, dict) and pick.get("quote"):   # 直接判读形态
                c = {"n": 0, "id": pick["id"], "quote": pick["quote"]}
                conf = pick.get("confidence")
                n = 0
            else:
                n = pick.get("n") if isinstance(pick, dict) else None
                conf = pick.get("confidence") if isinstance(pick, dict) else None
                c = None
            if pid in ov and not (isinstance(pick, dict) and pick.get("quote")):
                n = ov[pid].get("n")
            if not n:
                skipped.append((pid, "判 null"))
                continue
            if c is None:
                c = {x["n"]: x for x in cands.get(pid, {}).get("cands", [])}.get(n)
            if not c:
                bad.append((shard, pid, f"候选 n={n} 不存在"))
                continue
            if norm(c["quote"]) not in src:
                bad.append((shard, pid, "quote 未逐字命中课标 TXT"))
                continue
            if conf not in ("exact", "partial", "inferred"):
                conf = "partial"
            t["standards"] = [{"id": c["id"], "confidence": conf, "quote": c["quote"]}]
            t["curriculumRef"] = c["id"]
            applied.append((pid, t["name"], c["id"], conf, c["quote"][:26]))

    print(f"落标 {len(applied)} 点 | 跳过 {len(skipped)} | 异常 {len(bad)} | 缺片 {missing}")
    for a in applied:
        print("  ✓", a[0], a[1], "→", a[2], f"[{a[3]}]", a[4])
    for b in bad:
        print("  ⚠", b)
    tot = len(topics)
    n = sum(1 for t in topics if t.get("standards"))
    print(f"挂标率：{n}/{tot} = {n / tot * 100:.1f}%")
    if write:
        json.dump(topics, open(os.path.join(DATA, "math-bj", "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写 topics.json")
    else:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
