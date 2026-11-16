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
ANgAAA==
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
    cur.setdefault("WECHAT_KF_URL", "")
    cur.setdefault("QQ_GROUP", "1045844951")
    cur.setdefault("SUPPORT_EMAIL", "grantleyzyf@gmail.com")
    lines = ["# xueketupu.com 客服环境变量（600 权限，勿入库）"]
    lines += ["%s=%s" % (k, cur[k]) for k in
              ("CHAT_API_KEY", "CHAT_API_BASE", "CHAT_MODEL", "PORT",
               "CHAT_DAILY_BUDGET", "CHAT_IP_DAILY", "CHAT_MAX_TURNS",
               "WECHAT_KF_URL", "QQ_GROUP", "SUPPORT_EMAIL")]
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
