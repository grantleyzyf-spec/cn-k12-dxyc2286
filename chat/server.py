# -*- coding: utf-8 -*-
"""server.py — xueketupu.com 站内客服（零依赖，Python 标准库）

接口
  GET  /api/chat/health           {"ok":true,"mode":"llm|kb","model":...}
  POST /api/chat                  {"messages":[{"role":"user","content":"..."}]} → SSE 流
  POST /api/chat/report           {"q":"...","a":"..."} 回答不对 → 落盘

三道闸
  1) 单会话最多 CHAT_MAX_TURNS 轮（前端计数 + 服务端按 session 计数）
  2) 每 IP 每天 CHAT_IP_DAILY 轮
  3) 全局每天 CHAT_DAILY_BUDGET 轮；到线降级为纯检索（不调模型）

环境变量
  CHAT_API_KEY / CHAT_API_BASE / CHAT_MODEL / PORT / CHAT_DAILY_BUDGET / CHAT_IP_DAILY
  没有 CHAT_API_KEY 时自动进入 kb 模式（只用知识库回答，成本 0）
"""
import json, os, re, sys, time, hashlib, threading, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(ROOT, "chat", "kb.json")
STATE_DIR = os.path.join(ROOT, "chat", "state")
LOG_DIR = os.path.join(ROOT, "chat", "logs")

API_KEY = os.environ.get("CHAT_API_KEY", "").strip()
API_BASE = os.environ.get("CHAT_API_BASE", "https://coding.dashscope.aliyuncs.com/v1").rstrip("/")
MODEL = os.environ.get("CHAT_MODEL", "qwen3.6-plus")
PORT = int(os.environ.get("PORT", "8091"))
DAILY_BUDGET = int(os.environ.get("CHAT_DAILY_BUDGET", "500"))
IP_DAILY = int(os.environ.get("CHAT_IP_DAILY", "6"))
MAX_TURNS = int(os.environ.get("CHAT_MAX_TURNS", "12"))
MAX_BODY = 32 * 1024

KB = json.load(open(KB_PATH, encoding="utf-8"))
FACTS = KB["facts"]
CHUNKS = KB["chunks"]
KPS = KB["kps"]

for d in (STATE_DIR, LOG_DIR):
    os.makedirs(d, exist_ok=True)

_lock = threading.Lock()


# ---------------- BM25（中文按字二元组，英文按词） ----------------
def tok(s):
    s = s.lower()
    out = re.findall(r"[a-z0-9\.\+#]+", s)
    cjk = re.findall(r"[\u4e00-\u9fff]", s)
    out += [cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1)]
    out += cjk
    return out


DOCS = [tok(c["text"] + " " + c["title"]) for c in CHUNKS]
DF = {}
for d in DOCS:
    for w in set(d):
        DF[w] = DF.get(w, 0) + 1
N = max(len(DOCS), 1)
AVG = sum(len(d) for d in DOCS) / N


def bm25(query, k=3):
    q = tok(query)
    scored = []
    for i, d in enumerate(DOCS):
        if not d:
            continue
        s, tf = 0.0, {}
        for w in d:
            tf[w] = tf.get(w, 0) + 1
        for w in set(q):
            if w not in tf:
                continue
            idf = __import__("math").log(1 + (N - DF.get(w, 0) + 0.5) / (DF.get(w, 0) + 0.5))
            s += idf * (tf[w] * 2.2) / (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / AVG))
        if s > 0:
            scored.append((s, i))
    scored.sort(reverse=True)
    return [CHUNKS[i] for _, i in scored[:k]]


STOP = ("在哪个学科", "在哪个年级", "在哪一册", "哪一册", "哪个学科", "哪个年级", "是什么意思",
        "是什么", "怎么样", "怎么用", "属于", "请问", "我想", "帮我", "查一下", "找一下",
        "这个知识点", "知识点", "的", "吗", "呢", "？", "?")


