# -*- coding: utf-8 -*-
"""高中语文 5 册清单抽检：逐篇核对「篇名是否真在教材里」「清单页码与 PDF 实际页的偏移是否一致」。

做法（不依赖人工读页）：
  1. 对每篇：在 PDF 全文里搜篇名（去空白、去标点后子串匹配），记录命中的 PDF 页；
  2. 取「命中页 − 清单页码」的众数当作该册偏移，与其它篇的偏移比较：**偏移不一致 ⇒ 页码错**；
  3. 篇名搜不到的记为「篇名未在正文出现」（可能是目录写法差异，如《诗经·周南》的《》）。

产出：/tmp/cn/hs_check.md
"""
import glob
import json
import os
import re
from collections import Counter

import fitz

ROOT = "/Users/a627692/Desktop/中小学教材/中小学教材/语文/高中"
REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = "/tmp/cn/hs_check.md"
PDFS = {"必修上册": "*必修上册*.pdf", "必修下册": "*必修下册*.pdf",
        "选择性必修上册": "*选择性必修上册*.pdf", "选择性必修中册": "*选择性必修中册*.pdf",
        "选择性必修下册": "*选择性必修下册*.pdf"}


def norm(s):
    return re.sub(r"[\s　·・、，,。．.（）()《》“”\"'’—－\-：:；;！!？?]", "", s or "")


def main():
    L = ["# 高中语文 5 册 清单抽检", ""]
    for book, pat in PDFS.items():
        pdf = glob.glob(f"{ROOT}/{pat}")[0]
        rec = json.load(open(f"{REPO}/data/chinese/ke_toc/{book}.json", encoding="utf-8"))
        d = fitz.open(pdf)
        pages = [norm(d[i].get_text()) for i in range(d.page_count)]
        d.close()
        rows, offs = [], []
        for u in rec["units"]:
            for it in u["items"]:
                if it["kind"] != "篇":
                    continue
                nm0 = re.sub(r"（[^）]*）|\([^)]*\)", "", it["name"])      # 去掉「（节选）（其一）」这类后缀
                key = norm(nm0)[:5]                                          # 长标题只取前 5 字，避免副标题/标点差异
                if len(key) < 2:
                    continue
                hits = [i + 1 for i, t in enumerate(pages) if i >= 8 and key and key in t]   # 跳过封面/目录页
                off = (hits[0] - it["page"]) if hits else None
                if off is not None:
                    offs.append(off)
                rows.append((u["unit"], it["name"], it["page"], hits[:2], off))
        mode = Counter(offs).most_common(1)[0][0] if offs else 0
        bad = [r for r in rows if r[4] is None or r[4] != mode]
        L += [f"## {book}",
              f"- 篇 {len(rows)} · 篇名在正文命中 {sum(1 for r in rows if r[4] is not None)} · "
              f"页码偏移众数 **{mode:+d}** · 偏移不一致/未命中 **{len(bad)}**", ""]
        if bad:
            L.append("| 单元 | 篇名 | 清单页 | 实际 PDF 页 | 偏移 |")
            L.append("| --- | --- | ---: | --- | --- |")
            for u, nm, pg, hits, off in bad[:30]:
                L.append(f"| {u} | {nm} | {pg} | {hits or '未命中'} | {off if off is not None else '—'} |")
            L.append("")
        print(f"{book}: 篇 {len(rows)} · 命中 {sum(1 for r in rows if r[4] is not None)} · 偏移 {mode:+d} · 异常 {len(bad)}")
    os.makedirs("/tmp/cn", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("报告 →", OUT)


if __name__ == "__main__":
    main()
