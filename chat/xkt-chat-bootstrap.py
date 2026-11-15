#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xueketupu.com 站内客服 · 单文件自举安装器

    sudo python3 xkt-chat-bootstrap.py            # 安装/更新（缺 key 时会提示输入）
    sudo python3 xkt-chat-bootstrap.py status     # 看状态
    sudo python3 xkt-chat-bootstrap.py uninstall  # 卸载

做的事：解包 → 建知识库 → 写 /etc/xkt-chat.env → 装 systemd → 配 nginx（含全站注入）→ 自检
不依赖 ssh、不依赖 git、不联网下载。
"""
import base64, getpass, io, json, os, re, shutil, subprocess, sys, tarfile, time, urllib.request

ROOT = "/var/www/k12"
ENVF = "/etc/xkt-chat.env"
UNIT = "/etc/systemd/system/xkt-chat.service"
NGSNIP = "/etc/nginx/snippets/k12-chat.conf"
NGCONF = "/etc/nginx/conf.d/k12.conf"
SVC = "xkt-chat"
SPACEY = (" ", chr(9), chr(13), chr(10))

PAYLOAD_B64 = """
H4sIAKR4+WoAA+19a3sTR9Loftav6AzJayno7guOjMhCgMBJAmxM3t0c2+tHlka2sCwJzQjba/w8JuFig8Em4W7ugUASsElI
wNgYnmfff5J4JPlTzk84VdU9V41syCbs+57D7AZrZrqrq6urq6uqq3qCoT/94Vc4HN7Q3Mzobwv/C5f+l99EmqMbWqIbmqJN
TSwciTSGW/7Emv941P70p5KiJoqASgJab3knWrfcYJ8sZ1eBY+8U+93x/IOuYCjZl1D/WCZ4+fGPRqPNr8f/VVzBUEouZPPD
fyQH/IbxbwlHX4//q7iCISVZzBRU5Q9kgN8w/hs2vJ7/r+QKhhKKIv+hw/+b5n8k/Hr8X8VljD+qAYHBTKpXVoP7lN+1DaBH
CwxrnfGHpT7a7Bj/5sbmpj+x8O+KRZ3r//PxD73N7CPPfh47w4ZKcr+slgqlYDI/wCrfXdSOHtFmb5YvnyxPfra8+OjXp+Mr
M4+Wn12p/nTu16cTHvY206ZPVb6b+/XppT272/eyUKKQIZaCku3t26DMr09nludPalNzlTN3y+cfVY99qx2/u3LxZGXhzvL8
AsCvLM2y7Zv/8svYZwAu5PGmS7mkmsnnmNfHRjyMZdLMO5jJpfKDwe7uoX71PYD+YT6RklM+VgRki7k2KOVegsWZWizJbR4o
cSBRZNs+2rzzQ3go9RYTOTUrD/9jOP3n3oFEJosdltpEsc17dmIhozPGi482/6177ycf72qH15GoARbQhwcdcMdYh1R9fnF5
/tvK0mmgX/nCnHbo0vLi2PKT8cqlw5KfSXYaQ4Hl+fvazBL7IBCJMu3IXe3+15U7pyvXblfnjmozz6oPvgfilo8f508qnz35
ZeyQdmR8+fmsduRh5eEi3FbnjpfP3V+5eUH7YrI696x8/Vj5yo3KzGz1+dXy+PTy/Jj29Drg8+vTSRyEK7e12UvLSye1+99o
96d/GZvUTt7QLt/VvvwWSpbv3/5l7CQMBmCy8vld7cjJ6o9PoCKMIdStXFzUls7CW6nLL3pbHjuFfTtzF/u2PD8BAADfn09f
ZwCTheQh0DKLcoiVJyd4z8oTz7TxB9rSl9rESaNPwCU/n77B4AULpTKJ3lxegTorYxPa7OeI9sPFyuK18g/PrR3Xno1pM1er
z5eggDZ+Xju2UL48BoxW/XypfOIc8GX1yHOgOXSwfP2JNnMd+qU9eQTFgFDU3k0GaLNQVk4UcyFWfXyNhdR8IZNU4ObG7ers
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
"""


def sh(cmd, check=False, capture=True, timeout=300):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout)
    if check and r.returncode != 0:
        print("!! 失败:", cmd)
        print((r.stdout or "") + (r.stderr or ""))
        sys.exit(1)
    return r


def need_root():
    if os.geteuid() != 0:
        sys.exit("需要 root：请用 sudo python3 " + os.path.basename(__file__))


def unpack():
    print("== 1/6 解包 ==")
    raw = base64.b64decode("".join(PAYLOAD_B64.split()))
    os.makedirs(ROOT, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        names = tf.getnames()
        tf.extractall(ROOT)
    for rel in ("chat/server.py", "chat/build_kb.py", "assets/chat-widget.js",
                "assets/chat-widget.css", "deploy/chat/chat.conf", "deploy/chat/xkt-chat.service",
                "chat/selftest.py"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            sys.exit("解包缺文件: " + p)
    os.chmod(os.path.join(ROOT, "scripts/deploy-chat.sh"), 0o755)
    print("   已就位 %d 个条目" % len(names))


def env_file():
    print("== 2/6 环境变量 ==")
    cur = {}
    if os.path.exists(ENVF):
        for ln in open(ENVF, encoding="utf-8"):
            if "=" in ln and not ln.strip().startswith("#"):
                k, v = ln.strip().split("=", 1)
                cur[k] = v
    if not cur.get("CHAT_API_KEY"):
        print("   需要一个 DeepSeek API key（platform.deepseek.com → API keys）")
        k = getpass.getpass("   CHAT_API_KEY (输入不回显，直接回车则跳过): ").strip()
        if k:
            cur["CHAT_API_KEY"] = k
    cur.setdefault("CHAT_API_BASE", "https://api.deepseek.com")
    cur.setdefault("CHAT_MODEL", "deepseek-chat")
    cur.setdefault("PORT", "8091")
    cur.setdefault("CHAT_DAILY_BUDGET", "500")
    cur.setdefault("CHAT_IP_DAILY", "6")
    cur.setdefault("CHAT_MAX_TURNS", "12")
    lines = ["# xueketupu.com 客服环境变量（600 权限，勿入库）"]
    lines += ["%s=%s" % (k, cur[k]) for k in
              ("CHAT_API_KEY", "CHAT_API_BASE", "CHAT_MODEL", "PORT",
               "CHAT_DAILY_BUDGET", "CHAT_IP_DAILY", "CHAT_MAX_TURNS")]
    with open(ENVF, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENVF, 0o600)
    print("   写入 %s（key %s）" % (ENVF, "已配置" if cur.get("CHAT_API_KEY") else "为空→服务将以检索模式运行"))


def build_kb():
    print("== 3/6 知识库 ==")
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    r = subprocess.run(["python3", os.path.join(ROOT, "chat/build_kb.py"), ROOT],
                       capture_output=True, text=True, env=env, timeout=600)
    print("   " + (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else "   （无输出）")
    for d in ("chat/state", "chat/logs"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    sh("chown -R www-data:www-data %s/chat/state %s/chat/logs" % (ROOT, ROOT))


def systemd():
    print("== 4/6 systemd ==")
    shutil.copy(os.path.join(ROOT, "deploy/chat/xkt-chat.service"), UNIT)
    sh("systemctl daemon-reload", check=True)
    sh("systemctl enable %s >/dev/null 2>&1" % SVC)
    sh("systemctl restart %s" % SVC)
    time.sleep(1.2)
    st = sh("systemctl is-active %s" % SVC).stdout.strip()
    print("   状态: " + st)
    if st != "active":
        print(sh("journalctl -u %s -n 20 --no-pager" % SVC).stdout)


def _blocks(s):
    out, i, n = [], 0, len(s)
    while i < n:
        k = s.find("server", i)
        if k < 0:
            break
        j = k + 6
        while j < n and s[j] in SPACEY:
            j += 1
        if j < n and s[j] == "{":
            depth, j = 1, j + 1
            while j < n and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1
            out.append((k, j))
            i = j
        else:
            i = k + 6
    return out


def _has443(blk):
    for line in blk.splitlines():
        t = line.strip()
        if t.startswith("listen") and "443" in t:
            return True
    return False


def _sname(blk):
    for line in blk.splitlines():
        t = line.strip()
        if t.startswith("server_name"):
            v = t[len("server_name"):].strip().rstrip(";").strip()
            return v or "(empty)"
    return "(none)"


def _anchor(blk):
    pos = 0
    for line in blk.splitlines(True):
        pos += len(line)
        if line.strip().startswith("server_name"):
            return pos
    pos = 0
    for line in blk.splitlines(True):
        pos += len(line)
        if line.strip().startswith("listen"):
            return pos
    return blk.find("{") + 1


def _patch(s, inc):
    parts, last, log = [], 0, []
    for idx, (a, b) in enumerate(_blocks(s), 1):
        parts.append(s[last:a])
        blk = s[a:b]
        is443 = _has443(blk)
        nm = _sname(blk)
        has = inc in blk
        if is443 and not has:
            p = _anchor(blk)
            blk = blk[:p] + "    " + inc + chr(10) + blk[p:]
            log.append((idx, nm, "INSERTED", True))
        elif (not is443) and has:
            blk = blk.replace("    " + inc, "").replace(inc, "")
            log.append((idx, nm, "REMOVED", False))
        else:
            log.append((idx, nm, "already" if has else "skip", is443))
        parts.append(blk)
        last = b
    parts.append(s[last:])
    return "".join(parts), log


def nginx():
    print("== 5/6 nginx ==")
    os.makedirs(os.path.dirname(NGSNIP), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "deploy/chat/chat.conf"), NGSNIP)
    inc = "include snippets/k12-chat.conf;"
    files = []
    for d in ("/etc/nginx/conf.d", "/etc/nginx/sites-enabled"):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                p = os.path.realpath(os.path.join(d, f))
                if os.path.isfile(p) and p not in files:
                    files.append(p)
    hit = 0
    for p in files:
        try:
            s = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if "server" not in s:
            continue
        new, log = _patch(s, inc)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
        for idx, nm, act, is443 in log:
            if act == "INSERTED" and is443:
                hit += 1
            print("   [srv] %s block%d 443=%s name=%s %s" % (p, idx, "yes" if is443 else "no", nm, act))
    if not hit:
        print("   !! no 443 block patched; current listens:")
        print(sh("grep -rn listen /etc/nginx/conf.d /etc/nginx/sites-enabled 2>/dev/null | head -20").stdout)
    t = sh("nginx -t")
    print("   " + (t.stderr or t.stdout).strip().splitlines()[-1])
    if t.returncode != 0:
        sys.exit("nginx config test failed, not reloading")
    sh("systemctl reload nginx")
    print("   reload done")
    r = sh("curl -s -o /dev/null -w '%{http_code}' -H 'Host: xueketupu.com' http://127.0.0.1/api/chat/health")
    print("   local nginx probe /api/chat/health : " + r.stdout.strip())
    r = sh("nginx -T 2>/dev/null | grep -n 'k12-chat' | head -8")
    print("   nginx -T hits:" + chr(10) + (r.stdout or "   (none)"))


def verify():
    print("== 6/6 自检 ==")
    def get(url, timeout=8):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.status, r.read(4000)
        except Exception as e:
            return 0, str(e).encode()

    st, body = get("http://127.0.0.1:8091/api/chat/health")
    print("   本机 8091 : %s %s" % (st, body[:120].decode("utf-8", "ignore")))
    st, body = get("https://xueketupu.com/api/chat/health")
    print("   域名 /api : %s %s" % (st, body[:120].decode("utf-8", "ignore")))
    st, body = get("https://xueketupu.com/")
    print("   首页注入 chat-widget.js : %s" % ("是" if b"chat-widget.js" in body else "否"))
    st, body = get("https://xueketupu.com/assets/chat-widget.css")
    print("   挂件样式 : %s %d bytes" % (st, len(body)))
    print("\n完成。打开 https://xueketupu.com/ 看右下角「客服」按钮。")
    print("日志: /var/www/k12/chat/logs/   限额: %s" % ENVF)


def status():
    print(sh("systemctl status %s --no-pager -n 8" % SVC).stdout)
    sp = os.path.join(ROOT, "chat/state", time.strftime("%Y-%m-%d") + ".json")
    if os.path.exists(sp):
        print("今日用量:", open(sp).read()[:200])
    lp = os.path.join(ROOT, "chat/logs", time.strftime("%Y-%m-%d") + ".jsonl")
    if os.path.exists(lp):
        n = sum(1 for _ in open(lp, encoding="utf-8"))
        print("今日日志行数:", n)


def uninstall():
    sh("systemctl disable --now %s" % SVC)
    for p in (UNIT, NGSNIP):
        if os.path.exists(p):
            os.remove(p)
    s = open(NGCONF, encoding="utf-8").read() if os.path.exists(NGCONF) else ""
    s = re.sub(r"\n\s*include snippets/k12-chat\.conf;", "", s)
    open(NGCONF, "w", encoding="utf-8").write(s)
    sh("systemctl daemon-reload && nginx -t && systemctl reload nginx")
    print("已卸载服务与 nginx 注入（/etc/xkt-chat.env 与 chat/ 目录保留）")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"
    if cmd == "status":
        need_root(); status()
    elif cmd == "uninstall":
        need_root(); uninstall()
    else:
        need_root()
        unpack(); env_file(); build_kb(); systemd(); nginx(); verify()
