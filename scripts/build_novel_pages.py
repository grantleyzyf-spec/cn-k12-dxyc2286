#!/usr/bin/env python3
"""把长篇小说正文切成静态章节页，生成「连载」入口（/novel/）。

用法：
    python3 scripts/build_novel_pages.py                 # 默认：已发布 100 章（连载体量按需加）
    python3 scripts/build_novel_pages.py --limit 200     # 铺更多章
    python3 scripts/build_novel_pages.py --dry-run       # 只看解析

产物：
    novel/index.html                     书架（单本也保留书架，便于以后加第二本）
    novel/<book>/index.html              目录（分组 + 已读标记）
    novel/<book>/ch0001/index.html       章节页（上一章/下一章、字号、夜间、进度）
    novel/<book>/chapters.json           目录数据（前端排序/续读用）
    sitemap-novel.xml                    章节 sitemap（提交搜索引擎用）

约定：
- 源文件为「第N章 标题」逐行开头的纯文本；遇到 `第100章_xxx.md    2392 字` 这类文件清单行自动忽略（下划线不是空格）。
- 全书 4000 章计划、先铺 100 章：`--limit` 控制已发布章节数，之后日更 5 章时改这个数字重跑。
"""
import argparse
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DEFAULT = os.path.expanduser("~/Desktop/长篇小说撰写/学神讲题就强一分/导出/学神：讲一道题，强一分_正文.txt")
BOOK = {
    "slug": "xueshen",
    "title": "学神：讲一道题，强一分",
    "author": "学霸轻松养成过程",
    "account": "学霸轻松养成过程",      # 公众号
    "intro": "席远舟从倒数第一开始，靠给人讲题翻盘：每讲一道题，自己就强一分。一个普通高中班里，"
             "成绩、人情、家里的事一起压过来，他把每一道错题都掰开讲给同桌听，也把自己一点点讲明白了。",
    "plan": 4000,
}
CH_RE = re.compile(r"^第\s*(\d+)\s*章[\s　]+(.+?)\s*$")


def parse_chapters(path):
    chapters = []
    seen = set()
    cur = None
    for raw in open(path, encoding="utf-8", errors="ignore"):
        line = raw.rstrip("\n").rstrip("\r").strip()
        m = CH_RE.match(line)
        if m and "_" not in line[:12]:
            n = int(m.group(1))
            if n in seen:
                cur = None
                continue
            seen.add(n)
            cur = {"n": n, "title": m.group(2).strip(), "paras": []}
            chapters.append(cur)
            continue
        if cur is None or not line:
            continue
        cur["paras"].append(line)
    chapters.sort(key=lambda c: c["n"])
    return chapters


def esc(s):
    return html.escape(s or "")


