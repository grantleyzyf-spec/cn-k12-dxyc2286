# -*- coding: utf-8 -*-
"""北京版数学骨架生成：units.json + 教材目录 → topics 骨架（单元点 + 课时点）与 dependencies。

用法:
  python3 skeleton.py            # 只打印盘点
  python3 skeleton.py --write    # 写 data/math-bj/_skeleton.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.expanduser("~/Desktop/中小学教材/精准提取各学科教材TXT文档/数学/北京版")
SUBJECT = "math-bj"
PREFIX = "mbj"
BOOK_ORDER = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "四下",
              "五上", "五下", "六上", "六下", "七上", "七下", "八上", "八下", "九上", "九下"]
CN = "一二三四五六七八九十"
CN_NUM = {c: i + 1 for i, c in enumerate(CN)}
CN_NUM["十"] = 10


def grade_of(book):
    return CN_NUM[book[0]]


def sem_of(book):
    return "上" if book[1] == "上" else "下"


def cn_no(n):
    """1–99 → 中文序号"""
    if n <= 10:
        return ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"][n]
    if n < 20:
        return "十" + cn_no(n - 10)
    return cn_no(n // 10) + "十" + (cn_no(n % 10) if n % 10 else "")


def read_book_txt(book):
    for seg in ("小学", "初中"):
        p = os.path.join(TXT, seg, f"北京版数学{book}.txt")
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="ignore").read()
    return ""


def parse_sections(book):
    """初中教材目录的 x.y 节 → [(章号, 节号, 节名)]。"""
    s = read_book_txt(book)
    if not s:
        return []
    idx = -1
    for marker in ("目 录", "目　录", "目录"):
        idx = s.find(marker)
        if idx >= 0:
            break
    region = s[idx: idx + 9000] if idx >= 0 else s[:9000]
    lines = [re.sub(r"\s+", " ", x).strip() for x in region.split("\n")]
    out = []
    for i, ln in enumerate(lines):
        m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})", ln)
        if not m:
            continue
        title = None
        for j in range(i + 1, min(i + 5, len(lines))):
            cand = lines[j]
            if not cand:
                continue
            cand = re.sub(r"\s*\d+$", "", cand).strip()          # 去页码
            cand = re.sub(r"[…\.]{2,}.*$", "", cand).strip()      # 去点线
            # 目录里常有 GBK 乱码尾巴（U+FFFD / \x08 串），在第一个乱码段处切断
            cand = re.split(r"[^\u4e00-\u9fff（）()、，·°0-9A-Za-z]{2,}", cand)[0].strip()
            cand = re.sub(r"^[◇○※\s]+", "", cand).strip("、，。· ")
            if 2 <= len(cand) <= 30 and re.search(r"[\u4e00-\u9fff]", cand):
                title = cand
            break
        if title:
            out.append((int(m.group(1)), int(m.group(2)), title))
    # 去重（目录常重复出现页眉）
    seen, res = set(), []
    for ch, sec, name in out:
        k = (ch, sec)
        if k in seen:
            continue
        seen.add(k)
        res.append((ch, sec, name))
    return res


DOMAIN_RULES = [
    (r"统计|数据|条形|扇形|折线|平均|百分|可能|调查|抽样|概率|随机|频率", "统计与概率"),
    (r"图形|几何|三角形|四边形|圆|角|平行|垂直|对称|平移|旋转|立体|长方体|正方体|圆柱|圆锥|相似|全等|勾股|视图|投影|坐标|位置|方向",
     "图形与几何"),
    (r"数学百花园|总复习|综合|实践|活动|时间管理|营养午餐|跳绳|理财|聪明|阅读|数学文化", "综合与实践"),
]
DEFAULT_DOMAIN = "数与代数"


def domain_of(name, chapter):
    text = f"{name} {chapter}"
    for pat, dom in DOMAIN_RULES:
        if re.search(pat, text):
            return dom
    return DEFAULT_DOMAIN


def type_of(name):
    if re.search(r"复习|整理|总复习|回顾|百花园", name):
        return "conceptual"
    if re.search(r"计算|运算|口算|笔算|估算|简算|乘法|除法|加法|减法|乘法|乘方|开方|解方程|解不等式|因式分解|化简|求值|换算|作|画|测量",
                 name):
        return "procedural"
    if re.search(r"证明|推理|判定|性质|定理", name):
        return "reasoning"
    if re.search(r"方程|不等式|函数|应用|建模|问题|统计|调查|概率", name):
        return "modeling"
    return "conceptual"


def build():
    units = json.load(open(os.path.join(HERE, "units.json"), encoding="utf-8"))
    try:
        OVERRIDES = json.load(open(os.path.join(HERE, "_overrides.json"), encoding="utf-8"))["_books"]
    except FileNotFoundError:
        OVERRIDES = {}
    books = {}
    for u in units:
        books.setdefault(u["book"], []).append(u)

    topics, edges = [], []
    seq = 0
    for book in BOOK_ORDER:
        if book not in books:
            continue
        seg = books[book][0]["seg"]
        g, sem = grade_of(book), sem_of(book)
        book_label = f"{cn_no(g)}年级{sem}册"
        used_no = set()
        for u in sorted(books[book], key=lambda x: (x["unit_no"] or 99)):
            uno = u["unit_no"]
            # 无编号单元（数学百花园/总复习/主题活动）按出现顺序顺延编号
            if uno is None:
                nxt = 1
                while nxt in used_no:
                    nxt += 1
                uno = nxt
            used_no.add(uno)
            marker = "章" if seg == "初中" else "单元"
            chapter = f"{book_label} 第{cn_no(uno)}{marker} {u['unit_name']}"
            seq += 1
            uid = f"{PREFIX}_p{seq:03d}"
            topics.append(dict(
                id=uid, name=u["unit_name"], subject=SUBJECT,
                domain=domain_of(u["unit_name"], chapter),
                grade=g, semester=sem, chapter=chapter, level="unit",
                type="conceptual", book=book, seg=seg, unit_no=uno,
            ))
            # 课时点
            lessons = [l for l in u["lessons"] if l.get("name")]
            if seg == "初中" and book in OVERRIDES:
                lesson_names = [(o["no"], o["name"]) for o in OVERRIDES[book]
                                if int(o["no"].split(".")[0]) == u.get("unit_no")]
            elif seg == "初中":
                valid = {u2["unit_no"] for u2 in books[book] if u2["unit_no"] is not None}
                secs = [(s, n) for (c, s, n) in parse_sections(book)
                        if c == u.get("unit_no") and c in valid]
                lesson_names = []
                for sec_no, name in secs:
                    lesson_names.append((f"{u['unit_no']}.{sec_no}", name))
            else:
                lesson_names = [(str(l["no"]), l["name"]) for l in sorted(lessons, key=lambda x: x["no"])]
            prev = uid
            for lno, lname in lesson_names:
                seq += 1
                lid = f"{PREFIX}_p{seq:03d}"
                lchapter = f"{chapter} {lname}"
                topics.append(dict(
                    id=lid, name=lname, subject=SUBJECT,
                    domain=domain_of(lname, chapter),
                    grade=g, semester=sem, chapter=lchapter, level="lesson",
                    type=type_of(lname), book=book, seg=seg, unit_no=uno, lesson_no=lno,
                ))
                edges.append({"from": prev, "to": lid, "type": "hard"})
                prev = lid
    return topics, edges


def main():
    topics, edges = build()
    from collections import Counter
    print("点", len(topics), "| 单元点", sum(1 for t in topics if t["level"] == "unit"),
          "| 课时点", sum(1 for t in topics if t["level"] == "lesson"))
    print("边", len(edges))
    print("册分布:", dict(Counter(t["book"] for t in topics)))
    print("领域:", dict(Counter(t["domain"] for t in topics)))
    print("类型:", dict(Counter(t["type"] for t in topics)))
    missing = [t for t in topics if t["level"] == "lesson" and not t["name"]]
    print("空名点:", len(missing))
    no_lesson_units = [t for t in topics if t["level"] == "unit"
                       and not any(e["from"] == t["id"] for e in edges)]
    print("无课时点的单元:", [(t["book"], t["name"]) for t in no_lesson_units])
    if "--write" in sys.argv:
        dst = os.path.join(HERE, "_skeleton.json")
        json.dump(dict(subject=SUBJECT, topics=topics, edges=edges),
                  open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("写入", dst)


if __name__ == "__main__":
    main()
