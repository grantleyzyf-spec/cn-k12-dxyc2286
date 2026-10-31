# -*- coding: utf-8 -*-
"""重负载作业的「峰谷守护」（可复用到任何可断点续跑的长作业）：到波峰自动停，到波谷自动续跑。

为什么可以随便停：流水线是断点续跑的（每页一份 JSON，存在即跳过），停 = 下一个波谷从缺的页接着跑。

时段（用户口径 2026-10-29 确认）：**工作日**峰段 09:00–12:00、14:00–18:00；
其余时段（工作日 12–14、18–次日 9，以及周六周日全天）一律按谷段处理 → 自动跑。
峰段到点强制停（SIGTERM，强杀兜底），谷段自动续跑（断点续跑，不丢页）。

用法（把 WORK/CMD/LOG/剩余页判定换成自己作业的即可）：
  python3 peak_valley_guard.py --once      # 只看当前该跑还是该停
  python3 peak_valley_guard.py --daemon    # 常驻：每 45s 判一次
"""
import datetime as dt
import glob
import json
import os
import signal
import subprocess
import sys
import time

WORK = os.path.expanduser("~/Desktop/qbank-upgrade/math")
LEDGER = "/tmp/fml"
RISK = "/tmp/mtoc/formula_risk.json"
LOG = "/tmp/fml_guard.log"
THRESHOLD = 0   # 0 = 连低风险（<20 分）517 页一起读；高/中两档 457 页已完成
RUN_WHEN_NOT_PEAK = True              # 谷段（含 12–14、18–9、周末）都跑
PEAK = [((9, 0), (12, 0)), ((14, 0), (18, 0))]   # 工作日峰（周一 0:00–9:00 属谷，无需特例）
PEAK_WEEKDAYS_ONLY = True                            # 周六/周日全天 = 谷
TICK = 45


def minutes(hm):
    return hm[0] * 60 + hm[1]


def in_window(now_min, win):
    (sh, sm), (eh, em) = win
    a, b = minutes((sh, sm)), minutes((eh, em))
    return a <= now_min < b if a < b else (now_min >= a or now_min < b)   # 跨零点


def state_now(now=None):
    """→ 'peak'（该停）或 'valley'（该跑）。
    工作日峰 08:00–12:00、14:00–18:00；**周一 0:00–09:00 属谷**；周末全天谷。"""
    now = now or dt.datetime.now()
    if PEAK_WEEKDAYS_ONLY and now.weekday() >= 5:      # 周六=5、周日=6 → 全天谷
        return "valley"
    m = now.hour * 60 + now.minute
    win = PEAK
    return "peak" if any(in_window(m, w) for w in win) else "valley"


def log(msg):
    line = f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def remaining():
    risk = [x for x in json.load(open(RISK, encoding="utf-8")) if x["score"] >= THRESHOLD]
    return sum(1 for x in risk if not os.path.exists(f"{LEDGER}/{x['book']}_p{x['page']}.json")), len(risk)


def running_pids():
    out = subprocess.run(["pgrep", "-f", "formula_ledger.py"], capture_output=True, text=True).stdout
    return [int(x) for x in out.split() if x.strip()]


def stop_job():
    pids = running_pids()
    for p in pids:
        try:
            os.kill(p, signal.SIGTERM)
        except ProcessLookupError:
            pass
    if pids:
        time.sleep(3)
        for p in running_pids():          # 还不走就强杀
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
    return pids


def start_job():
    env = dict(os.environ)
    cmd = ["/usr/bin/python3", "formula_ledger.py", f"--threshold={THRESHOLD}", "--rounds=4"]
    with open("/tmp/fml_run_bg.log", "a", encoding="utf-8") as out:
        subprocess.Popen(cmd, cwd=WORK, stdout=out, stderr=subprocess.STDOUT,
                         env=env, start_new_session=True)
    log("▶ 已启动公式批读作业（threshold=%d）" % THRESHOLD)


def main():
    once = "--once" in sys.argv
    st, (left, total) = state_now(), remaining()
    if once:
        print(f"现在 {dt.datetime.now():%H:%M} → 时段 {st}；待读 {left}/{total} 页；"
              f"作业{'在跑' if running_pids() else '未跑'}")
        return
    log(f"守护启动：工作日峰段 {PEAK}（仅周一至周五）、其余全为谷段、tick={TICK}s")
    while True:
        st = state_now()
        left, total = remaining()
        if left == 0:
            if running_pids():
                stop_job()
            log(f"✅ 全部 {total} 页已读完，守护退出")
            return
        pids = running_pids()
        if st == "peak" and pids:
            killed = stop_job()
            log(f"⏸ 进入波峰，已停止作业 pid={killed}；剩 {left}/{total} 页，等下个波谷续跑")
        elif st == "valley" and not pids and RUN_WHEN_NOT_PEAK:
            log(f"（{st} 时段）作业未在跑，剩 {left}/{total} 页 → 启动")
            start_job()
        time.sleep(TICK)


if __name__ == "__main__":
    main()
