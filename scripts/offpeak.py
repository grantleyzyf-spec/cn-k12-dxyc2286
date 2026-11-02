#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""波峰/波谷判定器（用户 2026-11-02 定的运行策略）

  波峰（禁跑重负载）：09:00–12:00、14:00–18:00
  波谷（可跑重负载）：12:00–14:00、18:00–次日 09:00

用法：
  python3 scripts/offpeak.py            # 打印当前窗口与下一个波谷
  python3 scripts/offpeak.py --quiet    # 只靠退出码：0=波谷可跑，3=波峰别跑
  python3 scripts/offpeak.py --wait     # 若在波峰，打印还要等多久（不睡）
"""
import sys
from datetime import datetime, timedelta

PEAKS = [(9, 12), (14, 18)]


def is_peak(t: datetime) -> bool:
    m = t.hour * 60 + t.minute
    return any(a * 60 <= m < b * 60 for a, b in PEAKS)


def next_valley(t: datetime) -> datetime:
    """当前/下一个波谷起点"""
    if not is_peak(t):
        return t
    for a, b in PEAKS:
        if t.hour * 60 + t.minute < b * 60:
            return t.replace(hour=b, minute=0, second=0, microsecond=0)
    return (t + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def fmt(td: timedelta) -> str:
    m = int(td.total_seconds() // 60)
    return f"{m // 60} 小时 {m % 60} 分"


def main() -> int:
    quiet = "--quiet" in sys.argv
    now = datetime.now()
    peak = is_peak(now)
    if not quiet:
        tag = "波峰（不跑重负载）" if peak else "波谷（可跑重负载）"
        print(f"现在 {now:%Y-%m-%d %H:%M} · {tag}")
        if peak:
            nv = next_valley(now)
            print(f"下一个波谷：{nv:%m-%d %H:%M}（约 {fmt(nv - now)} 后）")
    return 3 if peak else 0


if __name__ == "__main__":
    sys.exit(main())
