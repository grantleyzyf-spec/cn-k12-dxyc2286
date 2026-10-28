# -*- coding: utf-8 -*-
"""义教数学 14 册（小学 9 册 + 初中 5 册）「小节/课时级」核对：教材小节 ↔ 图谱知识点。

与高中版（section_audit2.py）同口径，差别在「小节从哪来」：
  · 初中（人教 2024 新版）：教材目录有 `x.y 节名`，直接解析目录页文本（/tmp/mtoc/toc/*.txt）
  · 小学（人教 2024/2025 新版）：目录只有单元名，课时标题在正文里 ⇒ 按字号特征抽取
    （单元名 ≥24pt、课时号行 `1. xxx` ≥18pt），再按单元页码范围归组

产出：/tmp/mtoc/yijiao_sections.md
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

import fitz

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/小学/人教版"
CH = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/初中/人教版"
TOC = "/tmp/mtoc/toc"
OUT = "/tmp/mtoc/yijiao_sections.md"

# 册 → (目录 key, 图谱写 grade/semester)
BOOKS = [
    ("一年级上册", "g1a", 1, "上", XI), ("一年级下册", "g1b", 1, "下", XI),
    ("二年级上册", "g2a", 2, "上", XI), ("二年级下册", "g2b", 2, "下", XI),
    ("三年级上册", "g3a", 3, "上", XI), ("三年级下册", "g3b", 3, "下", XI),
    ("四年级上册", "g4a", 4, "上", XI), ("五年级上册", "g5a", 5, "上", XI),
    ("六年级上册", "g6a", 6, "上", XI),
    ("七年级上册", "g7a", 7, "上", CH), ("七年级下册", "g7b", 7, "下", CH),
    ("八年级上册", "g8a", 8, "上", CH), ("八年级下册", "g8b", 8, "下", CH),
    ("九年级上册", "g9a", 9, "上", CH),
]
STOP = ["的", "与", "和", "及", "其", "之", "中", "初步", "简单", "一般", "基本", "常见", "一些",
        "概念", "定义", "性质", "运算", "计算", "方法", "应用", "问题", "及其"]
GENERIC = ["练习", "整理和复习", "复习与关联", "数学游戏", "数学活动", "小结", "单元复习", "回顾整理"]


def core(s):
    s = re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-]", "", s or "")
    for w in STOP:
        s = s.replace(w, "")
    return s


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}


def score(a, b):
    ca, cb = core(a), core(b)
    if not ca or not cb:
        return 0.0
    if ca in cb or cb in ca:
        return 1.0
    ba, bb = bigrams(ca), bigrams(cb)
    return max(len(ba & bb) / max(1, len(ba)), len(ba & bb) / max(1, len(bb)))


def fw(s):
    """全角数字/句点 → 半角。"""
    return s.translate(str.maketrans("０１２３４５６７８９．", "0123456789."))


def parse_toc_units(key):
    """目录页 → [(单元名/章名, 教材起始页)]（小学用单元名，初中用章名）。"""
    p = f"{TOC}/{key}.txt"
    if not os.path.exists(p):
        return []
    txt = fw(open(p, encoding="utf-8").read())
    head = txt.split("=====PAGE=====")[0]
    lines = [l.strip() for l in head.split("\n") if l.strip()]
    units, buf = [], []
    for l in lines[1:]:
        if re.fullmatch(r"\d{1,3}", l):
            continue
        if re.match(r"^(第[一二三四五六七八九十]+章|\d{1,2}\s*[.．]\s*\d|\d{1,2}\s*[.．]\s*\d{1,2})", l):
            continue
        buf.append(l)
    return buf


def jie_from_toc(key):
    """初中：目录里的 x.y 小节。"""
    p = f"{TOC}/{key}.txt"
    txt = fw(open(p, encoding="utf-8").read())
    secs, ch = [], None
    for line in txt.split("\n"):
        line = line.strip()
        m = re.match(r"^第([一二三四五六七八九十]+)章[　 ]*(.+)$", line)
        if m:
            ch = f"第{m.group(1)}章 {m.group(2).strip()}"
            continue
        m = re.match(r"^(\d{1,2}\.\d{1,2})\s*[　 ]*(.+)$", line)
        if m:
            name = re.sub(r"[.．·…\s]+$", "", m.group(2)).strip()
            if name and len(core(name)) >= 2:
                secs.append({"no": m.group(1), "name": name, "unit": ch})
    return secs


SKIP_RE = re.compile(r"^(练习[一二三四五六七八九十\d]*|整理和复习|小讲堂|数学游戏|复习与关联|目录|致同学|"
                     r"数学活动|阅读与思考|成长小档案|自我评价|本单元学习评价|活动[一二三四五]|"
                     r"仅供个人学习|公众号|电子课本)")
# 水印/广告/页脚噪声（这些行也是 18pt，且会重复出现在每一页）
NOISE_RE = re.compile(r"仅供个人|未经授权|不得另做他用|电子课本|公众号|拼多多|淘宝|微信|"
                      r"^\d+$|^[\d\s\.\-—]+$")


def keshi_from_pdf(path, unit_names):
    """小学新版：单元标题≈21–30pt；课时标题＝页面靠前、字号 14.5–20pt 的短标题行
    （一二年级 18pt、五六年级 15.2pt，正文只有 10.5–12pt，故这个窗口不会抓正文）。"""
    d = fitz.open(path)
    rows, cur, seen = [], None, set()
    for pno in range(d.page_count):
        raw = []
        for b in d[pno].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                if t:
                    raw.append((round(max(s["size"] for s in l["spans"]), 1), t))
        if any(t.replace(" ", "") in ("目录", "目次") for _sz, t in raw):
            continue
        for sz, t in raw:
            if sz >= 21:
                hit = [u for u in unit_names if core(t) and core(t) == core(u)]
                if hit:
                    cur = hit[0]
        if not cur:
            continue
        # 只认页面最上方前 2 行、无数字、≤12 字的短标题（续页的图注/对话气泡都在正文层）
        for idx, (sz, t) in enumerate(raw[:2]):
            if not (14.5 <= sz <= 20):
                continue
            c = core(t)
            if not (2 <= len(c) <= 12):
                continue
            if re.search(r"[0-9０-９%％]", t) or "例" in t:
                continue
            if NOISE_RE.search(t) or SKIP_RE.match(t) or any(g in t for g in GENERIC):
                continue
            if re.fullmatch(r"[\d\W]+", t):
                continue
            key = (cur, c)
            if key in seen:
                break
            seen.add(key)
            rows.append({"unit": cur, "name": re.sub(r"\s+", "", t), "page": pno + 1})
            break
    d.close()
    return rows, 24.0, 0.0


def main():
    topics = json.load(open(f"{REPO}/data/math/topics.json", encoding="utf-8"))
    L = ["# 义教数学 14 册 · 小节/课时级核对（教材小节 ↔ 图谱知识点）", "",
         "- 初中（人教 2024 新版）：小节＝目录里的 `x.y 节名`",
         "- 小学（人教 2024/2025 新版）：目录只有单元，课时标题按字号抽取（`1. xxx` ≥18pt），按单元归组",
         "- 覆盖判定：去虚词 + 2-gram 覆盖率 ≥0.6（与高中版同口径）；`练习/整理和复习/数学游戏` 等通用课时不计", ""]
    rows_sum, todo = [], []
    for name, key, g, sem, base in BOOKS:
        ts = [t for t in topics if (t["grade"], t["semester"]) == (g, sem)]
        if not ts:
            L.append(f"## {name}（图谱无此册数据，跳过）\n")
            continue
        if base == CH:
            secs = jie_from_toc(key)
            gran = "小节"
        else:
            pdfs = [p for p in glob.glob(f"{base}/*.pdf") if name[:3] in p and name[-2:] in p]
            if not pdfs:
                pdfs = [p for p in glob.glob(f"{base}/*.pdf") if name[:3] in p]
            units = sorted({t["chapter"].split(" ", 1)[1].split(" ", 1)[-1] for t in ts})
            if pdfs:
                secs, unit_sz, ke_sz = keshi_from_pdf(pdfs[0], units)
            else:
                secs, unit_sz, ke_sz = [], 24.0, 18.0
            gran = "课时"
        for i, s2 in enumerate(secs, 1):
            s2.setdefault("no", s2.get("no") or f"#{i}")
        ok, miss = 0, []
        L.append(f"## {name}（图谱 {len(ts)} 点 · {gran} {len(secs)} 个）")

        L.append("")
        L.append(f"| {gran} | 名称 | 图谱对应知识点 |")
        L.append("| --- | --- | --- |")
        for s in secs:
            sc = sorted(((score(s["name"], t["name"]), t["name"]) for t in ts), reverse=True)
            hits = [(n, v) for v, n in sc[:3] if v >= 0.6]
            if hits:
                ok += 1
            else:
                miss.append(s)
            L.append(f"| {'✅' if hits else '❌'} {s['no']} | {s['name']} | "
                     + ("、".join(n for n, _ in hits) or "—") + " |")
        L.append("")
        L.append(f"- {gran} {len(secs)} 个：覆盖 **{ok}** · 未覆盖 **{len(miss)}**"
                 + (("：" + "；".join(f"{m['no']} {m['name']}" for m in miss)) if miss else ""))
        L.append("")
        orphan = []
        for t in ts:
            best = max(((score(t["name"], x["name"]), x["name"]) for x in secs), default=(0, ""))
            if best[0] < 0.6:
                orphan.append((t["name"], best[1]))
        L.append(f"- 图谱点 {len(ts)} 个：**教材里找不到出处（点→课时反向覆盖失败）{len(orphan)}**"
                 + (("：" + "、".join(f"{n}(最近 {m or '—'})" for n, m in orphan)) if orphan else ""))
        L.append("")
        rows_sum.append((name, len(ts), len(secs), ok, len(miss), gran))
        for m in miss:
            todo.append((name, m.get("unit", ""), m["no"], m["name"]))
    L += ["## 汇总", "", "| 册 | 图谱点 | 小节/课时 | 覆盖 | 未覆盖 | 粒度 |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for r in rows_sum:
        L.append("| {} | {} | {} | {} | {} | {} |".format(*r))
    ta = sum(r[2] for r in rows_sum)
    tb = sum(r[3] for r in rows_sum)
    L.append(f"| **合计** | {sum(r[1] for r in rows_sum)} | {ta} | {tb} | {ta - tb} | — |")
    L += ["", "## 未覆盖清单（候选真缺）", ""]
    for t in todo:
        L.append(f"- {t[0]} · {t[1]} · **{t[2]} {t[3]}**")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## 汇总"):]))


if __name__ == "__main__":
    main()
