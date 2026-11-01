#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版数学：盘点结果 → 知识图谱骨架（topics 结构 + 先修边 + 课标待挂）。

口径（与 data/math 人教版一致）：
- 一个**教材课时** = 一个知识点（课时级）；习题课/巩固练习/回顾与思考/复习课不成点（并入所在节）。
- id：`mbs_p001…`（小学 1–6 年级）/ `mbs_j001…`（初中）/ `mbs_h001…`（高中），按「册序→单元序→课时序」连续发号。
- chapter：`<册> 第<中文>单元 <单元名>`（小学）/ `第<中文>章 <章名>`（初中、高中）；
- grade：册 → 年级（小学 1–6、初中 7–9、高中 必修一=10 必修二=11 选必一=12 选必二=13）；
- semester：上册=上、下册=下；
- domain：先按关键词落课标四领域（数与代数/图形与几何/统计与概率/综合与实践），未命中进 TODO 清单人工裁定；
- 边：同单元课时顺次 hard；跨单元同领域纵向 soft；册际首末 soft。

用法: python3 scripts/build_bsd_skeleton.py --stage 小学 --scan /tmp/bsd_小学.json \
        --out data/math-bsd/_skeleton.json
"""
import argparse, json, os, re
from collections import defaultdict

CN = "一二三四五六七八九"
SKIP_LESSON = re.compile(r"习题|巩固练习|回顾与思考|复习课|单元检测|自测|阶段检测|章末|小结|整理与复习")

GRADE = {
    "一年级上册": 1, "一年级下册": 1, "二年级上册": 2, "二年级下册": 2, "三年级上册": 3, "三年级下册": 3,
    "四年级上册": 4, "四年级下册": 4, "五年级上册": 5, "五年级下册": 5, "六年级上册": 6, "六年级下册": 6,
    "七年级上册": 7, "七年级下册": 7, "八年级上册": 8, "八年级下册": 8, "九年级上册": 9, "九年级下册": 9,
    "必修第一册": 10, "必修第二册": 11, "选择性必修第一册": 12, "选择性必修第二册": 13,
    "选择性必修第三册": 14, "选择性必修第四册": 15,
}
UNIT_DOMAIN_OVERRIDE = {
    # 课标归类裁定（关键词规则抓不到的）
    "整理与分类": "统计与概率",     # 分类属于「数据分类」
    "分类": "统计与概率",
    "测量（一）": "图形与几何",     # 长度单位与测量属于图形与几何
    "测量（二）": "图形与几何",
}
# 领域关键词（课标四领域）。先按单元名判，再按课时名兜底。
DOMAIN_RULES = [
    ("图形与几何", r"图形|几何|角|三角|四边|平行|垂直|圆|周长|面积|体积|立体|观察物体|对称|平移|旋转|方向|位置|线|长方体|正方体|圆柱|圆锥|展开|视图|相似|投影|勾股|四边形|多边形|扇形|弧|坐标|向量|空间"),
    ("统计与概率", r"统计|概率|数据|平均|条形|折线|扇形|调查|可能|随机|抽样|频数|频率|直方|树状图|期望|方差|回归|相关|计数原理|排列|组合"),
    ("综合与实践", r"数学好玩|综合实践|综合与实践|实践|活动|探索|游戏|编码|导航|设计|调查与记录|关系与规律|动手做|填数游戏|数图形"),
    ("数与代数", r"数|加|减|乘|除|方程|式|小数|分数|百分数|比例|比|运算|计算|代数|函数|指数|对数|不等式|集合|逻辑|数列|导数|复数|整式|因式|分式|根|幂|估算|认识更大的数|生活中|加减|换算|单位|时间|质量|货币|字母表示"),
]


def cn_num(n):
    if n <= 10:
        return CN[n - 1] if n <= 9 else "十"
    if n < 20:
        return "十" + CN[n - 11]
    return str(n)


def pick_domain(unit_name, lesson_name):
    for key, dom in UNIT_DOMAIN_OVERRIDE.items():
        if key in (unit_name or ""):
            return dom, "override"
    for name in (lesson_name, unit_name):
        for dom, pat in DOMAIN_RULES:
            if re.search(pat, name or ""):
                return dom, "rule"
    return None, "todo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="小学", choices=["小学", "初中", "高中"])
    ap.add_argument("--scan", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    books = json.load(open(a.scan, encoding="utf-8"))
    prefix = {"小学": "mbs_p", "初中": "mbs_j", "高中": "mbs_h"}[a.stage]
    topics, todo, skipped = [], [], 0
    counter = 0
    for book, units in books.items():
        grade = GRADE.get(book)
        semester = "上" if book.endswith("上册") or book.endswith("第一册") else "下"
        if book.startswith("必修第") or book.startswith("选择性必修第"):
            semester = "上"
        for u in units:
            uname = u["unit_name"]
            marker = "单元" if a.stage == "小学" else "章"
            chap = f"{book} 第{cn_num(u['unit_no'])}{marker} {uname}"
            prev_id = None
            for k, lname in u["lessons"]:
                if SKIP_LESSON.search(lname):
                    skipped += 1
                    continue
                counter += 1
                tid = f"{prefix}{counter:03d}"
                dom, how = pick_domain(uname, lname)
                if dom is None:
                    todo.append({"id": tid, "book": book, "unit": uname, "lesson": lname})
                topics.append({
                    "id": tid, "name": lname, "subject": "math-bsd",
                    "domain": dom or "待定", "grade": grade, "semester": semester,
                    "chapter": chap, "level": "lesson",
                    "type": "procedural", "description": "", "mastery_criteria": [],
                    "diagnostic_question": {}, "external": False, "standards": [],
                    "tags": [dom or "待定"], "prerequisites": [], "verified": False,
                    "_unit_no": u["unit_no"], "_book": book, "_seq": k,
                    "_prev": prev_id,
                })
                prev_id = tid

    # 边：同单元顺次 hard
    byid = {t["id"]: t for t in topics}
    deps = []
    for t in topics:
        if t["_prev"]:
            deps.append({"from": t["_prev"], "to": t["id"], "type": "hard"})
            t["prerequisites"] = [t["_prev"]]
    # 册际软边：上一册最后一个点 → 本册首点
    book_first, book_last = {}, {}
    for t in topics:
        book_first.setdefault(t["_book"], t["id"])
        book_last[t["_book"]] = t["id"]
    order = [b for b in GRADE if b in book_first]
    for i in range(1, len(order)):
        a_id, b_id = book_last[order[i - 1]], book_first[order[i]]
        if a_id != b_id:
            deps.append({"from": a_id, "to": b_id, "type": "soft"})
            byid[b_id]["prerequisites"].append(a_id)

    for t in topics:
        for k in ("_unit_no", "_book", "_seq", "_prev"):
            t.pop(k, None)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"stage": a.stage, "topics": topics, "deps": deps,
               "todo_domain": todo, "skipped_lessons": skipped},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"知识点 {len(topics)} | 边 {len(deps)} | 跳过习题/复习课 {skipped} | 领域待定 {len(todo)}")
    print("领域分布:", Counter(t["domain"] for t in topics))
    print("册分布:", Counter(t["chapter"].split(" ")[0] for t in topics))
    print("written", a.out)
    if todo:
        print("待定样例:", [(x["lesson"], x["unit"]) for x in todo[:8]])


if __name__ == "__main__":
    main()
