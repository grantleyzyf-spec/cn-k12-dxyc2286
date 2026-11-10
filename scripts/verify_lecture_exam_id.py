#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲解↔现役卷「身份对齐」核验：examId 双向一一对应（元数据级，最便宜、最不容误报）。

为什么需要（2026-11-10 实抓）：
  · 苏教版必修第一册 8 份讲解仍是旧 examId（msj_exam_g10a_uN），现役卷已改成 msj_exam_b1_uN，
    且题面已换（旧讲解第 2 题讲「1<x≤4」、现役卷第 2 题是「x²<10」）⇒ 逐题精讲全错配；
  · 河北版一年级上册 10 份讲解根本没有 examId 字段 ⇒ 任何按 examId 归并的下游都看不见它们；
  · 湘教版 4 份讲解把 examId 写成 mxj_exam_exam_...（多一重 exam_，笔误）⇒ 查不到同名卷。
  这三类都不是「内容写得差」，是「讲解挂错了卷」，逐题对齐判据（verify_lecture_alignment.py）
  靠字面相似度，遇到同册换卷仍有 0.75~0.83 的重合度，可能放过；身份判据是精确判据，零误报。

判据（任一不满足即 FAIL，逐条打印到文件级）：
  A 每份讲解 examId 必填（非空字符串）；
  B 讲解 examId 必在同桶卷库中存在（无孤儿）；
  C 每卷必有讲解（无缺讲）；
  D 讲解 (book, paper) 必须能定位到同名现役卷，且该卷 examId 与讲解 examId 相同；
  E 卷侧 / 讲侧 examId 各自不重复。

用法：
  python3 scripts/verify_lecture_exam_id.py                # 全 12 版
  python3 scripts/verify_lecture_exam_id.py math-sujiao    # 单桶
  python3 scripts/verify_lecture_exam_id.py --selftest     # 合成夹具自检（杀伤力）
