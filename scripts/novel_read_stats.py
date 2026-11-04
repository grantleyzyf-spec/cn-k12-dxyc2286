#!/usr/bin/env python3
"""连载章节阅读计数（服务器侧，从 Nginx access log 增量统计）。

为什么这样做：
- 站点是纯静态站、零外链，不能引入第三方计数（不蒜子之类）；
- Nginx 本来就在记 access log，增量解析即可，不新增服务进程、不改前端取数口径；
- 输出一份静态 JSON（/_counts/novel.json），前端 fetch 后显示「阅读 N 次」。

增量口径：
- 状态文件 /var/lib/k12/novel_reads.json 记住「读到哪个文件的第几个字节」；
- 日志按天轮转（logrotate），inode 变化或文件变小 ⇒ 从头读新文件；
- 计数只认 /novel/<book>/chNNNN/ 页面请求，状态 200 或 304 都算一次
  （HTML 是 max-age=0 + must-revalidate，二次访问多数返回 304，只认 200 会严重少算）；
- UA 过滤爬虫/监控/命令行工具。

用法（服务器上，root）：
    python3 scripts/novel_read_stats.py            # 增量跑一次（cron/systemd 每 10 分钟）
    python3 scripts/novel_read_stats.py --rebuild  # 忽略状态，把现存所有轮转日志全量重算
"""
import glob
import gzip
import json
import os
import re
import sys
from datetime import datetime

LOG = os.environ.get("K12_ACCESS_LOG", "/var/log/nginx/k12.access.log")
STATE = os.environ.get("K12_NOVEL_STATE", "/var/lib/k12/novel_reads.json")
OUT = os.environ.get("K12_NOVEL_OUT", "/var/www/k12/_counts/novel.json")

CH_RE = re.compile(r'"GET /novel/([a-z0-9_-]+)/ch(\d{4})/ HTTP/[\d.]+" (\d{3}) ')
DATE_RE = re.compile(r"\[(\d{2})/([A-Za-z]{3})/(\d{4}):")
UA_RE = re.compile(r'"([^"]*)"\s*$')
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
BOT_UA = (
    "bot", "spider", "crawl", "curl/", "wget", "python-requests", "python-urllib", "go-http-client",
    "headless", "ahrefs", "semrush", "bytespider", "yisouspider", "sogou", "baiduspider", "googlebot",
    "bingbot", "applebot", "petalbot", "dataforseo", "discordbot", "telegrambot", "slackbot",
    "twitterbot", "uptimerobot", "monitor", "prometheus", "zgrab", "masscan", "nmap",
)


def load_state():
    try:
        with open(STATE, encoding="utf-8") as fh:
            st = json.load(fh)
    except Exception:
        st = {}
    st.setdefault("since", datetime.now().strftime("%Y-%m-%d"))
    st.setdefault("books", {})
    st.setdefault("inode", None)
    st.setdefault("offset", 0)
    return st


def rotated_logs():
    """现存所有日志，按时间从旧到新（base, base.1, base.N.gz）。"""
    cand = [p for p in glob.glob(LOG + "*") if re.fullmatch(re.escape(LOG) + r"(\.\d+)?(\.gz)?", p)]
    return sorted(cand, key=lambda p: os.stat(p).st_mtime)


def scan(path, start, books, stats):
    """从 start 字节读到文件尾，累加计数；返回 (读到的末尾偏移, 首条命中日期)。"""
    opener = gzip.open if path.endswith(".gz") else open
    end = start
    first_day = None
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        if start:
            fh.seek(start)
        while True:
            line = fh.readline()          # 必须 readline：for-in 迭代会让 tell() 抛 OSError
            if not line:
                break
            if not path.endswith(".gz"):
                end = fh.tell()
            m = CH_RE.search(line)
            if not m:
                continue
            book, ch, status = m.group(1), str(int(m.group(2))), m.group(3)
            if status not in ("200", "304"):
                continue
            ua = UA_RE.search(line)
            if ua and any(b in ua.group(1).lower() for b in BOT_UA):
                continue
            b = books.setdefault(book, {})
            b[ch] = b.get(ch, 0) + 1
            stats["added"] += 1
            if first_day is None:
                dm = DATE_RE.search(line)
                if dm:
                    first_day = f"{dm.group(3)}-{MONTHS.get(dm.group(2), 1):02d}-{dm.group(1)}"
    return end, first_day


def main():
    rebuild = "--rebuild" in sys.argv
    st = load_state()
    if rebuild:
        st["books"] = {}
        st["offset"] = 0
        st["inode"] = None

    if not os.path.exists(LOG):
        print(f"日志不存在：{LOG}")
        return 1

    stats = {"added": 0}
    first_day = None
    stt = os.stat(LOG)

    if rebuild:
        # 全量：按时间顺序把现存日志都读一遍（含 .1 / .gz），末尾偏移落在当前日志上
        for path in rotated_logs():
            _, fd = scan(path, 0, st["books"], stats)
            first_day = first_day or fd
        st["inode"] = stt.st_ino
        st["offset"] = stt.st_size
    else:
        start = st["offset"]
        if st["inode"] != stt.st_ino or stt.st_size < start:
            start = 0                       # 轮转过 / 换了文件
        end, first_day = scan(LOG, start, st["books"], stats)
        st["inode"] = stt.st_ino
        st["offset"] = end

    if first_day and (rebuild or st.get("since_auto") is not True):
        st["since"] = first_day
        st["since_auto"] = True

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs(os.path.dirname(STATE), exist_ok=True)

    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "since": st["since"],
        "books": {k: {"total": sum(v.values()), "chapters": v} for k, v in st["books"].items()},
    }
    if len(payload["books"]) == 1:          # 单书便捷键，前端直接读 chapters[n]
        only = next(iter(payload["books"].values()))
        payload["chapters"] = only["chapters"]
        payload["total"] = only["total"]

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, separators=(",", ":"))

    print(f"新增计数 {stats['added']} 条 → {OUT}（累计 {payload.get('total', 0)} 次，自 {st['since']}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