CH_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第{n}章 {title}｜{book} - 小说连载</title>
<meta name="description" content="{book} 第{n}章 {title}（作者：{author}）在线免费阅读。">
<link rel="canonical" href="{site}/{bookslug}/ch{n:04d}/">
<link rel="stylesheet" href="{root}assets/site.css">
<style>
  :root {{ --novel-size: 18px; }}
  body {{ background: var(--bg); }}
  main.ch {{ max-width: 760px; margin: 0 auto; padding: 20px 18px 80px; }}
  .bar {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 13px; color: var(--ink-2); margin-bottom: 14px; }}
  .bar a {{ color: var(--brand-ink); text-decoration: none; }}
  .bar .spacer {{ flex: 1; }}
  .bar button {{ padding: 5px 10px; font-size: 12.5px; border: 1px solid var(--line); background: var(--card);
                 color: var(--ink); border-radius: 6px; cursor: pointer; font-family: inherit; }}
  h1 {{ font-size: 21px; margin: 6px 0 4px; }}
  .meta {{ font-size: 12.5px; color: var(--ink-2); margin-bottom: 18px; }}
  .content p {{ font-size: var(--novel-size); line-height: 1.95; margin: 0 0 0.9em; text-indent: 2em; color: var(--ink); }}
  .pager {{ display: flex; gap: 10px; margin: 26px 0 0; }}
  .pager a, .pager span {{ flex: 1; text-align: center; padding: 12px; border: 1px solid var(--line);
                           border-radius: 8px; text-decoration: none; color: var(--brand-ink); background: var(--card); font-size: 14px; }}
  .pager span {{ color: var(--ink-2); background: transparent; }}
  .cta {{ margin-top: 26px; padding: 16px 18px; border: 1px solid color-mix(in srgb, var(--brand) 35%, transparent);
          background: linear-gradient(180deg, var(--brand-soft), var(--card)); border-radius: 12px; }}
  .cta b {{ color: var(--brand-ink); }}
  .cta .row {{ display: flex; gap: 14px; align-items: center; margin-top: 10px; flex-wrap: wrap; }}
  .cta img {{ width: 120px; height: 120px; border-radius: 8px; background: #fff; border: 1px solid var(--line); }}
  .cta .txt {{ flex: 1; min-width: 200px; font-size: 14px; line-height: 1.9; }}
  .note {{ font-size: 12px; color: var(--ink-2); margin-top: 22px; line-height: 1.7; }}
  body.night {{ background: #14181c; }}
  body.night .content p, body.night h1, body.night .meta, body.night .bar, body.night .note {{ color: #d6dde5; }}
  body.night .cta, body.night .bar button, body.night .pager a {{ background: #1c2228; border-color: #2c343c; color: #d6dde5; }}
</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}">
    <span class="brand-copy"><span class="brand-name">{book}</span><span class="brand-kicker">小说连载</span></span>
  </a>
  <nav class="site-nav">
    <a class="nav-link active" href="{root}novel/">小说连载</a>
    <a class="nav-link" href="{root}">学生入口</a>
    <a class="nav-link" href="{root}teacher/">教师入口</a>
  </nav>
</header>
<main class="ch">
  <div class="bar">
    <a href="{root}novel/{bookslug}/">目录</a>
    <span>·</span>
    <span id="pos">第 {n} 章 / 共 {total} 章</span>
    <span class="spacer"></span>
    <button id="font-minus">A−</button><button id="font-plus">A+</button><button id="night">夜间</button>
  </div>
  <h1>第{n}章 {title}</h1>
  <div class="meta">作者：{author} ｜ 全本免费 ｜ 每日 5 章</div>
  <div class="content">{body}</div>

  <div class="pager">{prev}{next}</div>

  <div class="cta">
    <b>追更 / 催更 / 讨论：公众号「{account}」</b>
    <div class="row">
      <img src="{root}assets/wechat-xueba-qr.png" alt="公众号 {account} 二维码" onerror="this.style.display='none'">
      <div class="txt">全本免费，不设付费章节。</div>
    </div>
  </div>

  <p class="note">本书为原创作品，AI 辅助创作，著作权归作者「{author}」所有；转载请保留出处。情节与人物均为虚构，与真实学校、个人无关。</p>
</main>
<script>
(function () {{
  var K = 'k12novel.v1', n = {n};
  try {{
    var st = JSON.parse(localStorage.getItem(K) || '{{}}');
    st.last = n; st['read_' + n] = 1; localStorage.setItem(K, JSON.stringify(st));
  }} catch (e) {{}}
  var size = parseInt(localStorage.getItem('k12novel.size') || '18', 10);
  var night = localStorage.getItem('k12novel.night') === '1';
  function apply() {{
    document.documentElement.style.setProperty('--novel-size', size + 'px');
    document.body.classList.toggle('night', night);
  }}
  apply();
  document.getElementById('font-plus').onclick = function () {{ size = Math.min(26, size + 1); localStorage.setItem('k12novel.size', size); apply(); }};
  document.getElementById('font-minus').onclick = function () {{ size = Math.max(14, size - 1); localStorage.setItem('k12novel.size', size); apply(); }};
  document.getElementById('night').onclick = function () {{ night = !night; localStorage.setItem('k12novel.night', night ? '1' : '0'); apply(); }};
}})();
</script>
</body>
</html>
"""

TOC_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{book} 目录（共 {total} 章） - 小说连载</title>
<meta name="description" content="{book} 章节目录，作者 {author}，全本免费连载，每日更新 5 章。">
<link rel="canonical" href="{site}/{bookslug}/">
<link rel="stylesheet" href="{root}assets/site.css">
<style>
  body {{ background: var(--bg); }}
  main.toc {{ max-width: 860px; margin: 0 auto; padding: 22px 18px 70px; }}
  .crumb {{ font-size: 13px; color: var(--ink-2); margin-bottom: 10px; }}
  .crumb a {{ color: var(--brand-ink); text-decoration: none; }}
  h1 {{ font-size: 22px; margin: 0 0 6px; }}
  .sub {{ font-size: 13.5px; color: var(--ink-2); margin-bottom: 16px; }}
  .act {{ display: flex; gap: 10px; margin-bottom: 18px; flex-wrap: wrap; }}
  .act a, .act button {{ padding: 10px 16px; border-radius: 8px; border: 1px solid var(--line);
        background: var(--card); color: var(--brand-ink); text-decoration: none; font-size: 14px; cursor: pointer; font-family: inherit; }}
  .act a.primary {{ background: var(--brand); color: #fff; border-color: var(--brand); font-weight: 650; }}
  .group {{ margin: 22px 0 8px; font-size: 15px; font-weight: 700; color: var(--brand-ink); }}
  .list {{ list-style: none; margin: 0; padding: 0; }}
  .list li {{ border-bottom: 1px solid var(--line); }}
  .list a {{ display: flex; gap: 10px; padding: 11px 4px; text-decoration: none; color: var(--ink); font-size: 15px; }}
  .list a:hover {{ color: var(--brand-ink); }}
  .list .no {{ color: var(--ink-2); font-size: 13px; min-width: 62px; }}
  .list .read {{ margin-left: auto; font-size: 12px; color: #15803d; }}
  .plan {{ margin-top: 26px; padding: 14px 16px; border: 1px dashed var(--brand); border-radius: 10px;
           font-size: 13.5px; line-height: 1.8; color: var(--ink-2); background: var(--card); }}
</style>
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}">
    <span class="brand-copy"><span class="brand-name">{book}</span><span class="brand-kicker">小说连载</span></span>
  </a>
  <nav class="site-nav">
    <a class="nav-link active" href="{root}novel/">小说连载</a>
    <a class="nav-link" href="{root}">学生入口</a>
    <a class="nav-link" href="{root}teacher/">教师入口</a>
  </nav>
</header>
<main class="toc">
  <div class="crumb"><a href="{root}novel/">小说连载书架</a> › 目录</div>
  <h1>{book}</h1>
  <div class="sub">作者：{author} ｜ 已发布 {total} 章 ｜ 全书预计 {plan} 章 ｜ 每日更新 5 章 ｜ 全本免费</div>
  <div class="act">
    <a class="primary" id="continue" href="ch0001/">开始阅读</a>
    <a href="ch{last:04d}/">读最新一章</a>
    <button id="jump-unread">跳到未读</button>
  </div>
  <div id="groups"></div>
  <div class="plan">
    <b>更新节奏：</b>当前已发布 {total} 章，之后每天 5 章。全书规划 {plan} 章，本页目录会随更新自动加长。<br>
    <b>追更方式：</b>关注公众号「{account}」，或在浏览器收藏本页（阅读进度存在本机，换设备不同步）。
  </div>
</main>
<script>
(function () {{
  if (location.protocol === 'file:') return;
  fetch('chapters.json').then(function (r) {{ return r.json(); }}).then(function (d) {{
    var st = {{}};
    try {{ st = JSON.parse(localStorage.getItem('k12novel.v1') || '{{}}'); }} catch (e) {{}}
    var groups = {{}}, order = [];
    d.chapters.forEach(function (c) {{
      var g = Math.floor((c.n - 1) / 50) + 1;
      if (!groups[g]) {{ groups[g] = []; order.push(g); }}
      groups[g].push(c);
    }});
    var html = order.map(function (g) {{
      var items = groups[g].map(function (c) {{
        var read = st['read_' + c.n] ? '<span class="read">已读</span>' : '';
        return '<li><a href="ch' + String(c.n).padStart(4, '0') + '/"><span class="no">第' + c.n + '章</span>' +
               '<span>' + c.title + '</span>' + read + '</a></li>';
      }}).join('');
      var a = groups[g][0].n, b = groups[g][groups[g].length - 1].n;
      return '<div class="group">第 ' + a + '–' + b + ' 章</div><ul class="list">' + items + '</ul>';
    }}).join('');
    document.getElementById('groups').innerHTML = html;
    if (st.last) {{
      var btn = document.getElementById('continue');
      btn.textContent = '继续阅读（第 ' + st.last + ' 章）';
      btn.setAttribute('href', 'ch' + String(st.last).padStart(4, '0') + '/');
    }}
    document.getElementById('jump-unread').onclick = function () {{
      var target = d.chapters.find(function (c) {{ return !st['read_' + c.n]; }}) || d.chapters[0];
      location.href = 'ch' + String(target.n).padStart(4, '0') + '/';
    }};
  }}).catch(function (e) {{
    document.getElementById('groups').innerHTML = '<p style="color:#b91c1c">目录载入失败：' + e.message + '</p>';
  }});
}})();
</script>
</body>
</html>
"""

SHELF_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>小说连载书架 - {book}</title>
<meta name="description" content="{book}，作者 {author}，全本免费连载，每日更新 5 章。">
<link rel="canonical" href="{site}novel/">
<link rel="stylesheet" href="{root}assets/site.css">
<style>
  body {{ background: var(--bg); }}
  main.shelf {{ max-width: 860px; margin: 0 auto; padding: 24px 18px 70px; }}
  h1 {{ font-size: clamp(22px, 3.6vw, 28px); margin: 0 0 6px; }}
  .lead {{ color: var(--ink-2); font-size: 14.5px; margin: 0 0 22px; }}
  .book {{ display: flex; gap: 18px; background: var(--card); border: 1px solid var(--line);
           border-radius: var(--radius); padding: 18px; box-shadow: var(--shadow); flex-wrap: wrap; }}
  .cover {{ width: 144px; height: 216px; border-radius: 6px; flex: none; overflow: hidden;
            border: 1px solid var(--line); box-shadow: 0 6px 18px rgba(15,110,98,.14); background: #0f6e62; }}
  .cover img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .info {{ flex: 1; min-width: 220px; }}
  .info h2 {{ margin: 0 0 6px; font-size: 19px; }}
  .info .meta {{ font-size: 13px; color: var(--ink-2); margin-bottom: 10px; }}
  .info p {{ font-size: 14px; line-height: 1.8; color: var(--ink-2); margin: 0 0 14px; }}
  .btns {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .btns a {{ padding: 10px 16px; border-radius: 8px; text-decoration: none; font-size: 14px;
             border: 1px solid var(--line); background: var(--card); color: var(--brand-ink); }}
  .btns a.primary {{ background: var(--brand); border-color: var(--brand); color: #fff; font-weight: 650; }}
  .tip {{ margin-top: 20px; font-size: 13px; color: var(--ink-2); line-height: 1.8; }}
</style>
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}">
    <span class="brand-copy"><span class="brand-name">中国 K-12 知识图谱</span><span class="brand-kicker">小说连载</span></span>
  </a>
  <nav class="site-nav">
    <a class="nav-link active" href="{root}novel/">小说连载</a>
    <a class="nav-link" href="{root}">学生入口</a>
    <a class="nav-link" href="{root}teacher/">教师入口</a>
    <a class="nav-link" href="{root}diagnose/?mode=exam">整卷测试</a>
  </nav>
</header>
<main class="shelf">
  <h1>小说连载</h1>
  <p class="lead">全本免费，每日 5 章。读完想做题的，旁边就是知识图谱和整卷测试。</p>
  <div class="book">
    <div class="cover"><img src="{root}assets/novel-cover.jpg?v=3" alt="{book} 封面"></div>
    <div class="info">
      <h2>{book}</h2>
      <div class="meta">作者：{author} ｜ 已发布 {total} 章 / 预计 {plan} 章 ｜ 每日 5 章 ｜ 全本免费</div>
      <p>{intro}</p>
      <div class="btns">
        <a class="primary" href="{bookslug}/">开始阅读</a>
        <a href="{bookslug}/ch{last:04d}/">最新一章</a>
        <a href="{bookslug}/">目录</a>
      </div>
    </div>
  </div>
  <p class="tip">阅读进度保存在本机浏览器；换设备或清缓存会重置。追更可关注公众号「{account}」。<br>
  本书为原创虚构作品，AI 辅助创作，著作权归作者所有。</p>
</main>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=SRC_DEFAULT)
    ap.add_argument("--limit", type=int, default=100, help="已发布章节数（日更 5 章后改这个数重跑）")
    ap.add_argument("--site", default="https://grantleyzyf-spec.github.io/cn-k12-dxyc2286")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    chapters = parse_chapters(args.source)
    if not chapters:
        raise SystemExit("没有解析到章节，检查源文件格式")
    pub = [c for c in chapters if c["n"] <= args.limit]
    print(f"解析 {len(chapters)} 章；本次发布 {len(pub)} 章（1–{pub[-1]['n']}）")
    if args.dry_run:
        for c in pub[:5]:
            print(f"  第{c['n']}章 {c['title']} | {len(c['paras'])} 段 | {sum(len(p) for p in c['paras'])} 字")
        return

    book = dict(BOOK)
    base = os.path.join(ROOT, "novel")
    book_dir = os.path.join(base, book["slug"])
    os.makedirs(book_dir, exist_ok=True)
    total = len(pub)

    for idx, c in enumerate(pub):
        slug = f"ch{c['n']:04d}"
        d = os.path.join(book_dir, slug)
        os.makedirs(d, exist_ok=True)
        body = "".join(f"<p>{esc(p)}</p>" for p in c["paras"])
        prev = f'<a href="../ch{pub[idx-1]["n"]:04d}/">← 上一章</a>' if idx > 0 else '<span>已是第一章</span>'
        nxt = f'<a href="../ch{pub[idx+1]["n"]:04d}/">下一章 →</a>' if idx + 1 < total else '<span>已是最新章</span>'
        jsonld = json.dumps({
            "@context": "https://schema.org", "@type": "Chapter",
            "name": f"第{c['n']}章 {c['title']}",
            "isPartOf": {"@type": "Book", "name": book["title"], "author": {"@type": "Person", "name": book["author"]}},
            "inLanguage": "zh-CN", "position": c["n"],
        }, ensure_ascii=False)
        html_out = CH_TMPL.format(
            root="../../../", book=esc(book["title"]), bookslug=book["slug"], author=esc(book["author"]),
            account=esc(book["account"]), n=c["n"], title=esc(c["title"]), body=body,
            total=total, prev=prev, next=nxt, jsonld=jsonld, site=args.site)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html_out)

    json.dump({"book": book["title"], "author": book["author"], "total": total,
               "chapters": [{"n": c["n"], "title": c["title"], "chars": sum(len(p) for p in c["paras"])} for c in pub]},
              open(os.path.join(book_dir, "chapters.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    open(os.path.join(book_dir, "index.html"), "w", encoding="utf-8").write(
        TOC_TMPL.format(root="../../", book=esc(book["title"]), bookslug=book["slug"], author=esc(book["author"]),
                        account=esc(book["account"]), total=total, plan=book["plan"], last=pub[-1]["n"], site=args.site))
    open(os.path.join(base, "index.html"), "w", encoding="utf-8").write(
        SHELF_TMPL.format(root="../", book=esc(book["title"]), bookslug=book["slug"], author=esc(book["author"]),
                          account=esc(book["account"]), total=total, plan=book["plan"],
                          last=pub[-1]["n"], intro=esc(book["intro"]), site=args.site))

    urls = [f'{args.site}/novel/', f'{args.site}/novel/{book["slug"]}/'] + \
           [f'{args.site}/novel/{book["slug"]}/ch{c["n"]:04d}/' for c in pub]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{u}</loc></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-novel.xml"), "w", encoding="utf-8").write("\n".join(sm))

    size = sum(os.path.getsize(os.path.join(r, f))
               for r, _d, fs in os.walk(base) for f in fs) / 1024 / 1024
    print(f"生成完成：{total} 章 + 目录 + 书架；novel/ 共 {size:.1f} MB；sitemap-novel.xml {len(urls)} 条 URL")


if __name__ == "__main__":
    main()
