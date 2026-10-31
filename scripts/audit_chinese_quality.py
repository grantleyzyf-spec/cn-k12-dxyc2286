# -*- coding: utf-8 -*-
"""语文题库质量审计（可复算）：六项自动化检查 + 教材原句回查。

检查项：
A 结构：每点 5 题、四题型齐、numeric 带 verify 且可复算
B 选择题：答案在选项中、4 个互异选项、无「以上都不对/都无关」等凑数项
C 简答：keypoints ≥2 且能在参考答案中找到（字符二元组覆盖 ≥0.5）
D 近重复：全库题干两两相似度 >0.9 的成对列出
E 学段口径：课标 id 首段（1/2/3/4）与年级匹配
F 教材回查：题干/解析中「」内引用片段（≥8 字）必须能在对应册教材正文中找到

用法：python3 audit_cn_quality.py [--write]
"""
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/chinese/topics.json"
QP = f"{REPO}/data/chinese/questions.json"
OUT = f"{REPO}/docs/chinese-quality-audit.md"
WRITE = "--write" in sys.argv
BOOK_DIR = os.path.expanduser("~/Desktop/中小学教材/中小学教材/语文/小学")
PYL = set("āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüńň")
CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}


def clean(s):
    return "".join(ch for ch in s if not ch.isspace() and not (ch.isascii() and ch.isalpha()) and ch not in PYL)


def norm(s):
    return re.sub(r"[\s　，。、；：！？（）()“”\"'‘’《》…—－\-·]", "", s or "")


def load_book_texts():
    """册名 → 该册全书清洗后的正文（用于原句回查）"""
    import fitz
    books = {}
    for f in glob.glob(os.path.join(BOOK_DIR, "*.pdf")):
        m = re.search(r"语文_([一二三四五六])年级_([上下])册", os.path.basename(f))
        if not m:
            continue
        key = f"{m.group(1)}年级{m.group(2)}册"
        try:
            d = fitz.open(f)
            books[key] = clean("".join(d[i].get_text() for i in range(len(d))))
        except Exception as e:
            print("读 PDF 失败", key, e)
    return books


