# -*- coding: utf-8 -*-
"""分片自检（子代必须跑到末行 PASS）。用法: python3 check_bank.py S01"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(os.path.dirname(HERE), "_bank")


def main():
    shard = sys.argv[1]
    src = json.load(open(os.path.join(HERE, f"{shard}.json"), encoding="utf-8"))
    path = os.path.join(BANK, f"{shard}.json")
    if not os.path.exists(path):
        print(f"FAIL 缺产物 {path}")
        sys.exit(1)
    bank = json.load(open(path, encoding="utf-8"))
    pts = {p["id"]: p for p in src["points"]}
    cands = {c["id"]: c["quote"] for c in src.get("std_candidates", [])}
    got = {}
    for row in bank.get("points", []):
        got[row.get("topicId")] = row
    errs = []
    if set(got) != set(pts):
        errs.append(f"点数不符：产出 {len(got)} / 应有 {len(pts)}；缺 {sorted(set(pts) - set(got))[:3]} 多 {sorted(set(got) - set(pts))[:3]}")
    qs = []
    answer_pos = Counter()
    for tid, p in pts.items():
        r = got.get(tid)
        if not r:
            continue
        d = r.get("description") or ""
        if not (40 <= len(d) <= 160):
            errs.append(f"{tid} description 长度 {len(d)}")
        mc = r.get("mastery_criteria") or []
        if not (1 <= len(mc) <= 3) or any(len(x) > 60 for x in mc):
            errs.append(f"{tid} mastery_criteria 条数/长度不合规：{len(mc)}")
        mis = r.get("misconceptions") or []
        if not (2 <= len(mis) <= 3) or any(len(x) > 50 for x in mis):
            errs.append(f"{tid} misconceptions 应为 2–3 条且 ≤50 字：{len(mis)}")
        st = r.get("std")
        if st:
            if st.get("id") not in cands:
                errs.append(f"{tid} std.id 不在候选集：{st.get('id')}")
            elif st.get("quote") != cands[st["id"]]:
                errs.append(f"{tid} std.quote 与候选项不一致")
        need = 5 if p["level"] == "unit" else 8
        rq = r.get("questions") or []
        if len(rq) != need:
            errs.append(f"{tid}({p['level']}) 题量 {len(rq)}，应 {need}")
        diffs = Counter(x.get("difficulty") for x in rq)
        if set(diffs) != {"basic", "standard", "hard"}:
            errs.append(f"{tid} 难度未三档齐：{dict(diffs)}")
        prompts = set()
        for i, q in enumerate(rq, 1):
            qid = q.get("id", "")
            if qid != f"{tid}_q{i}":
                errs.append(f"{tid} 题 id 应为 {tid}_q{i}，实为 {qid}")
            if q.get("topicId") != tid:
                errs.append(f"{qid} topicId 不符")
            if q.get("subject") != "math-bj":
                errs.append(f"{qid} subject 应为 math-bj")
            pr = q.get("prompt") or ""
            if len(pr) < 12:
                errs.append(f"{qid} 题干 <12 字")
            if pr in prompts:
                errs.append(f"{qid} 同点题干重复")
            prompts.add(pr)
            if q.get("question") != pr:
                errs.append(f"{qid} question 与 prompt 不一致")
            if re.search(r"[$\\^]|以上都对|以上均对|与.{0,6}无关|仅在大学", pr):
                errs.append(f"{qid} 题干含禁用串/符号")
            tp = q.get("type")
            if tp not in ("choice", "numeric", "fill", "short-answer"):
                errs.append(f"{qid} type 非法 {tp}")
            if q.get("difficulty") not in ("basic", "standard", "hard"):
                errs.append(f"{qid} difficulty 非法 {q.get('difficulty')}")
            if len(q.get("explanation") or "") < 20:
                errs.append(f"{qid} explanation <20 字")
            if tp == "choice":
                opts = q.get("options") or []
                labels = [o.get("label") for o in opts]
                if len(opts) != 4 or labels != ["A", "B", "C", "D"]:
                    errs.append(f"{qid} 选项应为 A–D 四项")
                if q.get("answer") not in labels:
                    errs.append(f"{qid} answer 不在选项内")
                answer_pos[q.get("answer")] += 1
                texts = [o.get("text") or "" for o in opts]
                if any(not t.strip() for t in texts) or len(set(texts)) != 4:
                    errs.append(f"{qid} 选项文本为空或重复")
                for t in texts:
                    if re.search(r"仅在大学|不属于.{0,6}课程|与.{0,6}无关|不会考", t):
                        errs.append(f"{qid} 干扰项为凑数串：{t[:12]}")
            elif tp == "numeric":
                v = q.get("verify")
                if not v:
                    errs.append(f"{qid} numeric 缺 verify")
                else:
                    try:
                        val = eval(v, {"__builtins__": {}}, {})
                        if abs(float(val) - float(str(q.get("answer")).strip())) > 1e-6:
                            errs.append(f"{qid} verify={v}→{val} 与 answer={q.get('answer')} 不等")
                    except Exception as e:
                        errs.append(f"{qid} verify 不可求值：{v} ({e})")
            elif tp == "short-answer":
                if len(str(q.get("answer") or "")) < 30:
                    errs.append(f"{qid} short-answer 参考答案 <30 字")
            qs.append(q)
    if answer_pos and max(answer_pos.values()) > 0:
        for lab in "ABCD":
            if answer_pos.get(lab, 0) < 2:
                errs.append(f"选择题答案位 {lab} 不足 2 次：{dict(answer_pos)}")
    if errs:
        print(f"FAIL {shard}：{len(errs)} 处")
        for e in errs[:40]:
            print("  -", e)
        sys.exit(1)
    print(f"  points={len(pts)} q={len(qs)} type={dict(Counter(x['type'] for x in qs))} "
          f"diff={dict(Counter(x['difficulty'] for x in qs))} std={sum(1 for r in got.values() if r.get('std'))}")
    print(f"PASS {shard}")


if __name__ == "__main__":
    main()
