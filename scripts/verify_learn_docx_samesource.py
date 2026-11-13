# -*- coding: utf-8 -*-
"""第 12 链：学层精讲 docx ↔ 现役 learn JSON 同源核验（12 版全库，逐份）。

为什么要有这一链
----------------
`verify_learn_batch.py`（技能库第 1 链）只核「件数=课时数 / 首行标题 / 合订本目录条数 /
合订本与单份的汉字比」——**完全不看正文是否来自现役源**。2026-11-13 在讲解 docx 上就栽过
一次同类型的事：11-02 重写之前渲染的旧稿 docx 一直躺在交付目录里，件数、标题全部合规，
学生拿到的却是另一套题干与答案（见 `verify_lecture_docx_samesource.py` 头注）。
学层是更大的面（4367 课时 / 130 册），原先没有任何「正文↔源」判据。

判据（全部实测标定，真件 0 误报）
--------------------------------
A 件数/命名：按 `build_math_learn_docx.py` 的命名规则（同名第二篇起补 `_<topicId>`）逐课时求
  期望文件名；缺件、目录里多出的 docx（旧命名残留）都算问题。
B 同源：markdown 与 docx 正文的**汉字二元字组 Jaccard ≥ 0.90**。
  标定：真件 min 0.960 / p1 0.967 / 中位 0.978；换课时、旧稿都落在 0.2 以下 ⇒ 两侧都有余量。
C 汉字比 docx/源 ∈ [0.95, 1.15]。真件 1.012–1.040。
D 小标题全覆盖：markdown 里每个 `## / ###` 标题的汉字串必须出现在 docx 正文里。
  实测 36057 条 0 未落（公式型标题且文档含 OMML 时计例外）。这条能抓「标题吞段」类渲染丢失
  （2026-11-05 修过一次 H1 与课时名不同就被整句跳过）。
E 合订本：每个课时的源正文 40% 处取 60 个汉字，必须出现在本册合订本里
  （合订本未重建 / 用旧稿拼册都会被抓到；实测 4367/4367 命中）。

用法
----
    python3 scripts/verify_learn_docx_samesource.py                 # 12 版全库
    python3 scripts/verify_learn_docx_samesource.py --ed 苏教版 苏科版
    python3 scripts/verify_learn_docx_samesource.py --selftest      # 判据夹具
    python3 scripts/verify_learn_docx_samesource.py --quiet         # 只打印汇总与问题

限度：本链只证「docx 逐字来自现役源」，不证学层内容好不好（内容由 `check_math_*_learn.py`
与 `audit_math_learn_all.py` 管）。B 对「同题换文体重写」敏感（会降到 ~0.5 判不同源），这是刻意的：
交付件应逐字来自现役源，改写请先改源再重渲。
"""
import argparse
import json
import os
import re
import statistics
import sys
import tempfile
import unicodedata
import zipfile

ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/学层精讲/数学")
REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
HAN = re.compile(r"[\u4e00-\u9fff]")
HEAD = re.compile(r"^#{2,3}\s*(.+?)\s*$", re.M)
FORM = re.compile(r"[√^≤≥÷/]|\^-|\d\s*/\s*\d")
PAIRS = {"人教版": "math", "北京版": "math-bj", "北师大版": "math-bsd", "华东师大版": "math-hds",
         "沪科技版": "math-hukeji", "沪教版": "math-hujiao", "河北版": "math-hebei",
         "青岛版": "math-qd", "苏教版": "math-sujiao", "苏科版": "math-suke",
         "湘教版": "math-xiangjiao", "鄂教版": "math-ejiao"}
J_MIN, HB_LO, HB_HI, SNIP = 0.90, 0.95, 1.15, 60


def nfc(s):
    return unicodedata.normalize("NFC", s)


def paras(path):
    with zipfile.ZipFile(path) as z:
        body = z.read("word/document.xml").decode("utf-8")
    out = []
    for pm in re.findall(r"<w:p[ >].*?</w:p>", body, re.S):
        t = "".join(re.findall(r"<(?:w|m):t[^>]*>(.*?)</(?:w|m):t>", pm, re.S))
        out.append(t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip())
    return out


def has_omml(path):
    try:
        with zipfile.ZipFile(path) as z:
            return "<m:oMath" in z.read("word/document.xml").decode("utf-8")
    except Exception:
        return False


def han(s):
    return "".join(HAN.findall(s))


