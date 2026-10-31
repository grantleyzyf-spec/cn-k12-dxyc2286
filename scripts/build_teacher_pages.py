#!/usr/bin/env python3
"""把本地教学设计 docx 生成为教师入口的静态详情页 + 列表索引 + 公众号关键词表。

用法：
    python3 scripts/build_teacher_pages.py --subject math --dry-run      # 只看解析结果
    python3 scripts/build_teacher_pages.py --subject math               # 真正生成

产物：
    teacher/unit-design/<subject>/<edition>/<册次>/<单元>/index.html   详情页（每篇一页，静态可收录）
    teacher/unit-design/index.json                                    列表索引（筛选用）
    teacher/keywords.csv                                              公众号关键词 → 文件 → 页面

原则：
- 原文 docx 不上站、不放直链，页面底部只给「公众号 天方乘风 + 本篇关键词」；
- 免费公开：单元概览 / 学习目标 / 重难点 / 课时安排 / 课标依据；教学过程只给开头 3 段；
- 去掉「学校：… 指导教师：…」这类个人信息行。
"""
import argparse
import csv
import html
import json
import os
import re
import unicodedata

from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESKTOP = os.path.expanduser("~/Desktop")
BASE = os.path.join(DESKTOP, "中小学教材", "中小学教材")

SUBJECT_NAME = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理",
                "chemistry": "化学", "biology": "生物", "history": "历史", "geography": "地理",
                "science": "科学", "information-technology": "信息科技", "music": "音乐", "art": "美术"}
SUBJECT_DIR = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理",
               "chemistry": "化学", "biology": "生物学", "history": "历史", "geography": "地理",
               "science": "科学", "information-technology": "信息科技", "music": "音乐", "art": "美术"}

CN_NUM = {"1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八",
          "9": "九", "10": "十", "11": "十一", "12": "十二"}

SECTION_KEYS = {
    "概览": ["内容分析与整合"],
    "目标": ["大单元目标叙写", "单元学习目标", "学习目标"],
    "重点": ["大单元教学重点", "教学重点"],
    "难点": ["大单元教学难点", "教学难点"],
    "思路": ["大单元整体教学思路", "教学思路"],
    "课时": ["教-学-评", "课时设计"],
    "作业": ["大单元作业设计", "作业设计"],
}


def html_esc(s):
    return html.escape(s or "")


def parse_filename(fn):
    """从文件名提取 册次 / 单元号 / 单元名 / 学期。"""
    name = re.sub(r"\[[^\]]*\]", "", fn).replace(".docx", "")
    term = "上册"
    if "下册" in name:
        term = "下册"
    book = ""
    m = re.search(r"((?:一|二|三|四|五|六|七|八|九|高[一二三])年级|必修第[一二三四]册|选择性必修第[一二三四]册)", name)
    if m:
        book = m.group(1)
        # 高中没有上下册概念（必修第一册已含学段），义教要补
        if "必修" not in book:
            book = book + term
    unit_no = ""
    m = re.search(r"第\s*(\d+|[一二三四五六七八九十]+)\s*(单元|章|课)", name)
    if m:
        num = m.group(1)
        if num.isdigit():
            num = CN_NUM.get(num, num)
        unit_no = f"第{num}{m.group(2)}"
    else:
        for kw in ("综合与实践", "总复习", "整理与复习", "单元复习"):
            if kw in name:
                unit_no = kw
                break
        if not unit_no:
            rest = name[m.end():] if m else name
            rest = re.split(r"大单元|单元整体|教学设计", rest)[0].strip(" ·-—_")
            if "综合实践" in rest or "实践" in rest:
                unit_no = "综合实践"
                unit_name_hint = re.split(r"[：:]", rest)[-1].strip()
                return book, unit_no, unit_name_hint or rest
            if rest:
                return book, "主题活动", rest
    unit_name = ""
    if m:
        rest = name[m.end():]
        unit_name = re.split(r"大单元|单元整体|教学设计", rest)[0].strip(" ·-—_")
    elif unit_no:
        rest = name.split(unit_no, 1)[-1]
        unit_name = re.split(r"大单元|单元整体|教学设计", rest)[0].strip(" ·-—_")
    if not unit_name:
        unit_name = unit_no or "未命名单元"
    return book, unit_no, unit_name


