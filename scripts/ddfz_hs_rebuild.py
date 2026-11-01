# -*- coding: utf-8 -*-
"""高中思想政治 7 册结构重建（单元→课→框），只读试跑：python3 scripts/ddfz_hs_rebuild.py --show

为什么要重建：原盘点把「课」标成「第N单元」，框题靠扫描正文里的「第X框」反推，
结果把目录页、目级子标题、重复框都卷进来（5 个「目录」点、14 个单元框号乱序）。
本脚本只读 PDF 目录页，按缩进与「第X单元／第X课／综合探究」层级还原真实结构。
"""
import argparse
import glob
import json
import os
import re
import subprocess

BASE = os.path.expanduser("~/Desktop/中小学教材/中小学教材/道德与法治/高中思想政治")
CN = "一二三四五六七八九十"
# 册序按课程顺序写死：文件名按 ISBN 排序会把选必3排到最前
BOOKS = [
    ("必修1", 10, "中国特色社会主义"),
    ("必修2", 10, "经济与社会"),
    ("必修3", 10, "政治与法治"),
    ("必修4", 10, "哲学与文化"),
    ("选择性必修1", 11, "当代国际政治与经济"),
    ("选择性必修2", 11, "法律与生活"),
    ("选择性必修3", 11, "逻辑与思维"),
]
RE_UNIT = re.compile(r"^第\s*([%s]+)\s*单元\s*(.+)$" % CN)
RE_KE = re.compile(r"^第\s*([%s]+)\s*课\s*(.+)$" % CN)
RE_TAN = re.compile(r"^综合探究\s*([%s]?)\s*(.+)$" % CN)
TAIL_PAGE = re.compile(r"\s*(\d{1,3})\s*$")


def cn2int(s):
    if not s:
        return 0
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def find_pdf(tag, title):
    for p in glob.glob(os.path.join(BASE, "*.pdf")):
        if tag in p and title[:4] in p:
            return p
    raise FileNotFoundError(tag)


def toc_lines(pdf, pages=40):
    out = subprocess.run(["pdftotext", "-f", "1", "-l", str(pages), "-layout", pdf, "-"],
                         capture_output=True, text=True, errors="replace").stdout
    lines = out.splitlines()
    start = next((i for i, l in enumerate(lines) if re.search(r"目\s*录", l)), 0)
    # 目录跨多页、每页页脚都印「目录 1」⇒ 不能见页脚就停；用「连续非目录行」判结束
    return lines[start:]


def parse(pdf, book, grade):
    units, cur_unit, cur_ke = [], None, None
    buf = None  # 折行的课名缓冲

    def flush_box(text, page):
        nonlocal cur_ke
        if cur_ke is None:
            return
        name = re.sub(r"\s{2,}", " ", text).strip()
        if not name or re.search(r"^(目\s*录|仅供|第.{1,3}版)", name):
            return
        cur_ke["boxes"].append({"no": len(cur_ke["boxes"]) + 1, "title": name, "page": page})

    streak = 0
    for raw in toc_lines(pdf):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()
        m_page = TAIL_PAGE.search(text)
        page = int(m_page.group(1)) if m_page else None
        body = TAIL_PAGE.sub("", text).strip() if page else text
        is_toc = bool(page) or bool(RE_UNIT.match(body) or RE_KE.match(body) or RE_TAN.match(body))
        if not is_toc:
            streak += 1
            if streak > 12:      # 连续十几行不是目录条目 ⇒ 已进入正文
                break
        else:
            streak = 0

        # 折行课名：「第四课 …才能实现」+「中华民族伟大复兴 42」
        if buf is not None:
            buf = (buf[0] + body, buf[1], buf[2])
            if page is not None:
                title, ind, kno = buf
                cur_ke = {"no": kno, "title": re.sub(r"\s+", "", title),
                          "boxes": [], "parent": cur_unit}
                if cur_unit is not None:
                    cur_unit["kes"].append(cur_ke)
                else:
                    units.append({"no": len(units) + 1, "title": "", "kes": [cur_ke], "flat": True})
                    cur_unit = units[-1]
                buf = None
            continue

        m = RE_UNIT.match(body)
        if m:
            cur_unit = {"no": cn2int(m.group(1)), "title": re.sub(r"\s+", "", m.group(2)), "kes": []}
            units.append(cur_unit)
            cur_ke = None
            continue
        m = RE_KE.match(body)
        if m:
            title = re.sub(r"\s+", "", m.group(2))
            if page is None:  # 课名折行
                buf = (title, indent, cn2int(m.group(1)))
                cur_ke = None
                continue
            cur_ke = {"no": cn2int(m.group(1)), "title": title, "boxes": [], "parent": cur_unit}
            if cur_unit is None:  # 必修1 无单元标题
                cur_unit = {"no": 1, "title": "", "kes": [], "flat": True}
                units.append(cur_unit)
                cur_ke["parent"] = cur_unit
            cur_unit["kes"].append(cur_ke)
            continue
        m = RE_TAN.match(body)
        if m and page is not None:
            t = "综合探究" + (m.group(1) or "") + " " + re.sub(r"\s+", " ", m.group(2)).strip()
            if cur_unit is not None:
                cur_unit.setdefault("explores", []).append({"title": t, "page": page})
            continue
        # 其余带页码的缩进行 = 框题
        if page is not None and cur_ke is not None and indent >= 4:
            flush_box(body, page)
    return units


