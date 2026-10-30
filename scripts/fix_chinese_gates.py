# -*- coding: utf-8 -*-
"""语文门禁批量修复器：
① 题干 <12 字 → 自动加「《课文名》一课中，」前缀（幂等，已有前缀则跳过）
② keypoints 单元 <4 字 → 按 KP_FIX 映射改；未登记的不动，只报出来（人工补）
用法：python3 fix_cn_gates.py [--write]
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP = f"{REPO}/data/chinese/topics.json", f"{REPO}/data/chinese/questions.json"
WRITE = "--write" in sys.argv

KP_FIX = {"不浪费": "不浪费食物", "不算晚": "补救还不算晚",
          "辽阔": "草原辽阔", "苍茫": "四野苍茫",
          "高矮": "树的高矮", "叶形": "叶子的形状", "叶色": "叶子的颜色",
          "当朋友": "把动物当朋友", "绑着睡": "绑在睡袋里睡",
          "木子李": "木子李的拆字法", "弓长张": "弓长张的拆字法"}


def main():
    ts = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    tname = {t["id"]: t["name"] for t in ts}
    p_fix, k_fix, k_unknown = [], [], []
    for q in qs:
        p = q.get("prompt") or ""
        if len(p) < 12:
            nm = tname.get(q.get("topicId"), "")
            pref = f"《{nm}》一课中，"
            if nm and not p.startswith(pref):
                p_fix.append((q["id"], p, pref + p))
        for x in (q.get("keypoints") or []):
            if len(x) < 4:
                if x in KP_FIX:
                    k_fix.append((q["id"], x, KP_FIX[x]))
                else:
                    k_unknown.append((q["id"], x))
    print(f"题干 <12 字：{len(p_fix)} 条")
    for i, a, b in p_fix:
        print(f"   {i}: {a}  →  {b}")
    print(f"keypoints <4 字可自动修：{len(k_fix)} 条；未登记：{len(k_unknown)} 条")
    for i, a in k_unknown:
        print(f"   ⚠ 未登记 {i}: {a}")
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    mp = {i: b for i, a, b in p_fix}
    mk = {(i, a): b for i, a, b in k_fix}
    n = 0
    for q in qs:
        if q["id"] in mp:
            q["prompt"] = q["question"] = mp[q["id"]]
            n += 1
        if q.get("keypoints"):
            new = [mk.get((q["id"], x), x) for x in q["keypoints"]]
            if new != q["keypoints"]:
                q["keypoints"] = new
                n += 1
    json.dump(qs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(QP, "a").write("\n")
    print(f"✅ 已修 {n} 处；未登记条目需人工处理")


if __name__ == "__main__":
    main()