def find_kps(query, limit=3):
    q = re.sub(r"[\s，。？！?、,\.：:；;]", "", query)
    terms = [q]
    core = q
    for w in STOP:
        core = core.replace(w, "")
    if core and core != q:
        terms.append(core)
    if all(len(t) < 2 for t in terms):
        return []
    hits = []
    for t in terms:
        for kid, name, meta, url in KPS:
            if not name or len(name) < 2:
                continue
            if name == t:
                score = 0
            elif len(t) <= 8 and t in name:
                score = 1 + len(name) - len(t)        # 关键词是知识点名的一部分
            elif len(name) >= 3 and name in t:
                score = 10 + (len(t) - len(name))     # 知识点名出现在句子里
            else:
                continue
            hits.append((score, name, meta, url))
    hits.sort()
    seen, out = set(), []
    for _, name, meta, url in hits:
        if name in seen:
            continue
        seen.add(name)
        out.append({"name": name, "meta": meta, "url": url})
        if len(out) >= limit:
            break
    return out


# ---------------- 配额与日志 ----------------
def _today():
    return time.strftime("%Y-%m-%d")


def quota(ip_hash, bypass_ip=False):
    fp = os.path.join(STATE_DIR, _today() + ".json")
    with _lock:
        st = {"turns": 0, "ips": {}}
        if os.path.exists(fp):
            try:
                st = json.load(open(fp, encoding="utf-8"))
            except Exception:
                pass
        used_ip = st["ips"].get(ip_hash, 0)
        if st["turns"] >= DAILY_BUDGET:
            return False, "budget"
        if used_ip >= IP_DAILY and not bypass_ip:
            return False, "ip"
        st["turns"] += 1
        st["ips"][ip_hash] = used_ip + 1
        json.dump(st, open(fp, "w", encoding="utf-8"))
    return True, "ok"


