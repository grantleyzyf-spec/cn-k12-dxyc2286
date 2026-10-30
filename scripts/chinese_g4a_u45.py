# -*- coding: utf-8 -*-
"""语文 四上 第四~五单元（6 点）建点。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
YD3 = {"id": "cyw-2022:2.YD.03", "confidence": "partial", "quote": "能初步把握文章的主要内容，体会文章表达的思想感情。学习圈点、批注等阅读方法", "sourceLine": 382}
YD2 = {"id": "cyw-2022:2.YD.02", "confidence": "partial", "quote": "能联系上下文，理解词句的意思", "sourceLine": 369}

U4, U5 = "四年级上册 第四单元", "四年级上册 第五单元（习作单元）"

PTS = [
 ("盘古开天地", 48, U4, YD3,
  "朗读《盘古开天地》，认识「混、沌、劈、浊、撑、竭」等字词；知道盘古劈开天地、撑在天地之间，倒下后身体化生万物。",
  ["能说出盘古开天地的经过", "能说出盘古身体化成的几种事物"],
  {"question": "盘古在混沌中醒来后做了什么？", "answer": "拿起斧头劈开天地"}),
 ("精卫填海", 50, U4, YD3,
  "朗读《精卫填海》，认识「炎、帝、少女、溺、衔、堙」等字词；知道女娃溺于东海化为精卫，常衔木石填海。",
  ["能借助注释读懂这则文言文", "能说出精卫填海的原因"],
  {"question": "精卫是谁变成的？", "answer": "炎帝的小女儿女娃"}),
 ("普罗米修斯", 51, U4, YD3,
  "朗读《普罗米修斯》，认识「普、罗、米、修、斯、罚、狠、屈」等字词；知道普罗米修斯为人类取火受罚，始终不屈服。",
  ["能说出普罗米修斯受罚的原因和表现", "能说出他最后被谁解救"],
  {"question": "普罗米修斯为什么受到宙斯的惩罚？", "answer": "他为人类拿取了火种"}),
 ("女娲补天", 54, U4, YD3,
  "朗读《女娲补天》，认识「娲、塌、裂、炼、龟、柱」等字词；知道女娲炼五色石补天、斩龟足撑天、烧芦灰堵洪水，拯救了人类。",
  ["能说出女娲补天的经过", "能说出女娲为人类做了哪几件事"],
  {"question": "女娲用什么来补天？", "answer": "炼五色石"}),
 ("麻雀", 62, U5, YD2,
  "朗读《麻雀》，认识「嗅、猎、嘶、哑、搏、扎、煞」等字词；知道老麻雀为救幼儿从树上飞下，用身体掩护小麻雀，猎狗后退了。",
  ["能说出老麻雀救子的经过", "能体会老麻雀的勇敢来自什么"],
  {"question": "老麻雀为什么从树上飞下来？", "answer": "为救掉下来的小麻雀，用身体掩护它"}),
 ("爬天都峰", 65, U5, YD2,
  "朗读《爬天都峰》，认识「级、链、攀、陡、勇、辫」等字词；知道「我」和老爷爷互相鼓励，终于爬上又高又陡的天都峰。",
  ["能说出天都峰的特点", "能说出「我」爬上顶峰的原因"],
  {"question": "天都峰有什么特点？", "answer": "又高又陡，石级像从天上挂下来"}),
]

QS = [
 ("盘古开天地", "choice", "basic", "盘古在混沌中醒来后做了什么？",
  [("A", "拿起斧头把天地劈开"), ("B", "又睡了一觉"), ("C", "开始造人"), ("D", "种下大树")], "A", "原文写他拿起大斧头朝黑暗猛劈，轻而清的东西上升成天，重而浊的下降成地。"),
 ("盘古开天地", "choice", "standard", "盘古倒下后，他的双眼变成了什么？",
  [("A", "太阳和月亮"), ("B", "两颗星星"), ("C", "两片云"), ("D", "两个湖泊")], "A", "课文写「他的双眼变成了太阳和月亮」，照亮大地。"),
 ("盘古开天地", "fill", "basic", "盘古的血液变成了奔流不息的____。", "江河", "身体化生万物，是这则神话最动人的部分。"),
 ("盘古开天地", "numeric", "basic", "「劈」字一共有几画？请用阿拉伯数字作答。", "15", "15", "「劈」上面辟 13 画、下面刀 2 画，共 15 画。"),
 ("盘古开天地", "short-answer", "standard", "说说盘古的身体化成了哪些事物。",
  "气息变成风和云，声音变成雷声，双眼变成太阳和月亮，四肢变成大地的四极，肌肤变成辽阔的大地，血液变成奔流不息的江河，汗毛变成花草树木。",
  ["气息风声、声音雷声", "双眼日月", "四肢四极、肌肤大地", "血液江河、汗毛花草"], "至少说出四组对应关系。"),
 ("精卫填海", "choice", "basic", "精卫是谁变成的？",
  [("A", "炎帝的小女儿女娃"), ("B", "黄帝的女儿"), ("C", "龙王的女儿"), ("D", "一只普通的海鸟")], "A", "原文「炎帝之少女，名曰女娃」，溺死后化为精卫。"),
 ("精卫填海", "choice", "standard", "精卫为什么要填东海？",
  [("A", "她在东海游玩时淹死没能回来，变成鸟后要把海填平"), ("B", "她想造出一片陆地"), ("C", "她想在海里捉鱼"), ("D", "她觉得好玩")], "A", "原文「女娃游于东海，溺而不返，故为精卫」，于是常衔木石填海。"),
 ("精卫填海", "fill", "basic", "常衔西山之木石，以____于东海。", "堙", "「堙」是填塞的意思，这正是「填海」二字的来历。"),
 ("精卫填海", "numeric", "basic", "「衔」字一共有几画？请用阿拉伯数字作答。", "11", "11", "「衔」左边彳 3 画、中间金 8 画，共 11 画。"),
 ("精卫填海", "short-answer", "standard", "说说精卫给你留下了什么印象。",
  "她虽然只是一只小鸟，却日日衔来西山的木石去填无边的大海，明知艰难也不停止——非常坚韧执着、不甘屈服。",
  ["小鸟填大海", "日复一日不停", "坚韧执着不屈服"], "印象＋课文依据。"),
 ("普罗米修斯", "choice", "basic", "普罗米修斯为什么受到宙斯的惩罚？",
  [("A", "他为人类拿取了火种"), ("B", "他偷了金子"), ("C", "他不肯敬神"), ("D", "他打了别的神")], "A", "他把火种带到人间，让人类有了火，宙斯因此大怒。"),
 ("普罗米修斯", "choice", "standard", "被锁在高加索山上、鹫鹰啄食肝脏时，普罗米修斯的表现是怎样的？",
  [("A", "忍受巨大痛苦，始终不屈服，不肯归还火种"), ("B", "立刻求饶认错"), ("C", "找机会逃走了"), ("D", "把火种交了出去")], "A", "他宁可受苦也不肯屈服，最后是大力神赫拉克勒斯解救了他。"),
 ("普罗米修斯", "fill", "basic", "最后，大力神____解救了他。", "赫拉克勒斯", "这是希腊神话中著名的英雄。"),
 ("普罗米修斯", "numeric", "basic", "「斯」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「斯」左边其 8 画、右边斤 4 画，共 12 画。"),
 ("普罗米修斯", "short-answer", "standard", "说说普罗米修斯是个怎样的神。",
  "他勇敢无私、一心为人类造福：为了让人间有火，不惜拿取火种；被锁在山上、被鹫鹰啄食肝脏也绝不屈服，是值得敬佩的英雄。",
  ["为人类取火", "受苦不屈服", "勇敢无私"], "品质＋两件事。"),
 ("女娲补天", "choice", "basic", "女娲用什么来补天？",
  [("A", "炼五色石"), ("B", "用白云"), ("C", "用大木头"), ("D", "用冰块")], "A", "课文写她「炼了五色石，把天补好了」。"),
 ("女娲补天", "choice", "standard", "女娲砍下什么来撑起天？",
  [("A", "大龟的四条腿"), ("B", "四棵大树"), ("C", "四座山峰"), ("D", "四根石柱")], "A", "她斩下大龟的四条腿当柱子，把天撑起来。"),
 ("女娲补天", "fill", "basic", "女娲炼了____色石，把天补好了。", "五", "「五色石」是女娲补天故事中最有名的细节。"),
 ("女娲补天", "numeric", "basic", "「娲」字一共有几画？请用阿拉伯数字作答。", "10", "10", "「娲」左边女 3 画、右边呙 7 画，共 10 画。"),
 ("女娲补天", "short-answer", "standard", "说说女娲为人类做了哪些事。",
  "天塌地裂、大火洪水、猛兽害人时，她炼五色石补好天；砍下龟的四条腿撑起天；烧芦苇的灰堵住洪水；还除掉害人的黑龙，让人类重新过上安宁的生活。",
  ["炼五色石补天", "斩龟足撑天", "烧芦灰堵洪水", "杀黑龙救人类"], "四件事逐条说。"),
 ("麻雀", "choice", "basic", "老麻雀为什么从树上飞下来？",
  [("A", "为救从巢里掉下来的小麻雀，用身体掩护它"), ("B", "想下来找食物"), ("C", "想飞走躲开"), ("D", "想和猎狗玩耍")], "A", "小麻雀掉在地上，猎狗逼近，老麻雀奋不顾身地飞下来护住它。"),
 ("麻雀", "choice", "standard", "猎狗后来为什么后退了？",
  [("A", "被老麻雀的勇敢震慑住了"), ("B", "看见有人来了"), ("C", "它没看见小麻雀"), ("D", "它太累了")], "A", "课文写猎狗「愣住了」，慢慢向后退——它被这种爱和勇气惊住了。"),
 ("麻雀", "fill", "basic", "老麻雀像一块石头似的落在猎狗面前，它____起全身的羽毛，绝望地尖叫着。", "扎煞", "「扎煞起羽毛」写出它虽弱小却拼死一搏的样子。"),
 ("麻雀", "numeric", "basic", "「雀」字一共有几画？请用阿拉伯数字作答。", "11", "11", "「雀」上面小 3 画、下面隹 8 画，共 11 画。"),
 ("麻雀", "short-answer", "standard", "说说课文写出了老麻雀怎样的精神。",
  "写出了一个弱小生命为了护住幼儿，敢于面对强大敌人的勇气：它明知不敌，仍像石头一样落在猎狗面前、扎煞起羽毛尖叫，这种奋不顾身的爱让猎狗都退却了。",
  ["弱小却敢于面对强敌", "奋不顾身护住幼儿", "勇气来自爱"], "精神＋具体表现。"),
 ("爬天都峰", "choice", "basic", "天都峰有什么特点？",
  [("A", "又高又陡，笔陡的石级像从天上挂下来的"), ("B", "又矮又平"), ("C", "很好走"), ("D", "有一条大路直通山顶")], "A", "课文写「笔陡的石级，石级边上的铁链，似乎是从天上挂下来的」。"),
 ("爬天都峰", "choice", "standard", "「我」为什么能爬上顶峰？",
  [("A", "从老爷爷身上得到勇气，两个人互相鼓励着往上爬"), ("B", "坐缆车上去的"), ("C", "爸爸背上去了"), ("D", "山路其实很短")], "A", "老爷爷说「咱们一起爬吧」，两人一路互相鼓励，都爬上了顶峰。"),
 ("爬天都峰", "fill", "basic", "老爷爷说：「咱们一起____吧！」", "爬", "这一句给了「我」勇气，是全文的转折。"),
 ("爬天都峰", "numeric", "basic", "「爬」字一共有几画？请用阿拉伯数字作答。", "8", "8", "「爬」左边爪 4 画、右边巴 4 画，共 8 画。"),
 ("爬天都峰", "short-answer", "standard", "说说「我」和老爷爷为什么最后互相道谢。",
  "因为「我」看到白发苍苍的老爷爷也来爬这么高的山，就有了勇气；老爷爷看到这么小的孩子都敢爬，也来了力气。两人互相鼓励，都爬上了顶峰，所以互相道谢。",
  ["我从老爷爷身上得到勇气", "老爷爷从小孩身上得到力气", "互相鼓励都爬上顶峰"], "要写出「互相」这个关键。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    prev = {"盘古开天地": [[t["id"] for t in topic if t["name"] == "蟋蟀的住宅"][0]]}
    newpts, name2id = [], {}
    for i, (nm, pg, ch, std, desc, mast, dq) in enumerate(PTS):
        pid = f"chi_p{pmax + 1 + i}"
        name2id[nm] = pid
        pre = prev.get(nm) or [f"chi_p{pmax + i}"]
        newpts.append({"id": pid, "name": nm, "subject": "chinese", "domain": "阅读与鉴赏",
                       "grade": 4, "semester": "上", "chapter": ch, "type": "conceptual",
                       "description": desc, "mastery_criteria": mast, "diagnostic_question": dq,
                       "external": False, "standards": [dict(std)],
                       "tags": ["课文", "阅读与鉴赏", "教材课级"],
                       "prerequisites": pre, "curriculumRef": std["id"], "verified": True,
                       "textbookRef": f"人教版语文四年级上册 第{pg}页"})
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
    newdeps = [{"from": p["prerequisites"][0], "to": p["id"], "type": "hard", "reason": "同一册前一课为本课打基础"} for p in newpts]
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
