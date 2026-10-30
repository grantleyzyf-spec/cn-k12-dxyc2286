# -*- coding: utf-8 -*-
"""语文 二上补齐两课：去外婆家(第三单元 p30)、快乐的小河(第八单元 p101)。
两课正文已从教材 PDF 读到（前一轮误判为缺页，实为拼音注音打散了文本层）。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
YD01 = {"id": "cyw-2022:1.YD.01", "confidence": "partial", "quote": "感受阅读的乐趣。学习用普通话正确、流利", "sourceLine": 284}

PTS = [
 ("去外婆家", 30, "二年级上册 第三单元 阅读",
  "朗读《去外婆家》，认识「婆、候、趣、舅、留、份、喂、逃」等字词；知道外婆家在山脚下，山上有吃的、玩的、看的，小山雀、杜鹃花和野花都给「我」带来乐趣。",
  ["能说出外婆家带给「我」哪些乐趣", "能说出课文写了哪几件有趣的事"],
  {"question": "课文写「我」小时候最大的乐趣是什么？", "answer": "去外婆家"}),
 ("快乐的小河", 101, "二年级上册 第八单元 阅读",
  "朗读《快乐的小河》，认识「撞、怨、软、呜、慈、祥、跌、摔、擦」等字词；知道小河撞山后抱怨，大山告诉它「不平静的水才有力量」，最后它和泉水、瀑布成了好朋友一起向前流。",
  ["能说出大山告诉小河的道理", "能说出小河是怎么得到快乐的"],
  {"question": "小河一开始为什么哭了？", "answer": "他撞在大山上，撞疼了"}),
]

QS = [
 ("去外婆家", "choice", "basic", "课文写「我」小时候最大的乐趣是什么？",
  [("A", "去外婆家"), ("B", "上山砍柴"), ("C", "去河边钓鱼"), ("D", "在院子里玩")], "A", "课文开头就写「小时候，我最大的乐趣就是去外婆家」。"),
 ("去外婆家", "choice", "standard", "舅舅从山上干活回来，常带回哪些吃的东西？",
  [("A", "山楂、柿子、毛栗子"), ("B", "苹果、梨、桃"), ("C", "鱼和虾"), ("D", "米和面")], "A", "课文写「会带一些山楂、柿子或毛栗子，外婆总要给我留一份」。"),
 ("去外婆家", "fill", "basic", "外婆家在山脚下，山上山下____多，有吃的，有玩的，还有看的。", "宝贝", "「宝贝多」是这一段的总起句。"),
 ("去外婆家", "numeric", "basic", "「婆」字一共有几画？请用阿拉伯数字作答。", "11", "11", "「婆」上面波 9 画、下面女 3 画，共 11 画。"),
 ("去外婆家", "short-answer", "standard", "说说外婆家给「我」带来了哪些乐趣。",
  "舅舅带回山楂、柿子、毛栗子，外婆给我留一份；屋后山上的小山雀蹦来跳去，从小喂大的还会飞到手上唱小曲；春天屋后开满杜鹃花和各种野花；舅妈把野花戴在头上、别在衣服上，香气扑鼻。",
  ["舅舅带回山果外婆留一份", "小山雀飞到手上唱小曲", "满山杜鹃与野花"], "按「吃的—玩的—看的」三类说，就覆盖全了。"),
 ("快乐的小河", "choice", "basic", "小河一开始为什么哭了？",
  [("A", "他撞在大山上，撞疼了"), ("B", "天气太热"), ("C", "没有人跟他玩"), ("D", "水流得太慢")], "A", "课文写小河「迎面撞在一座大山上」，疼得流出眼泪。"),
 ("快乐的小河", "choice", "standard", "大山告诉小河什么道理？",
  [("A", "不平静的水才有力量，跌几个跟头反而能让人更有劲儿"), ("B", "应该停下来休息"), ("C", "要绕开山走"), ("D", "越快越好，不用管别的")], "A", "大山说「不平静的水才有力量，跌几个跟头怕什么？这可以让你更有劲儿呢」。"),
 ("快乐的小河", "fill", "basic", "小河和泉水、瀑布成了三个好____，手拉着手一起流向远方。", "伙伴", "课文结尾写「三个好伙伴，手拉着手，蹦啊，跳啊」。"),
 ("快乐的小河", "numeric", "basic", "「河」字一共有几画？请用阿拉伯数字作答。", "8", "8", "「河」左边三点水 3 画、右边可 5 画，共 8 画。"),
 ("快乐的小河", "short-answer", "standard", "说说小河是怎么得到快乐的。",
  "他先是因为撞山而抱怨，听了大山「不平静的水才有力量」的话就不再哭；后来去和泉水做好朋友，又认识了更勇敢的瀑布，三个伙伴手拉手一起向前流，一路唱歌，就快乐起来了。",
  ["听大山的话不再抱怨", "和泉水瀑布做好朋友", "一起勇敢向前流"], "按「抱怨—听劝—交友—同流」四步说。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    pre_of = {"去外婆家": [[t["id"] for t in topic if t["name"] == "彩虹"][0]],
              "快乐的小河": [[t["id"] for t in topic if t["name"] == "纸船和风筝"][0]]}
    newpts, name2id = [], {}
    for i, (nm, pg, ch, desc, mast, dq) in enumerate(PTS):
        pid = f"chi_p{pmax + 1 + i}"
        name2id[nm] = pid
        newpts.append({"id": pid, "name": nm, "subject": "chinese", "domain": "阅读与鉴赏",
                       "grade": 2, "semester": "上", "chapter": ch, "type": "conceptual",
                       "description": desc, "mastery_criteria": mast, "diagnostic_question": dq,
                       "external": False, "standards": [dict(YD01)],
                       "tags": ["课文", "阅读与鉴赏", "教材课级"],
                       "prerequisites": pre_of[nm], "curriculumRef": YD01["id"], "verified": True,
                       "textbookRef": f"人教版语文二年级上册 第{pg}页"})
    newqs = []
    for k, item in enumerate(QS, 1):
        tname, typ, diff, prompt = item[0], item[1], item[2], item[3]
        rec = {"id": f"chi_q{qmax + k}", "topicId": name2id[tname], "prompt": prompt,
               "question": prompt, "type": typ, "difficulty": diff}
        if typ == "choice":
            rec["options"] = [{"label": l, "text": t} for l, t in item[4]]
            rec["answer"], rec["explanation"] = item[5], item[6]
        elif typ == "fill":
            rec["options"], rec["answer"], rec["explanation"] = [], item[4], item[5]
        elif typ == "numeric":
            rec["options"], rec["answer"], rec["verify"], rec["explanation"] = [], item[4], item[5], item[6]
        else:
            rec["options"], rec["answer"], rec["keypoints"], rec["explanation"] = [], item[4], item[5], item[6]
        newqs.append(rec)
    newdeps = [{"from": p["prerequisites"][0], "to": p["id"], "type": "hard", "reason": "同一单元 / 同册相邻课"} for p in newpts]
    print(f"新增：点 {len(newpts)} · 题 {len(newqs)} · 边 {len(newdeps)}（chi_p{pmax+1}–chi_p{pmax+len(newpts)}）")
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    json.dump(topic + newpts, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2); open(TP, "a").write("\n")
    json.dump(qs + newqs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=2); open(QP, "a").write("\n")
    if isinstance(dp, dict):
        dp["dependencies"] = deps + newdeps
        json.dump(dp, open(DP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    else:
        json.dump(deps + newdeps, open(DP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(DP, "a").write("\n")
    print("✅ 已写入")


if __name__ == "__main__":
    main()
