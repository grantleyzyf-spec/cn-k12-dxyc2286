# -*- coding: utf-8 -*-
"""小学《每节内容对应页码》自动生成（v4：按「课时字号」精确抓取，已用五上人工件校准）。

关键发现（校准自五上人工基准 30 条课时）：
  新版小学教材正文层级固定为 4 档字号 —— 单元号 40~42pt / 单元名 24pt / **课时名 16pt** / 正文 10.5~12pt，
  例题号 14pt。课时名并不在页首，而是夹在「想一想」之后；用「页首行」抓必然抓不到（这解释了之前命中率极低）。
  各册差异只在「正文与课时」的绝对字号（一上正文就 16pt、课时 18pt；五上正文 12pt、课时 16pt），
  所以按「严格大于正文字号、且该字号的行多为短中文标题」自适应选档即可。

流程：① 页脚数字定偏移 ② 自适应定单元/课时字号 ③ 抓 unit/课时 ④ 回写 TXT（与五上人工件同格式）

用法：python3 gen_keshi_toc.py [--book 一年级上册] [--write] [--verify 五年级上册]
"""
import argparse
import glob
import re
import sys
from collections import Counter

import fitz

XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/小学/人教版"
CN = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
BOOKS = ["一年级上册", "一年级下册", "二年级上册", "二年级下册",
         "三年级上册", "三年级下册", "四年级上册", "六年级上册"]
NOISE = re.compile(r"仅供个人|未经授权|不得另做他用|电子课本|公众号|微信|淘宝|义\s*务\s*教\s*育")
SKIP = re.compile(r"^(练习[一二三四五六七八九十\d]*|做一做|试一试|想一想|整理和复习|复习与关联|"
                  r"数学游戏|数学活动|阅读与思考|成长小档案|自我评价|本单元学习评价|总复习|"
                  r"活动[一二三四五]|目录|致同学|小讲堂|数学连环画)$")


def norm(s):
    return re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-]", "", s or "")


def find_pdf(book):
    c = [p for p in glob.glob(f"{XI}/*.pdf") if book[:3] in p and book[-2:] in p]
    return c[0] if c else (sorted(glob.glob(f"{XI}/*.pdf"))[0] if c == [] and False else None)


def load(book):
    pdf = find_pdf(book)
    d = fitz.open(pdf)
    pages = []
    for i in range(d.page_count):
        ls = []
        for b in d[i].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                if t and not NOISE.search(t):
                    ls.append((round(max(s["size"] for s in l["spans"]), 1), t))
        pages.append(ls)
    offs = []
    for i, ls in enumerate(pages):
        for _sz, t in reversed(ls[-3:]):
            if re.fullmatch(r"\d{1,3}", t):
                offs.append(int(t) - (i + 1))
                break
    offset = Counter(offs).most_common(1)[0][0] if offs else 0
    d.close()
    return pages, offset


def pick_sizes(pages):
    """返回 (单元字号, 课时字号)。"""
    hist, shortc = Counter(), Counter()
    for ls in pages:
        for sz, t in ls:
            hist[sz] += 1
            c = norm(t)
            if 2 <= len(c) <= 16 and re.search(r"[\u4e00-\u9fa5]", t) and not re.search(r"[0-9０-９=＝+＋]", t):
                shortc[sz] += 1
    body = hist.most_common(1)[0][0]
    unit = sorted([(shortc.get(sz, 0), sz) for sz in hist if 21 <= sz <= 30 and hist[sz] >= 3], reverse=True)
    unit_sz = unit[0][1] if unit else 24.0
    cands = [(shortc.get(sz, 0) / max(1, hist[sz]), sz, hist[sz]) for sz in hist
             if body < sz < unit_sz - 1 and hist[sz] >= 8]
    ke_sz = sorted(cands, reverse=True)[0][1] if cands else 16.0
    return unit_sz, ke_sz, body


def extract(book):
    pages, offset = load(book)
    unit_sz, ke_sz, body = pick_sizes(pages)
    rows, cur, seen = [], None, set()
    for i, ls in enumerate(pages):
        for sz, t in ls:
            if abs(sz - unit_sz) <= 1.2 and len(norm(t)) >= 3:
                cur = t
            elif (ke_sz - 1.6) <= sz <= (unit_sz - 2.1) and cur:
                nm = re.sub(r"^\d{1,2}\s*[.．、]\s*", "", re.sub(r"\s+", "", t))
                c = norm(nm)
                if not (2 <= len(c) <= 16) or SKIP.match(nm) or re.search(r"[0-9０-９=＝+＋%％]", nm) or "例" in nm:
                    continue
                if c in seen:
                    continue
                seen.add(c)
                rows.append({"unit": cur, "name": nm, "page": i + 1 + offset})
    return rows, offset, unit_sz, ke_sz, body


def verify(book):
    """用五上人工件当基准，算召回率。"""
    human = f"{XI}/{book}/教学设计/数学人教版{book}每节内容对应页码.txt"
    gold = [m.group(1).strip() for m in re.finditer(r"^　(.+?)\s+(\d+)$", open(human, encoding="utf-8").read(), re.M)]
    gold = [g for g in gold if not SKIP.match(g) and 2 <= len(norm(g)) <= 16]
    rows, offset, u, k, b = extract(book)
    got = {norm(r["name"]) for r in rows}
    hit = [g for g in gold if norm(g) in got]
    print(f"[校准] {book}: 人工 {len(gold)} 条 → 命中 {len(hit)}（{len(hit)/max(1,len(gold)):.0%}），"
          f"自动抽 {len(rows)} 条 | 字号 单元 {u} / 课时 {k} / 正文 {b} | 偏移 {offset:+d}")
    miss = [g for g in gold if norm(g) not in got]
    if miss:
        print("        漏:", "、".join(miss[:12]))
    extra = [r["name"] for r in rows if norm(r["name"]) not in {norm(g) for g in gold}]
    if extra:
        print("        多:", "、".join(extra[:12]))


def build_txt(book):
    rows, offset, u, k, b = extract(book)
    units = []
    for r in rows:
        if not units or units[-1] != r["unit"]:
            if r["unit"] not in units:
                units.append(r["unit"])
    lines = [f"数学（人教版）{book}　每节内容对应页码",
             f"（页码为教材印刷页码，按 PDF 页脚推算，偏移 {offset:+d}；字号标定：单元 {u}pt / 课时 {k}pt / 正文 {b}pt）",
             "", "【说明】按「课时字号」（{k}pt）自动抽取，已用五上人工件校准；`*` 为教材带星拓展课时。".format(k=k), ""]
    idx = 0
    for uname in units:
        idx += 1
        pts = [r for r in rows if r["unit"] == uname]
        lines.append(f"{CN[idx-1] if idx <= 10 else idx}　{uname}（第{pts[0]['page']}—{pts[-1]['page']}页）")
        for r in pts:
            lines.append(f"　{r['name']} {r['page']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n", len(rows), len(units)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", action="append", default=None)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", default=None)
    a = ap.parse_args()
    if a.verify:
        verify(a.verify)
        sys.exit(0)
    for book in a.book or BOOKS:
        txt, n, nu = build_txt(book)
        outdir = f"{XI}/{book}/教学设计"
        path = f"{outdir}/数学人教版{book}每节内容对应页码（自动稿·建议核对）.txt"
        print(f"{book}: {nu} 单元 / {n} 课时 → {path}")
        if a.write:
            import os
            os.makedirs(outdir, exist_ok=True)
            open(path, "w", encoding="utf-8").write(txt)
