# -*- coding: utf-8 -*-
"""检查某分片 _bank/<Sxxx>.json 是否达标：python3 check_bank.py S01"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(BASE)
BANK = os.path.join(DATA, "_bank")
SHARD = os.path.join(BASE, sys.argv[1] + ".json") if len(sys.argv) > 1 else None
if not SHARD:
    sys.exit("用法: python3 check_bank.py S01")


def main():
    sh = json.load(open(SHARD, encoding="utf-8"))
    bank_path = os.path.join(BANK, sh["shard"] + ".json")
    if not os.path.exists(bank_path):
        sys.exit(f"FAIL 缺文件 {bank_path}")
    b = json.load(open(bank_path, encoding="utf-8"))

    want_topics = {}
    for u in sh["units"]:
        want_topics[u["unit_id"]] = "unit"
        for l in u["lessons"]:
            want_topics[l["id"]] = "lesson"

    fails = []

    def ck(name, ok, detail=""):
        if not ok:
            fails.append(f"{name} {detail}")

    got = {}
    for t in b.get("topics", []):
        got[t.get("id")] = t
    ck("topics 覆盖完整", set(got) == set(want_topics),
       f"多 {sorted(set(got) - set(want_topics))[:5]} 缺 {sorted(set(want_topics) - set(got))[:5]}")

    for tid, kind in want_topics.items():
        t = got.get(tid) or {}
        d = t.get("description") or ""
        ck(f"{tid} description 字数", 60 <= len(d) <= 200, len(d))
        mc = t.get("mastery_criteria") or []
        ck(f"{tid} 掌握标准 2–3 条", 2 <= len(mc) <= 3, len(mc))
        ck(f"{tid} 每条掌握标准 ≤50 字", all(len(x) <= 50 for x in mc))
        dq = t.get("diagnostic_question") or {}
        ck(f"{tid} 诊断题有问答", bool((dq.get("question") or "").strip()) and
           bool((dq.get("answer") or "").strip()))
        ck(f"{tid} 诊断题答案非裸字母",
           (dq.get("answer") or "").strip() not in list("ABCD"))
        ck(f"{tid} tags 2–4", 2 <= len(t.get("tags") or []) <= 4)

    qs = b.get("questions", [])
    per = {}
    for q in qs:
        per[q.get("topicId")] = per.get(q.get("topicId"), 0) + 1
        qid = q.get("id", "?")
        ck(f"{qid} prompt≥12", len(q.get("prompt") or "") >= 12, len(q.get("prompt") or ""))
        ck(f"{qid} question=prompt", q.get("question") == q.get("prompt"))
        ck(f"{qid} explanation≥15", len(q.get("explanation") or "") >= 15)
        ck(f"{qid} difficulty 合规", q.get("difficulty") in ("basic", "standard", "hard"))
        ck(f"{qid} 无 Markdown", not re.search(r"\*\*|(^|\s)#\S|`", (q.get("prompt") or "") + (q.get("explanation") or "")))
        if q.get("type") == "choice":
            opts = q.get("options") or []
            ck(f"{qid} choice 4 选项", len(opts) == 4, len(opts))
            labels = [o.get("label") for o in opts]
            ck(f"{qid} 选项 label A-D", labels == ["A", "B", "C", "D"], labels)
            ck(f"{qid} 选项文本非空", all((o.get("text") or "").strip() for o in opts))
            ck(f"{qid} answer 在选项内", q.get("answer") in labels)
        else:
            ck(f"{qid} 非 choice 不带 options", not q.get("options"))
            ck(f"{qid} answer 非空", bool((q.get("answer") or "").strip()))
        ck(f"{qid} topicId 可解析", q.get("topicId") in want_topics)

    for tid, kind in want_topics.items():
        need = 5 if kind == "unit" else 8
        ck(f"{tid} 题量 {need}", per.get(tid, 0) >= need, per.get(tid, 0))

    diffs = {q.get("difficulty") for q in qs}
    ck("三档难度均出现", diffs == {"basic", "standard", "hard"}, sorted(diffs))
    ans = {}
    for q in qs:
        if q.get("type") == "choice":
            ans[q.get("answer")] = ans.get(q.get("answer"), 0) + 1
    n = sum(ans.values()) or 1
    ck("答案位均衡（单字母 ≤40%）", all(v / n <= 0.40 for v in ans.values()), ans)
    ids = [q.get("id") for q in qs]
    ck("题目 id 唯一", len(set(ids)) == len(ids))

    print(f"{sh['shard']} {sh['label']}：单元 {sum(1 for v in want_topics.values() if v=='unit')} + "
          f"课时 {sum(1 for v in want_topics.values() if v=='lesson')} = {len(want_topics)} 点；题 {len(qs)} 道")
    print("类型:", {t: sum(1 for q in qs if q.get('type') == t) for t in ('choice', 'fill', 'short-answer')})
    print("难度:", {d: sum(1 for q in qs if q.get('difficulty') == d) for d in ('basic', 'standard', 'hard')})
    print("答案分布:", ans)
    if fails:
        print(f"\n❌ {len(fails)} 项未通过（前 25）:")
        for f in fails[:25]:
            print("  -", f)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
