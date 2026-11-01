# -*- coding: utf-8 -*-
"""检查单元素养测评卷：python3 check_exam.py E01"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(BASE))          # data/mental-health
BANK = os.path.join(os.path.dirname(BASE), "_bank")
QS = os.path.join(DATA, "questions.json")
if len(sys.argv) < 2:
    sys.exit("用法: python3 check_exam.py E01")


def norm(s):
    return re.sub(r"\s+|[，。？！、；：「」“”（）()]", "", s or "")


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    sa = {a[i:i + 6] for i in range(max(1, len(a) - 5))}
    sb = {b[i:i + 6] for i in range(max(1, len(b) - 5))}
    return len(sa & sb) / max(1, len(sa | sb))


def main():
    sh = json.load(open(os.path.join(BASE, sys.argv[1] + ".json"), encoding="utf-8"))
    p = os.path.join(BANK, sh["shard"] + ".json")
    if not os.path.exists(p):
        sys.exit(f"FAIL 缺文件 {p}")
    e = json.load(open(p, encoding="utf-8"))
    fails = []

    def ck(name, ok, detail=""):
        if not ok:
            fails.append(f"{name} {detail}")

    items = [it for s in e.get("sections", []) for it in s.get("items", [])]
    ck("题量 20", len(items) == 20, len(items))
    by_type = {}
    for s in e.get("sections", []):
        by_type[s.get("type")] = by_type.get(s.get("type"), 0) + len(s.get("items", []))
    ck("choice 12 / judge 4 / short 4",
       by_type.get("choice") == 12 and by_type.get("judge") == 4 and by_type.get("short") == 4, by_type)
    total = sum(it.get("score", 0) for it in items)
    ck("满分 100", total == 100, total)
    ck("时长 40", e.get("duration") == 40, e.get("duration"))

    want_units = {u["unit_name"] for u in sh["units"]}
    seen_units = {it.get("unit") for it in items}
    ck("单元名都在派单内", seen_units <= want_units, sorted(seen_units - want_units)[:3])
    need = 4 if len(want_units) <= 3 else 2
    per_unit = {}
    for it in items:
        per_unit[it.get("unit")] = per_unit.get(it.get("unit"), 0) + 1
    ck(f"每单元 ≥{need} 题", all(per_unit.get(u, 0) >= need for u in want_units),
       {u: per_unit.get(u, 0) for u in want_units if per_unit.get(u, 0) < need})

    ids = {t["id"] for u in sh["units"] for t in u["lessons"]} | {u["unit_id"] for u in sh["units"]}
    noc = [i for i, it in enumerate(items, 1) if it.get("topicId") not in ids]
    ck("topicId 可解析", not noc, noc[:5])

    for it in items:
        no = it.get("no")
        ck(f"第{no}题 有解析", len(it.get("explain") or "") >= 15)
        if it.get("score") in (4,) and it.get("stem"):
            pass
        t = it.get("type") or ""
        if "options" in it:
            opts = it["options"]
            ck(f"第{no}题 4 选项", len(opts) == 4 and [o.get("label") for o in opts] == list("ABCD"))
            ck(f"第{no}题 答案在选项内", it.get("answer") in "ABCD")
        elif it.get("answer") in ("√", "×"):
            pass
        else:
            rub = it.get("rubric") or []
            ck(f"第{no}题 简答有 rubric", len(rub) == 3, len(rub))
            ssum = 0
            for r in rub:
                m = re.search(r"(\d+)\s*分", r)
                ssum += int(m.group(1)) if m else 0
            ck(f"第{no}题 rubric 合计=题分", ssum == it.get("score"), (ssum, it.get("score")))
            ck(f"第{no}题 参考答案 60–120 字", 60 <= len(it.get("answer") or "") <= 140,
               len(it.get("answer") or ""))

    bp = e.get("blueprint") or []
    ck("blueprint 20 行", len(bp) == 20, len(bp))
    ck("blueprint 分合计 100", sum(b.get("score", 0) for b in bp) == 100,
       sum(b.get("score", 0) for b in bp))
    ck("blueprint 素养合法",
       all(b.get("domain") in ("自我意识", "情绪管理", "人际交往", "学会学习", "生命与社会适应")
           for b in bp))

    # 与题库去重
    if os.path.exists(QS):
        pool = [q["prompt"] for q in json.load(open(QS, encoding="utf-8"))
                if q.get("topicId") in ids]
        worst = max((sim(it.get("stem", ""), q) for it in items for q in pool), default=0)
        ck("卷题与题库相似度 <0.85", worst < 0.85, round(worst, 3))

    print(f"{sh['shard']} {sh['label']}：{len(items)} 题 / {total} 分 / {e.get('duration')} 分钟；"
          f"覆盖 {len(per_unit)}/{len(want_units)} 单元")
    print("题型:", by_type, "| 每单元题量:", per_unit)
    if fails:
        print(f"\n❌ {len(fails)} 项未通过（前 20）:")
        for f in fails[:20]:
            print("  -", f)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
