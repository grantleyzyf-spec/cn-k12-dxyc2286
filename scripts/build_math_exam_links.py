# -*- coding: utf-8 -*-
"""给试卷注入稳定 id 与三向链接，并生成两个可复算索引（自适应诊断的数据底座）。

产出：
1) 回写每份卷 JSON：顶层 `examId`；每题 `itemId` / `prereq` / `reteach`
   - examId  = mat_exam_<册码>_<卷码>（如 mat_exam_g7a_u1）
   - itemId  = <examId>_q<两位题号>
   - prereq  = 主考知识点的**硬前置**（dependencies 里 type=hard 的直接前驱，自动展开，不手写）
   - reteach = 题库里同知识点的题（最多 3 道，排除题干与卷题近似的）
2) data/math/exam_links.json      —— 卷 → 题 → 知识点/前置/回练（诊断引擎读这个）
3) data/math/topic_exam_map.json  —— 知识点 → 考过它的 itemId（错题归因、掌握度看板读这个）

幂等：重复跑结果一致。用法：python3 scripts/build_math_exam_links.py [--check]
"""
import difflib
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
EXAM = f"{D}/exams"
LINKS = f"{D}/exam_links.json"
TMAP = f"{D}/topic_exam_map.json"
BOOK_CODE = {
 "一年级上册": "g1a", "一年级下册": "g1b", "二年级上册": "g2a", "二年级下册": "g2b",
 "三年级上册": "g3a", "三年级下册": "g3b", "四年级上册": "g4a", "四年级下册": "g4b",
 "五年级上册": "g5a", "五年级下册": "g5b", "六年级上册": "g6a", "六年级下册": "g6b",
 "七年级上册": "g7a", "七年级下册": "g7b", "八年级上册": "g8a", "八年级下册": "g8b",
 "九年级上册": "g9a", "九年级下册": "g9b",
 "必修第一册": "bx1", "必修第二册": "bx2",
 "选择性必修第一册": "xx1", "选择性必修第二册": "xx2", "选择性必修第三册": "xx3",
}


def norm(s):
    return re.sub(r"\s+", "", s or "")


CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn2int(s):
    """中文数字 → 整数。必须支持「二十五」「十八」「三十」这类两位数：
    早期实现只取末位字符，「第二十五单元」被算成 u5、「第十八单元」算成 u8，
    与写手写入的 g9a_u25 / g8a_u18 冲突，重跑链接器会把 examId 覆盖错。"""
    if not s:
        return 1
    if s == "十":
        return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN_DIGIT.get(a, 1) if a else 1) * 10 + (CN_DIGIT.get(b, 0) if b else 0)
    if "百" in s:
        a, _, b = s.partition("百")
        return (CN_DIGIT.get(a, 1) if a else 1) * 100 + (cn2int(b) if b else 0)
    return CN_DIGIT.get(s, 1)


def paper_code(paper, kind):
    """第一单元测试卷 → u1；第二十五单元测试卷 → u25；期中测试卷A → mid_a；期末测试卷B → fin_b"""
    if kind == "unit":
        # 小学/初中叫「第X单元测试卷」，高中叫「第X章测试卷」，两种都要认，
        # 否则高中卷会落到默认 u1，全部撞成同一个 examId
        m = re.search(r"第([一二三四五六七八九十百]+)(?:单元|章)", paper)
        return f"u{cn2int(m.group(1) if m else '一')}"
    if kind == "midterm":
        return "mid_" + (paper[-1].lower() if paper[-1] in "AB" else "a")
    return "fin_" + (paper[-1].lower() if paper[-1] in "AB" else "a")


