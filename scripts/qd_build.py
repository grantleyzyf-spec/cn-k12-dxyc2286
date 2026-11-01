# -*- coding: utf-8 -*-
"""青岛版数学：由 _inventory.json 生成知识点骨架与先修边。

层级：`level=unit`（单元点，展示用）/ `level=lesson`（信息窗・小节点，可诊断）。
- id：`qdm_p001…` 按「册序 → 单元序 → 课时序」连续发号（只增不改，二次扩点从最大号续编）。
- chapter：`<册> 第<中文>单元 <情境名>`；课时点再追加 ` 信息窗N <名>` / ` 第N节 <名>`。
- 课标：青岛版同属义务教育数学，quote 从本库 `data/math/topics.json`（人教版，601/601 已回表）
  按「同学段 + 名称最相似」借调，统一记 `confidence: inferred`；无相似项时退回该领域该学段最常见条目。
- domain：课标四领域（数与代数 / 图形与几何 / 统计与概率 / 综合与实践），关键词判定 + OVERRIDE 人工裁定。
- 边四类：单元→课时 hard、课内课时顺次 hard、册内单元衔接 soft、册际衔接 soft；镜像回 prerequisites。

用法: python3 scripts/qd_build.py [--write] [--books 一年级上册,二年级上册]
"""
import difflib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QD = os.path.join(ROOT, "data", "math-qd")
INV = os.path.join(QD, "_inventory.json")
DONOR = os.path.join(ROOT, "data", "math", "topics.json")

CN = "一二三四五六七八九十"

DOMAIN_RULES = [
    ("统计与概率", r"统计|数据|概率|可能性|平均数|条形|折线|扇形|抽样|随机|频数|频率|调查"),
    ("图形与几何", r"图形|几何|角|线段|垂线|平行|三角形|四边形|长方形|正方形|圆|面积|体积|周长|对称|平移|旋转|位置|方向|观察物体|视图|相似|全等|勾股|坐标|立体|展开图|轴对称|中心对称|尺规|投影"),
    ("数与代数", r"数|运算|加|减|乘|除|方程|分数|小数|比|百分|代数|函数|比例|负数|有理数|整式|因式|不等式|平方根|立方根|指数|对数|数列|集合|绝对值|相反数|倒数|估算|口诀|乘法表|单位|时间|人民币|元角分|质量|长度|毫米|厘米|米|千米|克|千克|吨|容积|升|毫升"),
]
SPECIAL = r"^(?:主题活动|智慧广场|项目学习|数学游戏|数学漫游)|整理与复习|总复习"

OVERRIDE = {}  # {(册, 单元号): 领域} 人工裁定用；打印未命中项后再补


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def domain_of(name, content, is_special=False):
    text = f"{name} {content}"
    if is_special or re.search(SPECIAL, name):
        return "综合与实践"
    for dom, pat in DOMAIN_RULES:
        if re.search(pat, text):
            return dom
    return "数与代数"


def band(grade):
    if grade >= 10:
        return "10-12"
    return "1-2" if grade <= 2 else ("3-6" if grade <= 6 else "7-9")


