# -*- coding: utf-8 -*-
"""合并历史题库分片（补点 + 补题）到 topics/questions/dependencies。

用法：
  python3 scripts/merge_history_bank.py            # 预演：只校验分片并打印将写入的内容
  python3 scripts/merge_history_bank.py --write    # 落盘（原子替换）

纪律：
  · 分片校验任何一条不过 ⇒ 整批拒绝写入（不写半份）
  · 新点的 `standards` 不从工人处取，由父代从「同单元已有点」借用（confidence 降为 partial）——
    quote 必须是已在库里的原文片段，保证 `test_history.py` 的逐字回表仍 100%
  · 新点先修边：插在同单元最后一个已有点之后，并把原有的「E→后继」边改挂到新链末端；无已有点的单元挂前一单元末点
  · `dependencies.json` 是派生件：由 `topics.prerequisites` 重建（保留原有 soft 边）
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "history")
SH = os.path.join(D, "_bank_shards")
HAN = re.compile(r"[\u4e00-\u9fa5]")
BAN = ("以上都不对", "以上都对", "以上都可以", "都不正确", "都正确", "无法确定")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def han(s):
    return len(HAN.findall(s or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    topics = load(os.path.join(D, "topics.json"))
    questions = load(os.path.join(D, "questions.json"))
    deps = load(os.path.join(D, "dependencies.json"))
    soft = {(e["from"], e["to"]) for e in deps if e.get("type") == "soft"}
    T = {t["id"]: t for t in topics}

    errs, warns = [], []
    new_topics, new_questions = [], []
    files = sorted(f for f in os.listdir(SH) if re.fullmatch(r"H\d+\.json", f))
    if not files:
        print("⛔ 没有作业单（HNN.json）")
        return 1

    for fn in files:
        shard = load(os.path.join(SH, fn))
        # 工位按合同写的是 `HNN_out.json`；作业单里的 out 字段曾误写成 HNN.json 本身（生成器 bug，已修），
        # 这里以 `_out.json` 为准、找不到才回落到作业单字段。
        out_p = os.path.join(SH, f"{shard['shard']}_out.json")
        if not os.path.exists(out_p):
            out_p = shard["out"]
        if not os.path.exists(out_p):
            errs.append(f"{shard['shard']}: 缺产物 {out_p}")
            continue
        out = load(out_p)
        if isinstance(out, list):          # 部分工位按 checker 的 --shard 形状直接写了题目数组
            out = {"shard": shard["shard"], "topics": [], "questions": out}
        # ---- 题目 ----
        got = {q.get("id"): q for q in out.get("questions") or []}
        for p in shard["points"]:
            for slot in p["questions"]:
                q = got.get(slot["qid"])
                if not q:
                    errs.append(f"{slot['qid']}: 缺失（{p['name']}）")
                    continue
                if q.get("topicId") != p["topicId"]:
                    errs.append(f"{slot['qid']}: topicId 应为 {p['topicId']}，实为 {q.get('topicId')}")
                if q.get("type") != "choice":
                    errs.append(f"{slot['qid']}: 只收 choice，实为 {q.get('type')}")
                if q.get("answer") != slot["label"]:
                    errs.append(f"{slot['qid']}: 答案位应为 {slot['label']}，实为 {q.get('answer')}")
                opts = q.get("options") or []
                if len(opts) != 4:
                    errs.append(f"{slot['qid']}: 选项 {len(opts)} 个")
                texts = [(o.get("text") or "").strip() for o in opts]
                if len(set(texts)) != len(texts):
                    errs.append(f"{slot['qid']}: 选项文本重复")
                if any(b in t for t in texts for b in BAN):
                    errs.append(f"{slot['qid']}: 出现凑数/无法确定选项")
                if len(q.get("prompt") or "") < 12:
                    errs.append(f"{slot['qid']}: 题干不足 12 字")
                if q.get("question") != q.get("prompt"):
                    warns.append(f"{slot['qid']}: question 别名与 prompt 不同，已统一")
                if han(q.get("explanation")) < 25:
                    errs.append(f"{slot['qid']}: 解析不足 25 汉字（{han(q.get('explanation'))}）")
                if q.get("difficulty") not in ("basic", "standard", "hard"):
                    errs.append(f"{slot['qid']}: difficulty 非法 {q.get('difficulty')}")
                q["question"] = q.get("prompt")
                new_questions.append(q)
        # ---- 新点内容 ----
        tnew = {t.get("id"): t for t in out.get("topics") or []}
        for p in shard["points"]:
            if not p["isNew"]:
                continue
            t = tnew.get(p["topicId"])
            if not t:
                errs.append(f"{p['topicId']}: 新点缺 topics 条目（{p['name']}）")
                continue
            if han(t.get("description")) < 40 or han(t.get("description")) > 120:
                errs.append(f"{p['topicId']}: description {han(t.get('description'))} 汉字（要 40–120）")
            mc = t.get("mastery_criteria") or []
            if not (1 <= len(mc) <= 3):
                errs.append(f"{p['topicId']}: mastery_criteria {len(mc)} 条（要 1–3）")
            if any(han(x) > 50 or han(x) < 8 for x in mc):
                errs.append(f"{p['topicId']}: mastery_criteria 单条字数越界")
            if t.get("type") not in ("conceptual", "procedural", "reasoning", "modeling", "application"):
                errs.append(f"{p['topicId']}: type 非法 {t.get('type')}")
            new_topics.append({"pid": p["topicId"], "shard": shard["shard"], "data": t,
                               "meta": {k: p[k] for k in ("name", "chapter", "domain", "grade", "semester", "book")}})

    if errs:
        print(f"❌ 分片校验 {len(errs)} 项不合格（整批不写入）：")
        for e in errs[:30]:
            print("  -", e)
        if len(errs) > 30:
            print(f"  …… 另有 {len(errs)-30} 项")
        return 1

    # ---- 组新点记录（借课标）----
    sk_plan = load(os.path.join(D, "_toc", "_gap_plan.json"))
    sk = {p["id"]: p for p in load(os.path.join(D, "_skeleton.json"))["points"]}
    by_chapter = defaultdict(list)
    for t in topics:
        by_chapter[t["chapter"]].append(t)
    # 每册的章节顺序（按骨架 lessonNo）
    chapter_seq = []
    for p in sk.values():
        if p["chapter"] not in chapter_seq:
            chapter_seq.append(p["chapter"])

    def borrow_std(chap):
        for t in by_chapter.get(chap, []):
            if t.get("standards"):
                return [dict(s, confidence="partial") for s in t["standards"]]
        i = chapter_seq.index(chap)
        for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(chapter_seq))):
            for t in by_chapter.get(chapter_seq[j], []):
                if t.get("standards"):
                    return [dict(s, confidence="inferred") for s in t["standards"]]
        return []

    added = []
    for nt in new_topics:
        m, d = nt["meta"], nt["data"]
        std = borrow_std(m["chapter"])
        if not std:
            print(f"⛔ {nt['pid']} 借不到课标引文（chapter={m['chapter']}），整批中止")
            return 1
        added.append({
            "id": nt["pid"], "name": sk[nt["pid"]]["name"], "subject": "history",
            "domain": m["domain"], "grade": m["grade"], "semester": m["semester"],
            "chapter": m["chapter"], "type": d["type"], "description": d["description"],
            "mastery_criteria": d["mastery_criteria"],
            "diagnostic_question": d.get("diagnostic_question") or {"question": "", "answer": ""},
            "external": False, "standards": std, "tags": [m["domain"], sk[nt["pid"]]["chapter"].split("单元")[-1].strip()],
            "prerequisites": [], "curriculumRef": std[0]["id"], "verified": False,
        })

    # ---- 先修边：插在同单元末点之后 ----
    for nt in added:
        chap = nt["chapter"]
        peers = [t for t in topics if t["chapter"] == chap]
        if peers:
            last = peers[-1]
            prev_chain_tail = last["id"]
        else:
            i = chapter_seq.index(chap)
            prev_chain_tail = None
            for j in range(i - 1, -1, -1):
                cands = [t for t in topics if t["chapter"] == chapter_seq[j]]
                if cands:
                    prev_chain_tail = cands[-1]["id"]
                    break
        nt["prerequisites"] = [prev_chain_tail] if prev_chain_tail else []
        if not nt["prerequisites"]:
            nt["root_reason"] = f"起始知识点：{nt['chapter']} 在教材中是本册开篇内容，图谱内无更早前置。"
        # 把原「上一末点 → 后继」的边改挂到本链末端
        topics.append(nt)                       # 让后续新点能找到同单元末点
        if prev_chain_tail:
            T[nt["id"]] = nt
            for e in deps:
                if e["from"] == prev_chain_tail and e.get("type") == "hard" and e["to"] in T \
                        and T[e["to"]].get("chapter") != chap:
                    e["from"] = nt["id"]
                    old = T[e["to"]].get("prerequisites") or []
                    T[e["to"]]["prerequisites"] = [nt["id"] if x == prev_chain_tail else x for x in old]

    # ---- 落盘顺序：教材序（同章内新点在末） ----
    order = {t["id"]: i for i, t in enumerate(topics)}
    topics.sort(key=lambda t: order[t["id"]])

    # ---- 重建 dependencies ----
    pairs = []
    for t in topics:
        for p in t.get("prerequisites") or []:
            if p in {x["id"] for x in topics}:
                pairs.append((p, t["id"]))
    edges = [{"from": a, "to": b, "type": "hard"} for a, b in dict.fromkeys(pairs)]
    have = {(e["from"], e["to"]) for e in edges}
    for a_, b_ in soft:
        if (a_, b_) not in have and a_ in {t["id"] for t in topics} and b_ in {t["id"] for t in topics}:
            edges.append({"from": a_, "to": b_, "type": "soft"})

    # ---- 合并题目（按 topics 序） ----
    qids = {q["id"] for q in questions}
    dup = [q["id"] for q in new_questions if q["id"] in qids]
    if dup:
        print(f"❌ 题目 id 撞库：{dup[:5]}")
        return 1
    allq = questions + new_questions
    pos = {t["id"]: i for i, t in enumerate(topics)}
    allq.sort(key=lambda q: (pos.get(q["topicId"], 99999), q["id"]))

    print(f"新点 {len(added)}｜新题 {len(new_questions)}｜题合计 {len(allq)}｜点合计 {len(topics)}｜边 {len(edges)}")
    print(f"答案位分布（新题）：{dict(Counter(q['answer'] for q in new_questions))}")
    if warns:
        print(f"（提示 {len(warns)} 条，如 {warns[:3]}）")

    if not a.write:
        print("\n（预演：未写盘；加 --write 落盘）")
        return 0

    for name, obj in (("topics.json", topics), ("questions.json", allq), ("dependencies.json", edges)):
        p = os.path.join(D, name)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
    print("✅ 已落盘 topics/questions/dependencies（原子替换）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