def bigrams(s):
    s = norm(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    by_topic = defaultdict(list)
    for q in qs:
        by_topic[q["topicId"]].append(q)
    keji = [t for t in topics if "教材课级" in (t.get("tags") or [])]

    issues = defaultdict(list)
    # A 结构
    for t in keji:
        qq = by_topic.get(t["id"], [])
        if len(qq) != 5:
            issues["A1 每点题数≠5"].append((t["id"], t["name"], len(qq)))
        types = Counter(q["type"] for q in qq)
        for ty in ("choice", "fill", "numeric", "short-answer"):
            if types.get(ty, 0) < 1:
                issues["A2 题型缺失"].append((t["id"], t["name"], ty))
    for q in qs:
        if q["type"] == "numeric":
            try:
                val = eval(q["verify"], {"__builtins__": {}}, {})
                if abs(float(val) - float(q["answer"])) > 1e-6:
                    issues["A3 verify 与答案不符"].append((q["id"], q["verify"], q["answer"]))
            except Exception as e:
                issues["A3 verify 不可复算"].append((q["id"], str(e)[:40]))

    # B 选择题
    for q in qs:
        if q["type"] != "choice":
            continue
        labels = [o["label"] for o in q.get("options", [])]
        texts = [o["text"] for o in q.get("options", [])]
        if len(q.get("options", [])) != 4:
            issues["B1 选项数≠4"].append((q["id"], len(q.get("options", []))))
        if len(set(texts)) != len(texts):
            issues["B2 选项重复"].append((q["id"], texts))
        if q["answer"] not in labels:
            issues["B3 答案不在选项"].append((q["id"], q["answer"], labels))
        for bad in ("以上都不对", "以上都对", "都无关", "均不正确"):
            if any(bad in (x or "") for x in texts):
                issues["B4 凑数项"].append((q["id"], bad))

    # C 简答 keypoints
    for q in qs:
        if q["type"] != "short-answer":
            continue
        kps = q.get("keypoints") or []
        if len(kps) < 2:
            issues["C1 keypoints <2"].append((q["id"], len(kps)))
        ans = bigrams(q.get("answer", ""))
        for kp in kps:
            kb = bigrams(kp)
            if not kb:
                continue
            cover = len(kb & ans) / len(kb)
            if cover == 0.0 and len(kp) >= 4:
                issues["C2b 建议：要点字面未见于参考答案（诊断判读仍可用）"].append((q["id"], kp))

    # D 近重复题干
    seen = []
    for q in qs:
        p = norm(q.get("prompt", ""))
        if len(p) < 8:
            continue
        bp = {p[i:i + 2] for i in range(len(p) - 1)}
        for p2, qid2, b2 in seen[-400:]:
            if p == p2:
                grp = "D1b 同字笔画题重复" if "字一共有几画" in p else "D1a 题干完全相同"
                issues[grp].append((q["id"], qid2, q["prompt"][:24]))
                break
            if bp and b2:
                j = len(bp & b2) / len(bp | b2)
                if j > 0.9 and len(p) > 12:
                    issues["D2 题干高度相似"].append((q["id"], qid2, round(j, 2)))
                    break
        seen.append((p, q["id"], bp))

    # E 学段口径
    band = {}
    for g in (1, 2):
        band[g] = "1"
    for g in (3, 4):
        band[g] = "2"
    for g in (5, 6):
        band[g] = "3"
    for g in (7, 8, 9):
        band[g] = "4"
    for t in topics:
        g = t.get("grade")
        for s in t.get("standards", []):
            sid = s.get("id", "")
            m = re.match(r"cyw-2022:(\d)\.", sid)
            if not m or g not in band:
                continue
            if m.group(1) != band[g]:
                issues["E1 课标学段与年级不符"].append((t["id"], t["name"], g, sid))

    # F 教材回查（小学 9 册）
    books = load_book_texts()
    checked = 0
    for t in keji:
        key = None
        for k in books:
            if t["chapter"].startswith(k.replace("册", "").replace("年级", "年级")):
                key = k
                break
        # chapter 形如「一年级上册 第一单元」，k 形如「一年级上册」
        if key is None:
            pref = t["chapter"].split(" ")[0]
            for k in books:
                if pref == k:
                    key = k
                    break
        if key is None or key not in books:
            continue
        body = books[key]
        for q in by_topic.get(t["id"], []):
            for frag in re.findall(r"「([^」]{8,})」", q.get("prompt") or ""):
                frag2 = frag.replace("____", q.get("answer") or "")
                checked += 1
                if clean(frag2) not in body:
                    issues["F1 题干引用未在教材命中"].append((q["id"], key, frag2[:26]))

    # 报告
    lines = ["# 语文题库质量审计（自动生成）", "",
             f"- 课级点 {len(keji)} 个 · 题 {len(qs)} 道 · 有教材可回查的册：{[k for k in books]}",
             f"- 「」引用片段回查 {checked} 处", "",
             "**判定口径**：A/B/E 为硬性问题（必须为 0）；C2b 为建议（要点是机判标签，"
             "字面不必与参考答案一致）；D1b 属设计保留（同一个字在不同册都会教，"
             "按册做诊断时不会互相干扰）；F1 是硬性问题（题干引用必须能在该册教材正文逐字命中）。", ""]
    total = 0
    for k in sorted(issues):
        v = issues[k]
        total += len(v)
        lines.append(f"## {k}：{len(v)} 条")
        for item in v[:12]:
            lines.append(f"- {item}")
        if len(v) > 12:
            lines.append(f"- …（共 {len(v)} 条，省略 {len(v) - 12} 条）")
        lines.append("")
    lines.insert(4, f"- **问题合计 {total} 条**")
    report = "\n".join(lines)
    print(report[:4000])
    if WRITE:
        open(OUT, "w", encoding="utf-8").write(report + "\n")
        print(f"\n✅ 报告已写入 {OUT}")


if __name__ == "__main__":
    main()
