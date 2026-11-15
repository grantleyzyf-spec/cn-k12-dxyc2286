# -*- coding: utf-8 -*-
"""build_kb.py — 为 xueketupu.com 生成客服知识库 chat/kb.json

来源：
  data/stats.json          站点规模数字（学科/知识点/题/边）
  data/subjects.json       学科清单
  index.html 等主页面      功能与使用说明（可见文本切块）
  topics/*/index.html     知识点名索引（用于“帮我找某个知识点”）

用法：python3 chat/build_kb.py [仓库根目录]
"""
import json, os, re, sys, html

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "chat", "kb.json")

PAGES = [
    ("index.html", "首页", "https://xueketupu.com/"),
    ("explore/index.html", "知识图谱探索", "https://xueketupu.com/explore/"),
    ("diagnose/index.html", "诊断出题", "https://xueketupu.com/diagnose/"),
    ("learn/index.html", "学层精讲", "https://xueketupu.com/learn/"),
    ("topics/index.html", "知识点总览", "https://xueketupu.com/topics/"),
    ("teacher/index.html", "教师入口", "https://xueketupu.com/teacher/"),
    ("sponsor/index.html", "赞助与合作", "https://xueketupu.com/sponsor/"),
    ("contact/index.html", "联系我们", "https://xueketupu.com/contact/"),
    ("novel/index.html", "连载小说", "https://xueketupu.com/novel/"),
]

TAG = re.compile(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", re.S | re.I)
TAG2 = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\r\f\v]+")


def visible_text(path):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = TAG.sub(" ", raw)
    text = TAG2.sub("\n", raw)
    text = html.unescape(text)
    lines = []
    for ln in text.split("\n"):
        ln = WS.sub(" ", ln).strip()
        if len(ln) >= 6 and not ln.startswith(("function", "var ", "const ", "window.", "{")):
            lines.append(ln)
    return "\n".join(lines)


def chunk(text, size=700, overlap=80):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return [c.strip() for c in out if len(c.strip()) > 80]


def main():
    stats = {}
    p = os.path.join(ROOT, "data", "stats.json")
    if os.path.exists(p):
        stats = json.load(open(p, encoding="utf-8"))

    chunks = []
    for rel, title, url in PAGES:
        fp = os.path.join(ROOT, rel)
        if not os.path.exists(fp):
            continue
        for k, c in enumerate(chunk(visible_text(fp))):
            chunks.append({"id": f"{rel}#{k}", "title": title, "url": url, "text": c})

    facts = f"""站点：xueketupu.com「中国 K-12 全学科知识图谱」。
规模（自动统计）：{stats.get('subjects','?')} 个学科版本，{stats.get('topics','?')} 个知识点，
{stats.get('questions','?')} 道题，{stats.get('dependencies','?')} 条先修关系
（硬先修 {stats.get('dep_hard','?')} / 软先修 {stats.get('dep_soft','?')}），
课标条目 {stats.get('standards_entries','?')} 条。学段分布：小学 {stats.get('stages',{}).get('小学','?')}、
初中 {stats.get('stages',{}).get('初中','?')}、高中 {stats.get('stages',{}).get('高中','?')} 个知识点。

四个功能页：
1) 知识图谱探索 /explore/ —— 按学科看知识点与先修连线，点开是知识点详情。
2) 诊断出题 /diagnose/ —— 选一个知识点，沿先修关系往回追，找出最可能拖后腿的"根因"知识点，并给题。
3) 学层精讲 /learn/ —— 按册/单元的讲解与例题，配套合订本。
4) 知识点库 /topics/ —— 全站知识点索引，可按学科、年级、关键词找。

使用方式：全部免费、无需注册登录，浏览器直接打开。手机与电脑都能用。
不提供：账号体系、在线答疑（人工）、视频课程、付费会员、导出 PDF 之外的批改服务。
版权与来源：知识点与课标条目为公开教材/课标整理，题目为自建；引用处标注了课标 quote。
联系：邮箱 grantleyzyf@gmail.com；QQ 群 1045844951；合作见 /sponsor/。
备案：渝ICP备2026027764号-1（个人网站，非经营性）。"""

    # 知识点索引：直接读 data/<subject>/topics.json（全量 1.2 万条）
    subj_name = {}
    sp = os.path.join(ROOT, "data", "subjects.json")
    if os.path.exists(sp):
        try:
            sj = json.load(open(sp, encoding="utf-8"))
            items = sj if isinstance(sj, list) else list(sj.values())
            for it in items:
                if isinstance(it, dict) and it.get("id"):
                    subj_name[it["id"]] = it.get("name") or it["id"]
        except Exception:
            pass

    kps = []
    import glob
    for fp in sorted(glob.glob(os.path.join(ROOT, "data", "*", "topics.json"))):
        sid = os.path.basename(os.path.dirname(fp))
        try:
            rows = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for t in rows:
            if not isinstance(t, dict):
                continue
            tid = t.get("id")
            name = (t.get("name") or "").strip()
            if not tid or not name:
                continue
            grade = t.get("grade")
            sem = t.get("semester") or ""
            meta = f"{subj_name.get(sid, sid)} {grade}年级{sem}".strip()
            kps.append([tid, name, meta, f"https://xueketupu.com/topics/{tid}/"])

    kb = {"facts": facts, "chunks": chunks, "kps": kps,
          "built": __import__("time").strftime("%Y-%m-%d %H:%M")}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(kb, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"kb.json: chunks={len(chunks)} kps={len(kps)} size={os.path.getsize(OUT)//1024}KB")


if __name__ == "__main__":
    main()
