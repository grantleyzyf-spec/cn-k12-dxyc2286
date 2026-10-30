# -*- coding: utf-8 -*-
"""语文 六上 第四~五单元（5 点）建点。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
YD2 = {"id": "cyw-2022:3.YD.02", "confidence": "partial", "quote": "能联系上下文和自己的积累，推想课文中有关词句的意思", "sourceLine": 471}
YD3 = {"id": "cyw-2022:3.YD.03", "confidence": "partial", "quote": "在阅读中了解文章的表达顺序，体会作者的思想感情，初步领悟文章的基本表达方法", "sourceLine": 475}

U4, U5 = "六年级上册 第四单元", "六年级上册 第五单元（习作单元）"

PTS = [
 ("桥", 50, U4, YD3,
  "朗读《桥》，认识「咆哮、狞、揪、呻、搀」等字词；知道洪水来临时老汉指挥群众排队过桥、让党员排在后面，自己和儿子牺牲。",
  ["能说出老汉在洪水中做了什么", "能说出老汉的性格特点"],
  {"question": "洪水来临时，老汉在桥边做什么？", "answer": "指挥群众有秩序地过桥，让党员排在后面"}),
 ("穷人", 53, U4, YD3,
  "朗读《穷人》，认识「怨、忐、忑、魁、梧、熬」等字词；知道桑娜和渔夫在极度贫困中收养了邻居的两个孤儿。",
  ["能说出桑娜为什么抱回孩子", "能说出渔夫的态度"],
  {"question": "桑娜为什么把邻居的两个孩子抱回家？", "answer": "西蒙死了，孩子没人照顾，她不忍心"}),
 ("金色的鱼钩", 58, U4, YD3,
  "朗读《金色的鱼钩》，认识「钩、饵、搪、瓷、衰」等字词；知道老班长把鱼汤让给三个病员，自己吃鱼骨头和草根，最后牺牲。",
  ["能说出老班长为什么吃鱼骨头", "能说出课文为什么以鱼钩为题"],
  {"question": "老班长为什么让小战士吃鱼，自己却吃鱼骨头和草根？", "answer": "粮食太少，他把吃的省给病员"}),
 ("灯光", 70, U5, YD3,
  "朗读《灯光》，认识「豫、歼、倚、钮、璀、璨」等字词；知道郝副营长为让后续部队找到突破口点亮书本，牺牲在战斗前。",
  ["能说出郝副营长为什么点燃书本", "能说出「灯光」在文中的含义"],
  {"question": "郝副营长为什么划着火柴点燃那本书？", "answer": "为了让后续部队看到火光，找到突破口"}),
 ("盼", 73, U5, YD3,
  "朗读《盼》，认识「袖、篷、缩、唇、梯」等字词；知道「我」盼着下雨好穿上新雨衣，课文细致写出盼望的心理。",
  ["能说出「我」为什么盼下雨", "能说出课文是怎样写「盼」的"],
  {"question": "「我」为什么盼着下雨？", "answer": "因为想穿上新买的雨衣"}),
]

QS = [
 ("桥", "choice", "basic", "洪水来临时，老汉站在桥边做什么？",
  [("A", "指挥群众有秩序地过桥，让党员排在后面"), ("B", "第一个跑过桥"), ("C", "四处去找人"), ("D", "去抢救家里的东西")], "A", "他像一座山一样站在水里指挥，把生的希望先给群众。"),
 ("桥", "choice", "standard", "老汉为什么把小伙子从队伍里揪出来？",
  [("A", "小伙子是党员，却挤在群众前面"), ("B", "他不认识路"), ("C", "他走得太慢"), ("D", "他害怕得发抖")], "A", "「党员排在后面」，这是他给党员立的规矩，对自己儿子也一样。"),
 ("桥", "fill", "basic", "老汉沙哑地喊话：「桥窄！排成一队，不要挤！____排在后面！」", "党员", "这一句是理解老汉形象的关键。"),
 ("桥", "numeric", "basic", "「洪」字一共有几画？请用阿拉伯数字作答。", "9", "9", "「洪」左边三点水 3 画、右边共 6 画，共 9 画。"),
 ("桥", "short-answer", "standard", "说说老汉是个怎样的人。",
  "他沉着果断、临危不乱，在洪水中像一座山一样站着指挥；他心里先想群众，让党员排在后面；连自己的儿子也被他揪出队伍——把生的希望留给别人，把死的危险留给自己。",
  ["沉着果断指挥有序", "群众优先、党员在后", "舍己为人连儿子也一样"], "品质＋两个细节。"),
 ("穷人", "choice", "basic", "桑娜为什么把邻居的两个孩子抱回家？",
  [("A", "西蒙死了，两个孩子没人照顾，她不忍心"), ("B", "她想收养孩子赚钱"), ("C", "渔夫让她抱回来的"), ("D", "孩子自己跑来的")], "A", "她自己已经穷得揭不开锅，还是把孩子抱了回来。"),
 ("穷人", "choice", "standard", "渔夫知道桑娜抱回孩子后是什么态度？",
  [("A", "也同意收养，说「我们总能熬过去的」"), ("B", "坚决反对"), ("C", "一时犹豫，最后同意"), ("D", "让孩子回去")], "A", "他们想到一起去了，两颗善良的心同时做了同样的选择。"),
 ("穷人", "fill", "basic", "桑娜脸色苍白，神情激动，她____地想：「他会说什么呢？」", "忐忑不安", "这个成语写出她既怕丈夫责备、又决心不改的复杂心情。"),
 ("穷人", "numeric", "basic", "「抱」字一共有几画？请用阿拉伯数字作答。", "8", "8", "「抱」左边提手旁 3 画、右边包 5 画，共 8 画。"),
 ("穷人", "short-answer", "standard", "说说桑娜和渔夫是怎样的人。",
  "他们虽然贫穷，却极其善良：桑娜在自家孩子都吃不饱的情况下抱回两个孤儿；渔夫听说后不但不反对，还说「我们总能熬过去的」。宁可自己受苦，也要帮助别人。",
  ["贫穷却善良", "桑娜抱回孤儿", "渔夫也同意、愿意熬过去"], "品质＋两人的表现。"),
 ("金色的鱼钩", "choice", "basic", "老班长为什么让小战士吃鱼，自己却吃鱼骨头和草根？",
  [("A", "粮食太少，他把吃的省给三个病员"), ("B", "他不爱吃鱼"), ("C", "他另有吃的"), ("D", "他在治病")], "A", "他把自己那份全省下来，只嚼剩下的鱼骨头和草根。"),
 ("金色的鱼钩", "choice", "standard", "课文为什么以「金色的鱼钩」为题？",
  [("A", "鱼钩闪着金光，象征老班长舍己为人的精神"), ("B", "鱼钩是金子做的"), ("C", "鱼钩非常值钱"), ("D", "鱼钩是纪念品")], "A", "鱼钩本身很普通，但上面凝结着老班长的牺牲，所以「金色」。"),
 ("金色的鱼钩", "fill", "basic", "老班长说：「你们一定要走出草地，我不能把你们丢下。」最后他牺牲在____上。", "草地", "他倒在了长征的草地上，至死还在想着战友。"),
 ("金色的鱼钩", "numeric", "basic", "「钩」字一共有几画？请用阿拉伯数字作答。", "9", "9", "「钩」左边金字旁 5 画、右边勾 4 画，共 9 画。"),
 ("金色的鱼钩", "short-answer", "standard", "说说老班长是个怎样的人。",
  "他忠于革命、舍己为人：把仅有的鱼汤让给三个病员，自己嚼鱼骨头和草根；病员不肯吃，他就想办法劝；直到牺牲前还在想着让大家走出草地。",
  ["把鱼汤让给病员", "自己吃鱼骨头草根", "临死仍想着战友"], "品质＋三处细节。"),
 ("灯光", "choice", "basic", "郝副营长为什么划着火柴点燃那本书？",
  [("A", "为了让后续部队看到火光，找到突破口"), ("B", "想取火取暖"), ("C", "想再看一会儿书"), ("D", "想照亮自己走路")], "A", "点燃书就等于暴露自己，但他选择了让部队找到路。"),
 ("灯光", "choice", "standard", "「我」为什么想起郝副营长？",
  [("A", "天安门广场璀璨的灯光让「我」想起他当年的愿望"), ("B", "有人提起了他"), ("C", "因为正在读书"), ("D", "因为走过广场")], "A", "当年他想让孩子在电灯下学习，如今广场上灯火辉煌，正是他愿望的实现。"),
 ("灯光", "fill", "basic", "郝副营长说：「赶明儿胜利了，咱们也能用上____，让孩子们在那样亮的灯光底下学习，该多好啊！」", "电灯", "这句话是他牺牲前最大的愿望。"),
 ("灯光", "numeric", "basic", "「营」字一共有几画？请用阿拉伯数字作答。", "11", "11", "「营」上面草字头 3 画、下面宫 8 画，共 11 画。"),
 ("灯光", "short-answer", "standard", "说说郝副营长是个怎样的人。",
  "他向往光明、为理想献身：战斗前还在憧憬孩子们在电灯下读书；为了让后续部队找到突破口，他点燃书本暴露自己，牺牲在胜利之前。",
  ["憧憬孩子能在电灯下读书", "点燃书本为部队指路", "为理想牺牲自己"], "愿望＋行动两面。"),
 ("盼", "choice", "basic", "「我」为什么盼着下雨？",
  [("A", "因为想穿上新买的雨衣"), ("B", "因为喜欢玩水"), ("C", "因为天气太热"), ("D", "因为想放假")], "A", "新雨衣买回来却一直晴天，她天天盼着下雨能穿上它。"),
 ("盼", "choice", "standard", "课文重点写了什么？",
  [("A", "「我」盼下雨、盼穿雨衣的细致心理活动"), ("B", "雨的样子"), ("C", "妈妈说的话"), ("D", "街道上的景色")], "A", "看天、听声、找借口出门，把一个「盼」字写得层层叠叠。"),
 ("盼", "fill", "basic", "「我」每天放学都盼着下雨，好穿上那件淡绿色的____。", "雨衣", "雨衣就是「盼」的全部理由。"),
 ("盼", "numeric", "basic", "「盼」字一共有几画？请用阿拉伯数字作答。", "9", "9", "「盼」左边目 5 画、右边分 4 画，共 9 画。"),
 ("盼", "short-answer", "standard", "说说课文是怎样写出「盼」的心情的。",
  "通过一连串细节：反复看天、盼乌云、听雨声、借口出门看雨、试穿雨衣、盼妈妈答应；还写她着急时说话撒娇、心里嘀咕，把一个孩子盼望的心理写得真实可爱。",
  ["反复看天听雨声", "找借口出门、试穿雨衣", "撒娇、心里嘀咕"], "要举出具体细节。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    prev = {"桥": [[t["id"] for t in topic if t["name"] == "故宫博物院"][0]]}
    newpts, name2id = [], {}
    for i, (nm, pg, ch, std, desc, mast, dq) in enumerate(PTS):
        pid = f"chi_p{pmax + 1 + i}"
        name2id[nm] = pid
        pre = prev.get(nm) or [f"chi_p{pmax + i}"]
        newpts.append({"id": pid, "name": nm, "subject": "chinese", "domain": "阅读与鉴赏",
                       "grade": 6, "semester": "上", "chapter": ch, "type": "conceptual",
                       "description": desc, "mastery_criteria": mast, "diagnostic_question": dq,
                       "external": False, "standards": [dict(std)],
                       "tags": ["课文", "阅读与鉴赏", "教材课级"],
                       "prerequisites": pre, "curriculumRef": std["id"], "verified": True,
                       "textbookRef": f"人教版语文六年级上册 第{pg}页"})
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