def big(s):
    s = han(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def safe_name(t):
    return re.sub(r'[\\/:*?"<>|]', "_", t)


def expected(lessons):
    """按 build_math_learn_docx.py 的规则求期望文件名（同名第二篇起补 _topicId）。"""
    used, out = set(), []
    for L in lessons:
        t = (L.get("title") or L.get("name") or "").strip().replace("\n", " ")
        safe = safe_name(t)
        if safe in used:
            safe = "%s_%s" % (safe, L.get("topicId"))
        used.add(safe)
        out.append((safe, t, L))
    return out


def booklet_path(bdir, book):
    subs = [x for x in os.listdir(bdir)
            if os.path.isdir(os.path.join(bdir, x)) and "合订本" in nfc(x)]
    if not subs:
        return None
    sd = os.path.join(bdir, subs[0])
    want = os.path.join(sd, "%s_学层精讲合订本.docx" % book)
    if os.path.exists(want):
        return want
    cand = [x for x in os.listdir(sd) if x.endswith(".docx") and not x.startswith("~$")]
    return os.path.join(sd, cand[0]) if len(cand) == 1 else None


def check_book(ed, book, bdir, lessons):
    """返回 (problems[(code,msg)], stats{jaccard,hanratio,lessons})"""
    probs, js, hs = [], [], []
    exp = expected(lessons)
    if not os.path.isdir(bdir):
        return [("A", "册目录缺 %s" % bdir)], {"lessons": len(lessons)}
    files = {x for x in os.listdir(bdir) if x.endswith(".docx") and not x.startswith(".~")}
    exp_names = {s + ".docx" for s, _, _ in exp}
    for x in sorted(files - exp_names):
        probs.append(("A", "多余 docx（不在现役课时集内）：%s" % x[:60]))
    bpath = booklet_path(bdir, book)
    btxt = han("".join(paras(bpath))).replace(" ", "") if bpath else ""
    if not bpath:
        probs.append(("E", "缺合订本"))
    for safe, title, L in exp:
        fp = os.path.join(bdir, safe + ".docx")
        if not os.path.exists(fp):
            probs.append(("A", "缺件 %s.docx（课时「%s」）" % (safe[:40], title[:24])))
            continue
        md = L.get("markdown") or ""
        ps = paras(fp)
        txt = "".join(ps)
        hdt = han(txt).replace(" ", "")
        j = jaccard(big(md), big(txt))
        js.append(j)
        if j < J_MIN:
            probs.append(("B", "Jaccard %.3f < %.2f（「%s」）" % (j, J_MIN, title[:24])))
        hm, hd = len(HAN.findall(md)), len(hdt)
        if hm:
            r = hd / hm
            hs.append(r)
            if not (HB_LO <= r <= HB_HI):
                probs.append(("C", "汉字比 %.3f 越界（「%s」源 %d / 成品 %d）" % (r, title[:24], hm, hd)))
        lost = []
        for h in HEAD.findall(md):
            hh = han(h).replace(" ", "")
            if not hh or hh in hdt:
                continue
            if FORM.search(h) and has_omml(fp):
                continue
            lost.append(h[:30])
        if lost:
            probs.append(("D", "小标题未落 %d 个（「%s」）：%s" % (len(lost), title[:24], "／".join(lost[:3]))))
        if btxt:
            sn = han(md)
            if len(sn) >= 200:
                frag = sn[int(len(sn) * 0.4):int(len(sn) * 0.4) + SNIP]
                if frag and frag not in btxt:
                    probs.append(("E", "合订本缺该课时正文（「%s」）——疑似未重建/旧稿拼册" % title[:24]))
    return probs, {"lessons": len(lessons), "j": js, "hb": hs}


def run(eds, root, repo, quiet=False):
    fails, allj, allh = [], [], []
    tot_l = tot_b = 0
    for ed in eds:
        bucket = PAIRS[ed]
        ldir = os.path.join(repo, "data", bucket, "learn")
        if not os.path.isdir(ldir):
            print("%s: ✗ 无 learn 目录" % ed)
            fails.append("%s: 无 learn 目录" % ed)
            continue
        n_b = n_l = n_p = 0
        for f in sorted(os.listdir(ldir)):
            if not f.endswith(".json") or f.startswith("_"):
                continue
            data = json.load(open(os.path.join(ldir, f), encoding="utf-8"))
            if "book" not in data:
                continue
            book = data["book"]
            lessons = data.get("lessons") or ([data] if data.get("markdown") else [])
            probs, st = check_book(ed, book, os.path.join(root, ed, book), lessons)
            n_b += 1
            n_l += st["lessons"]
            n_p += len(probs)
            allj += st.get("j") or []
            allh += st.get("hb") or []
            for code, msg in probs:
                fails.append("[%s] %s/%s：%s" % (code, ed, book, msg))
        if not quiet:
            print("%s: 册 %d｜课时 %d｜问题 %d" % (ed, n_b, n_l, n_p))
        tot_b += n_b
        tot_l += n_l
    jmin = min(allj) if allj else 0
    hlo = min(allh) if allh else 0
    hhi = max(allh) if allh else 0
    print("\n== 合计 册 %d｜课时 %d｜问题 %d｜Jaccard 最低 %.3f 中位 %.3f｜汉字比 %.3f–%.3f"
          % (tot_b, tot_l, len(fails), jmin, statistics.median(allj) if allj else 0, hlo, hhi))
    for x in fails[:40]:
        print("  ✗ " + x)
    if len(fails) > 40:
        print("  … 另有 %d 条" % (len(fails) - 40))
    return 0 if not fails else 1


# ---------------- selftest：合成夹具 ----------------
CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="xml" ContentType="application/xml"/></Types>')


def mkdocx(path, lines):
    body = "".join('<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
                   % x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for x in lines)
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body>%s</w:body></w:document>' % body)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("word/document.xml", doc)


def selftest():
    ok = 0
    tot = 0

    def case(name, mutate, want_codes):
        nonlocal ok, tot
        tot += 1
        tmp = tempfile.mkdtemp(prefix="learnsrc_")
        repo = os.path.join(tmp, "repo")
        root = os.path.join(tmp, "out")
        book = "苏教版一年级上册"
        def pad(seed, n=320):   # 汉字二元字组足够分散的填充文（避免重复句把 Jaccard 压低）
            return "".join(chr(0x4E00 + ((seed * 97 + i * 13) % 3000)) for i in range(n))
        md1 = "## 一、先说生活里的一件事\n\n" + pad(1)
        md2 = "## 二、把问题拆开\n\n" + pad(2)
        data = {"book": book, "lessons": [
            {"topicId": "p1", "title": "认识数", "markdown": md1},
            {"topicId": "p2", "title": "认识数", "markdown": md2},
        ]}
        os.makedirs(os.path.join(repo, "data", "math-sujiao", "learn"), exist_ok=True)
        json.dump(data, open(os.path.join(repo, "data", "math-sujiao", "learn", book + ".json"), "w",
                             encoding="utf-8"), ensure_ascii=False)
        bdir = os.path.join(root, "苏教版", book)
        mkdocx(os.path.join(bdir, "认识数.docx"),
               ["数学（苏教版）一年级上册　认识数"] + md1.split("\n"))
        mkdocx(os.path.join(bdir, "认识数_p2.docx"),
               ["数学（苏教版）一年级上册　认识数"] + md2.split("\n"))
        mkdocx(os.path.join(bdir, "合订本", book + "_学层精讲合订本.docx"),
               ["目　录", "1. 认识数", "2. 认识数"] + (md1 + md2).split("\n"))
        mutate(bdir, book, md1, md2)
        probs, _ = check_book("苏教版", book, bdir, data["lessons"])
        got = sorted({c for c, _ in probs})
        good = got == sorted(want_codes)
        print("%s %-28s 期望 %s 实得 %s" % ("✓" if good else "✗", name, want_codes or "无", got or "无"))
        ok += 1 if good else 0

    def m_ok(bdir, book, md1, md2):
        pass

    def m_swap(bdir, book, md1, md2):   # 换课时正文（模拟旧稿/错挂）
        mkdocx(os.path.join(bdir, "认识数.docx"),
               ["数学（苏教版）一年级上册　认识数"] + md2.split("\n"))

    def m_miss(bdir, book, md1, md2):
        os.remove(os.path.join(bdir, "认识数_p2.docx"))

    def m_head(bdir, book, md1, md2):   # 吞掉一个小标题
        lines = ["数学（苏教版）一年级上册　认识数"] + [x for x in md1.split("\n") if not x.startswith("##")]
        mkdocx(os.path.join(bdir, "认识数.docx"), lines)

    def m_book(bdir, book, md1, md2):   # 合订本未重建（只有第一篇）
        mkdocx(os.path.join(bdir, "合订本", book + "_学层精讲合订本.docx"),
               ["目　录", "1. 认识数"] + md1.split("\n"))

    def m_extra(bdir, book, md1, md2):  # 旧命名残留
        mkdocx(os.path.join(bdir, "认识数 副本.docx"), ["旧稿"])

    case("正常件", m_ok, [])
    case("换课时正文", m_swap, ["B", "D"])
    case("缺件", m_miss, ["A"])
    case("小标题丢失", m_head, ["D"])
    case("合订本未重建", m_book, ["E"])
    case("多余旧命名 docx", m_extra, ["A"])
    print("selftest %d/%d" % (ok, tot))
    return 0 if ok == tot else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--ed", nargs="*", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    eds = a.ed or list(PAIRS)
    bad = [e for e in eds if e not in PAIRS]
    if bad:
        print("未知版本：%s（可选：%s）" % ("、".join(bad), "、".join(PAIRS)))
        return 2
    return run(eds, a.root, a.repo, a.quiet)


if __name__ == "__main__":
    sys.exit(main())
