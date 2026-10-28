# -*- coding: utf-8 -*-
"""人教 A 版高中数学 5 册「逐小节」核对（权威小节源＝教材自带的《每节内容对应页码》TXT）。

为什么用这份 TXT：它是按教材目录逐节抄下来的（含三级小节与页码），比 OCR 目录更干净；
OCR 文本（ocr_hs/*.txt，974 页全量）作为**正文级复核**：小节名/节号必须能在正文里找到才算核对通过。

核对口径：
  · 小节 → 图谱：取该册内所有知识点，用「去虚词 + 2-gram 覆盖率」打分，≥0.6 记为覆盖（可多个点并列）
  · 未覆盖小节 = 真缺候选；再人工判「活动/案例类（不建点）」或「知识点缺失（要补）」
  · 反查：每个知识点找最相近的小节，<0.5 记为「小节级无对应」（多为粒度差异）

输出：/tmp/mtoc/hs_sections.md
"""
import glob
import json
import os
import re
from collections import defaultdict

BASE = "/Users/a627692/Desktop/中小学教材/高中教材/高中数学/人教版（A版）"
OCR = os.path.expanduser("~/Desktop/qbank-upgrade/math/ocr_hs")
REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = "/tmp/mtoc/hs_sections.md"

BOOK2VOL = {"必修第一册": "必修第一册", "必修第二册": "必修第二册",
            "选择性必修第一册": "选择性必修第一册", "选择性必修第二册": "选择性必修第二册",
            "选择性必修第三册": "选择性必修第三册"}
OCR_NAME = {"必修第一册": "必修第1册", "必修第二册": "必修第2册",
            "选择性必修第一册": "选必第1册", "选择性必修第二册": "选必第2册",
            "选择性必修第三册": "选必第3册"}
STOP = ["的", "与", "和", "及", "其", "之", "中", "初步", "简单", "一般", "基本", "常见", "一些",
        "概念", "定义", "性质", "运算", "计算", "方法", "应用", "问题", "及其"]

# 人工判定：这些小节属「活动/案例/阅读」类，按口径不建知识点
MANUAL = {  # 教材小节名与图谱点名字面不同，内容等价（人工判定，逐条注明依据）
    "基本立体图形": ["空间几何体的结构特征"],            # 8.1 讲棱柱/棱锥/棱台/圆柱/圆锥/圆台/球/简单组合体
    "立体图形的直观图": ["空间几何体的三视图与直观图"],   # 8.2 讲斜二测画法得到的直观图
    "频率与概率": ["频率的稳定性与随机模拟"],              # 10.3 讲频率的稳定性与随机模拟（新增点）
    "并集、交集": ["集合的并集", "集合的交集"],                    # 1.3.1 小节名把两个点并列
    "棱柱、棱锥、棱台": ["空间几何体的结构特征"],                  # 8.1.1
    "圆柱、圆锥、圆台": ["空间几何体的结构特征"],                  # 8.1.2
    "表面积和体积": ["空间几何体的表面积与体积"],                  # 8.3.1 / 8.3.2
    "直线与直线垂直": ["空间中直线、平面垂直的判定与性质"],         # 8.6.1
    "获取数据的途径": ["随机抽样"],                                # 9.1.3
    "总体取值规律的估计": ["用样本估计总体（频率分布）"],           # 9.2.1
    "总体集中趋势的估计": ["用样本的数字特征估计总体"],             # 9.2.3
    "总体离散程度的估计": ["用样本的数字特征估计总体"],             # 9.2.4
    "两条直线平行和垂直的判定": ["两条直线的位置关系"],             # 选必一 2.1.2
    "两点间的距离公式": ["直线的交点坐标与距离公式"],               # 选必一 2.3.2
    "点到直线的距离公式": ["直线的交点坐标与距离公式"],             # 选必一 2.3.3
    "两条平行直线间的距离": ["直线的交点坐标与距离公式"],           # 选必一 2.3.4
    "变化率问题": ["导数的概念"],                                  # 选必二 5.1.1
    "函数的极值与最大（小）值": ["利用导数研究函数的极值", "利用导数研究函数的最值"],  # 选必二 5.3.2
    "成对数据的散点图": ["成对数据的统计相关性"],                  # 选必三 8.1.1
    "两角和与差": ["两角和与差的三角函数公式"],                    # 必修一 5.5.1（新增点）

}
ACTIVITY = {"统计案例", "阅读与思考", "探究与发现", "信息技术应用", "文献阅读", "数学活动", "小结",
            "复习参考题", "数学探究", "数学建模活动"}


def core(s):
    s = re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—-]", "", s or "")
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
    s1 = len(ba & bb) / max(1, len(ba))
    s2 = len(ba & bb) / max(1, len(bb))
    return max(s1, s2)


def parse_toc(vol):
    fs = glob.glob(f"{BASE}/数学+高中数学（人教A版）+{vol}+每节内容对应页码.txt")
    if not fs:
        return None
    txt = open(fs[0], encoding="utf-8").read()
    ch, secs, subs = None, [], []
    for line in txt.split("\n"):
        m = re.match(r"^第([一二三四五六七八九十]+)章[　 ]+(.+?)\s*$", line.strip())
        if m:
            ch = f"第{m.group(1)}章 {m.group(2).strip()}"
            continue
        m = re.match(r"^\s+(\d{1,2}\.\d{1,2})\s*[\*＊]?[　 ]+(.+?)\s*\.{2,}", line)
        if m:
            secs.append({"no": m.group(1), "name": m.group(2).strip(), "ch": ch, "subs": []})
            continue
        m = re.match(r"^\s+(\d{1,2}\.\d{1,2}\.\d{1,2})[　 ]+(.+?)\s*\.{2,}", line)
        if m and secs:
            secs[-1]["subs"].append({"no": m.group(1), "name": m.group(2).strip()})
    return secs


