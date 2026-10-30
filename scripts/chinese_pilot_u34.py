# -*- coding: utf-8 -*-
"""语文 一上 第三、四单元（汉语拼音 10 课）建点：10 点 + 50 题。"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv
SX02 = {"id": "cyw-2022:1.SX.02", "confidence": "partial",
        "quote": "能准确地拼读音节，正确书写声母、韵母和音节", "sourceLine": 273}

U3 = "一年级上册 第三单元 汉语拼音"
U4 = "一年级上册 第四单元 汉语拼音"

PTS = [
 ("g k h", 32, U3, "认识声母 g、k、h，读准音、认清形；知道 g 不送气、k 送气，能用它们与单韵母拼读音节。",
  ["能准确读出 g、k、h", "能区分 g 与 k 的送气与否"],
  {"question": "g、k、h 三个声母中，发音时气流最强的是哪一个？", "answer": "k"}),
 ("j q x", 34, U3, "认识声母 j、q、x，读准音、认清形；知道 j、q、x 只与 ü 相拼，与 ü 相拼时 ü 上两点要省去。",
  ["能准确读出 j、q、x", "知道 j、q、x 与 ü 相拼时 ü 去掉两点"],
  {"question": "j、q、x 与 ü 相拼时，ü 上的两点应该怎样处理？", "answer": "去掉"}),
 ("z c s", 36, U3, "认识声母 z、c、s，知道它们是平舌音，发音时舌尖平放抵住下齿背。",
  ["能准确读出 z、c、s", "能说出 z、c、s 是平舌音"],
  {"question": "z、c、s 三个声母属于平舌音还是翘舌音？", "answer": "平舌音"}),
 ("zh ch sh r", 38, U3, "认识声母 zh、ch、sh、r，知道它们是翘舌音，发音时舌尖上翘抵住硬腭前部。",
  ["能准确读出 zh、ch、sh、r", "能区分平舌音与翘舌音"],
  {"question": "zh、ch、sh、r 四个声母属于平舌音还是翘舌音？", "answer": "翘舌音"}),
 ("y w", 40, U3, "认识声母 y、w，知道它们起隔音作用；会认读整体认读音节 yi、wu、yu。",
  ["能准确读出 y、w", "能认读 yi、wu、yu 三个整体认读音节"],
  {"question": "i 前面加上 y 以后写成的音节是什么？", "answer": "yi"}),
 ("ai ei ui", 45, U4, "认识复韵母 ai、ei、ui，知道它们由两个单韵母合成，发音时口形要滑动；知道 ui 的声调标在 i 上。",
  ["能准确读出 ai、ei、ui", "知道 ui 的声调标在 i 上"],
  {"question": "ai、ei、ui 是单韵母还是复韵母？", "answer": "复韵母"}),
 ("ao ou iu", 47, U4, "认识复韵母 ao、ou、iu，读准时注意起点的口形；知道 iu 是 iou 的省写，声调标在 u 上。",
  ["能准确读出 ao、ou、iu", "知道 iu 的声调标在 u 上"],
  {"question": "ao、ou、iu 中，由 i 和 ou 省写而成的是哪一个？", "answer": "iu"}),
 ("ie üe er", 49, U4, "认识复韵母 ie、üe 和特殊韵母 er；知道 üe 与 j、q、x 相拼时写作 ue，er 不能与声母相拼。",
  ["能准确读出 ie、üe、er", "知道 er 是特殊韵母，不与声母相拼"],
  {"question": "ie、üe、er 中，不能与声母相拼的是哪一个？", "answer": "er"}),
 ("an en in un ün", 51, U4, "认识五个前鼻韵母 an、en、in、un、ün，知道它们的韵尾是 -n，发音时舌尖抵住上齿龈、气流从鼻腔出。",
  ["能准确读出 an、en、in、un、ün", "知道前鼻韵母的韵尾是 -n"],
  {"question": "an、en、in、un、ün 属于前鼻韵母还是后鼻韵母？", "answer": "前鼻韵母"}),
 ("ang eng ing ong", 54, U4, "认识四个后鼻韵母 ang、eng、ing、ong，知道它们的韵尾是 -ng，发音时舌根抵住软腭、气流从鼻腔出。",
  ["能准确读出 ang、eng、ing、ong", "能分辨前鼻韵母与后鼻韵母"],
  {"question": "ang、eng、ing、ong 的韵尾是 -n 还是 -ng？", "answer": "-ng"}),
]

QS = [
 ("g k h", "choice", "basic", "g、k、h 三个声母中，发音时手掌能感到明显气流的是哪一个？",
  [("A", "g"), ("B", "k"), ("C", "h"), ("D", "都一样")], "B", "g 不送气、k 送气，读 k 时手掌能感到气流。"),
 ("g k h", "choice", "standard", "声母 h 的发音部位在什么地方？",
  [("A", "舌尖"), ("B", "舌根"), ("C", "双唇"), ("D", "鼻腔")], "B", "h 是舌根音，气流从舌根与软腭之间的缝隙擦出。"),
 ("g k h", "fill", "basic", "g、k、h 三个字母都是____。", "声母", "它们都要和韵母相拼成音节，是声母。"),
 ("g k h", "numeric", "basic", "「g k h」这一课一共学了几个声母？请用阿拉伯数字作答。", "3", "3", "本课学 g、k、h 共 3 个声母。"),
 ("g k h", "short-answer", "standard", "说说 g 和 k 的发音有什么不同，可以用什么办法区分。",
  "g 不送气，读时手掌几乎感觉不到气流；k 送气，读时手掌能感到明显气流。把手掌放在嘴前读一读就能分清。",
  ["g 不送气", "k 送气", "用手掌试气流"], "送气与否是这一课最容易混的地方。"),
 ("j q x", "choice", "basic", "j、q、x 与 ü 相拼时，ü 上的两点应该怎样处理？",
  [("A", "保留两点"), ("B", "去掉两点"), ("C", "改成一点"), ("D", "换成 o")], "B", "j、q、x 只与 ü 相拼，写成 ju、qu、xu 时去掉两点。"),
 ("j q x", "choice", "standard", "下面四个声母中，属于舌面音的是哪一个？",
  [("A", "g"), ("B", "j"), ("C", "z"), ("D", "h")], "B", "j、q、x 是舌面音，舌面前部贴近硬腭前部发音。"),
 ("j q x", "fill", "basic", "j、q、x 与 ü 相拼写成 ju、qu、xu，其中的 u 实际读作____。", "ü", "书写时去掉两点，读音仍是 ü。"),
 ("j q x", "numeric", "basic", "「j q x」这一课一共学了几个声母？请用阿拉伯数字作答。", "3", "3", "本课学 j、q、x 共 3 个声母。"),
 ("j q x", "short-answer", "standard", "为什么 ju、qu、xu 里的 u 要读作 ü？",
  "因为 j、q、x 不能与 u 相拼，只与 ü 相拼；书写规定与 ü 相拼时去掉两点，但读音不变，仍读 ü。",
  ["j q x 只与 ü 相拼", "去两点是书写规定", "读音仍是 ü"], "这是拼音里最典型的「写一套、读一套」。"),
 ("z c s", "choice", "basic", "z、c、s 三个声母属于下面哪一类？",
  [("A", "平舌音"), ("B", "翘舌音"), ("C", "韵母"), ("D", "鼻音")], "A", "z、c、s 发音时舌尖平放，是平舌音。"),
 ("z c s", "choice", "standard", "声母 s 的发音方法属于哪一种？",
  [("A", "塞音"), ("B", "塞擦音"), ("C", "擦音"), ("D", "边音")], "C", "s 发音时气流从窄缝中摩擦而出，是擦音。"),
 ("z c s", "fill", "basic", "z、c、s 发音时舌尖平放，所以叫____音。", "平舌", "与舌尖上翘的 zh、ch、sh 相对。"),
 ("z c s", "numeric", "basic", "「z c s」这一课一共学了几个声母？请用阿拉伯数字作答。", "3", "3", "本课学 z、c、s 共 3 个声母。"),
 ("z c s", "short-answer", "standard", "说说平舌音 z、c、s 和翘舌音 zh、ch、sh 在发音上有什么不同。",
  "平舌音发音时舌尖平放抵住下齿背；翘舌音发音时舌尖上翘抵住硬腭前部。",
  ["平舌舌尖平放", "翘舌舌尖上翘", "部位不同"], "舌尖位置是区分这两组声母的关键。"),
 ("zh ch sh r", "choice", "basic", "zh、ch、sh、r 四个声母都属于下面哪一类？",
  [("A", "平舌音"), ("B", "翘舌音"), ("C", "单韵母"), ("D", "复韵母")], "B", "这四个声母发音时舌尖上翘，是翘舌音。"),
 ("zh ch sh r", "choice", "standard", "声母 r 与 sh 相比，最主要的差别是什么？",
  [("A", "完全相同"), ("B", "r 发音时声带振动，sh 不振动"), ("C", "r 是韵母"), ("D", "sh 是鼻音")], "B", "sh 是清音、声带不振动；r 是浊音、声带要振动。"),
 ("zh ch sh r", "fill", "basic", "zh、ch、sh、r 四个声母都是____音。", "翘舌", "与平舌音 z、c、s 相对。"),
 ("zh ch sh r", "numeric", "basic", "「zh ch sh r」这一课一共学了几个声母？请用阿拉伯数字作答。", "4", "4", "本课学 zh、ch、sh、r 共 4 个声母。"),
 ("zh ch sh r", "short-answer", "standard", "同桌把「知识」读成了「姿势」，请说说他读错了哪一组声母。",
  "「知」的声母是翘舌音 zh，他读成了平舌音 z，所以听起来像「姿势」，要提醒他把舌尖上翘。",
  ["知 的声母是 zh", "误读成平舌 z", "舌尖上翘"], "平翘舌混读是小学生最常见的拼音错误。"),
 ("y w", "choice", "basic", "y、w 在拼音里起的主要作用是什么？",
  [("A", "只能当韵母"), ("B", "当声母，起隔音作用"), ("C", "表示声调"), ("D", "表示轻声")], "B", "y、w 用来隔开音节，避免两个韵母连写时读混。"),
 ("y w", "choice", "standard", "i 前面加上 y 以后，写成的音节是哪一个？",
  [("A", "yi"), ("B", "iy"), ("C", "y i"), ("D", "ii")], "A", "i 单独成音节时写作 yi，是整体认读音节。"),
 ("y w", "fill", "basic", "u 前面加上 w，写成的音节是____。", "wu", "u 单独成音节时写作 wu。"),
 ("y w", "numeric", "basic", "「y w」这一课一共学了几个声母？请用阿拉伯数字作答。", "2", "2", "本课学 y、w 共 2 个声母。"),
 ("y w", "short-answer", "standard", "说说为什么 yi、wu、yu 叫做整体认读音节。",
  "它们要整个记下来直接认读，不用把声母和韵母分开拼，所以叫整体认读音节。",
  ["整体记住", "直接认读", "不需分拼"], "整体认读音节是拼音学习里的特殊一类。"),
 ("ai ei ui", "choice", "basic", "ai、ei、ui 三个韵母属于下面哪一类？",
  [("A", "单韵母"), ("B", "复韵母"), ("C", "声母"), ("D", "鼻韵母")], "B", "它们由两个单韵母合成，是复韵母。"),
 ("ai ei ui", "choice", "standard", "复韵母 ui 的声调应该标在哪个字母上？",
  [("A", "u 上"), ("B", "i 上"), ("C", "两个都标"), ("D", "不标")], "B", "ui 的声调标在 i 上，如 guī。"),
 ("ai ei ui", "fill", "basic", "ai、ei、ui 都由两个单韵母合成，所以叫____韵母。", "复", "合成韵母即复韵母。"),
 ("ai ei ui", "numeric", "basic", "「ai ei ui」这一课一共学了几个复韵母？请用阿拉伯数字作答。", "3", "3", "本课学 ai、ei、ui 共 3 个复韵母。"),
 ("ai ei ui", "short-answer", "standard", "说说 ai 是怎样读出来的。",
  "先发 a 的音，口形张大，然后快速滑向 i，一口气连读成一个音。",
  ["先发 a 的音", "快速滑向 i", "一口气连读"], "复韵母的关键是「滑动」，不是两个音分开念。"),
 ("ao ou iu", "choice", "basic", "下面四个字母组合中，属于复韵母的是哪一个？",
  [("A", "ao"), ("B", "a"), ("C", "m"), ("D", "h")], "A", "ao 由 a 和 o 合成，是复韵母。"),
 ("ao ou iu", "choice", "standard", "复韵母 iu 的声调应该标在哪个字母上？",
  [("A", "i 上"), ("B", "u 上"), ("C", "两个都标"), ("D", "不标")], "B", "iu 是 iou 的省写，声调标在 u 上，如 liù。"),
 ("ao ou iu", "fill", "basic", "ao、ou、iu 三个韵母都是____韵母。", "复", "它们都由两个单韵母合成。"),
 ("ao ou iu", "numeric", "basic", "「ao ou iu」这一课一共学了几个复韵母？请用阿拉伯数字作答。", "3", "3", "本课学 ao、ou、iu 共 3 个复韵母。"),
 ("ao ou iu", "short-answer", "standard", "说说 ao 和 ou 在发音起点上有什么不同。",
  "ao 从 a 起音，嘴巴张得较大；ou 从 o 起音，嘴唇较圆。",
  ["ao 从 a 起音", "ou 从 o 起音", "口形大小不同"], "起点不同，两个复韵母听起来就不一样。"),
 ("ie üe er", "choice", "basic", "ie、üe、er 三个韵母中，不能与声母相拼的是哪一个？",
  [("A", "ie"), ("B", "üe"), ("C", "er"), ("D", "都可以相拼")], "C", "er 是特殊韵母，只能自成音节，如「儿」。"),
 ("ie üe er", "choice", "standard", "复韵母 üe 与 j、q、x 相拼时应该写成什么样子？",
  [("A", "üe"), ("B", "ue"), ("C", "ve"), ("D", "uë")], "B", "与 j、q、x 相拼时去掉两点，写成 jue、que、xue。"),
 ("ie üe er", "fill", "basic", "ie、üe、er 中，能单独成音节、不与声母相拼的特殊韵母是____。", "er", "er 永远自成音节，如「二」「儿」。"),
 ("ie üe er", "numeric", "basic", "「ie üe er」这一课一共学了几个韵母？请用阿拉伯数字作答。", "3", "3", "本课学 ie、üe、er 共 3 个韵母。"),
 ("ie üe er", "short-answer", "standard", "为什么说 er 是特殊韵母？",
  "因为它不与任何声母相拼，只能自己单独成音节，还带有卷舌动作，所以叫特殊韵母。",
  ["不与声母相拼", "单独成音节", "带卷舌动作"], "特殊就特殊在「不合群」。"),
 ("an en in un ün", "choice", "basic", "an、en、in、un、ün 五个韵母属于下面哪一类？",
  [("A", "前鼻韵母"), ("B", "后鼻韵母"), ("C", "复韵母"), ("D", "单韵母")], "A", "它们都以 -n 收尾，是前鼻韵母。"),
 ("an en in un ün", "choice", "standard", "读前鼻韵母 in 时，气流的出口在什么地方？",
  [("A", "口腔"), ("B", "鼻腔"), ("C", "喉部"), ("D", "齿缝")], "B", "前鼻韵母以 -n 收尾，气流从鼻腔出来。"),
 ("an en in un ün", "fill", "basic", "an、en、in、un、ün 五个韵母都是____鼻韵母。", "前", "它们的韵尾都是 -n。"),
 ("an en in un ün", "numeric", "basic", "这一课一共学了几个前鼻韵母？请用阿拉伯数字作答。", "5", "5", "an、en、in、un、ün 共 5 个。"),
 ("an en in un ün", "short-answer", "standard", "说说前鼻韵母韵尾的发音位置。",
  "韵尾 -n 发音时舌尖抵住上齿龈，气流从鼻腔出来。",
  ["舌尖抵上齿龈", "气流从鼻腔出"], "记住「舌尖抵齿龈」就抓住了前鼻音的特点。"),
 ("ang eng ing ong", "choice", "basic", "ang、eng、ing、ong 四个韵母属于下面哪一类？",
  [("A", "前鼻韵母"), ("B", "后鼻韵母"), ("C", "复韵母"), ("D", "声母")], "B", "它们都以 -ng 收尾，是后鼻韵母。"),
 ("ang eng ing ong", "choice", "standard", "后鼻韵母的韵尾是哪两个字母？",
  [("A", "-n"), ("B", "-ng"), ("C", "-r"), ("D", "没有韵尾")], "B", "后鼻韵母的韵尾是 -ng。"),
 ("ang eng ing ong", "fill", "basic", "ang、eng、ing、ong 四个韵母都是____鼻韵母。", "后", "它们的韵尾都是 -ng。"),
 ("ang eng ing ong", "numeric", "basic", "这一课一共学了几个后鼻韵母？请用阿拉伯数字作答。", "4", "4", "ang、eng、ing、ong 共 4 个。"),
 ("ang eng ing ong", "short-answer", "standard", "说说前鼻韵母和后鼻韵母在发音上最大的不同。",
  "前鼻韵母以 -n 收尾，舌尖抵住上齿龈；后鼻韵母以 -ng 收尾，舌根抵住软腭，听起来更「闷」。",
  ["前鼻 -n 舌尖抵齿龈", "后鼻 -ng 舌根抵软腭", "音色不同"], "舌尖与舌根，一前一后，是这两类的分水岭。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    last = sorted([t["id"] for t in topic if t["chapter"] == "一年级上册 第二单元 汉语拼音"])[-1]
    newpts, name2id = [], {}
    for i, (nm, pg, ch, desc, mast, dq) in enumerate(PTS):
        pid = f"chi_p{pmax + 1 + i}"
        name2id[nm] = pid
        pre = [last] if i == 0 else [f"chi_p{pmax + i}"]
        newpts.append({"id": pid, "name": nm, "subject": "chinese", "domain": "识字与写字",
                       "grade": 1, "semester": "上", "chapter": ch, "type": "conceptual",
                       "description": desc, "mastery_criteria": mast, "diagnostic_question": dq,
                       "external": False, "standards": [dict(SX02)],
                       "tags": ["识字写字", "汉语拼音", "教材课级"], "prerequisites": pre,
                       "curriculumRef": SX02["id"], "verified": False,
                       "textbookRef": f"人教版语文一年级上册 第{pg}页"})
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
    newdeps = [{"from": p["prerequisites"][0], "to": p["id"], "type": "hard",
                "reason": "同一册前一课为本课打基础"} for p in newpts]
    print(f"新增：点 {len(newpts)} · 题 {len(newqs)} · 边 {len(newdeps)}（点号 chi_p{pmax+1}–chi_p{pmax+len(newpts)}）")
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
