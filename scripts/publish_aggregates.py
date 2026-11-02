#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「全库聚合并集」重算并单独发布（Git Data API）。

背景（必读）
  原 push_buckets.py 只把派生文件（stats / standards / volume-map）登记进待推列表，
  聚合三件套（data/topics.json、data/questions.json、data/dependencies.json）写到临时树后
  **从未进 files** ⇒ 远端聚合长期停在旧值（实测：远端 topics 4957，而 stats 却是 5458，
  两者互相矛盾；苏教/苏科/沪教/冀教的点在线上全部缺失）。
  本脚本按「所有本地桶的并集」重算聚合，再单独提交这 5 个文件，避免下次再被覆盖。

用法
  python3 scripts/publish_aggregates.py            # 重算 + 提交 + 回读校验
  python3 scripts/publish_aggregates.py --dry      # 只算不推
"""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "grantleyzyf-spec/cn-k12-dxyc2286"
DATA = os.path.join(ROOT, "data")


def token():
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()


def api(path, method="GET", payload=None, raw=False, tries=8, timeout=900):
    """与 push_buckets.py 同一套上传通道（urllib + 重试 + gzip）。

    ⛔ 不要换成 `gh api -X POST git/blobs`：大 blob（26 MB 的 questions.json）
    走 gh 会 422 Validation Failed，必须用 urllib 直传。
    """
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{REPO}/{path}",
                data=json.dumps(payload).encode() if payload is not None else None,
                method=method)
            req.add_header("Authorization", f"Bearer {token()}")
            req.add_header("X-GitHub-Api-Version", "2022-11-28")
            req.add_header("Accept-Encoding", "gzip")
            if raw:
                req.add_header("Accept", "application/vnd.github.raw")
            if payload is not None:
                req.add_header("Content-Type", "application/json")
            resp = urllib.request.urlopen(req, timeout=timeout)
            body = resp.read()
            if body[:2] == b"\x1f\x8b":
                body = gzip.decompress(body)
            if raw:
                return body
            return json.loads(body or b"{}")
        except Exception as e:                     # noqa: BLE001
            last = e
            print(f"    retry {i} {type(e).__name__}: {str(e)[:80]}", flush=True)
            time.sleep(min(2 ** i, 20))
    raise RuntimeError(f"{method} {path} 失败：{last}")



def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--prune", default="", help="逗号分隔的 topic id：远端独有但确认要删（如目录页脏点），不再当孤儿保留")
    ap.add_argument("--message", default="fix(data): 重算全库聚合并集（补回苏教/苏科/沪教/冀教等被漏掉的点）")
    a = ap.parse_args()

    # ---------- 1. 本地桶清单 ----------
    buckets = []
    for d in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, d, "topics.json")
        if os.path.isfile(p):
            buckets.append(d)
    print(f"[1] 本地桶 {len(buckets)} 个")

    spec = importlib.util.spec_from_file_location("nz", os.path.join(ROOT, "scripts/normalize_to_ref_schema.py"))
    nz = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nz)

    # ---------- 2. 并集归一 ----------
    agg_t, agg_q, agg_d = [], [], []
    seen_t = set()
    for b in buckets:
        topics = json.load(open(os.path.join(DATA, b, "topics.json"), encoding="utf-8"))
        qs = json.load(open(os.path.join(DATA, b, "questions.json"), encoding="utf-8"))
        deps = json.load(open(os.path.join(DATA, b, "dependencies.json"), encoding="utf-8"))
        qmap = {}
        nq = [nz.norm_question(q, b) for q in qs]
        for q in nq:
            qmap.setdefault(q["topicId"], q)
        nt = [nz.norm_topic(t, b, qmap) for t in topics]
        ids = {t["id"] for t in nt}
        nd = []
        for dp in deps:
            if dp.get("from") not in ids or dp.get("to") not in ids:
                continue
            ty = (dp.get("type") or "hard").strip().lower()
            nd.append({"from": dp["from"], "to": dp["to"], "type": ty if ty in ("hard", "soft") else "hard"})
        dup = seen_t & ids
        if dup:
            print(f"    !! {b} 与前面的桶有 {len(dup)} 个重号 id，保留先出现的")
        nt = [t for t in nt if t["id"] not in seen_t]
        seen_t |= {t["id"] for t in nt}
        agg_t += nt
        agg_q += nq
        agg_d += nd
        print(f"    + {b}: {len(nt)} 点 / {len(nq)} 题 / {len(nd)} 边")

    # ---------- 3. 远端独有的点：不丢（孤儿保护） ----------
    tree = api("git/trees/main?recursive=1")
    sha = {e["path"]: e["sha"] for e in tree["tree"]}
    remote_t = json.loads(api(f"git/blobs/{sha['data/topics.json']}", raw=True))
    remote_q = json.loads(api(f"git/blobs/{sha['data/questions.json']}", raw=True))
    local_ids = seen_t
    prune = {x.strip() for x in (a.prune or "").split(",") if x.strip()}
    if prune:
        before = len(agg_t)
        agg_t = [t for t in agg_t if t["id"] not in prune]
        agg_q = [q for q in agg_q if q.get("topicId") not in prune]
        keep = {t["id"] for t in agg_t}
        agg_d = [d for d in agg_d if d.get("from") in keep and d.get("to") in keep]
        gone = [t["id"] for t in remote_t if t["id"] in prune]
        print(f"[3] 按 --prune 删除 {len(gone)} 点（{gone[:12]}）｜聚合点 {before} → {len(agg_t)}")
    orphan_t = [t for t in remote_t if t["id"] not in local_ids and t["id"] not in prune]
    if orphan_t:
        print(f"[3] 远端独有 {len(orphan_t)} 点，保留：{[t['id'] for t in orphan_t][:8]}")
        agg_t += orphan_t
        oids = {t["id"] for t in orphan_t}
        agg_q += [q for q in remote_q if q.get("topicId") in oids]
    print(f"[3] 并集：{len(agg_t)} 点 / {len(agg_q)} 题 / {len(agg_d)} 边（远端原为 {len(remote_t)} 点 / {len(remote_q)} 题）")
    if len(agg_t) < len(remote_t) - len(prune):
        print("!! 并集比远端还少，拒绝推送")
        return 2

    # ---------- 4. 落盘 + 派生 ----------
    for rel, obj in (("data/topics.json", agg_t), ("data/questions.json", agg_q),
                     ("data/dependencies.json", agg_d)):
        json.dump(obj, open(os.path.join(ROOT, rel), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    by_sub = {}
    for t in agg_t:
        by_sub.setdefault(t.get("subject") or "unknown", []).append(t)
    for sub, arr in by_sub.items():
        d = os.path.join(DATA, sub)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "topics.json")
        cur = json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else []
        if len(cur) != len(arr):      # 只补孤儿，不覆盖桶里更细的版本
            extra = [t for t in arr if t["id"] not in {x["id"] for x in cur}]
            if extra:
                json.dump(cur + extra, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                print(f"    ↳ {sub} 桶补孤儿 {len(extra)} 点")
    for s in ("build_stats.py", "build_standards_index.py"):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", s)] + (["--write"] if s == "build_stats.py" else []),
                           cwd=ROOT, capture_output=True, text=True)
        print(f"    {s} rc={r.returncode} {(r.stdout or r.stderr).strip().splitlines()[-1][:90] if (r.stdout or r.stderr).strip() else ''}")
    print(f"    ↳ 分学科 {len(by_sub)} 科")

    files = {rel: os.path.join(ROOT, rel) for rel in
             ("data/topics.json", "data/questions.json", "data/dependencies.json",
              "data/stats.json", "data/cn-curriculum-standards.json")}
    if a.dry:
        for rel, p in files.items():
            print(f"[dry] {rel} {os.path.getsize(p)/1e6:.2f} MB")
        return 0

    # ---------- 5. 提交 ----------
    head = api("git/refs/heads/main")["object"]["sha"]
    base_tree = api(f"git/commits/{head}")["tree"]["sha"]
    entries = []
    for rel, p in sorted(files.items()):
        data = open(p, "rb").read()
        json.loads(data) if rel.endswith(".json") else None
        s = api("git/blobs", "POST", {"content": base64.b64encode(data).decode(), "encoding": "base64"})["sha"]
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": s})
        print(f"    ↑ blob {rel} {len(data)/1e6:.2f} MB")
    tree_sha = api("git/trees", "POST", {"base_tree": base_tree, "tree": entries})["sha"]
    commit = api("git/commits", "POST", {"message": a.message, "tree": tree_sha, "parents": [head]})["sha"]
    api("git/refs/heads/main", "PATCH", {"sha": commit, "force": False})
    print(f"[5] PUSHED {commit}")

    # ---------- 6. 回读 ----------
    time.sleep(4)
    tree2 = api("git/trees/main?recursive=1")
    sha2 = {e["path"]: e["sha"] for e in tree2["tree"]}
    rt = json.loads(api(f"git/blobs/{sha2['data/topics.json']}", raw=True))
    rq = json.loads(api(f"git/blobs/{sha2['data/questions.json']}", raw=True))
    rs = json.loads(api(f"git/blobs/{sha2['data/stats.json']}", raw=True))
    print(f"[6] 线上 topics {len(rt)} | questions {len(rq)} | stats {rs.get('subjects')} 科 / {rs.get('topics')} 点 / {rs.get('questions')} 题 / {rs.get('dependencies')} 边")
    ok = len(rt) == len(agg_t) and len(rq) == len(agg_q)
    print("[6] 一致" if ok else "!! 线上与并集不一致")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
