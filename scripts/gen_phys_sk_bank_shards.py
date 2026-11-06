#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版地理：按「主题」生成题库派单槽位规格（_bank_spec/TNN.json）。

配方（写死，全库题型比例由此守住）：
- 课时 1–4：q01–q04 choice（3 basic ＋ 1 standard）＋ q05/q06 fill ＋ q07 short-answer ＋ q08 choice(hard)
- 课时 5–8：q01–q03 choice ＋ q04/q05 fill ＋ q06 short-answer ＋ q07 choice ＋ q08 numeric(hard，必带 verify)
- 课时点 q01 是完整库题（不是把 diagnostic_question 原句搬进来），diagnostic_question 另作点元数据
- 单元点：2 choice ＋ 1 fill ＋ 1 numeric ＋ 1 short-answer
⇒ 每片 56（课时）＋ 5（单元）＝ 61 题；全库 16 片 ＝ 976 题。
难度：每课时 7 题内 basic 3 / standard 3 / hard 1（既有三档，又贴合全库 41/45/14 的比例）。
答案位：choice 槽位在规格里**预分配 A/B/C/D**（按片内序号轮转），工人只许把正确项放在该 label 上，
不让工人自己决定，避免答案分布跑偏。
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
PTS = os.path.join(D, "_shards")
SPEC = os.path.join(D, "_bank_spec")

DIFF_LESSON = ["basic", "basic", "basic", "standard", "standard", "standard", "standard", "hard"]
DIFF_UNIT = ["basic", "basic", "standard", "standard", "hard"]


def main() -> int:
    os.makedirs(SPEC, exist_ok=True)
    if glob.glob(os.path.join(SPEC, "T*.json")) and "--force" not in sys.argv:
        print("⛔ _bank_spec 已存在（题槽规格是权威件，工位不得重生成）；确需重建请加 --force")
        return 0
    total = 0
    for fn in sorted(os.listdir(PTS)):
        if not fn.endswith(".json"):
            continue
        s = json.load(open(os.path.join(PTS, fn), encoding="utf-8"))
        items, letter_i = [], 0
        for i, les in enumerate(s["lessons"]):
            # 课时 8 题：q01..q08。课时 1–4 的第 8 题为 choice(hard)，5–8 为 numeric(hard)
            if i < 4:
                types = ["choice", "choice", "choice", "choice", "fill", "fill", "short-answer", "choice"]
            else:
                types = ["choice", "choice", "choice", "fill", "fill", "short-answer", "choice", "numeric"]
            slots = []
            for qn, (tp, diff) in enumerate(zip(types, DIFF_LESSON), start=1):
                slot = dict(id=f"{les['id']}_q{qn:02d}", type=tp, difficulty=diff)
                if tp == "choice":
                    slot["label"] = "ABCD"[letter_i % 4]
                    letter_i += 1
                slots.append(slot)
            items.append(dict(topicId=les["id"], name=les["name"], kind="lesson", slots=slots))
        # 单元点 5 题
        utypes = ["choice", "choice", "fill", "numeric", "short-answer"]
        uslots = []
        for qn, (tp, diff) in enumerate(zip(utypes, DIFF_UNIT), start=1):
            slot = dict(id=f"{s['unitId']}_q{qn:02d}", type=tp, difficulty=diff)
            if tp == "choice":
                slot["label"] = "ABCD"[letter_i % 4]
                letter_i += 1
            uslots.append(slot)
        items.append(dict(topicId=s["unitId"], name=s["unitLabel"], kind="unit", slots=uslots))

        spec = dict(shard=s["shard"], book=s["book"], unitLabel=s["unitLabel"], unitId=s["unitId"],
                    chapter=s["chapter"], domain=s["domain"], grade=s["grade"], semester=s["semester"],
                    items=items,
                    outBank=f"data/physics-sk/_bank/{s['shard']}.json",
                    parseNote="课时点 q01 也是库题，须与该点 diagnostic_question 的考点一致但措辞不同")
        json.dump(spec, open(os.path.join(SPEC, f"{s['shard']}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        n = sum(len(it["slots"]) for it in items)
        total += n
        print(f"  {s['shard']}: {len(items)} 点 / {n} 题规格")
    print(f"合计 {total} 题规格（＝全库成品题数）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
