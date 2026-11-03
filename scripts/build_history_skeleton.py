# -*- coding: utf-8 -*-
"""历史学科骨架生成 + 缺口对账（只写 _skeleton.json 与报告，不动 topics.json）。

用法：
  python3 scripts/build_history_skeleton.py            # 生成骨架 + 打印逐册/逐单元缺口
  python3 scripts/build_history_skeleton.py --write    # 同时落 data/history/_skeleton.json

口径（与语文一致）：一个「课」＝一个知识点，`chapter` 写「<册> 第N单元 <单元名>」（不带 ` · `），
课名进 `name`；「活动课」不建点（与数学「综合与实践不出卷」同理），但计入目录数。
id 段：义教 `his_p1xx` 续现有 max+1，高中 `his_h0xx` 续现有 max+1（⛔ 工人不得自行续号）。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "history")
TOC = os.path.join(D, "_toc")
OVR = os.path.join(TOC, "_overrides.json")
OVERRIDES = json.load(open(OVR, encoding="utf-8")) if os.path.exists(OVR) else {}

# 册 → (grade, semester, id前缀, 默认领域)
BOOK_META = OrderedDict([
    ("七年级上册", (7, "上", "his_p", "中国古代史")),
    ("七年级下册", (7, "下", "his_p", "中国古代史")),
    ("八年级上册", (8, "上", "his_p", "中国近代史")),
    ("八年级下册", (8, "下", "his_p", "中国现代史")),
    ("九年级上册", (9, "上", "his_p", "世界古代史")),
    ("九年级下册", (9, "下", "his_p", "世界现代史")),
    ("中外历史纲要（上）", (10, "上", "his_h", "中国古代史")),
    ("中外历史纲要（下）", (10, "下", "his_h", "世界古代史")),
    ("选择性必修1", (11, "上", "his_h", "国家制度与社会治理")),
    ("选择性必修2", (12, "上", "his_h", "经济与社会生活")),
    ("选择性必修3", (12, "下", "his_h", "文化交流与传播")),
])

# 册内按单元号覆盖领域（通史册一个单元跨时代，默认值会误标）
UNIT_DOMAIN = {
    "九年级上册": {1: "世界古代史", 2: "世界古代史", 3: "世界古代史", 4: "世界古代史",
                   5: "世界近代史", 6: "世界近代史", 7: "世界近代史"},
    "中外历史纲要（上）": {1: "中国古代史", 2: "中国古代史", 3: "中国古代史", 4: "中国古代史",
                          5: "中国近代史", 6: "中国近代史", 7: "中国近代史", 8: "中国近代史",
                          9: "中国现代史", 10: "中国现代史", 11: "中国现代史"},
    "中外历史纲要（下）": {1: "世界古代史", 2: "世界古代史", 3: "世界近代史", 4: "世界近代史",
                          5: "世界近代史", 6: "世界近代史", 7: "世界现代史", 8: "世界现代史",
                          9: "世界现代史"},
}
SKIP_LESSON = re.compile(r"活动课|复习|附录|大事年表")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def apply_lesson_names(book, units):
    """目录页缺课名（列被 OCR 打散）⇒ 用 _overrides.json 的 lessonNames 按课号补。"""
    names = (OVERRIDES.get(book, {}) or {}).get("lessonNames") or {}
    for u in units:
        for l in u["lessons"]:
            if not l["name"] and str(l["no"]) in names:
                l["name"] = names[str(l["no"])]
    return units


def apply_overrides(book, units):
    """按 _overrides.json 修正自动解析的 3 处「两单元并成一单元」，然后顺序重编号。"""
    ov = OVERRIDES.get(book, {})
    out = []
    for u in units:
        sp = (ov.get("split") or {}).get(str(u["no"]))
        name = (ov.get("rename") or {}).get(str(u["no"]), u["name"])
        if not sp:
            out.append({"no": u["no"], "name": name, "lessons": u["lessons"]})
            continue
        i = 0
        for part in sp:
            k = part["lessons"]
            out.append({"no": u["no"], "name": part["name"], "lessons": u["lessons"][i:i + k]})
            i += k
        if i != len(u["lessons"]):
            print(f"  ⚠ {book} 第{u['no']}单元：override 只覆盖 {i}/{len(u['lessons'])} 课，剩余归入最后一段")
            out[-1]["lessons"] += u["lessons"][i:]
    for n, u in enumerate(out, 1):
        u["no"] = n
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    topics = load(os.path.join(D, "topics.json"))
    exist = Counter(t["chapter"] for t in topics)
    # 按「册 + 单元号」索引现有章节：编辑器里历史章名比教材短（「史前时期」vs「史前时期：原始社会与中华文明的起源」），
    # 只按名对会全表 0 命中；骨架沿用库内既有章名，缺的才用教材名（避免为取名做一次 152 点全库改名）。
    unit_name, unit_cnt = {}, Counter()
    um = re.compile(r"^(.+?)\s+第([一二三四五六七八九十]+)单元\s*(.*)$")
    cn = "一二三四五六七八九十"
    for t in topics:
        m = um.match(t["chapter"])
        if not m:
            continue
        no = cn.index(m.group(2)) + 1 if m.group(2) in cn else 0
        key = (m.group(1), no)
        unit_name.setdefault(key, m.group(3).strip())
        unit_cnt[key] += 1
    maxp = max(int(re.search(r"(\d+)$", t["id"]).group(1)) for t in topics if t["id"].startswith("his_p"))
    maxh = max(int(re.search(r"(\d+)$", t["id"]).group(1)) for t in topics if t["id"].startswith("his_h"))

    points, per_book, skipped = [], [], []
    ctr = {"his_p": maxp, "his_h": maxh}
    for book, (grade, sem, pref, default_dom) in BOOK_META.items():
        fp = os.path.join(TOC, f"{book}.json")
        if not os.path.exists(fp):
            per_book.append({"book": book, "units": 0, "lessons": 0, "points": 0,
                             "existPoints": sum(v for k, v in exist.items() if k.startswith(book)),
                             "status": "教材 PDF 缺，未建目录"})
            print(f"⛔ {book}: 无目录（教材 PDF 缺）｜库内现有 {sum(v for k, v in exist.items() if k.startswith(book))} 点")
            continue
        toc = load(fp)
        toc["units"] = apply_overrides(book, apply_lesson_names(book, toc["units"]))
        n_lesson = n_point = 0
        rows = []
        for u in toc["units"]:
            use_toc = bool((OVERRIDES.get(book) or {}).get("useTocNames"))
            uname = u["name"] if use_toc else (unit_name.get((book, u["no"])) or u["name"])
            chap = f"{book} 第{u['no']}单元 {uname}"
            dom = UNIT_DOMAIN.get(book, {}).get(u["no"], default_dom)
            n_lesson += len(u["lessons"])
            k = 0
            for l in u["lessons"]:
                if SKIP_LESSON.search(l["name"] or ""):
                    skipped.append({"book": book, "unit": u["no"], "lesson": l["no"], "name": l["name"]})
                    continue
                k += 1
                n_point += 1
                ctr[pref] += 1
                pid = f"{pref}{ctr[pref]:03d}"
                clean = re.split(r"活动课|学史方法|附录", l["name"] or "")[0].strip()
                points.append({"id": pid, "name": clean, "subject": "history",
                               "domain": dom, "grade": grade, "semester": sem,
                               "chapter": chap, "level": "lesson",
                               "unitNo": u["no"], "lessonNo": l["no"],
                               "tocName": clean, "book": book})
            rows.append({"unit": u["no"], "name": uname, "lessons": len(u["lessons"]),
                         "newPoints": k, "existPoints": unit_cnt.get((book, u["no"]), 0)})
        per_book.append({"book": book, "units": len(toc["units"]), "lessons": n_lesson,
                         "points": n_point,
                         "existPoints": sum(v for (bk, _), v in unit_cnt.items() if bk == book),
                         "status": "ok", "rows": rows})

    # ---- 报告 ----
    print(f"{'册':18s}{'单元':>4s}{'教材课':>6s}{'应建点':>6s}{'库内点':>6s}{'缺口':>6s}")
    tu = tl = tp = te = 0
    for b in per_book:
        if b["status"] != "ok":
            print(f"{b['book']:18s}{'—':>4s}{'—':>6s}{'—':>6s}{b['existPoints']:>6d}{'?':>6s}  ⚠{b['status']}")
            te += b["existPoints"]
            continue
        gap = b["points"] - b["existPoints"]
        tu += b["units"]; tl += b["lessons"]; tp += b["points"]; te += b["existPoints"]
        print(f"{b['book']:18s}{b['units']:4d}{b['lessons']:6d}{b['points']:6d}{b['existPoints']:6d}{gap:+6d}")
    print(f"{'合计':18s}{tu:4d}{tl:6d}{tp:6d}{te:6d}{tp - te:+6d}")

    print("\n逐单元缺口（教材课 ≠ 库内点 的单元）：")
    for b in per_book:
        if b["status"] != "ok":
            continue
        bad = [r for r in b["rows"] if r["newPoints"] != r["existPoints"]]
        if bad:
            print(f"  {b['book']}")
            for r in bad:
                print(f"    第{r['unit']}单元 {r['name'][:24]:26s} 教材{r['newPoints']}课 / 库内{r['existPoints']}点"
                      f"（{r['existPoints'] - r['newPoints']:+d}）")

    if skipped:
        print(f"\n不建点的「活动课/复习」共 {len(skipped)} 条：")
        for s in skipped:
            print(f"  {s['book']} 第{s['unit']}单元 第{s['lesson']}课 {s['name']}")

    print(f"\n领域分布：{dict(Counter(p['domain'] for p in points))}")

    if args.write:
        out = {"subject": "history",
               "generatedBy": "scripts/build_history_skeleton.py",
               "note": "课级骨架：一课一点；chapter=「册 第N单元 单元名」；活动课/复习不建点",
               "books": [{k: v for k, v in b.items() if k != "rows"} for b in per_book],
               "points": points}
        path = os.path.join(D, "_skeleton.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)          # 原子落盘
        print(f"\n✅ 骨架已落盘：{path}（{len(points)} 点）")
    else:
        print("\n（dry-run：未写盘；加 --write 落 data/history/_skeleton.json）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