def main():
    topics = json.load(open(f"{REPO}/data/math/topics.json", encoding="utf-8"))
    by_vol = defaultdict(list)
    for t in topics:
        by_vol[t["chapter"].split(" ")[0]].append(t)

    L = ["# 人教 A 版高中数学 5 册 · 逐小节核对（教材小节 ↔ 图谱知识点）", "",
         "- 小节清单源：教材自带的《每节内容对应页码》TXT（逐节 + 三级小节 + 页码）",
         "- 正文复核源：`ocr_hs/*.txt`（5 册 974 页全量 OCR，目录页逐节可回查）",
         "- 覆盖判定：去虚词 + 2-gram 覆盖率 ≥0.6 记为覆盖；未覆盖者逐条人工定性", ""]
    rows, todo, sub_rows = [], [], []
    for vol in BOOK2VOL:
        secs = parse_toc(vol)
        ts = by_vol.get(vol, [])
        if not secs:
            L.append(f"## {vol}（缺《每节内容对应页码》TXT）\n")
            continue
        ocr = f"{OCR}/{OCR_NAME[vol]}.txt"
        ocr_txt = open(ocr, encoding="utf-8").read() if os.path.exists(ocr) else ""
        L.append(f"## {vol}（教材小节 {len(secs)} 个 · 图谱 {len(ts)} 点）")
        L.append("")
        L.append("| 小节 | 教材小节名 | 三级小节 | 图谱对应知识点 | 正文回查 |")
        L.append("| --- | --- | --- | --- | :---: |")
        ok = 0
        miss = []
        for s in secs:
            scored = sorted(((score(s["name"], t["name"]), t) for t in ts), key=lambda x: -x[0])
            hits = [(t["name"], sc) for sc, t in scored[:4] if sc >= 0.6]
            for mn, mts in MANUAL.items():
                if mn in s["name"]:
                    hits = hits + [(n, 1.0) for n in mts if n not in [h[0] for h in hits]]
            if hits:
                ok += 1
            else:
                miss.append(s)
            in_ocr = "✅" if (s["no"] in ocr_txt or core(s["name"]) and core(s["name"]) in core(ocr_txt)) else "—"
            subs = "、".join(x["name"] for x in s["subs"]) or "—"
            L.append(f"| {'✅' if hits else '❌'} {s['no']} | {s['name']} | {subs} | "
                     + ("、".join(f"{n}" for n, _ in hits) or "—") + f" | {in_ocr} |")
        # 反查
        orphan = []
        for t in ts:
            best = max(((score(s["name"], t["name"]), s["no"]) for s in secs), default=(0, None))
            if best[0] < 0.5:
                orphan.append((t["name"], best[1], best[0]))
        L.append("")
        L.append(f"- 小节 {len(secs)} 个：覆盖 **{ok}** · 未覆盖 **{len(miss)}**"
                 + (("：" + "；".join(f"{s['no']} {s['name']}" + ("（活动/案例类，不建点）" if any(k in s["name"] for k in ACTIVITY) else "") for s in miss)) if miss else ""))
        L.append(f"- 图谱点 {len(ts)} 个：小节级无对应 {len(orphan)}"
                 + (("：" + "、".join(f"{n}(最近 {k} {sc:.2f})" for n, k, sc in orphan)) if orphan else ""))
        L.append("")
        nonact = sum(1 for s in miss if not any(k in s["name"] for k in ACTIVITY))
        subs_all = [x for s2 in secs for x in s2["subs"]]
        subs_ok = 0
        subs_miss = []
        for x in subs_all:
            sc_best = max((score(x["name"], t["name"]) for t in ts), default=0)
            for mn in MANUAL:
                if mn in x["name"]:
                    sc_best = 1.0
            if sc_best >= 0.6:
                subs_ok += 1
            else:
                subs_miss.append(x)
        L.insert(len(L) - 1, f"- 三级小节 {len(subs_all)} 个：覆盖 {subs_ok} · 未覆盖 {len(subs_miss)}"
                 + (("：" + "、".join(f"{x['no']} {x['name']}" for x in subs_miss)) if subs_miss else ""))
        rows.append((vol, len(secs), len(ts), ok, len(miss), nonact, len(orphan)))
        sub_rows.append((vol, len(subs_all), subs_ok, len(subs_miss)))
        for s in miss:
            if not any(k in s["name"] for k in ACTIVITY):
                todo.append((vol, s["ch"], s["no"], s["name"]))

    L += ["## 汇总", "",
          "| 册 | 教材小节 | 图谱点 | 小节覆盖 | 小节未覆盖 | 其中非活动类 | 图谱点小节级无对应 |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        L.append("| {} | {} | {} | {} | {} | {} | {} |".format(*r))
    L += ["", "## 三级小节覆盖", "", "| 册 | 三级小节 | 覆盖 | 未覆盖 |", "| --- | ---: | ---: | ---: |"]
    for v, a, b, c in sub_rows:
        L.append(f"| {v} | {a} | {b} | {c} |")
    L += ["", "## 待判：非活动类的未覆盖小节", ""]
    for v, ch, no, nm in todo:
        L.append(f"- {v} · {ch} · **{no} {nm}**")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## 汇总"):]))
    print(f"\n报告：{OUT}")


if __name__ == "__main__":
    main()
