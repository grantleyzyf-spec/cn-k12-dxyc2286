# -*- coding: utf-8 -*-
"""青岛版数学：清理骨架里的脏条目 + 修正六上 4 个只剩序号的单元名。

来源：教材目录页混入表格行/页码行/栏目标题（例：'°'、'乙'、'乙的成绩/s'、'-,'、'm。'、空名），
以及八下目录页串入的整章「有理数的运算」（八下实际止于「数据的分析」）。

处置用**显式清单**，不按正则批量删——「角」「圆」这类单字是教材正名，不能被误删。

用法: python3 scripts/qd_fix_names.py [--write]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QD = os.path.join(ROOT, "data", "math-qd")

DROP_IDS = {
    "qdm_p245",  # 七上 一元一次方程 · 空名（目录噪声）
    "qdm_p253",  # 七上 基本的几何图形 · 空名
    "qdm_p258",  # 七下 数据的收集、整理与描述 · '°'
    "qdm_p323",  # 八下 二次根式 · '乙'
    "qdm_p342", "qdm_p343", "qdm_p344", "qdm_p345", "qdm_p346",  # 八下 整章「有理数的运算」= 目录页串入
    "qdm_p359", "qdm_p360",  # 九上 图形的相似 · 空名 / 'm。'
}

RENAME = {
    "qdm_p214": ("完美的图形—圆", "圆的认识、圆的周长、圆的面积", "六年级上册 第四单元 完美的图形—圆"),
    "qdm_p215": ("中国的世界遗产—解决问题", "用圆的知识解决实际问题", "六年级上册 第五单元 中国的世界遗产—解决问题"),
    "qdm_p216": ("抽奖转盘—可能性", "可能性的大小", "六年级上册 第六单元 抽奖转盘—可能性"),
    "qdm_p218": ("走进军营—方向与位置", "用数对、方向和距离确定位置", "六年级上册 第七单元 走进军营—方向与位置"),
}


def main():
    write = "--write" in sys.argv
    tp, qp, dp = (os.path.join(QD, f) for f in ("topics.json", "questions.json", "dependencies.json"))
    topics = json.load(open(tp, encoding="utf-8"))
    qs = json.load(open(qp, encoding="utf-8"))
    deps = json.load(open(dp, encoding="utf-8"))

    keep, dropped, renamed = [], [], []
    for t in topics:
        if t["id"] in DROP_IDS:
            dropped.append((t["id"], repr(t.get("name")), t["chapter"]))
            continue
        if t["id"] in RENAME:
            name, desc, chap = RENAME[t["id"]]
            renamed.append((t["id"], repr(t.get("name")), name))
            t["name"], t["description"], t["chapter"] = name, desc, chap
        keep.append(t)

    kept_qs = [q for q in qs if q["topicId"] not in DROP_IDS]
    kept_deps = [e for e in deps if e["from"] not in DROP_IDS and e["to"] not in DROP_IDS]
    for t in keep:
        t["prerequisites"] = [p for p in t.get("prerequisites", []) if p not in DROP_IDS]

    print(f"丢弃脏点 {len(dropped)}；改名 {len(renamed)}")
    for d in dropped:
        print("   丢", d[0], d[1], "|", d[2])
    for r in renamed:
        print("   改", r[0], r[1], "→", r[2])
    print(f"知识点 {len(topics)} → {len(keep)}；题目 {len(qs)} → {len(kept_qs)}；边 {len(deps)} → {len(kept_deps)}")
    if write:
        json.dump(keep, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(kept_qs, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(kept_deps, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("WRITTEN")
    else:
        print("dry-run（加 --write 落盘）")


if __name__ == "__main__":
    main()
