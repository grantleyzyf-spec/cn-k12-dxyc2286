# -*- coding: utf-8 -*-
"""语文 S2 试点：一年级上册 第一单元·识字（天地人/金木水火土/口耳目手足/日月山川）
4 个课级点 + 20 道题（每点 choice2 · fill1 · numeric1 · short-answer1），课标引文逐字取自既有回表条目。

用法：python3 build_cn_pilot.py [--write]     # 不带 --write 只打印将要写入的内容
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/chinese/topics.json"
QP = f"{REPO}/data/chinese/questions.json"
DP = f"{REPO}/data/chinese/dependencies.json"
WRITE = "--write" in sys.argv

# 既有回表条目（id / 引文 / sourceLine 全部沿用，避免新造引文）
STD = {
 "SX01": {"id": "cyw-2022:1.SX.01", "confidence": "partial",
          "quote": "认识常用汉字1600个左右，其中800个左右会写", "sourceLine": 269},
 "SX03": {"id": "cyw-2022:1.SX.03", "confidence": "partial",
          "quote": "掌握汉字的基本笔画和常用的偏旁部首", "sourceLine": 276},
 "SX04": {"id": "cyw-2022:1.SX.04", "confidence": "partial",
          "quote": "学习独立识字。能借助汉语拼音认读汉字", "sourceLine": 280},
}

PTS = [
 dict(id="chi_g1a_u1_01", name="天地人", std="SX01", page=8,
      desc="认识「天、地、人、你、我、他」6 个生字，读准字音，知道「你、我、他」分别指对方、自己和第三人。",
      mastery=["能认读「天、地、人、你、我、他」6 个生字并口头组词", "能用「你、我、他」各说一句完整的话"],
      dq={"question": "「天地人」一课中与「天」相对、指我们脚下土地的字是哪个？", "answer": "地"},
      tags=["识字写字", "第一单元"], pre=[], root="「天地人」是一年级上册第一单元第一课，是整套教材识字学习的起点，不需要前置知识。"),
 dict(id="chi_g1a_u1_02", name="金木水火土", std="SX01", page=9,
      desc="认识「金、木、水、火、土」等生字，读通「金木水火土，天地分上下，日月照今古」，知道这五个字是古人概括的五种基本物质。",
      mastery=["认读「金、木、水、火、土」5 个生字并说出它们指的事物", "背诵课文「金木水火土，天地分上下，日月照今古」"],
      dq={"question": "「金木水火土」中「木」指的是什么？", "answer": "树木"},
      tags=["识字写字", "第一单元"], pre=["chi_g1a_u1_01"]),
 dict(id="chi_g1a_u1_03", name="口耳目手足", std="SX03", page=11,
      desc="认识「口、耳、目、手、足」等与身体有关的字，把字与身体部位对应起来，并按笔顺规则书写基本笔画。",
      mastery=["认读「口、耳、目、手、足」5 个字并与身体部位对应", "按笔顺规则书写「口」「手」等简单字"],
      dq={"question": "「目」指的是身体的哪个部位？", "answer": "眼睛"},
      tags=["识字写字", "第一单元"], pre=["chi_g1a_u1_02"]),
 dict(id="chi_g1a_u1_04", name="日月山川", std="SX04", page=13,
      desc="认识「日、月、山、川」等象形字，能从字形看出所画的事物，感受汉字由图画演变而来的特点。",
      mastery=["认读「日、月、山、川」4 个字并说出它们像什么", "能借助字形猜出简单象形字的意思"],
      dq={"question": "「日月山川」中字形像三道水流的是哪个字？", "answer": "川"},
      tags=["识字写字", "第一单元"], pre=["chi_g1a_u1_03"]),
]

QS = [
 # chi_g1a_u1_01
 dict(t="chi_g1a_u1_01", type="choice", diff="basic",
      prompt="「天地人」一课中，「天」的正确读音是下面哪一个？",
      options=[("A", "tiān"), ("B", "tián"), ("C", "tān"), ("D", "diān")], ans="A",
      exp="「天」读 tiān，第一声，如「天空」「今天」。"),
 dict(t="chi_g1a_u1_01", type="choice", diff="standard",
      prompt="「你」「我」「他」三个人称中，说话人指自己时应该用哪一个？",
      options=[("A", "你"), ("B", "我"), ("C", "他"), ("D", "她")], ans="B",
      exp="说话人指自己用「我」，指对方用「你」，指第三个人用「他」。"),
 dict(t="chi_g1a_u1_01", type="fill", diff="basic",
      prompt="「天地人」中与「天」相对、指我们脚下土地的字是____。", ans="地",
      exp="「天地人」里「天」在上、「地」在下，地指我们脚下的土地。"),
 dict(t="chi_g1a_u1_01", type="numeric", diff="basic",
      prompt="「天」字一共有几画？请用阿拉伯数字作答。", ans="4", verify="4",
      exp="「天」的笔顺是横、横、撇、捺，共 4 画。"),
 dict(t="chi_g1a_u1_01", type="short-answer", diff="hard",
      prompt="用「你」「我」「他」各说一句话，并说明每个词指的是谁。",
      ans="你说的是对方，例如「你去哪儿」；我说的是自己，例如「我去学校」；他说的是第三个人，例如「他是我的同学」。",
      kp=["你说的是对方", "我说的是自己", "他说的是第三个人"],
      exp="三个人称分别对应听话人、说话人和第三方，说话时不能混用。"),
 # chi_g1a_u1_02
 dict(t="chi_g1a_u1_02", type="choice", diff="basic",
      prompt="「金木水火土」中，「木」指的是下面哪一样事物？",
      options=[("A", "金属"), ("B", "树木"), ("C", "流水"), ("D", "泥土")], ans="B",
      exp="「木」指树木，如「木头」「树木」；「金」才是金属。"),
 dict(t="chi_g1a_u1_02", type="choice", diff="standard",
      prompt="课文「天地分上下」中的「下」与哪一个字意思相反？",
      options=[("A", "上"), ("B", "天"), ("C", "地"), ("D", "分")], ans="A",
      exp="「上」和「下」是一对反义词，课文用它们说明天在地的上方、地在天的下方。"),
 dict(t="chi_g1a_u1_02", type="fill", diff="basic",
      prompt="「金木水火土」中，表示「火」的那个字是____。", ans="火",
      exp="「火」就是火，与「水」相对，如水火不容。"),
 dict(t="chi_g1a_u1_02", type="numeric", diff="standard",
      prompt="「金木水火土」这一课一共出现了几个表示物质的字？请用阿拉伯数字作答。", ans="5", verify="5",
      exp="金、木、水、火、土共 5 个字，古人用它们概括五种基本物质。"),
 dict(t="chi_g1a_u1_02", type="short-answer", diff="standard",
      prompt="课文中「日月照今古」是什么意思？请用自己的话说一说。",
      ans="太阳和月亮从古代一直照耀到现在，说明日月长久、天地永恒。",
      kp=["太阳和月亮", "从古到今一直照耀", "日月长久"],
      exp="这句写日月运行不息，从古至今照耀大地。"),
 # chi_g1a_u1_03
 dict(t="chi_g1a_u1_03", type="choice", diff="basic",
      prompt="「口耳目手足」中，「目」指的是身体的哪个部位？",
      options=[("A", "嘴巴"), ("B", "眼睛"), ("C", "耳朵"), ("D", "手")], ans="B",
      exp="「目」是眼睛，如「目光」「耳目」；「口」才是嘴巴。"),
 dict(t="chi_g1a_u1_03", type="choice", diff="standard",
      prompt="「口耳目手足」中，下面哪个字表示「脚」？",
      options=[("A", "手"), ("B", "口"), ("C", "足"), ("D", "耳")], ans="C",
      exp="「足」指脚，如「足球」「手足」。"),
 dict(t="chi_g1a_u1_03", type="fill", diff="basic",
      prompt="我们用来听声音的器官是耳朵，对应的字是「____」。", ans="耳",
      exp="「耳」就是耳朵，课文用「耳」表示听声音的器官。"),
 dict(t="chi_g1a_u1_03", type="numeric", diff="basic",
      prompt="「口」字一共有几画？请用阿拉伯数字作答。", ans="3", verify="3",
      exp="「口」的笔顺是竖、横折、横，共 3 画。"),
 dict(t="chi_g1a_u1_03", type="short-answer", diff="standard",
      prompt="请写出「手」的笔顺，并说说写这个字时哪一笔最长。",
      ans="「手」的笔顺是撇、横、横、竖钩，最后一笔竖钩最长。",
      kp=["撇、横、横、竖钩", "最后一笔竖钩最长"],
      exp="按基本笔顺规则先撇后横，最后写竖钩，竖钩贯穿全字所以最长。"),
 # chi_g1a_u1_04
 dict(t="chi_g1a_u1_04", type="choice", diff="basic",
      prompt="「日」这个字在古文字中画的是什么？",
      options=[("A", "月亮"), ("B", "太阳"), ("C", "山峰"), ("D", "河流")], ans="B",
      exp="「日」的古字形像一个圆圈中间加一点，画的正是太阳。"),
 dict(t="chi_g1a_u1_04", type="choice", diff="standard",
      prompt="「日月山川」一课中，「川」表示的是什么？",
      options=[("A", "高山"), ("B", "水流"), ("C", "太阳"), ("D", "月亮")], ans="B",
      exp="「川」的古字形像三道水流，表示河流，如「山川」「川流不息」。"),
 dict(t="chi_g1a_u1_04", type="fill", diff="standard",
      prompt="「日月山川」中，字形像三道水流的是「____」字。", ans="川",
      exp="「川」像三条并流的水，所以表示河流。"),
 dict(t="chi_g1a_u1_04", type="numeric", diff="standard",
      prompt="「月」字一共有几画？请用阿拉伯数字作答。", ans="4", verify="4",
      exp="「月」的笔顺是撇、横折钩、横、横，共 4 画。"),
 dict(t="chi_g1a_u1_04", type="short-answer", diff="hard",
      prompt="「日、月、山、川」都是象形字，请选其中一个说说它的字形和所画事物的关系。",
      ans="「山」的古字形像三座并立的山峰，中间高、两边低，所以用来表示山。",
      kp=["像三座并立的山峰", "中间高两边低", "用字形表示山"],
      exp="象形字用线条勾出事物的形状，看到字形就能想到它画的是什么。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    deps = json.load(open(DP, encoding="utf-8"))
    if isinstance(deps, dict):
        deps = deps.get("dependencies") or deps.get("edges") or []
    have = {t["id"] for t in topic}
    newpts = []
    for p in PTS:
        if p["id"] in have:
            continue
        t = {"id": p["id"], "name": p["name"], "subject": "chinese", "domain": "识字与写字",
             "grade": 1, "semester": "上", "chapter": "一年级上册 第一单元 识字",
             "type": "conceptual", "description": p["desc"], "mastery_criteria": p["mastery"],
             "diagnostic_question": p["dq"], "external": False,
             "standards": [dict(STD[p["std"]])], "tags": p["tags"] + ["教材课级"],
             "prerequisites": p["pre"], "curriculumRef": STD[p["std"]]["id"],
             "verified": False, "textbookRef": f"人教版语文一年级上册 第{p['page']}页"}
        if not p["pre"]:
            t["root_reason"] = p["root"]
        newpts.append(t)
    newqs = []
    n = 0
    existing_q = {q["id"] for q in qs}
    for q in QS:
        n += 1
        qid = f"{q['t']}_q{n:02d}"
        if qid in existing_q:
            continue
        rec = {"id": qid, "topicId": q["t"], "prompt": q["prompt"], "question": q["prompt"],
               "options": [{"label": l, "text": s} for l, s in q.get("options", [])],
               "answer": q["ans"], "type": q["type"], "difficulty": q["diff"],
               "explanation": q["exp"]}
        if q["type"] == "numeric":
            rec["verify"] = q["verify"]
        if q["type"] == "short-answer":
            rec["keypoints"] = q["kp"]
        newqs.append(rec)
    newdeps = []
    for p in PTS:
        for pre in p["pre"]:
            newdeps.append({"from": pre, "to": p["id"], "type": "hard", "reason": "同单元前一课的学习为后一课打基础"})
    print(f"待写入：点 {len(newpts)} · 题 {len(newqs)} · 边 {len(newdeps)}")
    print("样例点：", json.dumps(newpts[0], ensure_ascii=False)[:260])
    print("样例题：", json.dumps(newqs[3], ensure_ascii=False)[:200])
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    json.dump(topic + newpts, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(TP, "a").write("\n")
    json.dump(qs + newqs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(QP, "a").write("\n")
    if isinstance(json.load(open(DP, encoding="utf-8")), dict):
        d0 = json.load(open(DP, encoding="utf-8"))
        d0["dependencies"] = deps + newdeps
        json.dump(d0, open(DP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    else:
        json.dump(deps + newdeps, open(DP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(DP, "a").write("\n")
    print("✅ 已写入")


if __name__ == "__main__":
    main()
