# -*- coding: utf-8 -*-
"""语文 六上 第八单元（4 点）建点 —— 六上收官（31 点）。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
YD2 = {"id": "cyw-2022:3.YD.02", "confidence": "partial", "quote": "能联系上下文和自己的积累，推想课文中有关词句的意思", "sourceLine": 471}
YD3 = {"id": "cyw-2022:3.YD.03", "confidence": "partial", "quote": "在阅读中了解文章的表达顺序，体会作者的思想感情，初步领悟文章的基本表达方法", "sourceLine": 475}
YD4 = {"id": "cyw-2022:3.YD.04", "confidence": "partial", "quote": "阅读诗歌，大体把握诗意，想象诗歌描述的情境，体会作品的情感", "sourceLine": 481}

U8 = "六年级上册 第八单元"

PTS = [
 ("少年闰土", 110, U8, YD3,
  "朗读《少年闰土》，认识「胯、猹、畜、撒、缚」等字词；知道闰土给「我」讲雪地捕鸟、看瓜刺猹、看跳鱼儿，是一个见多识广的农村少年。",
  ["能说出闰土讲的几件事", "能说出「我」为什么佩服闰土"],
  {"question": "闰土给「我」讲了哪几件新鲜事？", "answer": "雪地捕鸟、夏日看瓜刺猹、看跳鱼儿"}),
 ("好的故事", 114, U8, YD3,
  "朗读《好的故事》，认识「幽、雅、锦、错、综」等字词；知道课文写的是一个美丽的梦境，醒来后仍在追忆。",
  ["能说出「好的故事」实际指什么", "能说出作者表达的情感"],
  {"question": "「好的故事」实际写的是什么？", "answer": "一个美丽的梦境"}),
 ("我的伯父鲁迅先生", 117, U8, YD3,
  "朗读《我的伯父鲁迅先生》，认识「悼、囫、囵、吞、枣」等字词；知道课文通过几件小事写出鲁迅先生的爱憎与和蔼。",
  ["能说出课文写了鲁迅先生的哪几件事", "能说出「碰壁」的实际含义"],
  {"question": "「四周围黑洞洞的，还不容易碰壁吗」中的「碰壁」实际指什么？", "answer": "旧社会里受到迫害、处处受阻"}),
 ("有的人——纪念鲁迅有感", 121, U8, YD4,
  "诵读臧克家《有的人——纪念鲁迅有感》，认识「朽、摔、垮、俯」等字词；知道诗中对比了两种人，赞颂为人民献身的人。",
  ["能背诵这首诗的第一节", "能说出诗中对比的两种人"],
  {"question": "「有的人活着，他已经死了」讽刺的是什么人？", "answer": "骑在人民头上、只为个人活着的人"}),
]

QS = [
 ("少年闰土", "choice", "basic", "闰土给「我」讲了哪几件新鲜事？",
  [("A", "雪地捕鸟、夏日看瓜刺猹、看跳鱼儿"), ("B", "只会讲捕鱼"), ("C", "讲读书考试"), ("D", "讲城里的热闹")], "A", "这三件事一件比一件新鲜，把「我」听得入了迷。"),
 ("少年闰土", "choice", "standard", "「我」为什么佩服闰土？",
  [("A", "他心里有无穷无尽的稀奇事，是「我」素不知道的"), ("B", "他力气特别大"), ("C", "他会写很多字"), ("D", "他家很有钱")], "A", "「我」只在院子里看天，闰土却在海边经历这些事，所以格外佩服。"),
 ("少年闰土", "fill", "basic", "深蓝的天空中挂着一轮金黄的圆月，下面是海边的沙地，都种着一望无际的碧绿的____。", "西瓜", "这幅画面是全文最著名的场景。"),
 ("少年闰土", "numeric", "basic", "「猹」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「猹」左边反犬旁 3 画、右边查 9 画，共 12 画。"),
 ("少年闰土", "short-answer", "standard", "说说闰土是个怎样的少年。",
  "他是一个活泼、勇敢、能干的农村少年：会装弶捕鸟、敢在月夜看瓜刺猹、认识跳鱼儿，见多识广，心里有说不完的稀奇事。",
  ["活泼勇敢", "会捕鸟敢刺猹", "见多识广"], "特点＋三件事。"),
 ("好的故事", "choice", "basic", "「好的故事」实际写的是什么？",
  [("A", "一个美丽的梦境，山阴道上的美景"), ("B", "一个真实发生的故事"), ("C", "一本故事书"), ("D", "一次旅行经历")], "A", "课文写「我」在朦胧中看见许多美的人和美的事，其实是一场梦。"),
 ("好的故事", "choice", "standard", "课文的结尾是怎样的？",
  [("A", "梦醒后「我」还在追忆那美好的景象"), ("B", "故事刚好讲完"), ("C", "天已经亮了"), ("D", "他把梦全忘了")], "A", "「我」总记得见过这一篇好的故事，在昏沉中追忆——余味悠长。"),
 ("好的故事", "fill", "basic", "这故事很美丽，幽雅，有趣。许多美的人和美的事，错综起来像一天____。", "云锦", "「云锦」这个比喻写出景象的绚烂。"),
 ("好的故事", "numeric", "basic", "「幽」字一共有几画？请用阿拉伯数字作答。", "9", "9", "「幽」共 9 画。"),
 ("好的故事", "short-answer", "standard", "说说《好的故事》表达了作者怎样的情感。",
  "借着梦中的美景，表达了对美好生活的向往和追求：景物明媚、人和事都美，醒来仍在追忆，说明这美好虽在梦中，却是作者心里真正想要的。",
  ["描绘梦中的美景", "向往美好生活", "醒来仍追忆"], "情感＋依据。"),
 ("我的伯父鲁迅先生", "choice", "basic", "课文写了鲁迅先生的哪几件事？",
  [("A", "谈《水浒传》、笑谈「碰壁」、除夕放爆竹、救助车夫、关心女佣"), ("B", "只写了一件"), ("C", "写他发表的文章"), ("D", "写他生病住院")], "A", "几件小事串起来，一个可敬可亲的鲁迅就站在面前。"),
 ("我的伯父鲁迅先生", "choice", "standard", "「四周围黑洞洞的，还不容易碰壁吗」中的「碰壁」实际指什么？",
  [("A", "旧社会里受到迫害、处处受阻"), ("B", "走路撞到墙"), ("C", "摔了一跤"), ("D", "光线太暗看不清")], "A", "鲁迅用幽默的话说出反动统治下的处境，含着愤怒与讽刺。"),
 ("我的伯父鲁迅先生", "fill", "basic", "鲁迅先生笑着说：「你想，四周围黑洞洞的，还不容易____吗？」", "碰壁", "一句玩笑话，把黑暗现实说透了。"),
 ("我的伯父鲁迅先生", "numeric", "basic", "「鲁」字一共有几画？请用阿拉伯数字作答。", "12", "12", "「鲁」上面鱼 8 画、下面日 4 画，共 12 画。"),
 ("我的伯父鲁迅先生", "short-answer", "standard", "说说课文中的鲁迅是个怎样的人。",
  "他爱憎分明、幽默风趣、慈祥和蔼：谈《水浒传》时循循善诱，用「碰壁」讽刺黑暗社会；除夕和孩子们一起放爆竹；又冒着风险救助车夫、关心女佣。",
  ["爱憎分明幽默风趣", "对亲人慈祥和蔼", "关心劳动人民"], "三方面＋事例。"),
 ("有的人——纪念鲁迅有感", "choice", "basic", "「有的人活着，他已经死了」讽刺的是什么人？",
  [("A", "骑在人民头上、只为个人活着的人"), ("B", "生病的病人"), ("C", "已经死去的人"), ("D", "年纪很大的老人")], "A", "他们虽然还活着，但在人民心里早已死了。"),
 ("有的人——纪念鲁迅有感", "choice", "standard", "诗中「有的人死了，他还活着」指的是谁？",
  [("A", "鲁迅这样为人民献身、被人民记住的人"), ("B", "所有去世的人"), ("C", "普通的过路人"), ("D", "古代的英雄")], "A", "这是全诗对比的另一半，也是献给鲁迅的评价。"),
 ("有的人——纪念鲁迅有感", "fill", "basic", "把诗句补全：有的人活着，他已经____。", "死了", "下一句是「有的人死了，他还活着」，一正一反。"),
 ("有的人——纪念鲁迅有感", "numeric", "basic", "「纪」字一共有几画？请用阿拉伯数字作答。", "6", "6", "「纪」左边绞丝旁 3 画、右边己 3 画，共 6 画。"),
 ("有的人——纪念鲁迅有感", "short-answer", "standard", "说说这首诗表达了怎样的思想感情。",
  "诗人用对比手法赞颂鲁迅那样为人民献身、被人民永远记住的人；同时鞭挞骑在人民头上、只为自己活着的人。表达了鲜明的人民立场。",
  ["对比两种人", "赞颂为人民献身者", "鞭挞压迫人民的人"], "手法＋两种态度。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    prev = {"少年闰土": [[t["id"] for t in topic if t["name"] == "他们那时候多有趣啊"][0]]}
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