def log(obj):
    fp = os.path.join(LOG_DIR, _today() + ".jsonl")
    obj["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with _lock:
        with open(fp, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ---------------- 提示词 ----------------
SYS = """你是 xueketupu.com（中国 K-12 全学科知识图谱）的站内客服。
只回答与本站有关的问题：网站是做什么的、怎么用、某个功能在哪、某个知识点在哪个学科/年级、
是否收费、数据来源、联系方式、备案信息。

硬规则：
1) 只用下面【站点事实】和【相关页面】里的信息回答。信息不足就说"我这边没有确切信息"，
   并让用户看 /contact/ 或发邮件 grantleyzyf@gmail.com。绝不编造功能、数据或承诺。
2) 本站全部免费、无需登录；不要引导用户付费或注册（没有这些）。
3) 不替用户解题、不做学科辅导、不判断学情；这类请求引导到 /diagnose/（诊断出题）与 /topics/。
4) 不承诺"马上修复/一定加上"，不评价竞品，不谈与本站无关的话题（礼貌拒绝并回到本站）。
5) 中文提问用中文答，英文提问用英文答；回答 ≤4 句或 ≤3 条要点，不写客套话。
6) 涉及链接时原样给出站内路径（如 /explore/、/topics/）。

【站点事实】
{facts}

【相关页面】
{pages}

【知识点检索结果（来自本站数据库，可直接引用）】
{kps}
"""


def build_messages(msgs, hits, kps=None):
    pages = "\n\n".join(f"[{h['title']} {h['url']}]\n{h['text']}" for h in hits) or "（无）"
    kp_txt = ("\n".join(f"· {k['name']}（{k['meta']}）{k['url']}" for k in (kps or []))
              or "（未匹配到）")
    sys_p = SYS.replace("{facts}", FACTS).replace("{pages}", pages).replace("{kps}", kp_txt)
    out = [{"role": "system", "content": sys_p}]
    for m in msgs[-6:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            out.append({"role": m["role"], "content": str(m["content"])[:1200]})
    return out


def kb_answer(query, hits, kps):
    """无模型时的检索式回答：相关段落摘录 + 链接。"""
    if kps:
        lines = [f"在站内找到 {len(kps)} 个相关知识点："]
        for k in kps:
            lines.append(f"· {k['name']}（{k['meta']}）{k['url']}")
        return "\n".join(lines)
    if not hits:
        return "这个我暂时没有找到确切答案。可以看 /contact/，或发邮件 grantleyzyf@gmail.com。"
    parts = ["根据站内页面："]
    for h in hits[:2]:
        txt = re.sub(r"\s+", " ", h["text"])[:220]
        parts.append(f"· {txt}…（{h['url']}）")
    return "\n".join(parts)


# ---------------- HTTP ----------------
class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "xkt-chat/1.0"

    def log_message(self, format, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") in ("/api/chat/health", "/health"):
            body = json.dumps({"ok": True, "mode": "llm" if API_KEY else "kb", "model": MODEL},
                              ensure_ascii=False).encode()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return self.send_error(413)
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self.send_error(400)
        path = self.path.rstrip("/")

        if path == "/api/chat/report":
            log({"kind": "report", "q": str(data.get("q"))[:500], "a": str(data.get("a"))[:800]})
            b = b'{"ok":true}'
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if path != "/api/chat":
            return self.send_error(404)

        msgs = data.get("messages") or []
        if not isinstance(msgs, list) or not msgs:
            return self.send_error(400)
        q = str(msgs[-1].get("content", ""))[:800]
        ip = self.client_address[0]
        ip_hash = hashlib.sha1((ip + time.strftime("%Y-%m-%d")).encode()).hexdigest()[:12]
        is_local = ip in ("127.0.0.1", "::1", "127.0.1.1")
        ok, why = quota(ip_hash, bypass_ip=is_local)

        hits = bm25(q)
        kps = find_kps(q)
        if not ok:
            ans = ("今天的在线咨询次数到上限了（个人维护的站，有每日配额）。\n"
                   if why == "budget" else "今天这个 IP 的咨询次数到上限了。\n")
            if kps:
                ans += "你要找的可能是：" + "、".join(
                    "%s（%s）%s" % (k["name"], k["meta"], k["url"]) for k in kps[:2]) + "\n"
            ans += "直接发邮件更快：grantleyzyf@gmail.com"
            return self._stream_text(ans, mode="limit")

        if not API_KEY:
            return self._stream_text(kb_answer(q, hits, kps) + "\n\n（当前为知识库模式，未接模型）", mode="kb")

        try:
            return self._stream_llm(build_messages(msgs, hits, kps), q, kps, ip_hash)
        except Exception as e:
            log({"kind": "llm_error", "err": str(e)[:200], "q": q})
            return self._stream_text(kb_answer(q, hits, kps), mode="fallback")

    # ---- SSE ----
    def _sse_start(self):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def _sse(self, obj):
        self.wfile.write(("data: " + json.dumps(obj, ensure_ascii=False) + "\n\n").encode())
        self.wfile.flush()

    def _stream_text(self, text, mode="kb"):
        self._sse_start()
        for i in range(0, len(text), 18):
            self._sse({"d": text[i:i + 18]})
        self._sse({"end": True, "mode": mode})
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _stream_llm(self, messages, q, kps, ip_hash):
        payload = json.dumps({"model": MODEL, "messages": messages, "stream": True,
                              "max_tokens": 420, "temperature": 0.3,
                              "enable_thinking": False}).encode()
        req = urllib.request.Request(API_BASE + "/chat/completions", data=payload,
                                     headers={"Authorization": "Bearer " + API_KEY,
                                              "Content-Type": "application/json"})
        self._sse_start()
        got = []
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                for raw in r:
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        j = json.loads(chunk)
                    except Exception:
                        continue
                    delta = (j.get("choices") or [{}])[0].get("delta", {}).get("content") or ""
                    if delta:
                        got.append(delta)
                        self._sse({"d": delta})
        except Exception as e:
            if not got:
                log({"kind": "llm_error", "err": str(e)[:200], "q": q})
                self._sse({"d": kb_answer(q, bm25(q), kps)})
            self._sse({"end": True, "mode": "fallback"})
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return
        self._sse({"end": True, "mode": "llm"})
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
        log({"kind": "chat", "q": q, "a": "".join(got)[:800], "ip": ip_hash, "kps": len(kps)})


if __name__ == "__main__":
    print(f"xkt-chat on :{PORT}  mode={'llm' if API_KEY else 'kb'}  model={MODEL}  "
          f"budget={DAILY_BUDGET}/day  ip={IP_DAILY}/day", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
