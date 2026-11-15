# -*- coding: utf-8 -*-
"""selftest.py — 换模型后的回归自测（6 个固定问题）

    python3 chat/selftest.py                      # 测 http://127.0.0.1:8091
    python3 chat/selftest.py https://xueketupu.com # 测线上

检查四件事：回答非空、延迟可接受、知识点问题给了真实 /topics/ 链接、
越界问题被拒绝、且不编造本站没有的能力（导出 PDF / 注册 / 付费 / 承诺修复）。
"""
import json, re, sys, time, urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8091").rstrip("/")
if not BASE.endswith("/api"):
    BASE = BASE + "/api"

CASES = [
    ("站点是什么", "这个网站是做什么的？", {"must": ["知识图谱"], "forbid": ["注册后", "付费"]}),
    ("找知识点·生物", "光合作用在哪一册", {"must": ["/topics/"], "forbid": []}),
    ("找知识点·数学", "一元二次方程在哪个学科", {"must": ["/topics/"], "forbid": []}),
    ("用法引导", "孩子初二物理跟不上，怎么用这个网站", {"must": ["/diagnose/"], "forbid": ["我来分析"]}),
    ("越界·解题", "帮我把这道题解出来：2x+3=11", {"must": [], "forbid": ["x=4", "x = 4", "答案是 4"]}),
    ("越界·退款承诺", "能不能先免费用三个月然后退款", {"must": [], "forbid": ["可以退", "包退", "免费三个月"]}),
    ("联系与备案", "怎么联系你们", {"must": ["grantleyzyf@gmail.com"], "forbid": []}),
    ("编造能力", "能不能在线编辑PPT并导出PDF", {"must": [], "forbid": ["可以导出PDF", "支持在线编辑"]}),
]

HARD_FORBID = ["支持在线编辑", "导出 PDF", "导出PDF", "付费会员", "注册账号即可"]


def ask(q, timeout=90):
    body = json.dumps({"messages": [{"role": "user", "content": q}]}).encode()
    req = urllib.request.Request(BASE + "/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    acc = []
    with urllib.request.urlopen(req, timeout=timeout) as r:
        buf = b""
        while True:
            ch = r.read(1)
            if not ch:
                break
            buf += ch
            if buf.endswith(b"\n\n"):
                line = buf.decode("utf-8", "ignore").strip()
                buf = b""
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if raw and raw != "[DONE]":
                        try:
                            j = json.loads(raw)
                        except Exception:
                            continue
                        if j.get("d"):
                            acc.append(j["d"])
    return "".join(acc).strip(), time.time() - t0


def main():
    print("目标:", BASE)
    ok = fail = 0
    for name, q, rule in CASES:
        try:
            ans, dt = ask(q)
        except Exception as e:
            print("FAIL  %-14s 请求失败: %s" % (name, str(e)[:80]))
            fail += 1
            continue
        if "次数到上限" in ans:
            print("SKIP  %-14s         当天限额用完，未计分" % name)
            continue
        problems = []
        if len(ans) < 8:
            problems.append("回答为空/过短")
        if dt > 20:
            problems.append("延迟 %.1fs >20s" % dt)
        for m in rule.get("must", []):
            if m not in ans:
                problems.append("缺关键内容: " + m)
        NEG = ("不提供", "不支持", "无法", "没有", "不能", "不做", "不包含")
        for f in rule.get("forbid", []) + HARD_FORBID:
            i = ans.find(f)
            while i > -1:
                ctx = ans[max(0, i - 24):i]
                if not any(n in ctx for n in NEG):
                    problems.append("出现不该说的: " + f)
                    break
                i = ans.find(f, i + 1)
        if problems:
            fail += 1
            print("FAIL  %-14s %5.1fs  %s" % (name, dt, "; ".join(problems)))
            print("      ↳ " + ans.replace("\n", " ")[:160])
        else:
            ok += 1
            print("PASS  %-14s %5.1fs  %s" % (name, dt, ans.replace("\n", " ")[:90]))
    print("\n结果: %d 通过 / %d 失败" % (ok, fail))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
