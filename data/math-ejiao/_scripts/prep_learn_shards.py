#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版数学 · 学层精讲分片准备：每个课时点一份 shard（含教材 OCR 片段＋课标引文）"""
import json, os, re

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
D = os.path.join(REPO, "data/math-ejiao")
SRC = os.path.join(D, "_src")
OUT = os.path.join(D, "_learn_shards")
os.makedirs(OUT, exist_ok=True)

skel = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
topics = {t["id"]: t for t in json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))}

# 册 → (tag, OCR 全文)
BOOK2TAG = {"鄂教版必修第一册": "h1", "鄂教版必修第二册": "h2", "鄂教版必修第三册": "h3",
            "鄂教版必修第四册": "h4", "鄂教版选择性必修第一册": "h5",
            "鄂教版选择性必修第二册": "h6", "鄂教版选择性必修第三册": "h7"}


def find_pdf_page(tag, title, hint):
    """印刷页→PDF 页：默认 印刷+4；若该窗口不含课时名关键词，再从正文页（p8 起）搜。"""
    off = (hint or 1) + 4
    key = re.sub(r"[（(].*?[）)]|第\d+课时", "", title or "")
    key = re.sub(r"[^\u4e00-\u9fa5]", "", key)
    probes = [k for k in (key[:4], key[:3], key[:2]) if len(k) >= 2]
    win = ""
    for q in (off - 1, off, off + 1):
        f = os.path.join(SRC, f"p_{tag}_{q:03d}.txt")
        if os.path.exists(f):
            win += open(f, encoding="utf-8").read()
    if any(pr in win for pr in probes):
        return off
    # 窗口不含关键词：从正文页开始找（跳过前言/目录）
    for q in range(8, 400):
        f = os.path.join(SRC, f"p_{tag}_{q:03d}.txt")
        if not os.path.exists(f):
            continue
        t = open(f, encoding="utf-8").read()
        if any(pr in t for pr in probes):
            return q
    return off


def page_text(tag, page, span=1, title=""):
    """取该课时所在 PDF 页前后 span 页的 OCR 文本，限 3000 字。"""
    page = find_pdf_page(tag, title, page) if title else (page or 1) + 4
    parts = []
    for p in range(max(1, page - 1), page + span + 1):
        f = os.path.join(SRC, f"p_{tag}_{p:03d}.txt")
        if os.path.exists(f):
            parts.append(open(f, encoding="utf-8").read())
    txt = re.sub(r"[ \t]+", " ", "\n".join(parts))
    txt = re.sub(r"\n{2,}", "\n", txt)
    return txt[:3000]


n = 0
for v in skel["volumes"]:
    tag = BOOK2TAG[v["book"]]
    for u in v["units"]:
        for l in u["lessons"]:
            n += 1
            t = topics[l["id"]]
            shard = {
                "taskId": l["id"],
                "title": l["name"],
                "book": v["book"],
                "chapter": l["chapter"],
                "unit": u["unit_name"],
                "grade": v["grade"],
                "page": l["page"],
                "standards": t.get("standards") or [],
                "textbook_excerpt": page_text(tag, l["page"] or 1, title=l["name"]),
                "outPath": os.path.join(D, "_learn_out", f"{l['id']}.json"),
                "specPath": os.path.join(D, "WORKER_LEARN.md"),
            }
            json.dump(shard, open(os.path.join(OUT, f"{l['id']}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
print("shards", n)
print("样例", json.dumps(next(iter([json.load(open(os.path.join(OUT, f), encoding='utf-8'))
                                   for f in sorted(os.listdir(OUT))[:1]])), ensure_ascii=False)[:300])