def structure():
    res = []
    for tag, grade, title in BOOKS:
        pdf = find_pdf(tag, title)
        units = parse(pdf, tag, grade)
        res.append({"book": f"高中{tag}{title}", "tag": tag, "grade": grade,
                    "pdf": os.path.basename(pdf), "units": units})
    return res


DOMAIN = {
    "必修1": {0: "政治认同"},
    "必修2": {0: "经济发展"},
    "必修3": {1: "政治认同", 2: "政治认同", 3: "法治教育"},
    "必修4": {1: "哲学思维", 2: "哲学思维", 3: "政治认同"},
    "选择性必修1": {1: "政治认同", 2: "政治认同", 3: "经济发展", 4: "政治认同"},
    "选择性必修2": {1: "法治教育", 2: "法治教育", 3: "法治教育", 4: "法治教育"},
    "选择性必修3": {1: "哲学思维", 2: "哲学思维", 3: "哲学思维", 4: "哲学思维"},
}
MASTERY = "能说出「%s」的核心观点并联系生活实例说明"


def build_points(st, start_no):
    """把结构展成知识点：课=单元点，框=课时点（综合探究不单独建点）。"""
    pts, edges = [], []
    n = start_no
    for b in st:
        book = b["book"]
        dom_unit = DOMAIN[b["tag"]]
        prev_ke = None
        prev_box_of_ke = {}
        prev_unit_last = None
        for u in b["units"]:
            dom = dom_unit.get(u["no"], next(iter(dom_unit.values())))
            first_ke_of_unit = None
            for k in u["kes"]:
                ch_ke = book + ("" if u.get("flat") else " 第%d单元 %s" % (u["no"], u["title"])) \
                    + " 第%d课 %s" % (k["no"], k["title"])
                ke_id = "pol_p%03d" % n
                n += 1
                pre = [prev_ke["id"]] if prev_ke else []
                pts.append({"id": ke_id, "name": k["title"], "subject": "politics",
                            "domain": dom, "grade": b["grade"], "semester": "上",
                            "chapter": ch_ke, "level": "unit", "type": "conceptual",
                            "description": k["title"],
                            "mastery_criteria": [MASTERY % k["title"]],
                            "diagnostic_question": {"question": "关于「%s」，下列说法正确的是？" % k["title"],
                                                    "answer": "A"},
                            "external": False, "standards": [], "tags": [dom],
                            "prerequisites": pre, "curriculumRef": "", "verified": False})
                if prev_ke:
                    edges.append({"from": prev_ke["id"], "to": ke_id, "type": "hard"})
                if first_ke_of_unit is None:
                    first_ke_of_unit = {"id": ke_id}
                prev_box = None
                for x in k["boxes"]:
                    bid = "pol_p%03d" % n
                    n += 1
                    pts.append({"id": bid, "name": x["title"], "subject": "politics",
                                "domain": dom, "grade": b["grade"], "semester": "上",
                                "chapter": ch_ke + " 第%d框 %s" % (x["no"], x["title"]),
                                "level": "lesson", "type": "conceptual",
                                "description": x["title"],
                                "mastery_criteria": [MASTERY % x["title"]],
                                "diagnostic_question": {"question": "关于「%s」，下列说法正确的是？" % x["title"],
                                                        "answer": "A"},
                                "external": False, "standards": [], "tags": [dom],
                                "prerequisites": [ke_id] + ([prev_box] if prev_box else []),
                                "curriculumRef": "", "verified": False})
                    edges.append({"from": ke_id, "to": bid, "type": "hard"})
                    if prev_box:
                        edges.append({"from": prev_box, "to": bid, "type": "hard"})
                    prev_box = bid
                prev_box_of_ke[k["no"]] = prev_box
                prev_ke = {"id": ke_id}
            # 单元衔接 soft：上一单元末个框 → 本单元首课
            if prev_unit_last and first_ke_of_unit:
                edges.append({"from": prev_unit_last, "to": first_ke_of_unit["id"], "type": "soft"})
            last_pt = prev_box or (first_ke_of_unit or {}).get("id")
            if u["kes"]:
                prev_unit_last = last_pt
    return pts, edges, n


