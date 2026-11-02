#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版高中数学图谱 · 骨架生成器（章级分片）

输入：/tmp/mej/docx_struct.json（章/课时权威源）＋ /tmp/mej/toc_h*.json（节名+页码）
输出：
  data/math-ejiao/_skeleton.json
  data/math-ejiao/_shards/c01..c20.json   每章一份派单（一个工位写一章）
  data/math-ejiao/_deps.json
口径：单元点 mej_h001… 题量 5；课时点 mej_h1001… 题量 8、带 page（页面取所属节的起始页）
"""
import json, os, re

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
SUBJ, PFX, SRC = "math-ejiao", "mej", "/tmp/mej"
OUT = os.path.join(REPO, "data", SUBJ)

VOLS = [("h1", "鄂教版必修第一册", 10, "上"), ("h2", "鄂教版必修第二册", 11, "下"),
        ("h3", "鄂教版必修第三册", 12, "上"), ("h4", "鄂教版必修第四册", 13, "下"),
        ("h5", "鄂教版选择性必修第一册", 14, "上"), ("h6", "鄂教版选择性必修第二册", 15, "下"),
        ("h7", "鄂教版选择性必修第三册", 16, "上")]

DOMAIN = [("统计与概率", r"概率|统计|抽样|分布|百分位|集中趋势|离散|计数原理|排列|组合|二项式"),
          ("几何与代数", r"向量|复数|立体几何|解析几何|圆锥曲线|直线|空间|平面|椭圆|双曲线|抛物线"),
          ("函数", r"集合|逻辑|不等式|函数|指数|对数|三角|数列|导数|幂|零点|增长")]


def _int_page(v):
    if v is None:
        return None
    m = re.search(r"\d+", str(v))
    return int(m.group()) if m else None


def domain_of(name):
    for dom, pat in DOMAIN:
        if re.search(pat, name):
            return dom
    return "函数"


def main():
    os.makedirs(os.path.join(OUT, "_shards"), exist_ok=True)
    struct = json.load(open(os.path.join(SRC, "docx_struct.json"), encoding="utf-8"))
    toc = {}
    for f in os.listdir(SRC):
        if f.startswith("toc_h") and f.endswith(".json"):
            d = json.load(open(os.path.join(SRC, f), encoding="utf-8"))
            if d.get("chapters"):
                toc[d["_tag"]] = d["chapters"]

    volumes, deps = [], []
    uc = lc = 0
    for tag, book, grade, sem in VOLS:
        src = struct.get(book.replace("鄂教版", ""))
        if not src:
            print("!! 缺结构", book); continue
        toc_ch = {c.get("ch_no"): c for c in toc.get(tag, [])}
        units, prev = [], None
        for ch in sorted(src["chapters"], key=lambda c: c["ch_no"]):
            ch_no = int(re.search(r"\d+", str(ch["ch_no"])).group())
            uc += 1
            uid = f"{PFX}_h{uc:03d}"
            uchapter = f"{book} {ch['chapter']}"
            tc = toc_ch.get(ch_no, {})
            secs = [((s.get("name") or "").strip(), _int_page(s.get("page"))) for s in (tc.get("sections") or [])]
            lessons = []
            last_page = secs[0][1] if secs else None
            for l in ch["lessons"]:
                lc += 1
                lid = f"{PFX}_h1{lc:03d}"
                name = l["title"]
                page = None
                for sname, sp in secs:
                    key = re.sub(r"[（(].*?[）)]", "", sname)
                    if key and (key in name or name in sname):
                        page, last_page = sp, sp
                        break
                if page is None:
                    page = last_page
                lessons.append({"id": lid, "name": name, "page": page,
                                "chapter": f"{uchapter} · {name}"})
                if prev:
                    deps.append({"from": prev, "to": lid, "type": "hard", "reason": "同册课时顺次"})
                deps.append({"from": uid, "to": lid, "type": "hard", "reason": "单元包含课时"})
                prev = lid
            units.append({"unit_no": ch["ch_no"], "unit_name": ch["chapter"], "unit_chapter": uchapter,
                          "unit_id": uid, "domain": domain_of(ch["chapter"]),
                          "sections": [{"no": s[0], "page": s[1]} for s in secs],
                          "lessons": lessons})
        volumes.append({"tag": tag, "book": book, "stage": "高中", "grade": grade, "semester": sem,
                        "units": units})
        print(f"{tag} {book}: {len(units)} 章 / {sum(len(u['lessons']) for u in units)} 课时")

    flat = [(v["tag"], v["units"][0]["unit_id"], v["units"][-1]["lessons"][-1]["id"])
            for v in volumes if v["units"] and v["units"][-1]["lessons"]]
    for i in range(len(flat) - 1):
        deps.append({"from": flat[i][2], "to": flat[i + 1][1], "type": "soft",
                     "reason": f"册际衔接：{flat[i][0]} → {flat[i+1][0]}"})

    skel = {"edition": "鄂教版", "subject": "math",
            "volumes": volumes, "missing_volumes": [],
            "known_gap": "教材库中鄂教版数学只有高中 7 册（必修一~四、选必一~三）；小学/初中无鄂教版教材，不在本图谱范围。"}
    json.dump(skel, open(os.path.join(OUT, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ci = 0
    for v in volumes:
        for u in v["units"]:
            ci += 1
            shard = {"tag": f"c{ci:02d}", "shard_kind": "chapter", "edition": "鄂教版",
                     "book": v["book"], "stage": "高中", "grade": v["grade"], "semester": v["semester"],
                     "units": [{"unit_id": u["unit_id"], "unit_name": u["unit_name"],
                                "unit_chapter": u["unit_chapter"], "domain": u["domain"],
                                "sections": u["sections"],
                                "lessons": [{"id": l["id"], "name": l["name"],
                                             "chapter": l["chapter"], "page": l["page"]}
                                            for l in u["lessons"]]}]}
            json.dump(shard, open(os.path.join(OUT, "_shards", f"c{ci:02d}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(OUT, "_deps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    nl = sum(len(u["lessons"]) for v in volumes for u in v["units"])
    nopage = sum(1 for v in volumes for u in v["units"] for l in u["lessons"] if not l["page"])
    print(f"\n合计：{len(volumes)} 册 / {ci} 单元点 / {nl} 课时点 / 边 {len(deps)} / 无页码 {nopage}")
    print("题量预估：", ci * 5 + nl * 8, "题")


if __name__ == "__main__":
    main()
