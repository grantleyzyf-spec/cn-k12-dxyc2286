# -*- coding: utf-8 -*-
"""单册 ke_json 自检器（写工位的人必须自己跑过再交）。

只读检查，不写数据仓库。用法：
    python3 scripts/check_math_ke_json.py data/math/ke_json/一年级上册.json

检查项（任一不过即 exit 1）：
  1 结构：book 在册次表内；keshi 每条 name/unit/unit_name/domain/type/description/mastery_criteria/tags/standards/questions
  2 课标：standards 至少 1 条，id 必须出现在 docs/math-std-quotes.md 的**本册**小节，
          quote 与该表逐字一致，sourceLine 一致（构造上保证 quote 回表命中）
  3 题量：每课时恰好 5 题，且题型为 2 choice + 1 fill + 1 numeric + 1 short-answer
  4 题干 ≥12 字、解析 ≥20 字、难度 ∈ {basic,standard,hard}
  5 选择题：4 个选项、label A–D 齐、选项文本互不相同、answer 在 label 内
  6 numeric：verify 存在且 eval(verify) == float(answer)，误差 ≤1e-6
  7 short-answer：keypoints ≥2 条，每条 ≥4 字
  8 去重：题干在**全库 questions.json** 与本文件内都不重复（去空白后比较）
  9 选项答案不偏置：本册 choice 里任一 label 占比 ≤45%
"""
import json
import os
import re
import sys
from collections import Counter

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
QUOTES = f"{REPO}/docs/math-std-quotes.md"
BOOKS = {"一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
         "四年级上册", "四年级下册", "五年级上册", "五年级下册", "六年级上册", "六年级下册",
         "七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册", "九年级下册",
         "必修第一册", "必修第二册", "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"}
DOMAINS = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}
TYPES = {"choice", "fill", "numeric", "short-answer"}
errs, warns = [], []


def E(msg):
    errs.append(msg)


