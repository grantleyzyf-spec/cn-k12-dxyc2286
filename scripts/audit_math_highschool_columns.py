# -*- coding: utf-8 -*-
"""人教 A 版高中数学 5 册「栏目」逐条核对（阅读与思考 / 探究与发现 / 信息技术应用 / 文献阅读与数学写作 / 数学探究 / 数学建模）。

数据源两路：
  · 栏目清单＝教材自带《每节内容对应页码》TXT 里的栏目行（带教材页码）
  · 正文回查＝OCR 文本（ocr_hs/*.txt），按页检索栏目名，给出命中的首个 PDF 页

产出：/tmp/mtoc/hs_columns.md（清单表）＋ 终端汇总
口径：栏目是拓展/活动板块，**不建知识点**（与 §5 第 1 条同口径），只登记清单与回查结果。
"""
import glob
import json
import os
import re

BASE = "/Users/a627692/Desktop/中小学教材/高中教材/高中数学/人教版（A版）"
OCR = os.path.expanduser("~/Desktop/qbank-upgrade/math/ocr_hs")
OUT = "/tmp/mtoc/hs_columns.md"
VOLS = ["必修第一册", "必修第二册", "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"]
OCR_NAME = {"必修第一册": "必修第1册", "必修第二册": "必修第2册", "选择性必修第一册": "选必第1册",
            "选择性必修第二册": "选必第2册", "选择性必修第三册": "选必第3册"}
# 真正的「栏目」（拓展/活动）；小结与词汇索引属结构性栏目，单独统计、不做正文回查
KINDS = ["阅读与思考", "探究与发现", "信息技术应用", "文献阅读与数学写作", "数学探究", "数学建模", "观察与猜想"]


def norm(s):
    s = re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-*＊]", "", s or "")
    for w in ("的", "与", "和", "及", "其"):
        s = s.replace(w, "")
    return s


def load_pages(vol):
    p = f"{OCR}/{OCR_NAME[vol]}.txt"
    if not os.path.exists(p):
        return {}
    parts = re.split(r"=====PAGE (\d+)=====", open(p, encoding="utf-8").read())
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def parse_columns(vol):
    f = glob.glob(f"{BASE}/数学+高中数学（人教A版）+{vol}+每节内容对应页码.txt")[0]
    ch, out = None, []
    for line in open(f, encoding="utf-8"):
        m = re.match(r"^第([一二三四五六七八九十]+)章[　 ]+(.+?)\s*$", line.strip())
        if m:
            ch = f"第{m.group(1)}章 {m.group(2)}"
            continue
        m = re.match(r"^\s+([^\d\s\.][^0-9\.]{1,12}?)[　 ]{1,}(.+?)\s*\.{2,}\s*教材页码\s*(\d+)", line)
        if not m:
            continue
        kind, name, page = m.group(1).strip(), m.group(2).strip(), int(m.group(3))
        if any(k.replace("*", "") in kind.replace("*", "") for k in KINDS) and name not in (".", ""):
            out.append({"kind": kind, "name": name, "page": page, "ch": ch})
    return out


def main():
    topics = json.load(open(os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/math/topics.json"), encoding="utf-8"))
    rows, tot = [], {}
    for vol in VOLS:
        cols = parse_columns(vol)
        pages = load_pages(vol)
        for c in cols:
            key = norm(c["name"])
            short = key[:8]
            hit = None
            if key:
                for k in (key, short):
                    if hit or len(k) < 3:
                        continue
                    for pno in sorted(pages):          # 目录页与正文页都算命中
                        if k in norm(pages[pno]):
                            hit = pno
                            break
            c["hit"] = hit
            rows.append((vol, c))
        tot[vol] = (len(cols), sum(1 for c in cols if c["hit"]))
    L = ["# 人教 A 版高中数学 5 册 · 栏目逐条核对（阅读与思考 / 探究与发现 / 信息技术应用 / 文献阅读与数学写作 / 数学探究 / 数学建模）", "",
         "- 清单来源：教材自带《每节内容对应页码》TXT 的栏目行（带教材页码）",
         "- 正文回查：`data/math/ocr_highschool/*.txt`（974 页 OCR），按页检索栏目名，给出首个命中的 PDF 页",
         "- 口径：栏目属拓展/活动板块，**不建知识点**，只登记清单与回查结果（与 docs/math.md §5 第 1 条一致）", ""]
    L += ["| 册 | 章 | 栏目类型 | 栏目名称 | 教材页码 | 正文回查 PDF 页 |", "| --- | --- | --- | --- | ---: | ---: |"]
    for vol, c in rows:
        L.append(f"| {vol} | {c['ch'] or '—'} | {c['kind']} | {c['name']} | {c['page']} | "
                 + (str(c["hit"]) if c["hit"] else "❌ 未命中") + " |")
    L += ["", "## 汇总", "", "| 册 | 栏目数 | 正文命中 | 未命中 |", "| --- | ---: | ---: | ---: |"]
    a = b = 0
    for vol in VOLS:
        n, h = tot[vol]
        a += n
        b += h
        L.append(f"| {vol} | {n} | {h} | {n - h} |")
    L.append(f"| **合计** | **{a}** | **{b}** | **{a - b}** |")
    by_kind = {}
    for _v, c in rows:
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
    L += ["", "按类型：" + "；".join(f"{k} {v} 个" for k, v in sorted(by_kind.items(), key=lambda x: -x[1]))]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## 汇总"):]))
    miss = [(v, c["kind"], c["name"], c["page"]) for v, c in rows if not c["hit"]]
    print("\n未命中明细：")
    for m in miss:
        print("  ", m)


if __name__ == "__main__":
    main()
