# -*- coding: utf-8 -*-
"""历史教材目录抽取 v3：从统编版历史 PDF 抽「单元 → 课」结构（不看页码，只认结构标记）。

用法：
  python3 scripts/extract_history_toc.py            # 全部册
  python3 scripts/extract_history_toc.py --book 七年级上册

产物：data/history/_toc/<册>.json
  {"book":…, "unitCount":N, "lessonCount":M,
   "units":[{"no":1,"name":"…","lessons":[{"no":1,"name":"…"}]}]}

四个版式差异都要吃（实测）：
  ① 义教：`第一单元` / 单元名 / `第1课` / 课名 / `4`
  ② 高中：`第一单元 第二单元 …` 先并列声明，再出现 `录`，之后「单元名 + 页码」与课混排；且部分册 `第9课` / 页码 / 课名（页码在课名之前）
  ③ 八上：课名后跟 `………………… 5`（同一行）
  ④ 目录后紧接正文（正文重复出现「第一单元」）⇒ 遇到成句正文即止，且单元号必须严格递增
中文路径先复制到 /tmp 再跑 poppler（否则 poppler 报 I/O Error）。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "history", "_toc")
LIB = "/Users/a627692/Desktop/中小学教材/中小学教材/历史"

BOOKS = {
    "七年级上册": "初中/义务教育教科书 中国历史 七年级 上册_1756191809294.pdf",
    "七年级下册": "初中/义务教育教科书 中国历史 七年级 下册_1756191809294.pdf",
    "八年级上册": "初中/义务教育教科书 中国历史 八年级 上册_1756191811159.pdf",
    "八年级下册": "初中/义务教育教科书 中国历史 八年级 下册_1756191811159.pdf",
    "九年级上册": "初中/1111111111111_义务教育教科书•历史_九年级_上册_人民教育出版社三科办_1787020760267.pdf",
    "九年级下册": None,
    "中外历史纲要（上）": "高中历史/9787107336690_普通高中教科书·历史_高一年级_必修中外历史纲要（上）_人民教育出版社三科办_1787020857801.pdf",
    "中外历史纲要（下）": "高中历史/9787107336690_普通高中教科书·历史_高一年级_必修中外历史纲要（下）_人民教育出版社三科办_1787020857801.pdf",
    "选择性必修1": "高中历史/9787107347214_普通高中教科书·历史_高二年级_选择性必修1国家制度与社会治理_人民教育出版社三科办_1787020857965.pdf",
    "选择性必修2": "高中历史/9787107348808_普通高中教科书·历史_高二年级_选择性必修2经济与社会生活_人民教育出版社三科办_1787020855861.pdf",
    "选择性必修3": "高中历史/9787107348792_普通高中教科书·历史_高三年级_选择性必修3文化交流与传播_人民教育出版社三科办_1787020857004.pdf",
}

CN = "一二三四五六七八九十"
HAN = re.compile(r"[\u4e00-\u9fa5]")
STOP = re.compile(r"^(附录|后记|学史方法|大事年表|（一）|（二）|图片索引|第\s*\d+\s*$)")
JUNK = re.compile(r"^(目\s*录?|录|仅供个人学习使用.*|义务教育教科书|普通高中教科书)$")
UNIT_RE = re.compile(r"^第\s*([一二三四五六七八九十\d]+)\s*单元\s*(.*)$")
LESSON_RE = re.compile(r"^第\s*(\d+)\s*课\s*(.*)$")
TAIL = re.compile(r"[\s·…\.．]+(\d{1,3})?\s*$")   # 尾部的点线/省略号/页码
PAGE = "\x00"                                     # 目录页码行占位（parse 用它判「课名续行」）


def cn2int(s):
    s = s.strip()
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1 if a else 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def pdf_text(pdf, pages=14):
    tmp = "/tmp/_his_toc.pdf"
    shutil.copyfile(pdf, tmp)
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", "1", "-l", str(pages), tmp, "-"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("pdftotext 失败：" + pdf + "\n" + r.stderr[:200])
    return r.stdout


def clean_name(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = TAIL.sub("", s).strip(" ·…")
    return s


def toc_lines(txt):
    """目录区＝从含「目录/目…录」那一页起，连续若干【含「第N课」】的页；正文页没有课标记，天然截断。

    页码行不丢弃，改写成 PAGE 标记（`\\x00`）——它是区分「课名续行」与「下一个单元名」的唯一信号。
    """
    pages = txt.split("\x0c")
    lesson_any = re.compile(r"^第\s*\d+\s*课", re.M)
    unit_any = re.compile(r"^第\s*[一二三四五六七八九十\d]+\s*单元", re.M)
    start = next((i for i, p in enumerate(pages)
                  if "目录" in p or re.search(r"^\s*目\s*$", p, re.M)), None)
    if start is None:
        return []
    out = []
    for p in pages[start:]:
        if not lesson_any.search(p) and out:
            break
        if not lesson_any.search(p) and not out and not unit_any.search(p):
            continue
        for ln in p.split("\n"):
            ln = re.sub(r"\s+", " ", ln).strip()
            if not ln:
                continue
            if JUNK.match(ln) or STOP.match(ln):
                continue
            if re.fullmatch(r"\d{1,3}", ln):
                out.append(PAGE)
                continue
            out.append(ln)
    return out


def parse(lines):
    """两遍式：先收「课」的有序表，再收「单元边界」（同一 start 的边界合并）。

    版式差异被消解在两条规则里：
      ① 单元标记若还没收过课（start 与上一单元相同）⇒ 视为高中那种「并列声明」，只入号队列；
      ② 单元名可能印在标记下一行、也可能单独成段（高中），跨行名字按同一 start 合并拼接。
    """
    lessons, units, queue = [], [], []
    prev_decl = False          # 上一行是「无名的单元标记」⇒ 本行也属并列声明
    page_open = True           # 上一行是页码 ⇒ 下一段名字一定是新单元名，不是课名续行
    for i, raw in enumerate(lines):
        if raw == PAGE:
            page_open = True
            continue
        mu, ml = UNIT_RE.match(raw), LESSON_RE.match(raw)
        if mu:
            no, nm = cn2int(mu.group(1)), clean_name(mu.group(2))
            if not nm and not prev_decl:
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if nxt and nxt != PAGE and not UNIT_RE.match(nxt) and not LESSON_RE.match(nxt):
                    nm = clean_name(nxt)          # 义教：单元名就在下一行
                    lines[i + 1] = PAGE           # 该行已消费
            if not nm:
                queue.append(no)                  # 高中：并列声明，名字稍后出现
                prev_decl = True
                continue
            prev_decl = False
            units.append({"no": no, "name": nm, "start": len(lessons)})
            page_open = False
            continue
        if ml:
            has_page = bool(re.search(r"\d{1,3}\s*$", raw))
            lessons.append({"no": int(ml.group(1)), "name": clean_name(ml.group(2))})
            prev_decl = False
            page_open = has_page
            continue
        nm = clean_name(raw)
        if not nm:
            continue
        prev_decl = False
        last = lessons[-1] if lessons else None
        ends_page = bool(re.search(r"\d{1,3}\s*$", raw))
        if last is not None and units and units[-1]["start"] < len(lessons):
            if not last["name"]:                   # 课名印在页码后面一行
                last["name"] = nm
                page_open = ends_page
                continue
            if not page_open:                      # 课名续行（中间没有页码）
                last["name"] += nm
                page_open = ends_page
                continue
        cont = bool(units) and units[-1]["start"] == len(lessons)   # 同一单元的名字续行
        units.append({"no": None if cont else (queue.pop(0) if queue else None),
                      "name": nm, "start": len(lessons)})
        page_open = False
    # 同一 start 的边界合并：前缀替换 / 包含跳过 / 否则拼接（单元名跨行）
    merged = []
    for u in units:
        if merged and merged[-1]["start"] == u["start"]:
            a, b = merged[-1], u
            if not a["name"]:
                a["name"] = b["name"]
            elif not b["name"] or b["name"] in a["name"]:
                pass
            elif a["name"] in b["name"]:
                a["name"] = b["name"]
            else:
                a["name"] = a["name"] + b["name"]
            a["no"] = a["no"] or b["no"]
            continue
        merged.append(u)
    # 单元号缺失的按顺序补，并丢弃无课单元
    clean, last_no = [], 0
    for k, u in enumerate(merged):
        u["no"] = u["no"] or (last_no + 1)
        u["lessons"] = lessons[u["start"]: (merged[k + 1]["start"] if k + 1 < len(merged) else len(lessons))]
        if not u["lessons"] or not u["name"] or u["no"] <= last_no:
            continue
        u.pop("start")
        clean.append(u)
        last_no = u["no"]
    return clean


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    todo = {args.book: BOOKS[args.book]} if args.book else BOOKS
    bad = []
    for book, rel in todo.items():
        if rel is None:
            print(f"⛔ {book}: 教材 PDF 缺（库级缺口，未建目录）")
            bad.append(book)
            continue
        pdf = os.path.join(LIB, rel)
        if not os.path.exists(pdf):
            print(f"⛔ {book}: 找不到 {pdf}")
            bad.append(book)
            continue
        units = parse(toc_lines(pdf_text(pdf)))
        n_lesson = sum(len(u["lessons"]) for u in units)
        ok = bool(units) and n_lesson > 0
        with open(os.path.join(OUT, f"{book}.json"), "w", encoding="utf-8") as f:
            json.dump({"book": book, "unitCount": len(units), "lessonCount": n_lesson,
                       "units": units}, f, ensure_ascii=False, indent=2)
        print(f"{'✅' if ok else '❌'} {book}: 单元 {len(units)} / 课 {n_lesson}")
        if not ok:
            bad.append(book)
            continue
        if not args.quiet:
            for u in units:
                nos = [l["no"] for l in u["lessons"]]
                gaps = [f"{a}→{b}" for a, b in zip(nos, nos[1:]) if b != a + 1]
                flag = f"  ⚠课号跳号{gaps}" if gaps else ""
                print(f"    U{u['no']} {u['name']}（{len(nos)} 课 {nos[0]}–{nos[-1]}）{flag}")
    print(f"\n合计：{len(todo) - len(bad)} 册成功 / {len(todo)}；缺口：{bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
