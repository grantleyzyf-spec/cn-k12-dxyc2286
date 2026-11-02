#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单个小文件直接走 Contents API 提交（比 push_prefix_robust 拉全量 tree 快得多）。

用途：只改一个派生文件（如 data/stats.json）时，重读远端 sha → base64 PUT → 撞 409/422 就重读再试。
用法：python3 scripts/put_single_file.py data/stats.json "commit message"
"""
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "grantleyzyf-spec/cn-k12-dxyc2286"
API = "https://api.github.com"


def token():
    t = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    if not t:
        sys.exit("拿不到 gh token")
    return t


TOK = token()


def api(path, method="GET", payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{API}/repos/{REPO}/{path}", data=body, method=method)
    req.add_header("Authorization", f"Bearer {TOK}")
    req.add_header("Accept", "application/vnd.github+json")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main():
    path, msg = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "chore: 单文件更新")
    data = open(path, "rb").read()
    for rnd in range(6):
        try:
            cur = api(f"contents/{path}?ref=main")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            cur = None
        if cur and base64.b64decode(cur["content"].replace("\n", "")) == data:
            print("远端已一致，无需提交")
            return 0
        payload = {"message": msg, "content": base64.b64encode(data).decode(), "branch": "main"}
        if cur:
            payload["sha"] = cur["sha"]
        try:
            out = api(f"contents/{path}", "PUT", payload)
            print(f"[PUSHED] {path} → commit {out['commit']['sha'][:8]}")
            return 0
        except urllib.error.HTTPError as e:
            print(f"  retry {rnd}: HTTP {e.code}（远端被并行会话推进）")
            time.sleep(3 + 3 * rnd)
    print("6 轮仍失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
