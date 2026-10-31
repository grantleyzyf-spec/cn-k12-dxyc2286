# -*- coding: utf-8 -*-
"""语文 七上 第二单元（6 点）建点。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
YD04 = {"id": "cyw-2022:4.YD.04", "confidence": "partial", "quote": "欣赏文学作品，有自己的情感体验，初步领悟作品的内涵", "sourceLine": 579}
YD06 = {"id": "cyw-2022:4.YD.06", "confidence": "partial", "quote": "诵读古代诗词，阅读浅易文言文，能借助注释和工具书理解", "sourceLine": 599}

U2 = "七年级上册 第二单元"

PTS = [
 ("秋天的怀念", 24, U2, YD04,
  "朗读《秋天的怀念》，认识「瘫痪、暴怒、沉寂、捶打、憔悴」等词语；知道母亲忍着病痛照顾残疾的「我」，临终嘱托「好好活儿」。",
  ["能说出母亲为「我」做了哪些事", "能说出结尾「好好活儿」的含义"],
  {"question": "母亲为什么一再劝「我」去看菊花？", "answer": "想让「我」出去散心，重新有生活的勇气"}),
 ("散步", 27, U2, YD04,
  "朗读《散步》，认识「信服、熬、委屈、各得其所」等词语；知道一家人散步时的分歧与体谅，体会尊老爱幼的温情。",
  ["能说出散步时的分歧和解决办法", "能说出结尾「整个世界」的含义"],
  {"question": "散步时产生的分歧是什么？", "answer": "母亲要走大路，儿子要走小路"}),
 ("金色花", 30, U2, YD04,
  "朗读《金色花》，认识「匿笑、沐浴、祷告、罗摩衍那」等词语；知道孩子变成金色花隐身陪伴母亲，体会孩子对母亲的爱。",
  ["能说出「我」变成金色花后做了什么", "能说出诗中的想象妙在哪里"],
  {"question": "诗中「我」变成金色花后做了什么？", "answer": "在高枝上看妈妈做事，暗暗陪伴她"}),
 ("荷叶·母亲", 30, U2, YD04,
  "朗读《荷叶·母亲》，认识「攲斜、荫蔽、徘徊、姊妹」等词语；知道作者由雨中荷叶护红莲，想到母亲对子女的庇护。",
  ["能说出荷叶与红莲各比喻什么", "能说出「心中的雨点」指什么"],
  {"question": "课文用荷叶护红莲比喻什么？", "answer": "母亲保护儿女"}),
 ("咏雪", 34, U2, YD06,
  "朗读《咏雪》，认识「俄而、骤、差可拟、未若、因风起」等词语；知道谢道韫以「柳絮因风起」咏雪，被赞为妙喻。",
  ["能借助注释读懂全文", "能说出两个比喻的优劣"],
  {"question": "谢道韫用什么比喻白雪？", "answer": "柳絮因风起"}),
 ("陈太丘与友期行", 34, U2, YD06,
  "朗读《陈太丘与友期行》，认识「期行、日中、舍去、乃、委、引」等词语；知道元方以「无信」「无礼」反驳父亲的朋友。",
  ["能借助注释读懂全文", "能说出元方反驳的两条理由"],
  {"question": "元方用什么理由反驳父亲的朋友？", "answer": "对方失信又无礼"}),
]

QS = [
 ("秋天的怀念", "choice", "basic", "母亲为什么一再劝「我」去看菊花？",
  [("A", "想让「我」出去散心，重新有生活的勇气"), ("B", "因为菊花很好看"), ("C", "想买几盆花回家"), ("D", "怕「我」一个人在家闷得慌而已")], "A", "母亲自己病得很重，还一心想让儿子从绝望里走出来，「看菊花」就是盼他好好活。"),
 ("秋天的怀念", "choice", "standard", "结尾母亲说的「好好活儿」是什么意思？",
  [("A", "既是母亲临终的嘱托，也是「我」后来的领悟"), ("B", "一句抱怨"), ("C", "一句玩笑话"), ("D", "一句诗")], "A", "母亲用命换来的这句话，成了「我」此后的生活态度。"),
 ("秋天的怀念", "fill", "basic", "「咱娘儿俩在一块儿，好好儿活，好好儿活……」这句话是____说的。", "母亲", "母亲说这句话时已经病得很重了。"),
 ("秋天的怀念", "numeric", "basic", "「瘫」字一共有几画？请用阿拉伯数字作答。", "17", "17", "「瘫」左边病字旁 5 画、右边难 12 画，共 17 画。"),
 ("秋天的怀念", "short-answer", "standard", "说说课文中的母亲是个怎样的人。",
  "她坚强、无私、极其细心：自己病重还瞒着儿子，忍着痛照顾他的起居；儿子发脾气时她只悄悄出去，回来还笑着劝他看菊花；临终最后一句仍是惦记儿女。",
  ["自己病重还瞒着", "细心照顾不发脾气", "临终仍嘱托儿女好好活"], "特点＋三处细节。"),
 ("散步", "choice", "basic", "散步时一家人产生了什么分歧？",
  [("A", "母亲要走大路，儿子要走小路"), ("B", "谁去买菜"), ("C", "到哪里吃饭"), ("D", "要不要带伞")], "A", "大路平顺适合老人，小路有意思适合孩子，两难之间见亲情。"),
 ("散步", "choice", "standard", "「我」最后决定走大路，理由是什么？",
  [("A", "母亲年迈，陪她的时间不多了，应该依着她"), ("B", "大路更近"), ("C", "大路风景更好"), ("D", "儿子改主意了")], "A", "「我」权衡之后选择「委屈儿子」，体现尊老的用心。"),
 ("散步", "fill", "basic", "「我和妻子都是慢慢地，稳稳地，走得很仔细，好像我背上的同她背上的加起来，就是整个____。」", "世界", "一老一小就是「整个世界」，这句话把亲情写到了极处。"),
 ("散步", "numeric", "basic", "「散」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「散」左边 8 画、右边攵 4 画，共 12 画。"),
 ("散步", "short-answer", "standard", "说说课文表现了怎样的家庭关系。",
  "表现了尊老爱幼、互相体谅的温馨关系：母亲体贴儿孙愿意迁就，儿子顾虑母亲的身体，「我」和妻子分头背起老人和孩子，一家人和和美美。",
  ["尊老爱幼", "互相体谅各得其所", "温馨和睦"], "关系＋文中依据。"),
 ("金色花", "choice", "basic", "诗中「我」变成金色花以后做了什么？",
  [("A", "长在高枝上看妈妈做事，暗暗陪伴她"), ("B", "去上学读书"), ("C", "找小朋友玩"), ("D", "在树上睡觉")], "A", "他看妈妈沐浴、祷告、读书，还悄悄把影子投在书页上。"),
 ("金色花", "choice", "standard", "这首诗表达了什么感情？",
  [("A", "孩子对母亲深深的爱和依恋"), ("B", "赞美花朵美丽"), ("C", "想出去玩的心思"), ("D", "对母亲严厉的抱怨")], "A", "全诗用孩子的顽皮写成，越顽皮越见真心的爱。"),
 ("金色花", "fill", "basic", "「假如我变成了一朵____花，为了好玩，长在树的高枝上……」", "金色", "「金色花」是印度圣树上的花，题目由此而来。"),
 ("金色花", "numeric", "basic", "「瓣」字一共有几画？请用阿拉伯数字作答。", "19", "19", "「瓣」左中右三部分共 19 画。"),
 ("金色花", "short-answer", "standard", "说说这首诗的想象奇妙在哪里。",
  "奇在「变成金色花」：孩子不声不响地隐身，躲在树上看着妈妈、陪着妈妈，还把影子投到妈妈读的书页上；最后又突然变回孩子要妈妈讲故事——用游戏的方式写出最深的爱。",
  ["变成金色花隐身", "暗暗陪伴、投影子", "变回孩子撒娇"], "想象＋效果。"),
 ("荷叶·母亲", "choice", "basic", "课文用荷叶护红莲来比喻什么？",
  [("A", "母亲保护儿女"), ("B", "雨下得很大"), ("C", "荷花非常美"), ("D", "池塘很安静")], "A", "「母亲啊！你是荷叶，我是红莲」，一句就把比喻点透了。"),
 ("荷叶·母亲", "choice", "standard", "「心中的雨点来了」指的是什么？",
  [("A", "生活中心灵受到的打击和困难"), ("B", "外面真的下雨了"), ("C", "天气忽然变冷"), ("D", "心情特别高兴")], "A", "自然的雨点有荷叶抵挡，心灵的雨点要靠母亲。"),
 ("荷叶·母亲", "fill", "basic", "「母亲啊！你是荷叶，我是红莲，心中的雨点来了，除了你，谁是我在无遮拦天空下的____？」", "荫蔽", "「荫蔽」是遮蔽、庇护的意思。"),
 ("荷叶·母亲", "numeric", "basic", "「莲」字一共有几画？请用阿拉伯数字作答。", "10", "10", "「莲」上面草字头 3 画、下面连 7 画，共 10 画。"),
 ("荷叶·母亲", "short-answer", "standard", "说说课文是怎样借景抒情的。",
  "先写雨打红莲、红莲被打得欹斜，再写荷叶慢慢倾侧过来覆盖住红莲；由这一动人的景，想到母亲庇护子女，于是直呼「你是荷叶，我是红莲」，托物寄情。",
  ["雨打红莲", "荷叶倾侧覆盖红莲", "由景想到母亲庇护"], "景—情两层。"),
 ("咏雪", "choice", "basic", "谢道韫用什么来比喻白雪？",
  [("A", "柳絮因风起"), ("B", "撒盐空中"), ("C", "一团白棉花"), ("D", "满地白羽毛")], "A", "「未若柳絮因风起」，谢太傅听了「大笑乐」。"),
 ("咏雪", "choice", "standard", "谢太傅为什么「大笑乐」？",
  [("A", "欣赏侄女这个比喻更妙"), ("B", "觉得侄子比错了"), ("C", "雪景太好看了"), ("D", "孩子们背出了课文")], "A", "笑里是对侄女才华的赞赏，所以文中特意点出她的身份。"),
 ("咏雪", "fill", "basic", "「未若____因风起。」", "柳絮", "柳絮轻、能随风飞舞，正合雪花飘落之态。"),
 ("咏雪", "numeric", "basic", "「絮」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「絮」上面如 6 画、下面糸 6 画，共 12 画。"),
 ("咏雪", "short-answer", "standard", "说说为什么「柳絮因风起」比「撒盐空中」更好。",
  "盐粒重、直落，只能比出雪的颜色和颗粒；柳絮又轻又软，遇风飘舞，既像雪花的轻，又有漫天纷飞之态，还带上春天的诗意，所以更妙。",
  ["盐重直落只比颜色", "柳絮轻盈随风飞舞", "更有诗意"], "两喻对比，各说一句。"),
 ("陈太丘与友期行", "choice", "basic", "元方用什么理由反驳父亲的朋友？",
  [("A", "对方失信（日中不至），又无礼（对子骂父）"), ("B", "对方迟到太久"), ("C", "对方没有带礼物"), ("D", "对方说话声音太大")], "A", "两条理由一条比一条硬，说得对方「惭，下车引之」。"),
 ("陈太丘与友期行", "choice", "standard", "元方「入门不顾」表现了什么？",
  [("A", "一个七岁孩子的率真和是非分明"), ("B", "他完全不懂礼貌"), ("C", "他心里害怕"), ("D", "他生气跑掉了")], "A", "该讲的理讲完了，转身进屋，写出孩子的直率。"),
 ("陈太丘与友期行", "fill", "basic", "「日中不至，则是无____；对子骂父，则是无礼。」", "信", "「信」与「礼」两个字，正是全文的骨。"),
 ("陈太丘与友期行", "numeric", "basic", "「期」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「期」左边其 8 画、右边月 4 画，共 12 画。"),
 ("陈太丘与友期行", "short-answer", "standard", "说说这个故事告诉我们什么。",
  "做人要讲信用、懂礼貌：朋友不守约定的时间，还当着孩子的面骂人，所以元方以「无信」「无礼」反击。同时也写出元方年幼而明理、率真可爱。",
  ["做人要守信有礼", "元方以无信无礼反驳", "写出元方年幼明理"], "道理＋人物形象。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    prev = {"秋天的怀念": [[t["id"] for t in topic if t["name"] == "天净沙·秋思"][0]]}
    newpts, name2id = [], {}
    for i, (nm, pg, ch, std, desc, mast, dq) in enumerate(PTS):
        pid = f"chi_p{pmax + 1 + i}"
        name2id[nm] = pid
        pre = prev.get(nm) or [f"chi_p{pmax + i}"]
        newpts.append({"id": pid, "name": nm, "subject": "chinese", "domain": "阅读与鉴赏",
                       "grade": 7, "semester": "上", "chapter": ch, "type": "conceptual",
                       "description": desc, "mastery_criteria": mast, "diagnostic_question": dq,
                       "external": False, "standards": [dict(std)],
                       "tags": ["课文", "阅读与鉴赏", "教材课级"],
                       "prerequisites": pre, "curriculumRef": std["id"], "verified": True,
                       "textbookRef": f"人教版语文七年级上册 第{pg}页"})
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
