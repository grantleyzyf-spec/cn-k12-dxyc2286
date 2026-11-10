# -*- coding: utf-8 -*-
"""讲解·答案面锚定自检：每个题块是不是真在讲卷面这一题（答案面判据）。

为什么要有这一条：`check_math_*_lecture.py` 只查结构、字数、题号覆盖、题分一致；
`verify_lecture_alignment.py` 查整篇与卷的用词重合（二元字组），都是**文档级**判据。
同册换卷、题号错位、讲的是另一题，这两条都可能全绿。本脚本按**题**核一遍答案面。

判据
  A 题块定位：卷内每个题号必须有且仅有一个题块（`**第 N 题（X 分）**` 与
    `### 第 N 题（X 分）` 两种写法都认）；缺块/重块 → 硬错
  B 题分一致：题块标题里的「N 分」必须等于卷面 score；不等 → 硬错
  C 结论冲突：题块里出现结论性写法「对应选项 X / 故选 X / 答案 X / 本题答案 X」时，
    X 必须等于卷面 answer；不等 → 硬错。只认结论性写法，
    不认「错项分析」「易错」里对干扰项的讨论（实测 962 处「选 X」几乎全是干扰项讨论）。
  D 答案面锚定（可疑项，不判死）：答案里 ≥2 位的数字 token 必须出现在题块内
    ——阿拉伯数字逐字命中，或等值中文数字（「七十二」）。选择题/多选题用**正确选项的文本**去比。
    0 命中记可疑，交人工；小学数学「八九七十二」、分式改写（4.06→406）、
    封闭题不落笔写答案值，都会落到这一类。

用法
    python3 scripts/verify_lecture_answer_anchor.py                      # 默认两桶
    python3 scripts/verify_lecture_answer_anchor.py --bucket math-sujiao
    python3 scripts/verify_lecture_answer_anchor.py --strict             # 可疑项非空时 rc=1
    python3 scripts/verify_lecture_answer_anchor.py --selftest
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.abspath(os.environ.get("REPO")
                       or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEFAULT_BUCKETS = ("math-sujiao", "math-suke")

HEAD = re.compile(r"^(?:\*\*|#{2,4}\s*)第\s*(\d+)\s*题[（(]\s*(\d+)\s*分[）)]", re.M)
CONCL = (
    r"对应选项\s*([A-D])",
    r"故选\s*([A-D])",
    r"答案\s*[:：是为]\s*([A-D])(?!\s*(?:本身|集合|中|与|和|项))",
    r"本题答案\s*[:：]?\s*([A-D])",
)
DIG = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
       "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
UNIT = {"十": 10, "百": 100, "千": 1000}


def han_num(s):
    """把「七十二」「三百零五」这类中文整数读成 int；不像数字就返回 None。"""
    total, cur, seen = 0, 0, False
    for ch in s:
        if ch in DIG:
            cur = DIG[ch]
            seen = True
        elif ch in UNIT:
            total += (cur if cur else 1) * UNIT[ch]
            cur = 0
            seen = True
        else:
            return None
    return total + cur if seen else None


def cn_forms(i):
    """int -> 可能的中文写法集合（七十二 / 一百零五）。"""
    ds = "零一二三四五六七八九"
    if i < 10:
        return {ds[i]}
    out = set()
    if i < 20:
        out.add("十" + (ds[i % 10] if i % 10 else ""))
    if i < 100:
        out.add(ds[i // 10] + "十" + (ds[i % 10] if i % 10 else ""))
    if 100 <= i < 1000:
        a, r = divmod(i, 100)
        s = ds[a] + "百"
        if r == 0:
            out.add(s)
        elif r < 10:
            out.add(s + "零" + ds[r])
        else:
            b, c = divmod(r, 10)
            out.add(s + (ds[b] + "十" + (ds[c] if c else "")))
    return out


def digitstr(s):
    return re.sub(r"\D", "", s)


def block_has(block, num):
    """题块里是否出现了这个数值（阿拉伯逐字 / 去小数点 / 中文数字）。"""
    d = digitstr(block)
    for form in {digitstr(num), num.replace(".", "")}:
        if form and len(form) >= 2 and form in d:
            return True
    try:
        v = float(num)
    except ValueError:
        return False
    if v == int(v) and 0 < int(v) < 1000:
        return any(c in block for c in cn_forms(int(v)))
    return False


def blocks_of(md):
    ms = list(HEAD.finditer(md))
    out = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(md)
        out.setdefault(int(m.group(1)), []).append((int(m.group(2)), md[m.start():end]))
    return out


def check_pair(paper, lecture):
    """返回 (hard, suspects, stats)。hard/suspects 都是 [(判据, 题号, 说明)]。"""
    hard, sus = [], []
    stats = {"题": 0, "题块": 0, "锚定成功": 0, "无可锚答案": 0, "重复题块": 0}
    md = lecture.get("markdown", "")
    bs = blocks_of(md)
    items = [it for s in paper["sections"] for it in s["items"]]
    for it in items:
        stats["题"] += 1
        n = it["no"]
        cand = bs.get(n)
        if not cand:
            hard.append(("A 缺题块", n, "讲解里找不到第 %d 题" % n))
            continue
        if len(cand) > 1:
            stats["重复题块"] += 1
            hard.append(("A 重复题块", n, "第 %d 题出现 %d 个题块" % (n, len(cand))))
        score, text = cand[0]
        stats["题块"] += 1
        if score != it["score"]:
            hard.append(("B 题分", n, "题块写 %d 分，卷面 %d 分" % (score, it["score"])))
        ans = str(it.get("answer", "")).strip()
        if it["type"] == "choice":
            for pat in CONCL:
                for m in re.finditer(pat, text):
                    if m.group(1) != ans:
                        hard.append(("C 结论冲突", n, "题块写「%s」，卷面答案 %s"
                                     % (m.group(0), ans)))
        if it["type"] in ("choice", "multi"):
            letters = re.findall(r"[A-D]", ans.replace(" ", ""))
            src = " ".join(o["text"] for o in it.get("options", []) if o["label"] in letters)
        else:
            src = ans
        toks = [t for t in re.findall(r"\d+(?:\.\d+)?", src) if len(digitstr(t)) >= 2]
        if not toks:
            stats["无可锚答案"] += 1
            continue
        if any(block_has(text, t) for t in toks):
            stats["锚定成功"] += 1
        else:
            sus.append(("D 答案面", n, "答案里的 %s 在题块里找不到 / 选项「%s」"
                        % ("、".join(toks[:3]), src[:36])))
    return hard, sus, stats


def run(buckets, strict=False, quiet=False):
    tot = {"讲解": 0, "题": 0, "锚定成功": 0, "无可锚答案": 0, "重复题块": 0}
    hard_all, sus_all = [], []
    for bk in buckets:
        lfs = sorted(glob.glob(os.path.join(REPO, "data", bk, "exam_lectures", "*", "*.json")))
        lfs = [f for f in lfs if "_stale" not in f]
        for lf in lfs:
            lec = json.load(open(lf, encoding="utf-8"))
            pf = os.path.join(REPO, "data", bk, "exams", lec["book"], lec["paper"] + ".json")
            if not os.path.exists(pf):
                hard_all.append(("E 无卷", "-", lf.replace(REPO + "/", "")))
                continue
            paper = json.load(open(pf, encoding="utf-8"))
            hard, sus, st = check_pair(paper, lec)
            tot["讲解"] += 1
            for k in ("题", "锚定成功", "无可锚答案", "重复题块"):
                tot[k] += st[k]
            rel = lf.replace(REPO + "/data/", "")
            for h in hard:
                hard_all.append((h[0], h[1], rel + "｜" + h[2]))
            for s in sus:
                sus_all.append((s[0], s[1], rel + "｜" + s[2]))
    print("讲解 %(讲解)d 份｜题 %(题)d｜答案面锚定成功 %(锚定成功)d｜无可锚答案 %(无可锚答案)d"
          "｜重复题块 %(重复题块)d" % tot)
    print("硬错 %d｜可疑 %d" % (len(hard_all), len(sus_all)))
    if not quiet:
        for tag, rows in (("硬错", hard_all), ("可疑", sus_all)):
            for r in rows:
                print("  [%s] %s｜第 %s 题｜%s" % (tag, r[0], r[1], r[2]))
    rc = 1 if hard_all or (strict and sus_all) else 0
    return rc, hard_all, sus_all, tot


def selftest():
    paper = {"sections": [{"items": [
        {"no": 1, "score": 5, "type": "choice", "stem": "已知 A={2,4}，补集是（　）",
         "options": [{"label": "A", "text": "{2,4}"}, {"label": "B", "text": "{1,3}"}],
         "answer": "B"},
        {"no": 2, "score": 5, "type": "fill", "stem": "9×8＝（　）", "answer": "72"},
        {"no": 3, "score": 12, "type": "solve", "stem": "求 4.06×1.5", "answer": "6.09；6.1"},
    ]}]}
    good = {"markdown": "**第 1 题（5 分）**\n划掉 2 与 4，补集为 {1,3}，对应选项 B。\n"
                        "**第 2 题（5 分）**\n八九七十二，所以是 72。\n"
                        "**第 3 题（12 分）**\n406×15＝6090，三位小数得 6.09。"}
    bad = {"markdown": "**第 1 题（5 分）**\n对应选项 A。\n"
                       "**第 2 题（10 分）**\n六七四十二。\n"
                       "**第 3 题（12 分）**\n完全不相干的一段话。"}
    cases = []
    h, s, st = check_pair(paper, good)
    cases.append(("正常件零硬错零可疑", not h and not s))
    h, s, st = check_pair(paper, bad)
    cases.append(("错误件报结论冲突", any(x[0].startswith("C") for x in h)))
    cases.append(("错误件报题分", any(x[0].startswith("B") for x in h)))
    cases.append(("错误件报答案面", any(x[0].startswith("D") for x in s)))
    cases.append(("中文数字可读", han_num("七十二") == 72 and han_num("一百零五") == 105))
    cases.append(("缺题块可报", any(x[0].startswith("A")
                                 for x in check_pair(paper, {"markdown": ""})[0])))
    ok = sum(1 for _, v in cases if v)
    for name, v in cases:
        print(("  PASS  " if v else "  FAIL  ") + name)
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", action="append", default=None)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--repo", default=None, help="仓库根（默认本脚本上一级）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.repo:
        global REPO
        REPO = os.path.abspath(a.repo)
    if a.selftest:
        return selftest()
    rc, _, _, _ = run(a.bucket or DEFAULT_BUCKETS, a.strict, a.quiet)
    return rc


if __name__ == "__main__":
    sys.exit(main())
