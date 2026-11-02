#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初高中「单元点」补建：按 chapter 聚合课时点 → 单元点 spec（含 5 题派单要点）。

现状：小学有 84 个 `level=unit` 单元点（每点 5 道诊断题），初高中没有 ⇒ 出不了单元卷
（gen_exam_shards.py 的单元卷按 `level==unit` 聚合）。

本器**只产 spec、不改库**：
  data/math-bsd/_unit_specs/<册>_第N单元.json
  含完整 unit 记录（level=unit/description/mastery_criteria/root_reason…）与 5 个预分配题 id。

合并（父代执行）：
  python3 scripts/make_bsd_unit_specs.py --apply data/math-bsd/_unit_parts/*.json
  —— 插入单元点、补「单元→各课时」hard 边与课时的 prerequisites 镜像、并入 5 题。
"""
import argparse
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "data", "math-bsd")
CN_DIGITS = "一二三四五六七八九十"
CN = {c: i for i, c in enumerate(CN_DIGITS, 1)}


def cn_num(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    return CN.get(s, 0)


def cn_of(n):
    return CN_DIGITS[n - 1] if 1 <= n <= 10 else str(n)


def unit_of(chapter):
    m = re.match(r"^(\S+)\s+第([一二三四五六七八九十\d]+)(单元|章)\s*(.*)$", chapter)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), m.group(4).split(" · ")[0].strip()


def build_specs(books):
    topics = json.load(open(os.path.join(B, "topics.json"), encoding="utf-8"))
    nums = [int(m.group(1)) for t in topics
            if t.get("level") == "unit" and (m := re.match(r"mbs_u(\d+)", t["id"]))]
    next_uid = (max(nums) + 1) if nums else 1
    qnums = [int(m.group(1)) for q in json.load(open(os.path.join(B, "questions.json"), encoding="utf-8"))
             if (m := re.match(r"mbs_q(\d+)", q.get("id", "")))]
    next_qid = (max(qnums) + 1) if qnums else 1

    groups = {}
    for t in topics:
        if t.get("level") != "lesson":
            continue
        book = t["chapter"].split(" ")[0]
        if book not in books:
            continue
        u = unit_of(t["chapter"])
        if not u:
            continue
        groups.setdefault((u[0], cn_num(u[1]), u[3]), []).append(t)

    out_dir = os.path.join(B, "_unit_specs")
    os.makedirs(out_dir, exist_ok=True)
    made = 0
    for (book, no, uname), ls in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        ls.sort(key=lambda t: t["id"])
        uid = f"mbs_u{next_uid:03d}"
        next_uid += 1
        qids = [f"mbs_q{next_qid + i:06d}" for i in range(5)]
        next_qid += 5
        dom = Counter(t.get("domain") for t in ls).most_common(1)[0][0]
        std = next((t.get("standards") for t in ls if t.get("standards")), [])
        names = [t["name"] for t in ls]
        desc = (f"本单元围绕「{uname}」展开，包含" + "、".join(names[:4])
                + (f" 等 {len(names)} 个课时" if len(names) > 4 else "")
                + "，重在理清本单元的知识线索与前后联系，把零散的课时串成一条完整的思路。")
        chapter = f"{book} 第{cn_of(no)}单元 {uname}"
        unit_rec = {
            "id": uid, "name": uname, "subject": "math-bsd", "domain": dom,
            "grade": ls[0].get("grade"), "semester": ls[0].get("semester"),
            "chapter": chapter, "level": "unit", "type": "conceptual",
            "description": desc,
            "mastery_criteria": [
                f"能说清「{uname}」这一单元的核心方法与适用条件",
                "能在本单元的典型题里独立完成至少八道并自查对错"],
            "diagnostic_question": {"question": f"下列各题中，属于「{uname}」这一单元核心方法的题目是（　）。",
                                    "answer": "A"},
            "external": False, "standards": std[:1],
            "tags": ["单元上位点", dom],
            "prerequisites": [], "root_reason": "单元上位点，不设先修课时",
            "verified": False,
        }
        if std:
            unit_rec["curriculumRef"] = std[0]["id"]
        payload = {
            "unitId": uid, "book": book, "unitNo": no, "name": uname, "chapter": chapter,
            "grade": unit_rec["grade"], "semester": unit_rec["semester"], "domain": dom,
            "lessonIds": [t["id"] for t in ls], "lessonNames": names,
            "standards": std[:1], "qidRange": qids,
            "unit": unit_rec,
            "out": f"data/math-bsd/_unit_parts/{uid}.json",
        }
        json.dump(payload, open(os.path.join(out_dir, f"{book}_第{no}单元.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        made += 1
    print(f"单元 spec {made} 份 → {out_dir}")


def apply_specs(paths):
    tp = os.path.join(B, "topics.json")
    qp = os.path.join(B, "questions.json")
    dp = os.path.join(B, "dependencies.json")
    topics = json.load(open(tp, encoding="utf-8"))
    qs = json.load(open(qp, encoding="utf-8"))
    deps = json.load(open(dp, encoding="utf-8"))
    tmap = {t["id"]: t for t in topics}
    qids = {q["id"] for q in qs}
    dset = {(d["from"], d["to"]) for d in deps}
    added_t = added_q = added_e = added_p = 0

    for p in sorted(paths):
        d = json.load(open(p, encoding="utf-8"))
        units = d.get("units") or [{"unit": d["unit"], "questions": d.get("questions", [])}]
        for u in units:
            unit = u["unit"]
            uid = unit["id"]
            if uid not in tmap:
                topics.append(unit)
                tmap[uid] = unit
                added_t += 1
            lesson_ids = [t["id"] for t in topics
                          if t.get("level") == "lesson" and t["chapter"].split(" · ")[0] == unit["chapter"]]
            for lid in lesson_ids:
                if (uid, lid) not in dset:
                    deps.append({"from": uid, "to": lid, "type": "hard"})
                    dset.add((uid, lid))
                    added_e += 1
                pre = tmap[lid].setdefault("prerequisites", [])
                if uid not in pre:
                    pre.append(uid)
                    added_p += 1
            for q in u.get("questions", []):
                if q["id"] in qids:
                    continue
                q.setdefault("topicId", uid)
                q.setdefault("topicIds", [uid])
                qs.append(q)
                qids.add(q["id"])
                added_q += 1

    for path, data in ((tp, topics), (qp, qs), (dp, deps)):
        tmp = path + ".tmp"
        json.dump(data, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    print(f"合并完成：新增单元点 {added_t} · 新增题 {added_q} · 新增边 {added_e} · 补 prerequisites {added_p}")
    print(f"现库：点 {len(topics)} · 题 {len(qs)} · 边 {len(deps)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", default=[])
    ap.add_argument("--apply", nargs="*", default=[])
    a = ap.parse_args()
    if a.apply:
        apply_specs(a.apply)
    if a.books:
        build_specs(set(a.books))


if __name__ == "__main__":
    main()
