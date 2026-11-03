#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""晋教版初中地理（geography-jin）→ 骨架 _skeleton.json ＋ 内容派单分片。

结构源：`_outline.json`（由 build_geo_jin_outline.py 从分课时 docx 与大单元 docx 抽出，
16 主题 × 8 课时 = 128 课时）。

口径（写死，改前先看 SKILL §3）：
- 单元点 id `gjin_u0NN`，课时点 id `gjin_j0NN`；按「册 → 主题号 → 课时号」顺序连续分配，只增不改。
- `chapter`：单元点 = `<册> 主题X <主题名>`；课时点 = 同上 ＋ ` · 第N课时 <课时名>`
  （与 exam scope 口径一致：`chapter == sc or chapter.startswith(sc + " · ")`）。
- `domain` 只用**义教地理**四领域：地球与地图 / 世界地理 / 中国地理 / 乡土地理。
- `grade`：七年级 7、八年级 8；`semester`：上/下。
- 题 id 段：课时点 q01 = 该点 diagnostic_question（由内容工位写），q02..q08 新写；单元点 q01..q05。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-jin")
OUTLINE = os.path.join(D, "_outline.json")
SKEL = os.path.join(D, "_skeleton.json")
PTS = os.path.join(D, "_points")

GRADE = {"七年级上册": (7, "上"), "七年级下册": (7, "下"),
         "八年级上册": (8, "上"), "八年级下册": (8, "下")}
BOOKCODE = {"七年级上册": "j7a", "七年级下册": "j7b", "八年级上册": "j8a", "八年级下册": "j8b"}

# 主题 → 义教地理四领域（逐主题人工裁定，见 docs/geography-jin.md）
DOMAIN = {
    ("七年级上册", 1): "地球与地图",   # 人类的太空家园（地球的宇宙环境）
    ("七年级上册", 2): "地球与地图",   # 模拟地球运动
    ("七年级上册", 3): "地球与地图",   # 海陆面貌与地图
    ("七年级上册", 4): "世界地理",     # 居住地：人口、气候、聚落
    ("七年级下册", 5): "世界地理",     # 大洲地理特征
    ("七年级下册", 6): "世界地理",     # 一带一路沿线地区
    ("七年级下册", 7): "世界地理",     # 认识国家发展差异
    ("七年级下册", 8): "世界地理",     # 共谋区域发展与合作
    ("八年级上册", 1): "中国地理",     # 中国版图与自然环境
    ("八年级上册", 2): "中国地理",     # 人口与自然资源
    ("八年级上册", 3): "中国地理",     # 工农业与交通运输业
    ("八年级上册", 4): "中国地理",     # 大河与生态
    ("八年级下册", 5): "中国地理",     # 北京
    ("八年级下册", 6): "中国地理",     # 一方水土一方人（区域比较）
    ("八年级下册", 7): "中国地理",     # 区域联系与合作发展
    ("八年级下册", 8): "乡土地理",     # 走进家乡（山西）
}


def cn_num(s):
    CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    return int(s) if s.isdigit() else CN[s]


def main() -> int:
    data = json.load(open(OUTLINE, encoding="utf-8"))
    os.makedirs(PTS, exist_ok=True)

    points, shards = [], []
    ui = ji = 0
    for book in ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]:
        grade, sem = GRADE[book]
        for u in data["books"][book]:
            m = re.match(r"主题([一二三四五六七八九十\d]+)\s+(.+)$", u["unit"])
            uno, uname = cn_num(m.group(1)), m.group(2).strip()
            ui += 1
            uid = f"gjin_u{ui:03d}"
            uchapter = f"{book} 主题{m.group(1)} {uname}"
            domain = DOMAIN[(book, uno)]
            points.append(dict(
                id=uid, name=f"主题{m.group(1)} {uname}", level="unit",
                chapter=uchapter, book=book, unitNo=uno, grade=grade, semester=sem,
                domain=domain, subject="geography-jin", type="conceptual", external=False,
            ))
            lesson_ids = []
            for les in u["lessons"]:
                ji += 1
                jid = f"gjin_j{ji:03d}"
                lesson_ids.append(jid)
                points.append(dict(
                    id=jid, name=les["name"], level="lesson",
                    chapter=f"{uchapter} · 第{les['no']}课时 {les['name']}",
                    book=book, unitNo=uno, lessonNo=les["no"], grade=grade, semester=sem,
                    domain=domain, subject="geography-jin", type="conceptual", external=False,
                    unitId=uid,
                ))
            shards.append(dict(
                shard=f"T{ui:02d}", book=book, unitNo=uno, unitLabel=f"主题{m.group(1)} {uname}",
                unitId=uid, chapter=uchapter, domain=domain, grade=grade, semester=sem,
                bookCode=BOOKCODE[book],
                lessons=[dict(id=i, **{k: v for k, v in p.items() if k in ("name", "lessonNo")})
                         for i, p in zip(lesson_ids, [x for x in points if x["id"] in lesson_ids])],
            ))

    # 统一按 id 排序写盘
    points.sort(key=lambda p: p["id"])
    json.dump(points, open(SKEL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 派单分片：每主题一片，自带落盘路径与题目 id 区间
    for s in shards:
        qids = []
        for i, les in enumerate(s["lessons"]):
            qids += [f"{les['id']}_q{n:02d}" for n in range(1, 9)]
        qids += [f"{s['unitId']}_q{n:02d}" for n in range(1, 6)]
        s["questionIds"] = qids
        s["outPoints"] = f"data/geography-jin/_points/{s['shard']}.json"
        s["outBank"] = f"data/geography-jin/_bank/{s['shard']}.json"
        json.dump(s, open(os.path.join(PTS, f"{s['shard']}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    units = [p for p in points if p["level"] == "unit"]
    lessons = [p for p in points if p["level"] == "lesson"]
    print(f"骨架：{len(points)} 点（单元 {len(units)} ＋ 课时 {len(lessons)}）→ {SKEL}")
    print(f"派单分片：{len(shards)} 片 → {PTS}/T01..T{len(shards):02d}.json")
    print(f"题 id 预分配：每主题 {len(shards[0]['questionIds'])} 题 × {len(shards)} ＝ {sum(len(s['questionIds']) for s in shards)} 题")
    for s in shards:
        print(f"  {s['shard']} {s['book']} {s['unitLabel']}（{s['domain']}）课时 {len(s['lessons'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
