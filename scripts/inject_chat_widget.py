# -*- coding: utf-8 -*-
"""inject_chat_widget.py — 给全站 HTML 注入客服挂件（幂等）

插入 <link chat-widget.css> 与 <script chat-widget.js defer> 到 </body> 前。
已注入的页面跳过。生成器重新出页后，再跑一次本脚本即可。
"""
import os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"out", "dist", ".git", "node_modules", "chat", "scripts", "deploy", "screenshots", "data", "assets"}
SNIP = ('<link rel="stylesheet" href="/assets/chat-widget.css">\n'
        '<script src="/assets/chat-widget.js" defer></script>\n')

done = skipped = failed = 0
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not f.endswith(".html"):
            continue
        fp = os.path.join(base, f)
        try:
            s = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            failed += 1
            continue
        if "chat-widget.js" in s:
            skipped += 1
            continue
        i = s.rfind("</body>")
        if i < 0:
            skipped += 1
            continue
        open(fp, "w", encoding="utf-8").write(s[:i] + SNIP + s[i:])
        done += 1

print(f"injected={done} skipped={skipped} unreadable={failed}")