def build():
    inv = json.load(open(INV, encoding="utf-8"))
    donor = json.load(open(DONOR, encoding="utf-8"))
    books = inv["books"]
    only = None
    for a in sys.argv:
        if a.startswith("--books"):
            only = set(a.split("=", 1)[1].split(",")) if "=" in a else None
    if "--books" in sys.argv:
        only = set(sys.argv[sys.argv.index("--books") + 1].split(","))

    # 借调表：按学段分组的人教版（名称, 课标条目）
    pool = defaultdict(list)
    for t in donor:
        st = (t.get("standards") or [{}])[0]
        if not st.get("quote"):
            continue
        pool[band(t["grade"])].append((t["name"], st))
    fallback = {}
    for b, items in pool.items():
        by_dom = defaultdict(Counter)
        for name, st in items:
            by_dom[domain_of(name, "")][st["id"]] += 1
        fallback[b] = {d: c.most_common(1)[0][0] for d, c in by_dom.items()}
    by_id = {st["id"]: st for items in pool.values() for _, st in items}

    topics, deps = [], []
    seq = 0
    unmatched_dom = []
    for b in books:
        if only and b["book"] not in only:
            continue
        units = b["units"]
        prev_last = None
        for u in units:
            seq += 1
            unit_id = f"qdm_p{seq:03d}"
            uname = re.sub(r"\s+", "", u["title"]).strip()
            ucontent = re.sub(r"\s+", "", u.get("content") or uname)
            special = bool(re.search(SPECIAL, uname))
            if special and ucontent and ucontent != uname:
                uname = f"{uname}·{ucontent}"   # 主题活动/智慧广场 同名多条，用副标题区分
            dom = OVERRIDE.get((b["book"], u["no"])) or domain_of(uname, ucontent, special)
            chapter = f"{b['book']} 第{_cn(u['no'])}单元 {uname}" if u.get("numbered") else f"{b['book']} {uname}"
            topics.append(_topic(unit_id, uname, b, dom, chapter, ucontent, "unit"))
            lesson_ids = []
            prev = None
            for k, l in enumerate(u.get("lessons") or [], 1):
                seq += 1
                lid = f"qdm_p{seq:03d}"
                lname = re.sub(r"\s+", "", l["name"]).strip()
                kind = "信息窗" if l.get("kind") == "信息窗" else "节"
                lchapter = f"{chapter} {kind}{l['no'] if kind == '信息窗' else ''} {lname}".replace("   ", " ").strip()
                topics.append(_topic(lid, lname, b, domain_of(lname, "") or dom, lchapter, lname, "lesson"))
                deps.append({"from": unit_id, "to": lid, "type": "hard"})
                if prev:
                    deps.append({"from": prev, "to": lid, "type": "hard"})
                prev = lid
                lesson_ids.append(lid)
            if prev_last and lesson_ids:
                deps.append({"from": prev_last, "to": lesson_ids[0], "type": "soft"})
            prev_last = lesson_ids[-1] if lesson_ids else (prev_last or unit_id)
            if not u.get("lessons"):
                unmatched_dom.append((b["book"], u["no"], uname, dom))

    # 课标借调
    for t in topics:
        b_ = band(t["grade"])
        cands = pool.get(b_) or []
        best = max(((difflib.SequenceMatcher(None, t["name"], n).ratio(), st) for n, st in cands),
                   key=lambda x: x[0], default=(0, None))
        sid = fallback.get(b_, {}).get(t["domain"]) or (fallback.get(b_, {}).get("数与代数"))
        st = best[1] if best[0] >= 0.55 else by_id.get(sid)
        if st:
            t["standards"] = [{"id": st["id"], "quote": st["quote"], "confidence": "inferred"}]
            if "sourceLine" in st:
                t["standards"][0]["sourceLine"] = st["sourceLine"]
            t["curriculumRef"] = st["id"]
        else:
            t["standards"] = []

    # prerequisites 镜像
    pre = defaultdict(set)
    for d in deps:
        pre[d["to"]].add(d["from"])
    for t in topics:
        t["prerequisites"] = sorted(pre.get(t["id"], []))

    # 根节点 reason（无先修的点必须写，门禁会断言）
    for t in topics:
        if not pre.get(t["id"]):
            t["root_reason"] = (f"起始知识点：《{t['chapter'].split(' ')[0]}》"
                                f"{'单元' if t['level']=='unit' else '课时'}起点，图谱内无更早前置")

    return inv, topics, deps, unmatched_dom


def _cn(n):
    if n <= 10:
        return CN[n - 1]
    if n < 20:
        return "十" + CN[n - 11]
    return CN[n // 10 - 1] + "十" + (CN[n % 10 - 1] if n % 10 else "")


def _topic(tid, name, b, dom, chapter, desc, level):
    return {
        "id": tid, "name": name, "subject": "math-qd", "domain": dom,
        "grade": b["grade"], "semester": b["semester"], "chapter": chapter, "level": level,
        "type": "procedural" if level == "lesson" else "conceptual",
        "description": desc,
        "mastery_criteria": [f"能说出/运用「{name}」的基本方法并解决对应练习"],
        "diagnostic_question": {"question": f"关于「{name}」，下列说法正确的是？", "answer": "A"},
        "external": False, "standards": [], "tags": [dom], "prerequisites": [],
        "curriculumRef": "", "verified": False,
    }


def main():
    write = "--write" in sys.argv
    inv, topics, deps, unmatched = build()
    print("知识点:", len(topics), "| unit:", sum(1 for t in topics if t["level"] == "unit"),
          "| lesson:", sum(1 for t in topics if t["level"] == "lesson"))
    print("先修边:", len(deps), Counter(d["type"] for d in deps))
    print("领域:", Counter(t["domain"] for t in topics))
    print("年级:", dict(sorted(Counter(t["grade"] for t in topics).items())))
    nostd = [t["id"] for t in topics if not t["standards"]]
    print("无课标:", len(nostd), nostd[:5])
    print("只有单元点的单元（无信息窗/小节）:", len(unmatched), unmatched[:5])
    if write:
        os.makedirs(QD, exist_ok=True)
        json.dump(topics, open(os.path.join(QD, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(deps, open(os.path.join(QD, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if not os.path.exists(os.path.join(QD, "questions.json")):
            json.dump([], open(os.path.join(QD, "questions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("WRITTEN data/math-qd/{topics,dependencies,questions}.json")


if __name__ == "__main__":
    main()
