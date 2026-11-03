#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版地理：题库分片生成（一单元一片，19 片）。

- 课时点 8 题：q01/q02 choice(basic)、q03/q04 choice(standard)、q05 fill(basic)、q06 fill(standard)、
  q07 short-answer(hard)、q08 numeric(standard，带 verify)
- 单元点 5 题：q01 choice(basic)、q02 choice(standard)、q03 fill(basic)、q04 numeric(standard)、q05 short-answer(hard)
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-yuejiao")
SD = os.path.join(D, "_bank_shards")
os.makedirs(SD, exist_ok=True)
os.makedirs(os.path.join(D, "_bank"), exist_ok=True)

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
units = [t for t in topics if t["level"] == "unit"]

LESSON_SLOTS = [("q01", "choice", "basic"), ("q02", "choice", "basic"),
                ("q03", "choice", "standard"), ("q04", "choice", "standard"),
                ("q05", "fill", "basic"), ("q06", "fill", "standard"),
                ("q07", "short-answer", "hard"), ("q08", "numeric", "standard")]
UNIT_SLOTS = [("q01", "choice", "basic"), ("q02", "choice", "standard"),
              ("q03", "fill", "basic"), ("q04", "numeric", "standard"),
              ("q05", "short-answer", "hard")]

index = []
for i, u in enumerate(units, 1):
    tag = f"GYJ_B{i:02d}"
    pts = [u] + [t for t in topics if t["chapter"].startswith(u["chapter"] + " · ")]
    items = []
    for t in pts:
        slots = UNIT_SLOTS if t["level"] == "unit" else LESSON_SLOTS
        items.append({
            "topicId": t["id"], "name": t["name"], "level": t["level"], "chapter": t["chapter"],
            "domain": t["domain"], "book": u["chapter"].split(" ")[0],
            "slots": [{"id": f"{t['id']}_{s[0]}", "type": s[1], "difficulty": s[2]} for s in slots],
        })
    payload = {"shard": tag, "subject": "geography-yuejiao", "edition": "粤教粤人版",
               "book": u["chapter"].split(" ")[0], "chapter": u["chapter"], "items": items,
               "out": f"data/geography-yuejiao/_bank/{tag}.json"}
    json.dump(payload, open(os.path.join(SD, f"{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    index.append({"shard": tag, "book": payload["book"], "chapter": u["name"],
                  "points": len(items), "questions": sum(len(x["slots"]) for x in items)})

json.dump(index, open(os.path.join(SD, "_INDEX.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"分片 {len(index)} 个 / 题 {sum(x['questions'] for x in index)}")
for x in index:
    print(f"  {x['shard']} {x['book']:6} {x['chapter']:14} 点{x['points']:2} 题{x['questions']:3}")