def docx_paragraphs(path):
    d = Document(path)
    out = []
    for p in d.paragraphs:
        t = (p.text or "").strip()
        if t:
            out.append(t)
    return out


HEAD_RE = re.compile(r"^([一二三四五六七八九十]+)、(.+)$")
SUB_RE = re.compile(r"^[（(]([一二三四五六七八九十]+)[)）](.+)$")


def split_sections(paras):
    """跳过目录（同一组标题出现两次），返回 {一级标题关键词: [段落]}。"""
    heads = [i for i, t in enumerate(paras) if HEAD_RE.match(t)]
    # 目录区的标题是连续的（间隔很小），正文区从第二次出现「一、」开始
    starts = [i for i in heads if paras[i].startswith("一、")]
    body_start = starts[1] if len(starts) >= 2 else (starts[0] if starts else 0)
    secs = {}
    order = []
    cur = None
    for i in range(body_start, len(paras)):
        t = paras[i]
        m = HEAD_RE.match(t)
        if m:
            cur = m.group(2).strip()
            secs.setdefault(cur, [])
            order.append(cur)
            continue
        if cur is not None:
            secs[cur].append(t)
    return secs


def pick(secs, keys):
    for k in keys:
        for name, lines in secs.items():
            if k in name:
                return lines
    return []


def to_list_items(lines, limit=8, maxlen=180):
    items = []
    for ln in lines:
        s = ln.strip()
        if not s or SUB_RE.match(s) or HEAD_RE.match(s):
            continue
        s = re.sub(r"^[（(]?\d+[)）.、]\s*", "", s)
        s = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", s)
        if len(s) < 4:
            continue
        items.append(s if len(s) <= maxlen else s[:maxlen] + "…")
        if len(items) >= limit:
            break
    return items


def extract(path):
    paras = docx_paragraphs(path)
    secs = split_sections(paras)
    overview_lines = pick(secs, SECTION_KEYS["概览"])
    # 概览取「（一）单元内容概览」之后的第一段
    overview = ""
    for i, ln in enumerate(overview_lines):
        if "单元内容概览" in ln and i + 1 < len(overview_lines):
            overview = overview_lines[i + 1]
            break
    if not overview and overview_lines:
        overview = overview_lines[0]
    goals = to_list_items(pick(secs, SECTION_KEYS["目标"]))
    key_pts = to_list_items(pick(secs, SECTION_KEYS["重点"]), limit=4)
    diff_pts = to_list_items(pick(secs, SECTION_KEYS["难点"]), limit=4)
    plan_lines = pick(secs, SECTION_KEYS["课时"])
    teach = [x for x in plan_lines if not SUB_RE.match(x) and len(x) > 20][:3]
    periods = extract_periods(paras, secs)
    return {"overview": overview, "goals": goals, "key": key_pts, "diff": diff_pts,
            "teach": teach, "periods": periods, "secs": list(secs.keys())}



def _num_of(tok):
    tok = str(tok).strip()
    if tok.isdigit():
        return int(tok)
    m = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    if tok == "十":
        return 10
    if tok.startswith("十"):
        return 10 + m.get(tok[1:], 0)
    if len(tok) == 2 and tok[1] == "十":
        return m.get(tok[0], 0) * 10
    if len(tok) == 3 and tok[1] == "十":
        return m.get(tok[0], 0) * 10 + m.get(tok[2], 0)
    return m.get(tok[0], 0)