def main():
    check_only = "--check" in sys.argv
    topics = {t["id"]: t for t in json.load(open(f"{D}/topics.json", encoding="utf-8"))}
    deps = json.load(open(f"{D}/dependencies.json", encoding="utf-8"))
    bank = json.load(open(f"{D}/questions.json", encoding="utf-8"))
    # 前置边分两类，诊断用法完全不同：
    #  - 课时点 ↔ 课时点（同单元上一课时，soft）＝真正的「学习顺序前置」，缺它是知识断层；
    #  - 单元级点 → 课时点（hard）＝上位概念，不是学习顺序，不能当「前置缺口」去判。
    # 早期数据里单元级点是按知识点命名的，按 chapter 连边会把「科学记数法」连成
    # 「1.1 正数和负数」的前置，语义是错的，所以这里必须按 chapter 是否含「 · 」分流。
    def is_ke(tid):
        return " · " in (topics.get(tid, {}).get("chapter") or "")

    prev_ke, prev_upper = {}, {}
    for e in deps:
        a, b = e["from"], e["to"]
        if not is_ke(b):
            continue
        (prev_ke if is_ke(a) else prev_upper).setdefault(b, []).append(a)
    bank_by_topic = {}
    for q in bank:
        bank_by_topic.setdefault(q["topicId"], []).append(q)

    exams, tmap, warn = [], {}, []
    for f in sorted(glob.glob(f"{EXAM}/*/*.json")):
        ex = json.load(open(f, encoding="utf-8"))
        book, kind = ex["book"], ex["kind"]
        code = BOOK_CODE.get(book)
        if not code:
            warn.append(f"{book} 没有册码，跳过")
            continue
        exam_id = f"mat_exam_{code}_{paper_code(ex['paper'], kind)}"
        ex["examId"] = exam_id
        items_out = []
        for sec in ex["sections"]:
            for it in sec["items"]:
                it["itemId"] = f"{exam_id}_q{int(it['no']):02d}"
                prereq, upper = [], []
                for tid in it.get("topicIds") or []:
                    for p in prev_ke.get(tid, []):
                        if p not in prereq:
                            prereq.append(p)
                    for p in prev_upper.get(tid, []):
                        if p not in upper:
                            upper.append(p)
                it["prereq"] = prereq
                it["prereqUpper"] = upper
                # 回练：题库同知识点题，排除题干与本题近似的
                cand = []
                base = norm(it["stem"])
                for tid in it.get("topicIds") or []:
                    for q in bank_by_topic.get(tid, []):
                        if difflib.SequenceMatcher(None, base, norm(q["prompt"])).ratio() > 0.7:
                            continue
                        cand.append({"qid": q["id"], "topicId": tid, "difficulty": q.get("difficulty")})
                uniq, seen = [], set()
                for c in cand:
                    if c["qid"] in seen:
                        continue
                    seen.add(c["qid"])
                    uniq.append(c)
                it["reteach"] = uniq[:3]
                if not it.get("topicIds"):
                    warn.append(f"{exam_id} 第 {it['no']} 题没有 topicIds")
                if not it["reteach"]:
                    warn.append(f"{exam_id} 第 {it['no']} 题无题库回练可用（该点无同点题）")
                for tid in it.get("topicIds") or []:
                    tmap.setdefault(tid, [])
                    if it["itemId"] not in tmap[tid]:
                        tmap[tid].append(it["itemId"])
                items_out.append({"itemId": it["itemId"], "no": it["no"], "type": it["type"],
                                  "score": it["score"], "difficulty": it.get("difficulty"),
                                  "topicIds": it.get("topicIds") or [],
                                  "prereq": prereq, "prereqUpper": upper,
                                  "reteach": [c["qid"] for c in it["reteach"]]})
        exams.append({"examId": exam_id, "book": book, "paper": ex["paper"], "kind": kind,
                      "grade": ex["grade"], "stage": ex["stage"],
                      "fullScore": ex["fullScore"], "duration": ex["duration"],
                      "scope": ex.get("scope") or [], "items": items_out})
        if not check_only:
            json.dump(ex, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(f, "a").write("\n")

    if not check_only:
        json.dump({"generatedBy": "scripts/build_math_exam_links.py",
                   "topicCount": len(tmap), "examCount": len(exams), "exams": exams},
                  open(LINKS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(tmap, open(TMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    n_items = sum(len(e["items"]) for e in exams)
    n_pre = sum(1 for e in exams for i in e["items"] if i["prereq"])
    n_ret = sum(1 for e in exams for i in e["items"] if i["reteach"])
    print(f"卷 {len(exams)} 份 / 题 {n_items} 道；带前置 {n_pre} 道；带回练 {n_ret} 道")
    print(f"知识点覆盖 {len(tmap)} 个 → {TMAP}")
    if warn:
        print(f"⚠️ {len(warn)} 条提示（前 10）：")
        for w in warn[:10]:
            print("  -", w)


if __name__ == "__main__":
    main()
