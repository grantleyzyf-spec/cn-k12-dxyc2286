# -*- coding: utf-8 -*-
"""数学自适应诊断答题站（本地单机版，只用标准库）。

启动：  python3 webapp/app.py            # 默认 http://127.0.0.1:8848
换端口：python3 webapp/app.py 9000

能力
- 选卷答题：读 data/math/exams 下所有卷（按册分组）
- 自动判题：choice/multi/fill/numeric 机判；solve 走「对评分标准自评」
- 诊断报告：按知识点算得分率 → 掌握/待巩固/未掌握/未涉及；未掌握时查前置点得分率，
  前置也低则判「前置缺口」；同时给出该知识点的错因标签
- 补练：按每题 reteach（题库同点题）自动组补练清单

数据依赖（都由仓内脚本生成，勿手改）
- data/math/exams/<册>/<卷>.json          卷面（含 examId/itemId/prereq/reteach）
- data/math/topics.json                   知识点（name/chapter/prerequisites/diagnostic_question/misconceptions）
- data/math/questions.json                题库（补练用）
- data/math/topic_exam_map.json           知识点 → itemId 反查
作答记录：data/math/attempts.db（SQLite，自动建）
"""
import json
import os
import re
import sqlite3
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
D = os.path.join(REPO, "data", "math")
STATIC = os.path.join(ROOT, "static")
DB = os.path.join(D, "attempts.db")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8848

CACHE = {}


def load(name, key=None):
    p = os.path.join(D, name)
    mt = os.path.getmtime(p)
    c = CACHE.get(p)
    if c and c[0] == mt:
        return c[1]
    obj = json.load(open(p, encoding="utf-8"))
    CACHE[p] = (mt, obj)
    return obj


def topics():
    return {t["id"]: t for t in load("topics.json")}


def papers():
    out = []
    base = os.path.join(D, "exams")
    for book in sorted(os.listdir(base)):
        d = os.path.join(base, book)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            ex = json.load(open(os.path.join(d, fn), encoding="utf-8"))
            out.append({"examId": ex["examId"], "book": book, "paper": ex["paper"],
                        "kind": ex["kind"], "fullScore": ex["fullScore"],
                        "duration": ex["duration"], "grade": ex["grade"],
                        "stage": ex["stage"], "scope": ex.get("scope") or [],
                        "itemCount": sum(len(s["items"]) for s in ex["sections"])})
    order = {"unit": 0, "midterm": 1, "final": 2}
    out.sort(key=lambda x: (x["book"], order.get(x["kind"], 9), x["paper"]))
    return out


def find_exam(exam_id):
    for p in papers():
        if p["examId"] == exam_id:
            ex = json.load(open(os.path.join(D, "exams", p["book"], p["paper"] + ".json"), encoding="utf-8"))
            return ex
    return None


def paper_view(ex):
    """给前端的卷面：不含 answer/analysis（防泄题）"""
    secs = []
    for s in ex["sections"]:
        items = []
        for it in s["items"]:
            items.append({"no": it["no"], "itemId": it.get("itemId"), "type": it["type"],
                          "score": it["score"], "stem": it["stem"],
                          "options": it.get("options") or []})
        secs.append({"title": s["title"], "rule": s["rule"], "items": items})
    return {"examId": ex["examId"], "book": ex["book"], "paper": ex["paper"],
            "duration": ex["duration"], "fullScore": ex["fullScore"],
            "scope": ex.get("scope") or [], "sections": secs}


# ---------- 判题 ----------
def norm_ans(s):
    s = (s or "").strip()
    s = s.replace("　", " ").replace("，", ",").replace("。", ".")
    s = re.sub(r"\s+", "", s)
    return s.replace("－", "-").replace("−", "-").replace("×", "*").replace("÷", "/")


NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")


def to_num(s):
    s = norm_ans(s).replace("%", "")
    if NUM_RE.match(s):
        return float(s)
    m = re.match(r"^(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)$", s)
    if m:
        d = float(m.group(2))
        return float(m.group(1)) / d if d else None
    return None