def write_all(st):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub = os.path.join(root, "data", "politics")
    topics = json.load(open(os.path.join(sub, "topics.json"), encoding="utf-8"))
    deps = json.load(open(os.path.join(sub, "dependencies.json"), encoding="utf-8"))
    keep = [p for p in topics if p["grade"] <= 9]
    max_no = max(int(p["id"].split("_p")[1]) for p in keep)
    pts, edges, nxt = build_points(st, max_no + 1)
    # 根节点 reason
    for p in pts:
        if not p["prerequisites"]:
            p["root_reason"] = "起始知识点：《%s》课程序起点，图谱内无更早前置" % p["chapter"].split(" ")[0]
    keep_ids = {p["id"] for p in keep}
    deps = [e for e in deps if e["from"] in keep_ids and e["to"] in keep_ids]
    all_topics = keep + pts
    all_deps = deps + edges
    json.dump(all_topics, open(os.path.join(sub, "topics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(all_deps, open(os.path.join(sub, "dependencies.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # 盘点表的高中段
    inv_path = os.path.join(sub, "_inventory.json")
    inv = json.load(open(inv_path, encoding="utf-8"))
    inv["books"] = [b for b in inv["books"] if b.get("stage") != "高中"]
    for b in st:
        inv["books"].append({
            "book": b["book"], "grade": b["grade"], "semester": "上", "stage": "高中",
            "pdf": b["pdf"],
            "units": [{"no": u["no"], "title": u["title"] or "（本书不分单元）",
                       "lessons": [{"no": k["no"], "title": k["title"]} for k in u["kes"]],
                       "boxes": [{"ke": k["no"], "no": x["no"], "title": x["title"], "page": x["page"]}
                                 for k in u["kes"] for x in k["boxes"]],
                       "explores": u.get("explores") or []} for u in b["units"]],
        })
    json.dump(inv, open(inv_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("义教 %d 点保留；高中重建 %d 点（课 %d / 框 %d）；边 %d（新增 %d）"
          % (len(keep), len(pts), sum(1 for p in pts if p["level"] == "unit"),
             sum(1 for p in pts if p["level"] == "lesson"), len(all_deps), len(edges)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    st = structure()
    tot_u = tot_k = tot_b = 0
    for b in st:
        kes = sum(len(u["kes"]) for u in b["units"])
        boxes = sum(len(k["boxes"]) for u in b["units"] for k in u["kes"])
        tot_u += len(b["units"]); tot_k += kes; tot_b += boxes
        print("== %-28s 单元 %d / 课 %d / 框 %d" % (b["book"], len(b["units"]), kes, boxes))
        if a.show:
            for u in b["units"]:
                print("  第%d单元 %s%s" % (u["no"], u["title"] or "（本书不分单元）",
                                          "  [综合探究 %d]" % len(u.get("explores") or [])
                                          if u.get("explores") else ""))
                for k in u["kes"]:
                    print("    第%d课 %s" % (k["no"], k["title"]))
                    for x in k["boxes"]:
                        print("      %d) %s  p%s" % (x["no"], x["title"], x["page"]))
    print("合计：单元 %d / 课 %d / 框 %d" % (tot_u, tot_k, tot_b))
    if a.json:
        json.dump(st, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("写出", a.json)
    if a.write:
        write_all(st)


if __name__ == "__main__":
    main()
