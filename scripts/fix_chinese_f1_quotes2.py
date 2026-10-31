# -*- coding: utf-8 -*-
"""修 F1 第二轮：填空题题干里带 ____ 的引文（14 条）。"""
import json
import sys

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
QP = f"{REPO}/data/chinese/questions.json"
WRITE = "--write" in sys.argv

FIX = {
 "chi_q1643": ("「假如我变成了一朵____花，为了好玩，长在树的高枝上……」",
               "「假如我变成了一朵____花，只是为了好玩，长在那棵树的高枝上……」", {}),
 "chi_q1708": ("「母亲最大的特点是一生____，直到老年也还是这样。」",
               "「母亲最大的特点是一生____。」", {"answer": "不曾脱离过劳动"}),
 "chi_q1798": ("「邓稼先是中国几千年传统文化所孕育出来的有最高____的共产党员。」",
               "「邓稼先是中国几千年传统文化所孕育出来的有最高____的儿子。」", {}),
 "chi_q1823": ("「老山界是我们长征中所过的第一座____的山。」",
               "「老山界是我们长征中所过的第一座____的山。」", {"answer": "难走"}),
 "chi_q1828": ("「他们的品质是那样的纯洁和____。」",
               "「他们的品质是那样地纯洁和____，」", {}),
 "chi_q1983": ("「正入万山圈子里，一山放出一山____。」",
               "「政入万山围子里，一山放出一山____。」", {}),
 "chi_q2353": ("「曲径通幽处，禅房花木____。」", "「竹径通幽处，禅房花木____。」", {}),
 "chi_q2418": ("「处处是创造之地，天天是创造之时，人人都是创造之____。」",
               "「处处是创造之地，天天是创造之时，人人是创造之____。」", {}),
 "chi_q2573": ("「而今识尽愁滋味，欲说还休，却道天凉好个____。」",
               "「而今识尽愁滋味，欲说还休。欲说还休，却道天凉好个____。」", {}),
 "chi_q2713": ("而只是上帝交给他的一个____。」", "而只是上天交给他的一个____。」", {}),
 "chi_q2793": ("让他第一次思考「更高维的____」。", "让他第一次思考「更高维____世界」。", {"answer": "数"}),
 "chi_q2818": ("「泰山不让土壤，故能成其大；河海不择细流，故能就其____。」",
               "「太山不让土壤，故能成其大；河海不择细流，故能就其____。」", {}),
 "chi_q2838": ("别里科夫的口头禅是「千万别出什么____」。",
               "别里科夫的口头禅是「千万别闹出什么____」。", {}),
 "chi_q3058": ("「再见吧，自由的____！」", "「再见吧，自由的____！」", {"answer": "元素"}),
}


def main():
    qs = json.load(open(QP, encoding="utf-8"))
    idx = {q["id"]: q for q in qs}
    miss, done = [], 0
    for qid, (old, new, extra) in FIX.items():
        q = idx.get(qid)
        if q is None:
            miss.append((qid, "不存在")); continue
        p = q.get("prompt", "")
        if p.count(old) != 1:
            miss.append((qid, f"命中 {p.count(old)} 次")); continue
        q["prompt"] = p.replace(old, new)
        q["question"] = q["prompt"]
        for k, v in extra.items():
            q[k] = v
        done += 1
    print(f"可修 {done} / {len(FIX)}；问题 {miss}")
    if not WRITE:
        return
    json.dump(qs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(QP, "a").write("\n")
    print("✅ 已写入")


if __name__ == "__main__":
    main()