def _clean_period_title(t):
    t = re.split(r"本课时|本课时的|这一课时", t)[0]
    t = re.split(r"[，,]\s*第\s*[0-9一二三四五六七八九十]+\s*课时", t)[0]
    t = re.sub(r"第\s*[0-9一二三四五六七八九十]+\s*课时", "", t)
    t = re.split(r"[，,]\s*学生", t)[0]
    t = re.split(r"[，,]\s*(?:其中|并|同时|进而)", t)[0]
    if len(t) > 18:
        t = re.split(r"[，,]", t)[0]
    t = re.sub(r'^任务\s*[“"「]([^”"」]+)[”"」]\s*[：:]\s*', "", t)
    t = re.sub(r"完成(.+?)的教学", r"\1", t)
    t = re.sub(r"的教学$", "", t)
    t = t.strip(" ，,。；;：:、·-—（）()0123456789")
    return t[:24]


def extract_periods(paras, secs):
    """优先取「以第N课时开头」的段落（课时设计正文），再退回全文正则；最后按课时号排序。"""
    found = {}
    scores = {}
    head_re = re.compile(r"^第\s*(\d+|[一二三四五六七八九十]+)\s*课时[：:，,、\s]+(.{2,40})$")

    def scan(lines, strict=False):
        for p in lines:
            m = head_re.match(p.strip())
            if not m:
                continue
            if strict and ("完成" in m.group(2)[:4] or "教学" == m.group(2)[:2]):
                continue          # 「完成…的教学」是概述句，不是课时标题
            n = _num_of(m.group(1))
            title = _clean_period_title(m.group(2))
            if not n or not title:
                continue
            score = 0 if title.startswith("完成") else 2
            prev = found.get(n)
            if prev is None:
                found[n] = title
                scores[n] = score
            else:
                ps = scores.get(n, 0)
                if score > ps or (score == ps and 4 < len(title) < len(prev)):
                    found[n] = title
                    scores[n] = score

    # ① 先只在「课时设计」段里找（最可靠）
    for name, lines in secs.items():
        if "教-学-评" in name or "课时设计" in name:
            scan(lines, strict=True)
    # ② 不足 3 条再用全文档
    if len(found) < 3:
        found.clear()
        scan(paras, strict=True)
    if len(found) < 3:
        found.clear()
        scan(paras)
    if len(found) < 3:            # 没有「课时标题」式段落，退回全文扫描
        all_text = "".join(paras)
        for m in re.finditer(r"第\s*(\d+|[一二三四五六七八九十]+)\s*课时[：:，,、\s]*([^。；;\n]{2,40})", all_text):
            n = _num_of(m.group(1))
            title = _clean_period_title(m.group(2))
            if n and title and n not in found:
                found[n] = title
    cn = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十",
          11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五", 16: "十六", 17: "十七", 18: "十八",
          19: "十九", 20: "二十", 21: "二十一", 22: "二十二", 23: "二十三", 24: "二十四", 25: "二十五"}
    return [{"label": f"第{cn.get(n, n)}课时", "title": found[n]} for n in sorted(found)]


def slugify(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)
    return s.strip(" .-") or "unit"


def keyword_of(subject, book, unit_no):
    sn = SUBJECT_NAME.get(subject, subject)
    short_book = (book.replace("年级", "").replace("上册", "上").replace("下册", "下")
                  if "年级" in book else book)
    return f"{sn}{short_book}{unit_no}"


PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="{root}assets/site.css">
<style>
  body {{ background: var(--bg); }}
  main.td {{ max-width: 860px; margin: 0 auto; padding: 26px 18px 64px; }}
  .crumb {{ font-size: 13px; color: var(--ink-2); margin-bottom: 12px; }}
  .crumb a {{ color: var(--brand-ink); text-decoration: none; }}
  h1 {{ font-size: clamp(22px, 3.6vw, 30px); margin: 0 0 8px; letter-spacing: -.01em; }}
  .meta {{ font-size: 13.5px; color: var(--ink-2); margin-bottom: 18px; }}
  .chip {{ display: inline-block; padding: 2px 8px; margin-right: 6px; border-radius: 5px;
           background: var(--brand-soft); color: var(--brand-ink); font-size: 12.5px; font-weight: 650; }}
  section.block {{ background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
                   padding: 18px 20px; margin-bottom: 14px; box-shadow: var(--shadow); }}
  section.block h2 {{ font-size: 16.5px; margin: 0 0 10px; color: var(--brand-ink); }}
  section.block p {{ margin: 0 0 10px; line-height: 1.75; font-size: 15px; color: var(--ink); }}
  section.block ol, section.block ul {{ margin: 0; padding-left: 22px; }}
  section.block li {{ line-height: 1.7; font-size: 14.5px; margin-bottom: 6px; }}
  .periods li b {{ color: var(--brand-ink); }}
  .fade {{ position: relative; max-height: 190px; overflow: hidden; }}
  .fade::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 90px;
                  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, var(--card) 90%); }}
  .cta {{ background: linear-gradient(180deg, var(--brand-soft), var(--card)); border: 1px solid color-mix(in srgb, var(--brand) 35%, transparent);
          border-radius: var(--radius); padding: 20px; margin: 18px 0 10px; }}
  .cta h2 {{ margin: 0 0 6px; font-size: 17px; color: var(--brand-ink); }}
  .cta .sub {{ font-size: 13.5px; color: var(--ink-2); margin-bottom: 14px; }}
  .cta .row {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
  .cta img {{ width: 132px; height: 132px; border-radius: 8px; background: #fff; border: 1px solid var(--line); }}
  .steps {{ flex: 1; min-width: 220px; font-size: 14px; line-height: 1.9; color: var(--ink); }}
  .kw {{ display: inline-flex; align-items: center; gap: 8px; margin-top: 8px; padding: 8px 12px;
         background: #fff; border: 1px dashed var(--brand); border-radius: var(--radius-sm); font-weight: 700; }}
  .copy {{ border: 1px solid var(--line); background: var(--card); border-radius: 6px; padding: 4px 10px;
           font-size: 12.5px; cursor: pointer; color: var(--brand-ink); }}
  .links {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }}
  .links a {{ font-size: 13.5px; color: var(--brand-ink); text-decoration: none; border-bottom: 1px dashed currentColor; }}
  .note {{ font-size: 12.5px; color: var(--ink-2); line-height: 1.7; margin-top: 18px; }}
</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}">
    <span class="brand-copy"><span class="brand-name">中国 K-12 知识图谱</span><span class="brand-kicker">教师入口</span></span>
  </a>
  <nav class="site-nav">
    <a class="nav-link" href="{root}teacher/">教师入口</a>
    <a class="nav-link" href="{root}diagnose/?mode=exam">整卷测试</a>
    <a class="nav-link" href="{root}">学生入口</a>
  </nav>
</header>
<main class="td">
  <div class="crumb">{crumb}</div>
  <h1>{h1}</h1>
  <div class="meta"><span class="chip">{subject}</span><span class="chip">{edition}</span><span class="chip">{book}</span>更新：{date}</div>

  <section class="block"><h2>单元内容概览</h2><p>{overview}</p></section>
  {goals_block}
  {key_block}
  {diff_block}
  {periods_block}
  {teach_block}

  <div class="cta">
    <h2>获取完整 Word 原件</h2>
    <div class="sub">本页只展示概览与要点；完整教学设计（含学历案、板书、作业与评价量表）按下面方式获取。</div>
    <div class="row">
      <img src="{root}assets/wechat-tfc-qr.png" alt="公众号 天方乘风 二维码">
      <div class="steps">
        1. 微信扫码关注公众号 <b>天方乘风</b><br>
        2. 在公众号对话框回复关键词<br>
        <span class="kw"><span id="kw">{keyword}</span><button class="copy" onclick="navigator.clipboard.writeText('{keyword}');this.textContent='已复制'">复制关键词</button></span><br>
        3. 自动收到本单元的 Word 文件
      </div>
    </div>
  </div>

  <div class="links">
    <a href="{root}diagnose/?mode=exam">本册单元卷 / 期中期末卷 →</a>
    <a href="{root}diagnose/">按知识点诊断 →</a>
    <a href="{root}teacher/unit-design/">同册其它单元 →</a>
  </div>

  <p class="note">声明：本页内容由 AI 依据教材与课程标准生成初稿，未经教研审核；教学目标、重难点与课时安排仅供参考，请结合本班学情调整。教学设计的著作权归作者所有，转载或商用请联系公众号「天方乘风」。</p>
</main>
</body>
</html>
"""


def build_page(rec, out_dir, root):
    goals_block = ""
    if rec["goals"]:
        goals_block = "<section class=\"block\"><h2>单元学习目标</h2><ol>" + "".join(
            f"<li>{html_esc(x)}</li>" for x in rec["goals"]) + "</ol></section>"
    key_block = ""
    if rec["key"]:
        key_block = "<section class=\"block\"><h2>教学重点</h2><ul>" + "".join(
            f"<li>{html_esc(x)}</li>" for x in rec["key"]) + "</ul></section>"
    diff_block = ""
    if rec["diff"]:
        diff_block = "<section class=\"block\"><h2>教学难点</h2><ul>" + "".join(
            f"<li>{html_esc(x)}</li>" for x in rec["diff"]) + "</ul></section>"
    periods_block = ""
    if rec["periods"]:
        periods_block = "<section class=\"block\"><h2>课时安排（%d 课时）</h2><ol class=\"periods\">" % len(rec["periods"]) + "".join(
            f"<li><b>{html_esc(p['label'])}</b>　{html_esc(p['title'])}</li>" for p in rec["periods"]) + "</ol></section>"
    teach_block = ""
    if rec["teach"]:
        teach_block = ("<section class=\"block\"><h2>教学过程（节选）</h2><div class=\"fade\">" +
                       "".join(f"<p>{html_esc(x)}</p>" for x in rec["teach"]) + "</div></section>")

    crumb = (f'<a href="{root}teacher/">教师入口</a> › <a href="{root}teacher/unit-design/">大单元整体教学设计</a>'
             f' › {html_esc(rec["edition"])} › {html_esc(rec["book"])}')
    title = f'{rec["unit_name"]} 大单元整体教学设计｜{rec["book"]} {rec["edition"]}{rec["subject"]} - 中国 K-12 知识图谱'
    desc = (rec["overview"] or f'{rec["book"]}{rec["unit_name"]} 大单元整体教学设计：单元学习目标、教学重点难点、课时安排。')[:110]
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "name": f'{rec["unit_name"]} 大单元整体教学设计',
        "inLanguage": "zh-CN",
        "educationalLevel": rec["book"],
        "learningResourceType": "教学设计",
        "about": rec["subject"],
        "isAccessibleForFree": True,
        "publisher": {"@type": "Organization", "name": "中国 K-12 知识图谱"},
    }, ensure_ascii=False)

    html_out = PAGE_TMPL.format(
        root=root, title=html_esc(title), desc=html_esc(desc),
        keywords=html_esc(f'{rec["unit_name"]},{rec["book"]},{rec["subject"]}教学设计,大单元,{rec["keyword"]}'),
        canonical=rec["url"], crumb=crumb, h1=html_esc(f'{rec["book"]} {rec["unit_name"]}'),
        subject=html_esc(rec["subject"]), edition=html_esc(rec["edition"]), book=html_esc(rec["book"]),
        date=rec["date"], overview=html_esc(rec["overview"] or "（本文件未提供单元概览段落）"),
        goals_block=goals_block, key_block=key_block, diff_block=diff_block,
        periods_block=periods_block, teach_block=teach_block,
        keyword=html_esc(rec["keyword"]), jsonld=jsonld)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="math")
    ap.add_argument("--edition", default="人教版")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    sub_dir = SUBJECT_DIR[args.subject]
    base = os.path.join(BASE, sub_dir)
    files = []
    ed_key = args.edition
    for root_dir, _dirs, names in os.walk(base):
        if ed_key and ed_key not in root_dir and ed_key not in os.path.basename(root_dir):
            continue
        for n in names:
            if not n.endswith(".docx") or n.startswith("~$"):
                continue
            if "大单元" not in n:      # 高中把文件直接放在 人教版（A版）/ 下，目录名不含"大单元"
                continue
            files.append(os.path.join(root_dir, n))
    files.sort()
    if args.limit:
        files = files[: args.limit]
    print(f"扫描到 {len(files)} 份大单元 docx")

    records = []
    seen = {}
    for fp in files:
        fn = os.path.basename(fp)
        book, unit_no, unit_name = parse_filename(fn)
        try:
            rec = extract(fp)
        except Exception as e:  # noqa: BLE001
            print(f"跳过（解析失败）{fn}: {e}")
            continue
        edition_guess = "人教版（B版）" if "人教B" in fn or "B版" in fn else ("人教版（A版）" if ("人教A" in fn or "A版" in fn) else "人教版")
        dedup_key = (edition_guess, book or "未标注册次", unit_no, unit_name)
        if dedup_key in seen:
            prev = seen[dedup_key]
            if os.path.getmtime(fp) <= os.path.getmtime(prev["fp"]):
                print(f"  重复跳过 {os.path.basename(fp)}（已有 {os.path.basename(prev['fp'])}）")
                continue
            print(f"  重复替换为更新版本 {os.path.basename(fp)}")
        edition = edition_guess
        keyword = keyword_of(args.subject, book, unit_no)
        rec.update({
            "subject": SUBJECT_NAME.get(args.subject, args.subject),
            "edition": edition, "book": book or "未标注册次",
            "unit_no": unit_no, "unit_name": unit_name, "keyword": keyword,
            "source": os.path.relpath(fp, DESKTOP), "date": "2026-10-31",
        })
        rel = "/".join([args.subject, slugify(edition), slugify(book or "未标注册次"), slugify(unit_no + "-" + unit_name)])
        rec["path"] = f"unit-design/{rel}/"
        rec["url"] = f"https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/teacher/{rec['path']}"
        rec["fp"] = fp
        seen[dedup_key] = rec
        records.append(rec)
        if args.dry_run:
            print(f"  {book} | {unit_no} {unit_name} | 目标{len(rec['goals'])} 课时{len(rec['periods'])} | {keyword}")

    if args.dry_run:
        return

    for rec in records:
        out_dir = os.path.join(ROOT, "teacher", rec["path"].replace("/", os.sep))
        build_page(rec, out_dir, "../" * (rec["path"].count("/") + 1))

    # 列表索引
    idx_dir = os.path.join(ROOT, "teacher", "unit-design")
    os.makedirs(idx_dir, exist_ok=True)
    index = [{k: rec[k] for k in ("subject", "edition", "book", "unit_no", "unit_name",
                                  "keyword", "path", "overview")} for rec in records]
    for it in index:
        it["overview"] = (it["overview"] or "")[:120]
        it["periods"] = 0
    with open(os.path.join(idx_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(index), "generated": "2026-10-31", "items": index}, f, ensure_ascii=False, indent=1)

    # 关键词表（公众号后台批量配置用）
    with open(os.path.join(ROOT, "teacher", "keywords.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["关键词", "学科", "教材版本", "册次", "单元", "页面相对路径", "原文件（本地）"])
        for rec in records:
            w.writerow([rec["keyword"], rec["subject"], rec["edition"], rec["book"],
                        f'{rec["unit_no"]} {rec["unit_name"]}', rec["path"], rec["source"]])
    print(f"生成 {len(records)} 个详情页 → teacher/unit-design/；索引与关键词表已写好")


if __name__ == "__main__":
    main()
