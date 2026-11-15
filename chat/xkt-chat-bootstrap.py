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
                "assets/chat-widget.css", "deploy/chat/chat.conf", "deploy/chat/xkt-chat.service"):
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
