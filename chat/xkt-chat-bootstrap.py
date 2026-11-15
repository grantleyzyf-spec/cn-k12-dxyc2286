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
H4sIAAqK+WoAA+19+3cTR9Lo/qy/ojNJPktBbz8wcsQuBAjcJMDG5NvNZ3t9xtLIFpYloRlhe43PMUkAGww2SXiadyCQBGzy
4mFjOGfvf5J4JPmn/Au3qrrnqZEN2SR777nMbrBmuru6urq6uqq7ujoc+dPv/kSj0Y2trYz+tvG/8Bh/+UusNb6xrTnaGo3F
WTQWi2+M/4m1/v6o/elPZVWTS4CK3AYIbIo3zDc8oCi5NeA4G8V+czx/pyccSQ3I2u/LBC/e//F4LPay//+IJxxJK8VcYfT3
5IBf0f+tbW0v+/+PeMIRNVXKFjX1d2SAX9H/G9tejv8/5AlHZFVVftfu/1Xjf2PLy/7/Ix6z/1ENCA1n0/2KFt6v/qZ1AD3a
Wloa9X+8LdbS5ur/1uaW5j+x6G+KRYPn//P+j7zBnD3Pfpr4nI2UlUFFKxfL4VRhiFW/uaAfPaLP36hcOlmZ/mhl6cEvTyZX
5x6sPL1c+/HsL0+mfOwNps+eqn6z8MuTi3v3dO5jEbmYJZaCnJ2d2yHPL0/mVh6d1GcWqp/fqZx7UDv2tX78zuqFk9XF2yuP
FgF+dXme7djy158nPgJwEZ8/U86ntGwhz/wBNuZjLJth/uFsPl0YDvf2jgxqbwH0dwtyWkkHWAmQLeU7IJd3DpZkWqmsdPgg
x0G5xLa/t2XXu/BR6i/JeS2njP5zNPOX/iE5m8MGSx0i25a9uzCT2Rgz4b0tf+/d98H7uzshORY3wQL68KEL3hjrkmrPLqw8
+rq6fBroVzm/oB++uLI0sfJ4snrxEynIJCeNIcPKo3v63DJ7JwRDQD9yR7/3ZfX26erVW7WFo/rc09r9b4G4lePH+ZfqR49/
njisH5lceTavH/m++v0SvNYWjlfO3lu9cV7/dLq28LRy7Vjl8vXq3Hzt2ZXK5OzKown9yTXA55cn09gJl2/p8xdXlk/q977S
783+PDGtn7yuX7qjf/Y15Kzcu/XzxEnoDMBk9eM7+pGTtR8eQ0HoQyhbvbCkL5+BVKknKFpbmTiFbfv8DrZt5dEUAAB8fzp9
jQFMFlFGQMssKRFWmZ7iLatMPdUn7+vLn+lTJ802AZf8dPo6gwQWSWfl/nxBhTKrE1P6/MeI9vdL1aWrle+e2RuuP53Q567U
ni1DBn3ynH5ssXJpAhit9vFy5cRZ4MvakWdAc2hg5dpjfe4atEt//ACyAaGovhsM0GaRnCKX8hFWe3iVRbRCMZtS4eX6rdr8
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
Xj6/7/N/AGKcNTYA1gAA
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