def judge(item, resp):
    """→ (是否对, 判题说明)"""
    t = item["type"]
    if t == "choice":
        return norm_ans(resp).upper() == norm_ans(item["answer"]).upper(), "选择"
    if t == "multi":
        return set(norm_ans(resp).upper()) == set(norm_ans(item["answer"]).upper()), "多选（须全对）"
    if t == "numeric":
        a, b = to_num(resp), to_num(item["answer"])
        if a is not None and b is not None:
            return abs(a - b) <= 1e-6, "数值"
        return norm_ans(resp) == norm_ans(item["answer"]), "数值（按文本比对）"
    if t == "fill":
        alts = re.split(r"[或/]", item["answer"]) if item["answer"] else [""]
        got = norm_ans(resp)
        return any(got == norm_ans(x) for x in alts), "填空"
    return False, "解答题（需自评）"


def ensure_db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id TEXT, book TEXT, paper TEXT,
        created TEXT DEFAULT (datetime('now','localtime')),
        full_score REAL, earned REAL, payload TEXT)""")
    c.commit()
    return c


# ---------- 诊断 ----------
def report(ex, answers, self_scores, earned_map):
    T = topics()
    per_topic = {}
    for s in ex["sections"]:
        for it in s["items"]:
            no = it["no"]
            r = answers.get(str(no), "")
            ok, how = judge(it, r)
            if it["type"] == "solve":
                sc = float(self_scores.get(str(no), 0) or 0)
                sc = max(0.0, min(sc, float(it["score"])))
                got = sc
            else:
                got = float(it["score"]) if ok else 0.0
            for tid in it.get("topicIds") or []:
                b = per_topic.setdefault(tid, {"earned": 0.0, "total": 0.0, "items": [], "wrong": []})
                b["earned"] += got / max(1, len(it.get("topicIds") or [1]))
                b["total"] += float(it["score"]) / max(1, len(it.get("topicIds") or [1]))
                b["items"].append(no)
                if got < float(it["score"]) - 1e-9:
                    b["wrong"].append(no)
            earned_map[no] = {"got": got, "full": it["score"], "type": it["type"],
                              "ok": ok, "how": how, "resp": r}
    rows = []
    for tid, b in per_topic.items():
        t = T.get(tid, {})
        rate = b["earned"] / b["total"] if b["total"] else 0.0
        if rate >= 0.8:
            verdict = "掌握"
        elif rate >= 0.6:
            verdict = "待巩固"
        else:
            verdict = "未掌握"
        prereq_gap, prereq_unknown = [], []
        if verdict != "掌握":
            for p in t.get("prerequisites") or []:
                pb = per_topic.get(p)
                if pb and pb["total"]:
                    r0 = pb["earned"] / pb["total"]
                    if r0 < 0.5:
                        prereq_gap.append({"topicId": p, "name": T.get(p, {}).get("name", p),
                                           "rate": round(r0, 2)})
                else:
                    # 前置点本卷没考 ⇒ 不能断言它是缺口，但也提示「先探一下」
                    prereq_unknown.append({"topicId": p, "name": T.get(p, {}).get("name", p)})
        rows.append({
            "topicId": tid, "name": t.get("name", tid),
            "chapter": t.get("chapter", ""),
            "earned": round(b["earned"], 1), "total": round(b["total"], 1),
            "rate": round(rate, 4), "verdict": "前置缺口" if prereq_gap else verdict,
            "prereqGap": prereq_gap,
            "prereqUnknown": prereq_unknown,
            "wrongItems": sorted(set(b["wrong"])),
            "misconceptions": (t.get("misconceptions") or [])[:3],
            "diagnostic": (t.get("diagnostic_question") or {}).get("question", ""),
            "prereqNames": [T.get(p, {}).get("name", p) for p in (t.get("prerequisites") or [])][:3],
        })
    rank = {"前置缺口": 0, "未掌握": 1, "待巩固": 2, "掌握": 3}
    rows.sort(key=lambda r: (rank.get(r["verdict"], 9), r["rate"]))
    return rows


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(STATIC, "index.html"), encoding="utf-8").read(),
                              "text/html; charset=utf-8")
        if u.path.startswith("/static/"):
            p = os.path.join(STATIC, os.path.basename(u.path))
            if not os.path.exists(p):
                return self._send(404, {"error": "not found"})
            ct = "text/css" if p.endswith(".css") else "application/javascript; charset=utf-8"
            return self._send(200, open(p, encoding="utf-8").read(), ct)
        if u.path == "/api/papers":
            return self._send(200, papers())
        if u.path == "/api/paper":
            ex = find_exam(q.get("examId", [""])[0])
            return self._send(200, paper_view(ex)) if ex else self._send(404, {"error": "no such exam"})
        if u.path == "/api/topics":
            return self._send(200, {k: {"name": v["name"], "chapter": v.get("chapter"),
                                        "prerequisites": v.get("prerequisites") or []}
                                    for k, v in topics().items()})
        if u.path == "/api/report":
            c = ensure_db()
            row = c.execute("SELECT payload FROM attempts WHERE id=?", (q.get("attempt", ["0"])[0],)).fetchone()
            if not row:
                return self._send(404, {"error": "no such attempt"})
            return self._send(200, json.loads(row[0]))
        if u.path == "/api/practice":
            c = ensure_db()
            row = c.execute("SELECT payload FROM attempts WHERE id=?", (q.get("attempt", ["0"])[0],)).fetchone()
            if not row:
                return self._send(404, {"error": "no such attempt"})
            rep = json.loads(row[0])
            bank = {q["id"]: q for q in load("questions.json")}
            tmap = load("topic_exam_map.json")
            out = []
            for r in rep["diagnosis"]:
                if r["verdict"] == "掌握":
                    continue
                pool = []
                for tid in [r["topicId"]] + [p["topicId"] for p in r["prereqGap"]]:
                    for iid in tmap.get(tid, []):
                        pass
                # 取该知识点题库同点题（题库题 id 形如 <topicId>_qN 或 mat_hqNNN，用 topicId 字段精确取）
                targets = [r["topicId"]] + [p["topicId"] for p in r["prereqGap"]]
                probes = [p["topicId"] for p in (r.get("prereqUnknown") or [])]
                for q in bank.values():
                    if q.get("topicId") in targets:
                        pool.append(q)
                    elif q.get("topicId") in probes and q.get("difficulty") == "basic":
                        # 前置点本卷未考：只给 1 道基础题当探针，用来判断是不是前置没打好
                        if not any(x.get("probe") and x["topicId"] == q["topicId"] for x in pool):
                            pool.append(dict(q, probe=True))
                uniq, seen = [], set()
                for q in pool:
                    if q["id"] in seen:
                        continue
                    seen.add(q["id"])
                    uniq.append({"qid": q["id"], "topicId": q["topicId"], "type": q["type"],
                                 "difficulty": q.get("difficulty"), "prompt": q["prompt"],
                                 "options": q.get("options") or [], "answer": q.get("answer"),
                                 "analysis": q.get("explanation", ""), "probe": bool(q.get("probe"))})
                out.append({"topicId": r["topicId"], "name": r["name"], "verdict": r["verdict"],
                            "misconceptions": r["misconceptions"], "items": uniq[:5]})
            return self._send(200, {"examId": rep["examId"], "practice": out})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        if u.path != "/api/submit":
            return self._send(404, {"error": "not found"})
        ex = find_exam(body.get("examId", ""))
        if not ex:
            return self._send(404, {"error": "no such exam"})
        answers = body.get("answers") or {}
        self_scores = body.get("selfScores") or {}
        earned = {}
        diag = report(ex, answers, self_scores, earned)
        total = sum(float(s_it["score"]) for s in ex["sections"] for s_it in s["items"])
        got = sum(v["got"] for v in earned.values())
        payload = {"examId": ex["examId"], "book": ex["book"], "paper": ex["paper"],
                   "earned": round(got, 1), "fullScore": total,
                   "rate": round(got / total, 4) if total else 0,
                   "items": earned, "diagnosis": diag}
        c = ensure_db()
        cur = c.execute("INSERT INTO attempts(exam_id,book,paper,full_score,earned,payload) VALUES(?,?,?,?,?,?)",
                        (ex["examId"], ex["book"], ex["paper"], total, round(got, 1),
                         json.dumps(payload, ensure_ascii=False)))
        c.commit()
        payload["attempt"] = cur.lastrowid
        return self._send(200, payload)


def main():
    ensure_db()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"数学自适应诊断答题站已启动： http://127.0.0.1:{PORT}")
    print(f"卷数 {len(papers())} · 知识点 {len(topics())} · 数据库 {DB}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
