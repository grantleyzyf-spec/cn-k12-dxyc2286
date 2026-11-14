#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""试卷 docx ↔ 现役卷 JSON「同源」核验（交付件 vs 源，逐份逐册）。

为什么要有这一条（2026-11-14 建链，接住 11-13 18:00 段记账的限度）：
  第 11 链管讲解 docx、第 12 链管学层 docx，**试卷 docx（1304 卷 × 2 = 2608 份）是唯一的
  「正文↔源」盲区**。11-13 那段量过「题干覆盖率 min 0.963、答案区 0.695」，因为答案区
  的 scoreRule 序列化口径不统一（list[dict] / dict / list[int] / str / list[str] 五种写法），
  覆盖率阈值不可用 ⇒ 当时挂账未做。
  11-13 上午刚在讲解上抓到「源已换、成品没重渲」的旧稿残留（8 份），试卷同一失败模式无锁。

判据换了一条更硬的路子：**用现役渲染器重渲一份到临时目录，与交付件逐字比对**。
  这条路不依赖复刻版式，也不依赖 scoreRule 序列化口径 —— 渲染器怎么排，交付件就该是什么样。

判据（任一不满足即 FAIL）：
  A 件数：每份现役卷 JSON 必有 `<根>/<版本>/<册>/<卷>_试卷.docx` 与 `_参考答案与评分标准.docx`；
  B 逐份同源：重渲文本 vs 交付文本，汉字二元字组 Jaccard ≥ 0.98 且汉字数比 ∈ [0.97, 1.03]
    （标定：全库 2608 份实测 Jaccard 恒 1.000、汉字逐份相等 ⇒ 阈值两侧留足余量，
     只放过「空白/段落合并」级别的等价差异，任何题干/答案/解析/评分标准的改动都会掉下来）；
  B2 版式同源（2026-11-14 12:00 加，接住 09:00 段记账的「只证文本不证版式」限度）：
    同一份重渲件的**版式指纹**必须与交付件**完全相等**（零容差）。指纹只取渲染器会写的属性：
    段落数 / 空段落数（＝答题空行）/ 表格数与逐表列数（＝选项两列）/ 分节数 / 显式分页数 /
    pageBreakBefore / 对齐直方图 / 字号直方图 / 段落样式直方图 / 缩进直方图 / 行距直方图 / run 数；
    刻意不取 proofErr、lastRenderedPageBreak 等 Word 编辑痕迹（那不是版式，是打开过）。
    标定：全库 2608 份实测 **零差异** ⇒ 零容差可用；文本没变而版式被换（重排、丢空行、改字号）
    只有这一条能抓（B 的 Jaccard 仍是 1.000）；
  C 合订本：`<根>/<版本>/<册>/_合订本/<册>_{试卷,参考答案}合订本.docx` 存在，且
    ① 目录行 `i. <册>　<卷>` 逐卷在册且顺序与渲染器排序一致；
    ② 每卷重渲正文 35%/75% 处各 60 字特征串在合订本内（防「单份重渲了、合订本没重建」）；
    ③ 合订本汉字数 / 各卷重渲汉字之和 ∈ [0.90, 1.10]（防漏卷、防旧稿拼册）；
  C2 合订本版式同源（2026-11-14 18:00 加，接住 12:00 段记账的「指纹不覆盖合订本」限度）：
    用现役合订本渲染器（`build_math_exam_booklet.build`）把**本次重渲的单份**重新拼成合订本，
    与交付合订本比：① 版式指纹**零容差**（属性与 B2 同一套，含分节数 / 段前分页 / 空段 / 表格列数）；
    ② 文本 Jaccard ≥ 0.98。标定：全库 260 本实测指纹零差异、Jaccard 恒 1.0000 ⇒ 零容差可用。
    为什么需要：C 只看「目录行 + 特征串 + 汉字数」，同一册被换成同字数、同目录的旧版式照样过；
    C2 复用的是 B/B2 已经渲好的单份文件，不额外重渲，整链只多 ~30 秒。
  F 多余件：交付目录里出现「无对应现役卷」的 docx（旧卷名残留）即 FAIL。