def load_quotes():
    """→ {册: {(id, quote): sourceLine}}"""
    out, cur = {}, None
    sec = {}
    for ln in open(QUOTES, encoding="utf-8"):
        s = ln.rstrip("\n")
        if s.startswith("## "):
            cur = s[3:].strip()
            out[cur] = []
            sec = {}
            continue
        m = re.match(r"- `([^`]+)` · sourceLine (\d+)", s)
        if m and cur:
            sec["id"], sec["line"] = m.group(1), int(m.group(2))
            continue
        if s.strip().startswith("> ") and cur and sec:
            out[cur].append((sec["id"], s.strip()[2:].strip(), sec["line"]))
            sec = {}
    return out


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not path or not os.path.exists(path):
        print("用法：python3 scripts/check_math_ke_json.py data/math/ke_json/<册>.json")
        sys.exit(1)
    spec = json.load(open(path, encoding="utf-8"))
    book = spec.get("book")
    if book not in BOOKS:
        E(f"book 不在册次表：{book}")
        book = None
    quotes = load_quotes()
    pool = {b: {(i, q): ln for i, q, ln in v} for b, v in quotes.items()}
    if book and book not in pool:
        E(f"docs/math-std-quotes.md 里没有本册小节：{book}")
    # 全库题干去重池：必须排除**本册自己的课时点**，否则已合并的册再自检时会自己撞自己
    # （chapter 形如「一年级上册 第一单元 X · 1～5的认识」的就是课时点）
    own_topics, other_topics = set(), set()
    tp = f"{REPO}/data/math/topics.json"
    if os.path.exists(tp) and book:
        for t in json.load(open(tp, encoding="utf-8")):
            ch = t.get("chapter") or ""
            (own_topics if (ch.startswith(book + " ") and " · " in ch) else other_topics).add(t["id"])
    glob_prompts = set()
    gp = f"{REPO}/data/math/questions.json"
    if os.path.exists(gp):
        for q in json.load(open(gp, encoding="utf-8")):
            if q.get("topicId") in own_topics:
                continue
            glob_prompts.add(norm(q.get("prompt")))
    seen = set()
    labels = Counter()
    kes = spec.get("keshi") or []
    if len(kes) < 1:
        E("keshi 为空")
    for ke in kes:
        nm = ke.get("name", "?")
        for k in ("name", "unit", "unit_name", "domain", "type", "description",
                  "mastery_criteria", "tags", "standards", "questions"):
            if not ke.get(k):
                E(f"{nm}: 缺字段 {k}")
        if ke.get("domain") not in DOMAINS:
            E(f"{nm}: domain 不是课标四领域：{ke.get('domain')}")
        if not (ke.get("tags") or [None])[0] == ke.get("domain"):
            E(f"{nm}: tags 首位必须＝domain")
        if "教材课时" not in (ke.get("tags") or []):
            E(f"{nm}: tags 必须含「教材课时」")
        if len(ke.get("description") or "") < 20:
            E(f"{nm}: description <20 字")
        if not (1 <= len(ke.get("mastery_criteria") or []) <= 3):
            E(f"{nm}: mastery_criteria 必须 1–3 条")
        st = ke.get("standards") or []
        ids = [x.get("id") for x in st]
        if len(set(ids)) != len(ids):
            E(f"{nm}: standards 里 id 重复 → {ids}（同一 id 引用两次等于没写第二条）")
        if not st:
            E(f"{nm}: 缺 standards")
        for s in st:
            key = (s.get("id"), (s.get("quote") or "").strip())
            table = pool.get(book, {}) if book else {}
            if key in table:
                if table[key] != s.get("sourceLine"):
                    E(f"{nm}: sourceLine 不符，应为 {table[key]}，实为 {s.get('sourceLine')}")
                continue
            # 允许「截断变体」：与表中同 id 的某条互为前缀（老数据里 quote 常在 30 字处被截断），
            # 但行号必须与该条一致，防止拿 A 条的行号配 B 条的文字
            cand = [(q, ln) for (i, q), ln in table.items()
                    if i == s.get("id") and (q.startswith(key[1]) or key[1].startswith(q))]
            if not cand:
                E(f"{nm}: 课标引用不在本册引用表内 → {s.get('id')} / {s.get('quote')}")
            elif not any(ln == s.get("sourceLine") for _q, ln in cand):
                E(f"{nm}: sourceLine 不符（截断变体应取 {[ln for _q, ln in cand]}），实为 {s.get('sourceLine')}")
            if s.get("confidence") not in ("exact", "partial", "inferred"):
                E(f"{nm}: confidence 只能用 exact/partial/inferred")
        qs = ke.get("questions") or []
        cnt = Counter(q.get("type") for q in qs)
        if len(qs) != 5:
            E(f"{nm}: 必须 5 题，实为 {len(qs)}")
        if cnt != Counter({"choice": 2, "numeric": 1, "fill": 1, "short-answer": 1}):
            E(f"{nm}: 题型配比应为 2 choice + 1 fill + 1 numeric + 1 short-answer，实为 {dict(cnt)}")
        for q in qs:
            qid = q.get("id") or f"{nm}/{q.get('type')}"
            p = q.get("prompt") or ""
            if q.get("type") not in TYPES:
                E(f"{qid}: type 非法 {q.get('type')}")
            if len(p) < 12:
                E(f"{qid}: 题干 <12 字 → {p}")
            if len(q.get("explanation") or "") < 20:
                E(f"{qid}: 解析 <20 字")
            if q.get("difficulty") not in ("basic", "standard", "hard"):
                E(f"{qid}: difficulty 非法")
            key = norm(p)
            if key in glob_prompts:
                E(f"{qid}: 题干与全库已有题重复 → {p[:30]}")
            if key in seen:
                E(f"{qid}: 本册内题干重复 → {p[:30]}")
            seen.add(key)
            if q.get("type") == "choice":
                opts = q.get("options") or []
                labs = [o.get("label") for o in opts]
                texts = [norm(o.get("text")) for o in opts]
                if len(opts) != 4 or labs != ["A", "B", "C", "D"]:
                    E(f"{qid}: 选项必须 4 个且 label 为 A–D，实为 {labs}")
                if len(set(texts)) != len(texts):
                    E(f"{qid}: 选项文本有重复")
                if q.get("answer") not in labs:
                    E(f"{qid}: answer 不在选项内")
                if any(not t for t in texts):
                    E(f"{qid}: 有选项文本为空")
                labels[q.get("answer")] += 1
            if q.get("type") == "numeric":
                v, a = q.get("verify"), q.get("answer")
                a0 = str(q.get("answer")).strip()
                vv = str(v or "").replace(" ", "")
                if v and (vv == a0 or vv in (f"1*{a0}", f"{a0}*1", f"0+{a0}", f"{a0}+0", f"1*{a0}+0")):
                    E(f"{qid}: verify={v} 是把答案抄了一遍（伪 verify），必须写成能独立复算的表达式（计数题可用 len([...])）")
                if not v:
                    E(f"{qid}: numeric 缺 verify")
                else:
                    try:
                        if abs(eval(str(v)) - float(a)) > 1e-6:
                            E(f"{qid}: verify={v} 与 answer={a} 不符")
                    except Exception as ex:
                        E(f"{qid}: verify 不可求值（{ex}）")
            if q.get("type") == "short-answer":
                kp = q.get("keypoints") or []
                if len(kp) < 2:
                    E(f"{qid}: keypoints 需 ≥2 条")
                if any(len(norm(k)) < 4 for k in kp):
                    E(f"{qid}: keypoints 每条需 ≥4 字")
    tot = sum(labels.values())
    if tot:
        for lb, c in labels.items():
            if c > tot * 0.45:
                E(f"本册答案偏置：{lb} 占 {c}/{tot}（>45%）")
    print(f"册：{book} · 课时 {len(kes)} · 题 {len(kes)*5} · 选项分布 {dict(labels)}")
    for w in warns:
        print("  ⚠️ ", w)
    if errs:
        print(f"\n❌ {len(errs)} 条问题：")
        for e in errs[:40]:
            print("  -", e)
        if len(errs) > 40:
            print(f"  …另有 {len(errs)-40} 条")
        sys.exit(1)
    print("✅ 自检通过")


if __name__ == "__main__":
    main()
