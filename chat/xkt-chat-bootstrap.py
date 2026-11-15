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
