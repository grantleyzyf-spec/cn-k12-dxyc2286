#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重拍 README 三张配图（screenshots/01-home|02-explore|03-diagnose）。

用私有 headless Chrome（独立 profile + CDP），不依赖共享浏览器，也不受并行会话干扰。
用法：/usr/bin/python3 scripts/shoot_screenshots.py   # 需 Chrome + websocket-client
产出写到 /tmp/shots/，人工确认后拷贝到 screenshots/ 再提交。

⚠️ 数据一变（stats.json / subject-groups.json），这三张图和 assets/og.png 就会过期——
README 上的数字看着像「没改」，其实是图片没重拍。改完数据记得跑本脚本 + make_og_image.py。"""
import json, os, subprocess, time, base64, itertools, sys
import requests, websocket

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333
PROF = "/tmp/cn-shot-profile"
OUT = "/tmp/shots"
os.makedirs(OUT, exist_ok=True)

proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROF}", "--hide-scrollbars", "--no-first-run",
    "--no-default-browser-check", "--disable-gpu", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_devtools():
    for _ in range(60):
        try:
            return requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=1).json()
        except Exception:
            time.sleep(0.4)
    raise SystemExit("devtools 未起来")

ver = wait_devtools()
tgt = requests.put(f"http://127.0.0.1:{PORT}/json/new?about:blank", timeout=5).json()
ws = websocket.create_connection(tgt["webSocketDebuggerUrl"], timeout=60)
_id = itertools.count(1)

def cdp(method, **params):
    mid = next(_id)
    ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            if "error" in msg:
                raise RuntimeError(f"{method}: {msg['error']}")
            return msg.get("result", {})

def js(expr, await_promise=False):
    r = cdp("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=await_promise)
    if r.get("exceptionDetails"):
        raise RuntimeError(str(r["exceptionDetails"])[:300])
    return r.get("result", {}).get("value")

def goto(url, wait=3.0):
    cdp("Page.navigate", url=url)
    time.sleep(wait)
    for _ in range(40):
        if js("document.readyState") == "complete":
            break
        time.sleep(0.3)

def shot(name, clip_h=900):
    time.sleep(1.2)
    data = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=False)
    p = os.path.join(OUT, name)
    open(p, "wb").write(base64.b64decode(data["data"]))
    print("  →", p, os.path.getsize(p) // 1024, "KB")

cdp("Page.enable"); cdp("Runtime.enable")
cdp("Emulation.setDeviceMetricsOverride", width=1440, height=900, deviceScaleFactor=2, mobile=False)

BASE = "https://xueketupu.com"

# ① 首页
print("① 首页")
goto(BASE + "/?shot=1", 5)
for _ in range(40):
    if js("(document.getElementById('n-subjects')||{}).textContent") not in (None, "—"):
        break
    time.sleep(0.4)
print("   统计:", js("Array.from(document.querySelectorAll('[id^=n-]')).map(e=>e.id+'='+e.textContent).join(' ')"))
shot("01-home.png")

# ② 知识图谱
print("② 知识图谱")
goto(BASE + "/explore/?subject=math#mat_p711", 6)
for _ in range(30):
    if js("document.querySelectorAll('#graph-canvas g.node').length") > 0:
        break
    time.sleep(0.4)
js("(()=>{const s=document.getElementById('depth-select');if(s){s.value='2';s.dispatchEvent(new Event('change'));}})()")
time.sleep(2)
print("   节点:", js("document.querySelectorAll('#graph-canvas g.node').length"),
      "| 图注:", js("document.getElementById('graph-meta')?.textContent"))
shot("02-explore.png")

# ③ 诊断结果
print("③ 诊断")
goto(BASE + "/diagnose/", 5)
js("(()=>{const s=document.getElementById('subject-select');s.value='math';s.dispatchEvent(new Event('change'));})()")
time.sleep(4)
js("(()=>{const s=document.getElementById('topic-select');s.value='mat_p711';s.dispatchEvent(new Event('change'));document.getElementById('start-btn').click();})()")
time.sleep(2)
for i in range(90):
    done = js("(()=>{const r=document.getElementById('result-area');return !!(r && r.offsetHeight>0 && getComputedStyle(r).display!=='none')})()")
    if done:
        print("   结果页已出现（第 %d 步）" % i); break
    kind = js("""(()=>{const os=document.querySelectorAll('#options .option');
        if(os.length){os[0].click();return 'opt';}
        const inp=document.querySelector('#options input, input[type=text]');
        if(inp){inp.value='0';inp.dispatchEvent(new Event('input',{bubbles:true}));return 'fill';}
        return 'none';})()""")
    time.sleep(0.25)
    js("document.getElementById('next-btn')?.click()")
    time.sleep(0.55)
print("   进度:", js("document.getElementById('progress-text')?.textContent"))
print("   结果摘要:", js("document.getElementById('result-content')?.innerText.slice(0,120).replace(/\\n/g,' | ')"))
time.sleep(1.5)
# 诊断结果页整页抓取（含路径与逐题记录），再压到宽 1440
m = cdp("Page.getLayoutMetrics")
cs = m.get("cssContentSize") or m.get("contentSize")
h = min(int(cs["height"]), 2600)
cdp("Emulation.setDeviceMetricsOverride", width=1440, height=h, deviceScaleFactor=1, mobile=False)
time.sleep(1.0)
data = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=True)
raw = os.path.join(OUT, "_03_raw.png")
open(raw, "wb").write(base64.b64decode(data["data"]))
from PIL import Image
im = Image.open(raw)
if im.width != 1440:
    im = im.resize((1440, round(im.height * 1440 / im.width)), Image.LANCZOS)
im.save(os.path.join(OUT, "03-diagnose.png"), optimize=True)
print("  → 03 整页:", im.size, os.path.getsize(os.path.join(OUT,'03-diagnose.png'))//1024, "KB")

ws.close()
proc.terminate()
print("完成")
