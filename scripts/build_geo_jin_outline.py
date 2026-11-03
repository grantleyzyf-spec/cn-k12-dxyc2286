#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""晋教版初中地理：从两个结构源抽「主题（单元）→ 课时」清单。

三级结构源（SKILL §7）在本桶的实际形态：
  ① 分课时教学设计 docx —— 只有七年级上册、八年级上册（各 4 主题 × 8 课时）；
     文件名自带「主题X <主题名>·第N课时 <课时名>」，最可靠。
  ② 大单元整体教学设计 docx —— 四册齐全（16 份），取「十五、『教-学-评』一致性课时设计」
     段里的「（一）第一课时：<课时名>」列表，用于七年级下册、八年级下册。
  ③ 教材 PDF 目录 —— 只作核对（见 docs/geography-jin.md 的核对记录）。

产物：data/geography-jin/_outline.json
  {"books": {"<册>": {"unit_no": 1, "unit_name": "主题一 探寻人类的太空家园",
                       "lessons": [{"no": 1, "name": "地球在太阳系中的位置"}, ...]}, ...}}

⛔ 不做并集：同一册只用一个源（①优先，缺则②），避免两源编号打架。
"""
import glob
import json
import os
import re
import sys

SDF = os.path.expanduser("~/Desktop/中小学教材/中小学教材/各学科分课时设计/地理/晋教版/初中")
DU = os.path.expanduser("~/Desktop/中小学教材/中小学教材/地理/初中/晋教版")
OUT = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/geography-jin/_outline.json")

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
      "十一": 11, "十二": 12}
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]

# 课时名里要剥掉的尾巴（不是知识内容，是教材的收尾活动）
TAIL = re.compile(r"[·•]?\s*(?:与|和|、|及)?\s*单元收官\s*$")
TRAIL = re.compile(r"[与和、·—\-]+$")  # 剥完「单元收官」后残留的连接词（实测 8 例）


def cn2int(s: str) -> int:
    s = s.strip()
    if s.isdigit():
        return int(s)
    return CN.get(s, 0)


def unit_label(raw: str) -> str:
    """「主题三 探索地球海陆面貌」→ 规范化（保留中文数字，与语文/数学口径一致）"""
    raw = raw.strip()
    m = re.match(r"主题([一二三四五六七八九十\d]+)\s*(.+)$", raw)
    if not m:
        return raw
    return f"主题{m.group(1)} {m.group(2).strip()}"


def from_shard_docx(book: str):
    """结构源①：分课时 docx 文件名。返回 {unit_label: {lesson_no: lesson_name}}"""
    pat = re.compile(
        r"晋教版初中地理" + re.escape(book) +
        r"(主题[一二三四五六七八九十\d]+\s*[^·]*?)"      # 主题X 主题名
        r"(?:·[^·]*?)?"                                    # 可选的节名（八上「·1 描绘中国版图」）
        r"·第(\d+)课时\s*(.+?)分课时教学设计"
    )
    got = {}
    for f in glob.glob(os.path.join(SDF, book, "*.docx")):
        base = os.path.basename(f)
        if base.startswith(".~"):
            continue
        m = pat.search(base)
        if not m:
            continue
        unit = unit_label(m.group(1))
        no = int(m.group(2))
        name = TRAIL.sub("", TAIL.sub("", m.group(3).strip()))
        got.setdefault(unit, {})[no] = name
    return got


def from_danyuan_docx(book: str):
    """结构源②：大单元 docx 的「十五、『教-学-评』一致性课时设计」段。"""
    import docx  # 延迟导入：只有走这条路时才需要

    got = {}
    for f in glob.glob(os.path.join(DU, f"*{book}*大单元*.docx")):
        base = os.path.basename(f)
        if base.startswith(".~"):
            continue
        m = re.search(r"主题([一二三四五六七八九十\d]+)\s*([^\s]+)", base.replace(book, ""))
        if not m:
            continue
        unit = unit_label(f"主题{m.group(1)} {m.group(2)}")
        d = docx.Document(f)
        paras = [p.text.strip() for p in d.paragraphs if p.text.strip()]
        # 取该标题**最后一次**出现（目录里通常也会出现一次）
        idx = [i for i, p in enumerate(paras) if "教-学-评" in p and "课时设计" in p]
        if not idx:
            continue
        seg = paras[idx[-1] + 1:]
        for p in seg:
            mm = re.match(r"[（(]([一二三四五六七八九十\d]+)[）)]\s*第([一二三四五六七八九十\d]+)课时[：:]\s*(.+)$", p)
            if not mm:
                if got.get(unit) and p.startswith("十") and "、" in p:  # 下一节开始
                    break
                continue
            no = cn2int(mm.group(2))
            name = TRAIL.sub("", TAIL.sub("", mm.group(3).strip()))
            got.setdefault(unit, {})[no] = name
    return got


def main() -> int:
    books = {}
    report = []
    for book in BOOKS:
        src = "①分课时docx"
        got = from_shard_docx(book)
        if sum(len(v) for v in got.values()) < 20:
            got2 = from_danyuan_docx(book)
            if sum(len(v) for v in got2.values()) > sum(len(v) for v in got.values()):
                got, src = got2, "②大单元docx 十五段"
        if not got:
            print(f"❌ {book}: 两源都没抽到课时")
            return 1
        units = []
        for unit in sorted(got, key=lambda u: cn2int(re.match(r"主题([一二三四五六七八九十\d]+)", u).group(1))):
            nos = sorted(got[unit])
            gaps = [n for n in range(1, max(nos) + 1) if n not in got[unit]]
            units.append(dict(unit=unit, lessons=[dict(no=n, name=got[unit][n]) for n in nos], gaps=gaps))
            report.append(f"  {book} / {unit}: {len(nos)} 课时" + (f"（缺号 {gaps}）" if gaps else ""))
        books[book] = units

    total_u = sum(len(v) for v in books.values())
    total_l = sum(len(u["lessons"]) for v in books.values() for u in v)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(books=books, unitCount=total_u, lessonCount=total_l), fh, ensure_ascii=False, indent=1)
    print("\n".join(report))
    print(f"\n合计 主题 {total_u} 个 · 课时 {total_l} 个 → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