"""
import glob
import json
import os
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = ("苏教版", "苏科版", "人教版", "北师大版", "沪教版", "湘教版", "青岛版",
          "冀教版", "北京版", "河北版", "华东师大版", "统编版", "人教鄂教版", "北师大")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def find_exam(bucket, book, paper, root):
    """(book, paper) → 现役卷路径；容忍 book 带/不带版本前缀、paper 带/不带书名前缀。"""
    books = [book] + [book[len(p):] for p in PREFIX if book.startswith(p)]
    papers = [paper]
    for b in books:
        if paper.startswith(b + " "):
            papers.append(paper[len(b) + 1:])
    for b in books:
        for pp in papers:
            f = os.path.join(root, "data", bucket, "exams", b, pp + ".json")
            if os.path.exists(f):
                return f
    return None


def audit_bucket(bucket, root):
    """→ (计数 dict, 问题列表)"""
    ex, lec = {}, {}
    no_id, dup_ex, dup_le = [], [], []
    for f in sorted(glob.glob(os.path.join(root, "data", bucket, "exams", "*", "*.json"))):
        d = load(f)
        k = d.get("examId")
        if not k:
            no_id.append(("卷缺 examId", f))
            continue
        if k in ex:
            dup_ex.append((k, f, ex[k]))
        ex[k] = f
    for f in sorted(glob.glob(os.path.join(root, "data", bucket, "exam_lectures", "*", "*.json"))):
        if "_stale" in f:
            continue
        d = load(f)
        k = d.get("examId")
        if not k:
            no_id.append(("讲解缺 examId", f))
            continue
        if k in lec:
            dup_le.append((k, f, lec[k]))
        lec[k] = f
    probs = list(no_id)
    probs += [("卷 examId 重复", str(x)) for x in dup_ex]
    probs += [("讲解 examId 重复", str(x)) for x in dup_le]
    for k in sorted(set(lec) - set(ex)):
        probs.append(("孤儿讲解（examId 在卷库不存在）", lec[k]))
    for k in sorted(set(ex) - set(lec)):
        probs.append(("缺讲解（卷无对应讲解）", ex[k]))
    for k, f in sorted(lec.items()):
        d = load(f)
        ep = find_exam(bucket, str(d.get("book") or ""), str(d.get("paper") or ""), root)
        if not ep:
            probs.append(("讲解定位不到同名卷（book/paper 对不上）", f))
            continue
        eid = load(ep).get("examId")
        if eid != k:
            probs.append((f"讲解 examId 与同名卷不符：讲解 {k} / 卷 {eid}", f))
    st = {"exams": len(ex), "lectures": len(lec), "problems": len(probs)}
    return st, probs


def buckets(root):
    out = []
    for d in sorted(glob.glob(os.path.join(root, "data", "math*"))):
        if os.path.isdir(os.path.join(d, "exams")):
            out.append(os.path.basename(d))
    return out


def selftest():
    """合成夹具：4 类缺陷各 1 例 + 2 例正常，必须全抓、正常项不得误报。"""
    root = tempfile.mkdtemp(prefix="lecid")
    try:
        b = os.path.join(root, "data", "math-x")
        os.makedirs(os.path.join(b, "exams", "册A"))
        os.makedirs(os.path.join(b, "exam_lectures", "册A"))
        os.makedirs(os.path.join(b, "exam_lectures", "_stale"))

        def w(p, o):
            with open(p, "w", encoding="utf-8") as f:
                json.dump(o, f, ensure_ascii=False)

        # 正常：p1 对应正常
        w(os.path.join(b, "exams", "册A", "p1.json"), {"examId": "e1"})
        w(os.path.join(b, "exam_lectures", "册A", "p1.json"),
          {"examId": "e1", "book": "册A", "paper": "p1"})
        # A 缺陷：讲解缺 examId
        w(os.path.join(b, "exams", "册A", "p2.json"), {"examId": "e2"})
        w(os.path.join(b, "exam_lectures", "册A", "p2.json"), {"book": "册A", "paper": "p2"})
        # B 缺陷：孤儿讲解
        w(os.path.join(b, "exams", "册A", "p3.json"), {"examId": "e3"})
        w(os.path.join(b, "exam_lectures", "册A", "stale.json"),
          {"examId": "e_old", "book": "册A", "paper": "p3"})
        # C 缺陷：缺讲解
        w(os.path.join(b, "exams", "册A", "p4.json"), {"examId": "e4"})
        # D 缺陷：examId 与同名卷不符
        w(os.path.join(b, "exams", "册A", "p5.json"), {"examId": "e5"})
        w(os.path.join(b, "exam_lectures", "册A", "p5.json"),
          {"examId": "e_exam_exam_5", "book": "册A", "paper": "p5"})
        # 正常：book 带版本前缀、paper 带书名前缀都要能定位
        w(os.path.join(b, "exams", "册A", "p6.json"), {"examId": "e6"})
        w(os.path.join(b, "exams", "册A", "p6.json"), {"examId": "e6"})
        w(os.path.join(b, "exam_lectures", "册A", "p6.json"),
          {"examId": "e6", "book": "苏教版册A", "paper": "册A p6"})
        # _stale 里的讲解不得计入
        w(os.path.join(b, "exam_lectures", "_stale", "p1.json"),
          {"examId": "e1", "book": "册A", "paper": "p1"})

        st, probs = audit_bucket("math-x", root)
        kinds = {}
        for why, where in probs:
            key = why.split("：")[0]
            kinds[key] = kinds.get(key, 0) + 1
        # 夹具算账：e2 讲解缺 id ⇒ 既算「缺 examId」也算「卷 e2 缺讲解」；
        # e3 的讲解挂了 e_old ⇒ 孤儿 1 + 卷 e3 缺讲解；e4 无讲解；e5 讲解 id 笔误 ⇒ 孤儿 1 + 卷 e5 缺讲解。
        want = {"讲解缺 examId": 1, "孤儿讲解（examId 在卷库不存在）": 2,
                "缺讲解（卷无对应讲解）": 4, "讲解 examId 与同名卷不符": 2}
        ok = 0
        total = 0
        for k, v in want.items():
            total += 1
            hit = kinds.get(k, 0) == v
            ok += hit
            print(("✅" if hit else "❌") + f" 抓 {k} 期望 {v} 实得 {kinds.get(k, 0)}")
        total += 1
        clean = kinds.get("讲解定位不到同名卷（book/paper 对不上）", 0) == 0 and st["lectures"] == 4
        ok += clean
        print(("✅" if clean else "❌") + f" 前缀容忍 + _stale 排除（讲解计 {st['lectures']}，应 4；p6 带前缀仍须定位成功）")
        print(f"\n自检 {ok}/{total}")
        return 0 if ok == total else 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    args = [a for a in sys.argv[1:]]
    if "--selftest" in args:
        return selftest()
    root = REPO
    if "--repo" in args:
        i = args.index("--repo")
        root = args[i + 1]
        del args[i:i + 2]
    bs = args or buckets(root)
    rc = 0
    tot = {"exams": 0, "lectures": 0, "problems": 0}
    for b in bs:
        st, probs = audit_bucket(b, root)
        for k in tot:
            tot[k] += st[k]
        flag = "" if not probs else "  ✗"
        print(f"{b:<16} 卷 {st['exams']:>4}｜讲解 {st['lectures']:>4}｜问题 {st['problems']}{flag}")
        for why, where in probs[:12]:
            print(f"   - {why}：{os.path.relpath(where, root)}")
        if len(probs) > 12:
            print(f"   … 另有 {len(probs) - 12} 条")
        if probs:
            rc = 1
    print(f"\n== 合计 桶 {len(bs)}｜卷 {tot['exams']}｜讲解 {tot['lectures']}｜问题 {tot['problems']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
