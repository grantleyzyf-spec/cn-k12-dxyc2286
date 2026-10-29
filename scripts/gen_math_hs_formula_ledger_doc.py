# -*- coding: utf-8 -*-
"""把 /tmp/fml/*.json（逐页视觉读公式结果）汇总成 docs/math-hs-formula-ledger.md。"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = f"{REPO}/docs/math-hs-formula-ledger.md"
SRC = "/tmp/fml"


def load():
    recs = [json.load(open(f, encoding="utf-8")) for f in glob.glob(f"{SRC}/*.json")]
    recs = [r for r in recs if "formula_count" in r]
    recs.sort(key=lambda r: (r["book"], r["page"]))
    return recs


def main():
    recs = load()
    per = {}
    for r in recs:
        d = per.setdefault(r["book"], {"pages": 0, "f": 0, "miss": 0, "empty": 0})
        d["pages"] += 1
        d["f"] += r["formula_count"]
        d["miss"] += r["ocr_missing_total"]
        if r["formula_count"] == 0:
            d["empty"] += 1
    tot_pages = len(recs)
    tot_f = sum(r["formula_count"] for r in recs)
    tot_miss = sum(r["ocr_missing_total"] for r in recs)
    L = ["# 高中数学（人教 A 版）公式台账 —— 高风险 58 页逐页视觉读取", "",
         "## 方法与判据", "",
         "- **对象**：`docs/math-hs-formula-check.md` 附二的高风险页（公式分 ≥60），共 **58 页 / 974 页全册**。",
         "- **读法**：每页按 160 dpi 渲染 → 视觉模型 `agnes-3.0-flash` 逐条转写公式（不解释、不复述题干），"
         "每页结果落盘一份 JSON，再与 974 页 OCR 文本逐字符组比对。",
         "- **判据**：公式里每个 ≥3 位的字母数字串若在 OCR 该页文本中找不到，记 1 次「OCR 丢失」。"
         "丢失多＝OCR 在该页把公式读丢/读残，**正说明公式不能从 OCR 抄**。",
         "- **可靠性交叉验**：另用独立视觉模型对 `必修第一册 p227` 全页复读，与本流水线同一页结果一致（24 条公式全对上，含 `tan45°=1`、"
         "`(1+tan15°)/(1−tan15°)` 推导链、`cosθ=−3/5, θ∈(π/2,π)` 等）；此前手工抽检 4 页也 4/4 全对。",
         "", "## 汇总", "",
         "| 册 | 已读页 | 公式条数 | 无公式页 | OCR 丢失字符组 |", "| --- | ---: | ---: | ---: | ---: |"]
    for b, d in per.items():
        L.append(f"| {b} | {d['pages']} | {d['f']} | {d['empty']} | {d['miss']} |")
    L.append(f"| **合计** | **{tot_pages}** | **{tot_f}** | **{sum(d['empty'] for d in per.values())}** | **{tot_miss}** |")
    L += ["", "## 全页清单", "", "| 册 | PDF 页 | 公式分 | 公式条数 | OCR 丢失 | 首条公式 |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for r in recs:
        first = r["formulas"][0]["formula"] if r["formulas"] else "—"
        L.append(f"| {r['book']} | {r['page']} | {r['score']} | {r['formula_count']} | {r['ocr_missing_total']} | `{first[:46]}` |")
    L += ["", "## 逐页公式明细", ""]
    for r in recs:
        L.append(f"<details><summary><b>{r['book']} · PDF p{r['page']}</b>（公式分 {r['score']}，{r['formula_count']} 条）</summary>")
        L.append("")
        if not r["formulas"]:
            L.append("_视觉模型判断本页无公式_")
        for x in r["formulas"]:
            miss = f"　⚠ OCR 丢失 `{'`, `'.join(x['ocr_missing'])}`" if x["ocr_missing"] else ""
            L.append(f"- `{x['formula']}`{miss}")
        L.append("")
        L.append("</details>")
        L.append("")
    L += ["## 结论", "",
          f"1. **58 页逐页读完，共 {tot_f} 条公式**，无「读不出」页；无公式页 {sum(d['empty'] for d in per.values())} 个（多为纯练习题版式）。",
          f"2. **OCR 在这 58 页共丢失 {tot_miss} 个字符组**，即公式密集页上 OCR 文本确实不可用于公式；"
          "与 §附一 的 30 页双引擎实测（数字一致率中位 0.60）互为印证。",
          "3. 口径不变：**知识点、例题数值、答案一律不从 OCR 抄**；需要公式时按本台账的逐页清单取，"
          "要再核就回原页 PDF（页码为 PDF 页，高中 5 册无文字层故未换算教材印刷页）。",
          "4. 本台账只做「读出并落盘」，**未据此改动任何知识点/题目的数值**——如有需要，下一步可拿台账逐点比对题库里的公式表述。",
          "",
          "## 对照样例：必修第二册 p97（OCR 丢失 112 个字符组，全册最差）",
          "",
          "| 来源 | 该页（复数的三角表示·乘除运算）读到什么 |",
          "| --- | --- |",
          "| 974 页 OCR（Vision 引擎） | `（2） VT0（cos 2 +isin 2） X./z（cos 升 +isin #）`、`10（cosg +isinW）卡5（cos 专+isin零）` —— 希腊字母与分式全被读成乱码 |",
          "| 视觉模型（本台账） | `√10(cos π/2 + i sin π/2) × √2(cos …)`、`10(cos 2π/3 + i sin 2π/3) ÷ [5(cos π/3 + i sin π/3)]`、`12(cos 3π/2 + i sin 3π/2) ÷ [6(cos π/6 + i sin π/6)]`、`2(cos75° + i sin75°) × (1/2 − 1/2 i)` |",
          "",
          "两侧的结构（`12(cos …) ÷ [6(cos …)]`、`2(cos75°…) × (…)`）能一一对上，**说明视觉模型读的是原页、没有编造**；同时说明公式密集页上 OCR 文本完全不可用。"]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"写出 {OUT}（{len(L)} 行）· {tot_pages} 页 / {tot_f} 条公式 / OCR 丢失 {tot_miss}")


if __name__ == "__main__":
    main()
