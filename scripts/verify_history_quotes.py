# -*- coding: utf-8 -*-
"""历史学层「课本原文」引文回表校验（只读）。

对 `## 二、课本原文` 节里的每个 `> ` 引用块，判定它是否逐字出现在该册教材 txt 中
（九下无教材源时，退回比对该课 standards[].quote）。规范化口径与 check_history_learn.py 一致：去空白与标点。

用法：python3 scripts/verify_history_quotes.py <part.json | 册.json>
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_DIRS = [os.path.join(REPO, "data", "history", "_text"),
            os.path.expanduser("~/Desktop/学科图谱相关资料/历史_教材文本")]
PUNCT = "，。；：、？！“”‘’（）《》〈〉—…·,.;:?!\"'()<>[]{} \t\r\n\u3000"


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", str(s)))


def qnorm(s):
    s = str(s)
    for ch in PUNCT:
        s = s.replace(ch, "")
    return s


def lessons_of(obj):
    if isinstance(obj, dict) and isinstance(obj.get("lessons"), list):
        return obj["lessons"]
    if isinstance(obj, dict) and obj.get("markdown"):
        return [obj]
    return []


def quotes_of(md):
    m = re.search(r"##\s*二、课本原文(.*?)(?=\n##\s)", md, re.S)
    body = m.group(1) if m else md
    out = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith(">"):
            q = line.lstrip(">").strip()
            if han(q) >= 8:
                out.append(q)
    return out


def std_quotes(topic_id):
    p = os.path.join(REPO, "data", "history", "topics.json")
    try:
        T = {t["id"]: t for t in json.load(open(p, encoding="utf-8"))}
    except Exception:
        return []
    return [s.get("quote", "") for s in (T.get(topic_id, {}).get("standards") or [])]


def main():
    path = sys.argv[1]
    obj = json.load(open(path, encoding="utf-8"))
    bad = 0
    checked = 0
    for l in lessons_of(obj):
        book = l.get("book") or obj.get("book")
        src = ""
        for d in TXT_DIRS:
            p = os.path.join(d, f"{book}.txt")
            if os.path.exists(p):
                src = qnorm(open(p, encoding="utf-8").read())
                break
        sq = [qnorm(x) for x in std_quotes(l.get("topicId")) if x]
        standards = "".join(sq)
        for q in quotes_of(l.get("markdown", "")):
            checked += 1
            nq = qnorm(q)
            in_txt = bool(src) and nq in src
            in_std = bool(standards) and (nq in standards or any(s in nq for s in sq if len(s) >= 10))
            ok = in_txt or in_std
            if not ok:
                bad += 1
                print(f"  - {book} / {l.get('topicId')}: 引文未回表 → {q[:34]}…")
    print(f"共 {len(lessons_of(obj))} 篇 · 引文 {checked} 处 · 失配 {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
