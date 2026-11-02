#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只推「文件」，不重算聚合：给一批前缀（学科桶 + 站点索引）打包成一个提交。

为什么要单独有这个脚本：
- `push_buckets.py` 每批都要先把远端 `data/topics.json`(9–10 MB) 拉下来当底再重算聚合，
  大文件常 `IncompleteRead`，且它的 ref 更新只在开头读一次 head —— 并行会话一推，
  末尾 `git/refs PATCH` 必然 422（实测连重试 8 次都 422），整批作废。
- 聚合若已由 `publish_aggregates.py` 单独发布过（本仓常态），这里就**只推分学科文件与站点索引**。

做法固定三步，且对 422（远端前移）自愈：
1. 读远端 head → 递归 tree → 算出「哪些文件内容真的变了」（用 git blob sha 对比，免重复上传）；
2. 变化的文件建 blob（已建的 sha 缓存在内存里，重试不重传）；
3. 建 tree（base_tree 取**当次**远端 head 的 tree）→ commit → PATCH ref；
   PATCH 报 422 就重读 head 再来一轮（最多 6 轮），blob 不重传。

用法:
    python3 scripts/push_prefix_robust.py --prefix data/math-bsd learn/data learn/exam/data \
        learn/index.json learn/exam/index.json diagnose/exam-index.json data/subjects.json \
        --message "feat(math-bsd): ..."
    python3 scripts/push_prefix_robust.py --prefix data/math-bsd --dry
"""
import argparse
import base64
import http.client
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "grantleyzyf-spec/cn-k12-dxyc2286"
API = "https://api.github.com"


def token():
    t = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    if not t:
        sys.exit("拿不到 gh token")
    return t


TOK = token()


def api(path, method="GET", payload=None, raw=False, tries=5):
    """带重试的 API 调用：大文件（>1 MB）常 IncompleteRead 断流，实测重试几次就能过。"""
    url = f"{API}/repos/{REPO}/{path}"
    body = json.dumps(payload).encode() if payload is not None else None
    last = None
    for k in range(tries):
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Authorization", f"Bearer {TOK}")
        req.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            return data if raw else json.loads(data)
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            print(f"    retry {k} {type(e).__name__}")
            time.sleep(2 + 3 * k)
    raise last


def blob_sha(data):
    h = __import__("hashlib").sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def collect(prefixes):
    out = {}
    for p in prefixes:
        full = os.path.join(ROOT, p)
        if os.path.isfile(full):
            out[p] = full
        elif os.path.isdir(full):
            for dp, _dn, fns in os.walk(full):
                for fn in fns:
                    if fn.startswith(".") or fn == ".DS_Store":
                        continue
                    fp = os.path.join(dp, fn)
                    out[os.path.relpath(fp, ROOT)] = fp
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", nargs="+", required=True)
    ap.add_argument("--message", default="chore: 同步分学科文件")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--max-round", type=int, default=6)
    a = ap.parse_args()

    files = collect(a.prefix)
    if not files:
        sys.exit("前缀没匹配到任何文件")
    print(f"[1] 本地文件 {len(files)} 个，共 {sum(os.path.getsize(p) for p in files.values())/1e6:.1f} MB")

    blobs = {}          # rel -> sha（重试轮次复用，不重传）
    for rnd in range(a.max_round):
        head = api("git/refs/heads/main")["object"]["sha"]
        tree = api(f"git/trees/{head}?recursive=1")
        remote = {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}
        todo = []
        for rel, fp in sorted(files.items()):
            data = open(fp, "rb").read()
            sha = blobs.get(rel)
            if sha is None:
                sha = blob_sha(data)
            if remote.get(rel) == sha:
                continue
            todo.append((rel, fp, data, sha))
        print(f"[2] 第{rnd+1}轮 head {head[:8]} · 待推 {len(todo)} 个（其余未变）")
        if not todo and rnd == 0:
            print("[3] 全部已是最新，无需提交")
            return 0
        if a.dry:
            for rel, _fp, _d, _s in todo[:20]:
                print("    ", rel)
            print("[dry] 未上传")
            return 0

        for i, (rel, fp, data, sha) in enumerate(todo, 1):
            if rel not in blobs:
                if rel.endswith(".json"):
                    json.loads(data)                 # 坏 JSON 早点炸，别推上去
                blobs[rel] = api("git/blobs", "POST",
                                 {"content": base64.b64encode(data).decode(), "encoding": "base64"})["sha"]
            if i % 50 == 0:
                print(f"    … blob {i}/{len(todo)}", flush=True)

        entries = [{"path": rel, "mode": "100644", "type": "blob", "sha": blobs[rel]} for rel, _f, _d, _s in todo]
        new_tree = api("git/trees", "POST", {"base_tree": tree["sha"], "tree": entries})["sha"]
        commit = api("git/commits", "POST", {"message": a.message, "tree": new_tree, "parents": [head]})["sha"]
        try:
            api("git/refs/heads/main", "PATCH", {"sha": commit, "force": False})
            print(f"[4] PUSHED {commit}")
            break
        except urllib.error.HTTPError as e:
            if e.code == 422:                        # 远端前移 → 重读 head 再来
                print(f"    422（远端已前移），第{rnd+1}轮重试")
                time.sleep(3)
                continue
            raise
    else:
        sys.exit("多轮仍被 422 拒绝，放弃")

    time.sleep(3)
    for p in a.prefix[:3]:
        if p.endswith(".json") and os.path.isfile(os.path.join(ROOT, p)):
            try:
                d = json.loads(api(f"contents/{p}?ref=main", raw=True))
                n = len(d) if isinstance(d, (list, dict)) else "?"
                print(f"[5] 线上 {p}: {n}")
            except Exception as e:                   # noqa: BLE001
                print(f"[5] !! {p} 回读失败 {type(e).__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
