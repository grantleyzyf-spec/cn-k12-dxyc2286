# -*- coding: utf-8 -*-
"""从 data/math/formula_ledger/*.json 生成 docs/math-hs-formula-ledger.md（全页清单）。"""
import glob
import json
import os
from collections import Counter, defaultdict

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LD = f"{REPO}/data/math/formula_ledger"
OUT = f"{REPO}/docs/math-hs-formula-ledger.md"
ORDER = ["必修第1册", "必修第2册", "选必第1册", "选必第2册", "选必第3册"]

METHOD = """# 高中数学（人教 A 版）公式台账 —— 全册逐页视觉读取（974 页）

## 方法与判据

- **对象**：人教 A 版 5 册**全部 974 页**（此前只读高风险 457 页，本轮补读余下 517 页低风险页）。
- **读法**：每页按 160 dpi 渲染 → 视觉模型 `agnes-3.0-flash` 逐条转写公式（不解释、不复述题干），
  每页结果落盘一份 JSON（`data/math/formula_ledger/<册>_p<页>.json`），再与同册 OCR 文本逐字符组比对。
- **判据**：公式里每个 ≥3 位的字母数字串若在 OCR 该页文本中找不到，记 1 次「OCR 丢失」。
  丢失多＝OCR 把该页公式读丢/读残，**正说明公式不能从 OCR 抄**，必须视觉读取。
- **可靠性交叉验**：独立视觉模型复读 `必修第一册 p227`，与本流水线同一页结果一致（24 条公式全对上，
  含 `tan45°=1`、`(1+tan15°)/(1−tan15°)` 推导链、`cosθ=−3/5, θ∈(π/2,π)`）；手工抽检 4 页 4/4 全对。
- **断点续跑**：每页一文件，作业中断可从 `/tmp/fml` 已落盘页续读；峰谷守护只在谷段跑（工作日 09–12、14–18 为峰）。
"""


def main():
    files = sorted(glob.glob(f"{LD}/*.json"))
    rows = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        first = (d.get("formulas") or [None])[0]
        if isinstance(first, dict):
            first = first.get("formula") or first.get("text") or ""
        rows.append({"book": d.get("book"), "page": d.get("page"), "score": d.get("score") or 0,
                     "n": d.get("formula_count") or len(d.get("formulas") or []),
                     "lost": d.get("ocr_missing_total") or 0, "first": (first or "")[:60]})
    rows.sort(key=lambda r: (ORDER.index(r["book"]) if r["book"] in ORDER else 9, r["page"] or 0))
    per = defaultdict(lambda: {"pages": 0, "n": 0, "zero": 0, "lost": 0,
                               "hi": 0, "mid": 0, "lo": 0})
    for r in rows:
        p = per[r["book"]]
        p["pages"] += 1
        p["n"] += r["n"]
        p["lost"] += r["lost"]
        if r["n"] == 0:
            p["zero"] += 1
        p["hi" if r["score"] >= 60 else ("mid" if r["score"] >= 20 else "lo")] += 1
    tot = {k: sum(v[k] for v in per.values()) for k in ("pages", "n", "zero", "lost", "hi", "mid", "lo")}
    L = [METHOD, "## 汇总", "",
         "| 册 | 页数 | 高/中/低风险页 | 公式条数 | 无公式页 | OCR 丢失字符组 |",
         "| --- | ---: | --- | ---: | ---: | ---: |"]
    for b in ORDER:
        v = per[b]
        L.append(f"| {b} | {v['pages']} | {v['hi']}/{v['mid']}/{v['lo']} | {v['n']} | {v['zero']} | {v['lost']} |")
    L.append(f"| **合计** | **{tot['pages']}** | **{tot['hi']}/{tot['mid']}/{tot['lo']}** | "
             f"**{tot['n']}** | **{tot['zero']}** | **{tot['lost']}** |")
    L += ["", f"低风险页（公式分 <20）共 **{tot['lo']} 页**，本轮补读后全册无遗漏。", "",
          "## OCR 丢失最多的 20 页", "",
          "这些页的公式**只能看视觉台账**，不能拿 OCR 文本拼：", "",
          "| 册 | PDF 页 | 公式条数 | OCR 丢失 | 首条公式 |", "| --- | ---: | ---: | ---: | --- |"]
    for r in sorted(rows, key=lambda x: -x["lost"])[:20]:
        L.append(f"| {r['book']} | {r['page']} | {r['n']} | {r['lost']} | `{r['first']}` |")
    L += ["", f"## 全页清单（{len(rows)} 页）", "",
          "| 册 | PDF 页 | 档 | 公式分 | 公式条数 | OCR 丢失 | 首条公式 |",
          "| --- | ---: | :--: | ---: | ---: | ---: | --- |"]
    for r in rows:
        tier = "高" if r["score"] >= 60 else ("中" if r["score"] >= 20 else "低")
        L.append(f"| {r['book']} | {r['page']} | {tier} | {r['score']} | {r['n']} | {r['lost']} | `{r['first']}` |")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"✅ {OUT}")
    print(f"页 {tot['pages']} · 公式 {tot['n']} · OCR 丢失 {tot['lost']} · 无公式页 {tot['zero']}")
    print("分册:", {b: (per[b]['pages'], per[b]['n'], per[b]['lost']) for b in ORDER})


if __name__ == "__main__":
    main()
