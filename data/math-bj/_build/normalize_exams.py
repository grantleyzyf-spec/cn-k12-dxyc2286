# -*- coding: utf-8 -*-
"""把 80 份单元卷的 卷名 / examId / itemId 统一到口径（父代归一，不重写题目内容）。

口径：
  卷名  小学 `第X单元测试卷.json`；初中 `第X章 <章名> 测试卷.json`
  examId `mbj_exam_g<年级><a|b>_u<两位单元号>`（a=上册 b=下册）
  itemId `<examId>_q<两位题号>`

用法: python3 normalize_exams.py [--write]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(os.path.dirname(HERE), "exams")
CN = "一二三四五六七八九十"


def cn2int(s):
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1 if len(s) > 1 else 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1 if s in CN else None


def main():
    write = "--write" in sys.argv
    rows = []
    for book in sorted(os.listdir(EX)):
        d = os.path.join(EX, book)
        if not os.path.isdir(d):
            continue
        g = cn2int(re.match(r"([一二三四五六七八九])年级", book).group(1))
        sem = "a" if book.endswith("上册") else "b"
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"):
                print("  ⚠ 非 json 文件：", book, f)
                continue
            p = os.path.join(d, f)
            ex = json.load(open(p, encoding="utf-8"))
            scope = ex.get("scope") or []
            kind = ex.get("kind")
            if kind in ("mid", "midterm", "fin", "final"):
                # 期中/期末：paper = 期中测试卷A/B、期末测试卷A/B；examId 后缀 mid_a/mid_b/fin_a/fin_b
                cur = (ex.get("paper") or f[:-5])
                # A/B 判定要能吃多种命名：期中测试卷B / …_mid_b / …B.json / B卷
                ab = "b" if re.search(r"(_mid_b|_fin_b|测试卷\s*B|B卷|[Bb]\.json$|[Bb]$)", cur) else "a"
                base = "期中" if kind in ("mid", "midterm") else "期末"
                paper = f"{base}测试卷{'A' if ab == 'a' else 'B'}"
                exam_id = f"mbj_exam_g{g}{sem}_{base == '期末' and 'fin' or 'mid'}_{ab}"
            else:
                m = re.match(r"第([一二三四五六七八九十]+)(单元|章)\s*(.*)$", scope[0] if scope else "")
                if not m:
                    print("  ⚠ 无法解析 scope：", book, f, scope[:1])
                    continue
                no = cn2int(m.group(1))
                kindw, name = m.group(2), m.group(3).strip()
                paper = f"第{m.group(1)}单元测试卷" if kindw == "单元" else f"第{m.group(1)}章 {name} 测试卷"
                exam_id = f"mbj_exam_g{g}{sem}_u{no:02d}"
            old_id = ex.get("examId")
            ex["paper"] = paper
            ex["examId"] = exam_id
            n = 0
            for sec in ex.get("sections") or []:
                for it in sec.get("items") or []:
                    it["itemId"] = f"{exam_id}_q{int(it.get('no') or 0):02d}"
                    n += 1
            new_p = os.path.join(d, paper + ".json")
            rows.append((book, f, paper + ".json", old_id, exam_id, n))
            if write:
                json.dump(ex, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                if os.path.abspath(new_p) != os.path.abspath(p):
                    os.replace(p, new_p)
    for r in rows:
        flag = "" if r[1] == r[2] else f"  ← {r[1]}"
        print(f"  {r[0]:6s} {r[2]:28s} {r[4]:22s} 题{r[5]:3d}{flag}")
    print("卷数", len(rows), "| 改卷名", sum(1 for r in rows if r[1] != r[2]),
          "| 改 examId", sum(1 for r in rows if r[3] != r[4]))
    if not write:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
