#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）地理：出卷派单（32 卷 = 16 单元卷 ＋ 4 册 × 4 期中期末）。

卷面口径（与 geography 桶一致，写进派单不许现算）：
  初中 120 分 / 120 分钟 / 24 题 —— 选择题 18×3＝54，综合题 6×11＝66。
  sections 只有两段，`rule` 文本固定为「每小题 3 分，共 54 分」「每小题 11 分，共 66 分」。

examId：单元卷 `gztu_exam_<bookcode>_u0N`（N＝主题号），期中 A/B `_mid_a/_mid_b`，期末 `_fin_a/_fin_b`。
班级拆分：每片 4 卷（一册一片）→ E01..E04 单元卷按册各 1 片（4 主题 4 卷）、E05..E08 期中期末按册各 1 片。
⛔ 生成后必须断言：32 卷 examId 唯一；卷名唯一；单元卷 scope 与主题名逐字一致。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
SHARDS = os.path.join(D, "_exam_shards")
BOOKCODE = {"七年级上册": "j7a", "七年级下册": "j7b", "八年级上册": "j8a", "八年级下册": "j8b"}
BOOKS = list(BOOKCODE)
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
          "十": 10, "十一": 11, "十二": 12}


def main() -> int:
    os.makedirs(SHARDS, exist_ok=True)
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    units = [t for t in topics if t["level"] == "unit"]

    paper_ids, all_ids, names = [], [], []
    shards = []
    e = 0
    # 单元卷：一册一片，4 卷/片
    for book in BOOKS:
        e += 1
        # 绪论是开学第一课、不是正式单元 ⇒ 不出卷（与「综合与实践/总复习不出卷」同口径）
        us = [t for t in units if t["chapter"].split(" ")[0] == book and "绪论" not in t["chapter"]]
        us.sort(key=lambda t: t["chapter"])
        papers = []
        for t in us:
            n = re.search(r"第([一二三四五六七八九十\d]+)章", t["chapter"])
            uno = n.group(1) if n else ""
            code = CN_NUM.get(uno, 0)
            assert code, f"{t['id']} 章号解析失败：{t['chapter']}"
            pid = f"gztu_exam_{BOOKCODE[book]}_u{code:02d}"
            paper = f"{t['chapter']} 测试卷"
            papers.append(dict(
                examId=pid, kind="unit", paper=paper, scope=[t["chapter"]],
                unitPoint=t["id"], lessonPoints=[x["id"] for x in topics
                                                 if x.get("prereqUpper") == t["id"]],
                topicIds=[t["id"]] + [x["id"] for x in topics if x.get("prereqUpper") == t["id"]],
                sections=[dict(rule="每小题 3 分，共 54 分", count=18),

                          dict(rule="每小题 11 分，共 66 分", count=6)]))
            paper_ids.append(pid)
            names.append((book, paper))
        shards.append(dict(shard=f"E{e:02d}", book=book, grade=(7 if "七年级" in book else 8),
                           term=("上" if "上册" in book else "下"), stage="初中",
                           duration=120, fullScore=120,
                           out=f"data/geography-zhongtu-cz/_exam_out/E{e:02d}.json",
                           papers=papers))
    # 期中期末：一册一片，4 卷/片（期中覆盖前半册、期末覆盖全册）
    for book in BOOKS:
        e += 1
        us = sorted([t for t in units if t["chapter"].split(" ")[0] == book], key=lambda t: t["chapter"])
        ch = [t["chapter"] for t in us]
        half = max(2, len(ch) // 2)
        papers = []
        for kind, tag, scope in (("mid", "a", ch[:half]), ("mid", "b", ch[:half]),
                                 ("fin", "a", ch), ("fin", "b", ch)):
            pid = f"gztu_exam_{BOOKCODE[book]}_{kind}_{tag}"
            paper = f"{'期中' if kind == 'mid' else '期末'}测试卷{tag.upper()}"
            tids = [t["id"] for t in topics
                    if any(t["chapter"] == sc or t["chapter"].startswith(sc + " · ") for sc in scope)]
            papers.append(dict(examId=pid, kind=kind, paper=paper, scope=scope,
                               topicIds=tids,
                               sections=[dict(rule="每小题 3 分，共 54 分", count=18),
                                         dict(rule="每小题 11 分，共 66 分", count=6)]))
            paper_ids.append(pid)
            names.append((book, paper))
        shards.append(dict(shard=f"E{e:02d}", book=book, grade=(7 if "七年级" in book else 8),
                           term=("上" if "上册" in book else "下"), stage="初中",
                           duration=120, fullScore=120,
                           out=f"data/geography-zhongtu-cz/_exam_out/E{e:02d}.json",
                           papers=papers))

    for s in shards:
        json.dump(s, open(os.path.join(SHARDS, f"{s['shard']}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    expect = len([t for t in units if "绪论" not in t["chapter"]]) + 4 * len(BOOKS)
    assert len(paper_ids) == expect, f"卷数 {len(paper_ids)} ≠ {expect}"
    assert len(set(paper_ids)) == expect, f"examId 撞号 {[k for k in paper_ids if paper_ids.count(k) > 1][:5]}"
    assert len(set(names)) == len(names), "同一册内卷名重复"
    for s in shards:
        ps = [p["paper"] for p in s["papers"]]
        assert len(set(ps)) == len(ps), f"{s['shard']} 片内卷名重复"
        assert not any("单元第" in p for p in ps), f"{s['shard']} 有坏卷名"
    print(f"派单 {len(shards)} 片 / {expect} 卷（单元 {expect - 16} ＋ 期中期末 16）")
    for s in shards:
        print(f"  {s['shard']} {s['book']}: " + "、".join(p["paper"] for p in s["papers"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
