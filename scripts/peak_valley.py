#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""峰谷调度闸门（用户口径，2026-11-02 明确）。

时间口径（本地时区，周一至周日同一口径）：
    波峰  09:00–12:00 、 14:00–18:00
    波谷  12:00–14:00 、 18:00–次日 09:00

用途：批量生产（多工位并发写题库/学层/讲解、批量渲染、全量扫描）**只在波谷开跑**；
波峰只做轻量活（合并、门禁、索引重建、docx、文档、汇报）。在飞的工位不中途杀（已投入的不白烧），
但波峰期间**不再新开批**。

用法：
    python3 scripts/peak_valley.py                 # 打印当前状态与下一次切换
    python3 scripts/peak_valley.py --is-valley     # 波谷退出码 0，波峰退出码 3（可直接用 && 串命令）
    python3 scripts/peak_valley.py --next-valley   # 打印下一个波谷起点
    python3 scripts/peak_valley.py --at 13:30      # 查某个时刻属于哪一段
"""
import argparse
import datetime
import sys

PEAK = [((9, 0), (12, 0)), ((14, 0), (18, 0))]
VALLEY_LABEL = "12:00–14:00 、 18:00–次日 09:00"
PEAK_LABEL = "09:00–12:00 、 14:00–18:00"


def in_peak(dt):
    t = (dt.hour, dt.minute)
    return any(s <= t < e for s, e in PEAK)


def phase(dt):
    return "波峰" if in_peak(dt) else "波谷"


def next_transition(dt):
    """返回 (下一次切换时刻, 切换后属于哪一段)。"""
    t = (dt.hour, dt.minute)
    points = []
    for s, e in PEAK:
        points.append((s, "波峰"))
        points.append((e, "波谷"))
    points.sort()
    for (h, m), ph in points:
        if (h, m) > t:
            return dt.replace(hour=h, minute=m, second=0, microsecond=0), ph
    # 次日 09:00 进入波峰
    nxt = (dt + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    return nxt, "波峰"


def next_valley(dt):
    cand = dt
    for _ in range(48):
        cand, ph = next_transition(cand)
        if ph == "波谷":
            return cand
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--is-valley", action="store_true", help="波谷返回 0，波峰返回 3")
    ap.add_argument("--next-valley", action="store_true", help="打印下一个波谷起点")
    ap.add_argument("--at", help="指定时刻 HH:MM 查询")
    a = ap.parse_args()

    now = datetime.datetime.now()
    if a.at:
        h, m = a.at.split(":")
        now = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)

    if a.is_valley:
        return 0 if not in_peak(now) else 3

    if a.next_valley:
        nv = next_valley(now)
        if nv is None:                      # 理论上到不了，兜底防 None.strftime
            print("无法计算下一个波谷（检查 PEAK 配置）", file=sys.stderr)
            return 1
        print(nv.strftime("%Y-%m-%d %H:%M"))
        return 0

    nxt, ph = next_transition(now)
    print(f"现在 {now.strftime('%Y-%m-%d %H:%M')} → 【{phase(now)}】")
    print(f"  波峰：{PEAK_LABEL}")
    print(f"  波谷：{VALLEY_LABEL}")
    print(f"  下一次切换：{nxt.strftime('%H:%M')} 进入{ph}"
          + ("（重负载请收尾）" if ph == "波峰" else "（可开新批）"))
    print("  纪律：波峰只做轻量活（合并/门禁/索引/docx/文档）；批量生产只在波谷开跑。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