用法：
    python3 scripts/verify_exam_docx_samesource.py                 # 全 12 版
    python3 scripts/verify_exam_docx_samesource.py 苏教版 math-sujiao
    python3 scripts/verify_exam_docx_samesource.py --quiet
    python3 scripts/verify_exam_docx_samesource.py --stats         # 只打分布（标定用，不改判据）
    python3 scripts/verify_exam_docx_samesource.py --selftest      # 合成夹具（含杀伤力断言）
"""
import argparse
import glob
import html
import importlib
import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.expanduser(os.environ.get("REPO")
                          or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/学科图谱原创试卷/数学")
PAIRS = {"人教版": "math", "北京版": "math-bj", "北师大版": "math-bsd", "华东师大版": "math-hds",
         "沪科技版": "math-hukeji", "沪教版": "math-hujiao", "河北版": "math-hebei",
         "青岛版": "math-qd", "苏教版": "math-sujiao", "苏科版": "math-suke",
         "湘教版": "math-xiangjiao", "鄂教版": "math-ejiao"}
SUFFIXES = ("_试卷.docx", "_参考答案与评分标准.docx")
TAGS = ("试卷合订本", "参考答案合订本")
J_MIN = 0.98
HB_LO, HB_HI = 0.97, 1.03
SNIP = 60
HAN = re.compile(r"[\u4e00-\u9fff]")
# 渲染器排序：kind 先、卷名中文数字后（与 build_math_exam_booklet.main 一致）
KIND_RANK = {"unit": 0, "mid": 1, "fin": 2}
CN = "一二三四五六七八九十"


# ---------- 基础工具 ----------
def doc_text(p):
    """Word 把根式/分数排成 OMML ⇒ 同时取 w:t 与 m:t。"""
    with zipfile.ZipFile(p) as z:
        x = z.read("word/document.xml").decode("utf-8", "ignore")
    return html.unescape("".join(re.findall(r"<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>", x)))


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def doc_sig(p):
    """版式指纹：只看「排出来是什么样」，不看文字（见文件头 B2）。"""
    with zipfile.ZipFile(p) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        # 页码在 footer 的 PAGE 域里，document.xml 完全没有它 ⇒ 不取这一面，「页码丢了」查不出
        foot = []
        for n in sorted(z.namelist()):
            if not re.search(r"word/(?:footer|header)\d*\.xml$", n):
                continue
            fx = z.read(n).decode("utf-8", "ignore")
            ftxt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", fx))
            foot.append((n, fx.count("<w:fldSimple"), fx.count("<w:instrText"),
                         re.sub(r"\s+", "", ftxt)[:40]))
    c = {"p": 0, "p_empty": 0, "r": 0, "tbl": 0, "sect": 0, "br_page": 0, "pbb": 0,
         "foot": tuple(foot)}
    jc, sz, sty, ind, spc, cols = {}, {}, {}, {}, {}, []
    for para in root.iter(W + "p"):
        c["p"] += 1
        txt = "".join(t.text or "" for t in para.iter(W + "t")) + \
              "".join(t.text or "" for t in para.iter(M + "t"))
        if not txt.strip() and para.find(".//" + W + "drawing") is None \
                and para.find(".//" + W + "pict") is None:
            c["p_empty"] += 1
        ppr = para.find(W + "pPr")
        if ppr is not None:
            j = ppr.find(W + "jc")
            if j is not None:
                jc[j.get(W + "val")] = jc.get(j.get(W + "val"), 0) + 1
            if ppr.find(W + "pageBreakBefore") is not None:
                c["pbb"] += 1
            st = ppr.find(W + "pStyle")
            if st is not None:
                sty[st.get(W + "val")] = sty.get(st.get(W + "val"), 0) + 1
            i = ppr.find(W + "ind")
            if i is not None:
                k = "|".join(i.get(W + x) or "" for x in ("left", "firstLine", "hanging"))
                ind[k] = ind.get(k, 0) + 1
            s0 = ppr.find(W + "spacing")
            if s0 is not None:
                k = "|".join(s0.get(W + x) or "" for x in ("line", "lineRule", "before", "after"))
                spc[k] = spc.get(k, 0) + 1
    for run in root.iter(W + "r"):
        c["r"] += 1
        rpr = run.find(W + "rPr")
        if rpr is not None:
            z_ = rpr.find(W + "sz")
            if z_ is not None:
                sz[z_.get(W + "val")] = sz.get(z_.get(W + "val"), 0) + 1
    for b in root.iter(W + "br"):
        if b.get(W + "type") == "page":
            c["br_page"] += 1
    c["sect"] = len(list(root.iter(W + "sectPr")))
    for t in root.iter(W + "tbl"):
        cols.append(len(list(t.iter(W + "gridCol"))))
    c["tbl"] = len(cols)
    c["tbl_cols"] = cols
    c["jc"], c["sz"], c["pStyle"], c["ind"], c["spacing"] = jc, sz, sty, ind, spc
    return c


def han(s):
    return len(HAN.findall(s or ""))


def norm(s):
    return re.sub(r"[\s\u3000]+", "", s or "")


def bigrams(s):
    s = re.sub(r"[^\u4e00-\u9fff]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jaccard(a, b):
    ba, bb = bigrams(a), bigrams(b)
    return len(ba & bb) / max(1, len(ba | bb))


def cn_number(text):
    m = re.search(r"第([一二三四五六七八九十百零〇\d]+)", text or "")
    if not m:
        return 999
    s = m.group(1)
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch == "十":
            total += (cur or 1) * 10
            cur = 0
        elif ch in CN:
            cur = CN.index(ch) + 1
    return total + cur


def renderer(repo):
    sys.path.insert(0, os.path.join(repo, "scripts"))
    if "build_math_exam_docx" in sys.modules:
        return sys.modules["build_math_exam_docx"]
    return importlib.import_module("build_math_exam_docx")


def exam_files(repo, bucket):
    out = []
    for p in sorted(glob.glob(f"{repo}/data/{bucket}/exams/*/*.json")):
        if "_stale" in p:
            continue
        out.append(p)
    return out


def render_pairs(R, repo, bucket, edition, files, tmp):
    """把每份卷重渲成 (试卷文本, 答案文本)；返回 {(册, 卷): (t1, t2)}。

    必须连 BUCKET/EDITION 一起改：卷头与标题用的是模块级 EDITION（漏改会渲成「数学（人教版）」，
    实测会把 85 份真件全判成不同源 —— 2026-11-14 踩过）。
    """
    R.BUCKET = bucket
    R.EDITION = edition
    R.EXAM = f"{repo}/data/{bucket}/exams"
    got = {}
    for i, f in enumerate(files):
        raw = open(f, encoding="utf-8").read()
        ex1, ex2 = json.loads(raw), json.loads(raw)
        p1, p2 = os.path.join(tmp, "s%d.docx" % i), os.path.join(tmp, "a%d.docx" % i)
        R.render_paper(ex1, p1)
        R.render_answer(ex2, p2)
        # 卷名在同版多册间会重名（「期中测试卷A」）⇒ 键必须带册名，否则后册覆盖前册
        # 文本 + 版式指纹 + 文件路径一起取：B / B2 / C2 共用这一次重渲，不加耗时
        # 路径**不删**：C2 要用重渲单份重新拼合订本（tmp 由 check() 统一清）
        got[(ex1["book"], ex1["paper"])] = (doc_text(p1), doc_text(p2),
                                           doc_sig(p1), doc_sig(p2), p1, p2)
    return got


def booklet_builder(repo):
    """现役合订本渲染器（独立模块实例，E 里的 BUCKET/EDITION/EXAM 由调用方设置）。"""
    key = "build_math_exam_booklet"
    if key in sys.modules:
        return sys.modules[key]
    # 与 renderer() 同款解析：靠 sys.path 里的 scripts 目录，自检用假 repo 也能导入
    sys.path.insert(0, os.path.join(repo, "scripts"))
    return importlib.import_module(key)


def rebuild_booklet(BB, edition, book, kind_cn, pairs, out):
    """按现役 build() 拼一本合订本（目录 + 逐卷深拷贝 + 页脚页码）。"""
    master = BB.E.new_doc()
    BB.build(master, pairs, f"{BB.E.SUBJECT_NAME}（{edition}）{book}",
             f"{kind_cn}合订本 · 共 {len(pairs)} 卷 · 学生打印版", out)


def check(repo, edition, bucket, root=ROOT, stats=None):
    errs = []
    R = renderer(repo)
    files = exam_files(repo, bucket)
    base = f"{root}/{edition}"
    BB = booklet_builder(repo)
    BB.E.BUCKET, BB.E.EDITION, BB.E.EXAM = bucket, edition, f"{repo}/data/{bucket}/exams"
    tmp = tempfile.mkdtemp(prefix="exdocx_")
    try:
        got = render_pairs(R, repo, bucket, edition, files, tmp)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    by_book = {}
    for (book, paper), (t1, t2, s1, s2, p1, p2) in got.items():
        by_book.setdefault(book, []).append((paper, t1, t2, s1, s2, p1, p2))
    for book in sorted(by_book):
        vols = by_book[book]
        d = f"{base}/{book}"
        have = sorted(x for x in glob.glob(f"{d}/*.docx")
                      if not os.path.basename(x).startswith(".~"))
        have_set = {os.path.basename(x) for x in have}
        want = {f"{v[0]}{s}" for v in vols for s in SUFFIXES}
        for name in sorted(want - have_set):
            errs.append(f"[A] {book}·{name}: 交付 docx 缺失")
        for name in sorted(have_set - want):
            errs.append(f"[F] {book}·{name}: 无对应现役卷的多余 docx（旧名/孤儿）")
        for paper, t1, t2, s1, s2, _p1, _p2 in vols:
            for suf, fresh, fsig in zip(SUFFIXES, (t1, t2), (s1, s2)):
                f = f"{d}/{paper}{suf}"
                if not os.path.exists(f):
                    continue
                t = doc_text(f)
                j = jaccard(t, fresh)
                hr = han(t) / max(1, han(fresh))
                if stats is not None:
                    stats["doc"].append((j, hr))
                if j < J_MIN:
                    errs.append(f"[B] {book}·{paper}{suf}: 与现役卷不同源"
                                f"（Jaccard {j:.3f} < {J_MIN}）")
                elif not (HB_LO <= hr <= HB_HI):
                    errs.append(f"[B] {book}·{paper}{suf}: 汉字比 {hr:.3f} 越界"
                                f"（docx {han(t)} / 重渲 {han(fresh)}）")
                dsig = doc_sig(f)
                bad = [k for k in fsig if dsig.get(k) != fsig[k]]
                if stats is not None:
                    stats.setdefault("sig", []).append(len(bad))
                if bad:
                    detail = "；".join(f"{k}: {str(dsig.get(k))[:60]} ≠ {str(fsig[k])[:60]}"
                                       for k in bad[:3])
                    errs.append(f"[B2] {book}·{paper}{suf}: 版式与现役渲染器不符"
                                f"（{len(bad)} 项 / {detail}）")
        # C 合订本
        bdir = f"{d}/_合订本"
        order = sorted(vols, key=lambda v: (KIND_RANK.get(_kind(repo, bucket, book, v[0]), 9),
                                            cn_number(v[0])))
        for tag, idx, kind_cn, pi in (("试卷合订本", 1, "试卷", 5),
                                      ("参考答案合订本", 2, "参考答案与评分标准", 6)):
            b = f"{bdir}/{book}_{tag}.docx"
            if not os.path.exists(b):
                errs.append(f"[C] {book}: {tag} 缺失")
                continue
            T = norm(doc_text(b))
            for i, v in enumerate(order, 1):
                line = norm(f"{i}. {book}　{v[0]}")
                if line not in T:
                    errs.append(f"[C] {book}: {tag} 目录缺第 {i} 条「{v[0]}」")
                    break
            for v in order:
                fresh = norm(v[idx])
                if not fresh:
                    continue
                probes = [fresh[int(len(fresh) * fr):int(len(fresh) * fr) + SNIP] for fr in (0.35, 0.75)]
                if not all(x and x in T for x in probes):
                    errs.append(f"[C] {book}: {tag} 内找不到「{v[0]}」正文（合订本未重建）")
            want_han = sum(han(v[idx]) for v in order)
            if want_han:
                bhan = han(doc_text(b))
                # 合订本多出的是封面 + 目录（每卷一行「i. 册　卷」约 10–20 汉字）⇒ 用「差值 + 允许增量」判，
                # 不用比值：单卷册的目录占比可到 20%，比值带会把正常册判红（自检第一节就踩到）
                diff = bhan - want_han
                slack = 30 * len(order) + 200
                if stats is not None:
                    stats["book"].append(diff / want_han)
                if diff < -0.03 * want_han or diff > slack:
                    errs.append(f"[C] {book}: {tag} 汉字数 {bhan} 与各卷和 {want_han} 不符"
                                f"（差 {diff:+d}，允许 −{int(0.03 * want_han)}…+{slack}）")
            # C2 合订本版式同源：拿本次重渲的单份重新拼一本，与交付本比指纹与文本。
            # 复用 B/B2 的临时文件 ⇒ 不额外重渲；C 的「目录 + 特征串」抓不到同字数换版式。
            if not os.path.exists(b):
                continue
            fresh = f"{tmp}/bk_{book}_{tag}.docx"
            try:
                rebuild_booklet(BB, edition, book, kind_cn,
                                [({"book": book, "paper": v[0]}, v[pi]) for v in order], fresh)
            except Exception as e:
                errs.append(f"[C2] {book}: {tag} 重渲失败（{type(e).__name__}: {e}）")
                continue
            a_sig, b_sig = doc_sig(b), doc_sig(fresh)
            bad = [k for k in b_sig if a_sig.get(k) != b_sig[k]]
            if stats is not None:
                stats.setdefault("bsig", []).append(len(bad))
            if bad:
                detail = "；".join(f"{k}: {str(a_sig.get(k))[:60]} ≠ {str(b_sig.get(k))[:60]}"
                                   for k in bad[:3])
                errs.append(f"[C2] {book}: {tag} 版式与现役合订本渲染器不符"
                            f"（{len(bad)} 项 / {detail}）")
                continue
            j = jaccard(doc_text(b), doc_text(fresh))
            if stats is not None:
                stats.setdefault("bj", []).append(j)
            if j < J_MIN:
                errs.append(f"[C2] {book}: {tag} 与现役合订本渲染器不同源"
                            f"（Jaccard {j:.3f} < {J_MIN}）")
    shutil.rmtree(tmp, ignore_errors=True)
    return errs, len(got)


def _kind(repo, bucket, book, paper):
    f = f"{repo}/data/{bucket}/exams/{book}/{paper}.json"
    try:
        return json.load(open(f, encoding="utf-8")).get("kind")
    except Exception:
        return None


# ---------- 自检 ----------
def mk_docx(path, text):
    from docx import Document
    doc = Document()
    for line in text.split("\n"):
        if line.strip():
            doc.add_paragraph(line)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc.save(path)


def selftest():
    tmp = tempfile.mkdtemp(prefix="exdocx_st_")
    repo = os.path.join(tmp, "repo")
    root = os.path.join(tmp, "root")
    book, edition, bucket = "版X一年级上册", "版X", "math-x"
    stems = ["直接写出得数：7＋5＝（　）", "小明有 12 支铅笔，送给同学 5 支，还剩多少支？"]
    ex = {
        "book": book, "kind": "unit", "paper": "第一单元 测试卷", "stage": "小学", "grade": 1,
        "duration": 40, "fullScore": 100, "scope": ["10以内加减法"], "examId": "x_u1",
        "sections": [{"title": "一、计算题", "rule": "每小题 5 分，共 10 分", "items": [
            {"no": 1, "type": "fill", "stem": stems[0], "answer": "12", "analysis": "七加五，个位相加满十进一。",
             "score": 5, "scoreRule": [{"step": "算对得数", "score": 5}]},
            {"no": 2, "type": "solve", "stem": stems[1], "answer": "7 支", "analysis": "十二减五等于七。",
             "score": 5, "scoreRule": ["列式 2 分", "结果 3 分"]}]}],
    }
    R = renderer(repo)
    src = os.path.join(repo, "data", bucket, "exams", book, "第一单元 测试卷.json")

    def write_json(d):
        os.makedirs(os.path.dirname(src), exist_ok=True)
        json.dump(d, open(src, "w", encoding="utf-8"), ensure_ascii=False)

    def render_all(d=None):
        d = d or ex
        R.BUCKET, R.EDITION = bucket, edition
        p1 = f"{root}/{edition}/{book}/{d['paper']}_试卷.docx"
        p2 = f"{root}/{edition}/{book}/{d['paper']}_参考答案与评分标准.docx"
        os.makedirs(os.path.dirname(p1), exist_ok=True)
        R.render_paper(json.loads(json.dumps(d)), p1)
        R.render_answer(json.loads(json.dumps(d)), p2)

    def booklet():
        # 必须用现役合订本渲染器：C2 比的是「交付本 vs 重渲本」的指纹，手搓纯段落必红
        BB = booklet_builder(repo)
        BB.E.BUCKET, BB.E.EDITION = bucket, edition
        d = f"{root}/{edition}/{book}/_合订本"
        os.makedirs(d, exist_ok=True)
        for tag, kind_cn, suf in (("试卷合订本", "试卷", "_试卷.docx"),
                                  ("参考答案合订本", "参考答案与评分标准", "_参考答案与评分标准.docx")):
            rebuild_booklet(BB, edition, book, kind_cn,
                            [({"book": book, "paper": ex["paper"]},
                              f"{root}/{edition}/{book}/{ex['paper']}{suf}")],
                            f"{d}/{book}_{tag}.docx")

    def good():
        write_json(ex)
        render_all()
        booklet()

    def run():
        return check(repo, edition, bucket, root=root)[0]

    ok = True

    def case(name, mutate, want):
        nonlocal ok
        good()
        mutate()
        e = run()
        if want is None:
            if e:
                print(f"✗ 夹具（{name}）误报: {e[:2]}")
                ok = False
        elif not any(x.startswith(want) for x in e):
            print(f"✗ 夹具（{name}）未报 {want}: {e[:2]}")
            ok = False

    case("正常", lambda: None, None)
    case("源改未重渲", lambda: write_json(dict(ex, sections=[dict(ex["sections"][0],
                                                              items=ex["sections"][0]["items"] + [
                                                                  {"no": 3, "type": "fill", "stem": "9＋9＝（　）",
                                                                   "answer": "18", "analysis": "两个九相加。",
                                                                   "score": 5, "scoreRule": "算对得 5 分"}])])), "[B]")
    def bump_sz(p):
        """只改字号、一字不动。"""
        with zipfile.ZipFile(p) as z:
            items = {n: z.read(n) for n in z.namelist()}
        x = items["word/document.xml"].decode("utf-8")
        m = re.search(r'<w:sz w:val="(\d+)"', x)
        x = x.replace(m.group(0), f'<w:sz w:val="{int(m.group(1)) + 2}"', 1)
        items["word/document.xml"] = x.encode("utf-8")
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in items.items():
                z.writestr(n, b)

    def drift_layout():
        """只改单份字号、一字不动 ⇒ B 仍 1.000，只有 B2 能抓。"""
        bump_sz(f"{root}/{edition}/{book}/{ex['paper']}_试卷.docx")

    def drift_booklet():
        """只改**合订本**字号（单份不动、目录不动）⇒ C 照过，只有 C2 能抓。"""
        bump_sz(f"{root}/{edition}/{book}/_合订本/{book}_试卷合订本.docx")

    case("版式漂移（同字不同字号）", drift_layout, "[B2]")
    def drop_page_number():
        """删合订本页脚里的 PAGE 域（页码丢了，正文与汉字数全不变）。"""
        p = f"{root}/{edition}/{book}/_合订本/{book}_试卷合订本.docx"
        with zipfile.ZipFile(p) as z:
            items = {n: z.read(n) for n in z.namelist()}
        x = items["word/footer1.xml"].decode("utf-8")
        x2 = x.replace('<w:fldSimple w:instr="PAGE"/>', "")
        assert x2 != x, "夹具失效：footer 里没有 PAGE 域"
        items["word/footer1.xml"] = x2.encode("utf-8")
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in items.items():
                z.writestr(n, b)

    case("合订本版式漂移（单份不动）", drift_booklet, "[C2]")
    case("合订本页码丢失（页脚 PAGE 域）", drop_page_number, "[C2]")
    case("缺件", lambda: os.remove(f"{root}/{edition}/{book}/{ex['paper']}_试卷.docx"), "[A]")
    case("旧名残留", lambda: mk_docx(f"{root}/{edition}/{book}/第一单元 测试卷(旧)_试卷.docx", "旧卷"),
         "[F]")
    case("合订本未重建", lambda: mk_docx(f"{root}/{edition}/{book}/_合订本/{book}_试卷合订本.docx",
                                     f"1. {book}　{ex['paper']}\n只有目录，没有正文"), "[C]")
    shutil.rmtree(tmp, ignore_errors=True)
    print(("✅ selftest 8/8" if ok else "❌ selftest 未过"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("pairs", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    pairs = [(a.pairs[0], a.pairs[1])] if len(a.pairs) >= 2 else list(PAIRS.items())
    rc, total, nvol = 0, 0, 0
    st = {"doc": [], "book": [], "bsig": [], "bj": []}
    for edition, bucket in pairs:
        errs, n = check(a.repo, edition, bucket, root=a.root, stats=st)
        nvol += n
        total += len(errs)
        if not a.quiet:
            print(f"== {edition} 卷 {n}｜问题 {len(errs)}")
            for x in errs[:12]:
                print("   ✗", x)
        if errs:
            rc = 1
    if a.stats and st["doc"]:
        js = sorted(x[0] for x in st["doc"])
        hrs = sorted(x[1] for x in st["doc"])
        bk = sorted(st["book"]) or [0.0]
        sg = st.get("sig") or [0]
        bs = st.get("bsig") or [0]
        bj = sorted(st.get("bj") or [1.0])
        print(f"== 分布 单份 {len(js)} 份：Jaccard min {js[0]:.4f} p1 {js[len(js)//100]:.4f} "
              f"中位 {js[len(js)//2]:.4f}｜汉字比 {hrs[0]:.4f}–{hrs[-1]:.4f}｜"
              f"合订本增量 {bk[0]*100:+.2f}%…{bk[-1]*100:+.2f}%｜版式指纹差异 max {max(sg)} 项｜"
              f"合订本 {len(bs)} 本：指纹差异 max {max(bs)} 项、Jaccard min {bj[0]:.4f}")
    print(f"== 合计 卷 {nvol}｜问题 {total}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
