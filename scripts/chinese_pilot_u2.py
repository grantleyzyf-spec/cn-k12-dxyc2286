# -*- coding: utf-8 -*-
"""语文试点（一年级上册）第二批 + 历史 id 规范化。

① 把上一批不符合 schema 的 id 改名：
   点 chi_g1a_u1_01..04 → chi_p336..339（schema 要求 ^[a-z]{2,6}_[ph]\\d{2,4}$）
   题 chi_g1a_u1_0X_qNN → chi_q206..225
   同步改 questions.topicId、dependencies.from/to、其他点的 prerequisites
② 新增「第二单元 汉语拼音」4 个课级点（a o e / i u ü / b p m f / d t n l）+ 20 题。

用法：python3 build_cn_pilot2.py [--write]
"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP, QP, DP = (f"{REPO}/data/chinese/{x}" for x in ("topics.json", "questions.json", "dependencies.json"))
WRITE = "--write" in sys.argv

STD_SX02 = {"id": "cyw-2022:1.SX.02", "confidence": "partial",
            "quote": "能准确地拼读音节，正确书写声母、韵母和音节", "sourceLine": 273}
STD_SX03 = {"id": "cyw-2022:1.SX.03", "confidence": "partial",
            "quote": "掌握汉字的基本笔画和常用的偏旁部首", "sourceLine": 276}

PTS = [
 dict(name="a o e", page=20, std=STD_SX02,
      desc="认识单韵母 a、o、e，读准音、认清形，会在四线三格中书写，并知道它们都是韵母。",
      mastery=["能准确读出 a、o、e 三个单韵母", "能在四线三格中正确书写 a、o、e"],
      dq={"question": "a、o、e 属于声母还是韵母？", "answer": "韵母"}),
 dict(name="i u ü", page=22, std=STD_SX02,
      desc="认识单韵母 i、u、ü，读准音、认清形；知道 ü 上两点用来和 u 区别，声调标在 i 上时要去掉上面的点。",
      mastery=["能准确读出 i、u、ü 并区分 ü 与 u", "知道给 i 标声调时要去点"],
      dq={"question": "i、u、ü 中带两点的韵母是哪一个？", "answer": "ü"}),
 dict(name="b p m f", page=24, std=STD_SX02,
      desc="认识声母 b、p、m、f，读准音、认清形；能借助它们与单韵母拼出音节。",
      mastery=["能准确读出 b、p、m、f 四个声母", "能拼读 b、p、m、f 与单韵母组成的音节"],
      dq={"question": "b、p、m、f 都是声母，其中字形圈在右边、竖在左边的是哪一个？", "answer": "b"}),
 dict(name="d t n l", page=26, std=STD_SX03,
      desc="认识声母 d、t、n、l，读准音、认清形；能区分鼻音 n 与边音 l 的发音。",
      mastery=["能准确读出 d、t、n、l", "能分辨 n 与 l 的发音差别"],
      dq={"question": "d、t、n、l 中，发音时气流从鼻腔出来的是哪一个？", "answer": "n"}),
]

QS = [
 ("a o e", "choice", "basic", "「a o e」这一课中，a 属于下面哪一类字母？",
  [("A", "声母"), ("B", "韵母"), ("C", "整体认读音节"), ("D", "声调符号")], "B",
  "a 是单韵母，发音时气流不受阻；声母如 b、p 要先闭住再放开。"),
 ("a o e", "choice", "standard", "读单韵母 a 时，口形应该是下面哪一种？",
  [("A", "嘴巴张大"), ("B", "嘴唇拢圆"), ("C", "嘴角向两边扁"), ("D", "双唇紧闭")], "A",
  "读 a 时嘴巴张大；读 o 时嘴唇拢圆；读 e 时嘴角向两边扁。"),
 ("a o e", "fill", "basic", "a、o、e 这三个字母都是单____。", "韵母",
  "a、o、e 可以单独给汉字注音，是单韵母。"),
 ("a o e", "numeric", "basic", "「a o e」这一课一共学了几个单韵母？请用阿拉伯数字作答。", "3", "3",
  "本课学 a、o、e 共 3 个单韵母。"),
 ("a o e", "short-answer", "standard", "说说 a、o、e 的读音在口形上有什么不同。",
  "读 a 时嘴巴张大，读 o 时嘴唇拢圆，读 e 时嘴角向两边扁。",
  ["a 嘴巴张大", "o 嘴唇拢圆", "e 嘴角向两边扁"],
  "三个单韵母口形不同，口形对了音就准了。"),
 ("i u ü", "choice", "basic", "「i u ü」中，上面带两点的单韵母是哪一个？",
  [("A", "i"), ("B", "u"), ("C", "ü"), ("D", "o")], "C",
  "ü 上面的两点是用来和 u 区别的标记，不能省。"),
 ("i u ü", "choice", "standard", "给 i 加声调时，正确的做法是什么？",
  [("A", "直接点在字母上方，不去点"), ("B", "去掉 i 上面的点，声调标在原处"), ("C", "声调标在字母下面"), ("D", "声调标在字母右边")], "B",
  "声调要标在 i 上时要先去掉原来的点，再把声调符号标在那里。"),
 ("i u ü", "fill", "basic", "i、u、ü 中与 u 只差两点的韵母是____。", "ü",
  "ü 与 u 的区别就在上面两点，书写时不能丢。"),
 ("i u ü", "numeric", "basic", "「i u ü」这一课一共学了几个单韵母？请用阿拉伯数字作答。", "3", "3",
  "本课学 i、u、ü 共 3 个单韵母。"),
 ("i u ü", "short-answer", "standard", "说说 ü 和 u 在字形和读音上有什么不同。",
  "字形上 ü 比 u 多两点；读音上 ü 要把嘴唇拢圆并发出「迂」的音，u 发「乌」的音。",
  ["字形多两点", "ü 读「迂」", "u 读「乌」"],
  "ü 的两点是区分标记，读音也不同。"),
 ("b p m f", "choice", "basic", "下面四个字母中，属于声母的是哪一个？",
  [("A", "a"), ("B", "b"), ("C", "o"), ("D", "e")], "B",
  "b 是声母，a、o、e 是韵母。"),
 ("b p m f", "choice", "standard", "b 和 p 发音最主要的区别是什么？",
  [("A", "笔画数不同"), ("B", "一个不送气、一个送气"), ("C", "一个圆一个方"), ("D", "声调不同")], "B",
  "b 不送气，p 送气；把手掌放在嘴前，读 p 能感到明显气流。"),
 ("b p m f", "fill", "basic", "b、p、m、f 都是____。", "声母",
  "这四个字母都要和韵母相拼才能成音节，是声母。"),
 ("b p m f", "numeric", "basic", "「b p m f」这一课一共学了几个声母？请用阿拉伯数字作答。", "4", "4",
  "本课学 b、p、m、f 共 4 个声母。"),
 ("b p m f", "short-answer", "standard", "b 和 p 的字形只差一点点，请说说怎样分清它们。",
  "b 的竖在左、圆圈在右，p 的竖在右、圆圈在左；再看送气，读 p 时手掌能感到气流。",
  ["b 竖左圈右", "p 竖右圈左", "读 p 送气"],
  "字形方位加上送气特点，两招一起用就不会混。"),
 ("d t n l", "choice", "basic", "d、t、n、l 中，读音时气流从鼻腔出来的是哪一个？",
  [("A", "d"), ("B", "t"), ("C", "n"), ("D", "l")], "C",
  "n 是鼻音，气流从鼻腔出；l 是边音，气流从舌头两边出。"),
 ("d t n l", "choice", "standard", "d 与 b 的字形相比，圆圈的位置有什么不同？",
  [("A", "d 的圆圈在左，b 的圆圈在右"), ("B", "d 的圆圈在右，b 的圆圈在左"), ("C", "两个都圈在左"), ("D", "两个都圈在右")], "A",
  "d 的圆圈在左、竖在右；b 的圆圈在右、竖在左。"),
 ("d t n l", "fill", "basic", "d、t、n、l 中，与 d 字形左右相反的是____。", "b",
  "d 与 b 左右相反，是容易混淆的一对字母。"),
 ("d t n l", "numeric", "basic", "「d t n l」这一课一共学了几个声母？请用阿拉伯数字作答。", "4", "4",
  "本课学 d、t、n、l 共 4 个声母。"),
 ("d t n l", "short-answer", "standard", "说说怎样区分 n 和 l 的发音。",
  "n 是鼻音，舌尖抵住上牙床，气流从鼻腔出来；l 是边音，舌尖抵住上牙床后放开，气流从舌头两边出来。",
  ["n 是鼻音", "l 是边音", "气流通道不同"],
  "捏住鼻子读 n 会读不出，读 l 不受影响，这是最快的判别办法。"),
]


def main():
    topic = json.load(open(TP, encoding="utf-8"))
    qs = json.load(open(QP, encoding="utf-8"))
    dp = json.load(open(DP, encoding="utf-8"))
    deps = dp["dependencies"] if isinstance(dp, dict) else dp

    # ① 历史 id 规范化
    pmax = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_[ph]\d+$", t["id"]))
    qmax = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    old_pts = sorted({t["id"] for t in topic if not re.match(r"^chi_[ph]\d+$", t["id"])})
    pmap = {oid: f"chi_p{pmax + 1 + i}" for i, oid in enumerate(old_pts)}
    old_qs = sorted({q["id"] for q in qs if not re.match(r"^chi_q\d+$", q["id"])})
    qmap = {oid: f"chi_q{qmax + 1 + i}" for i, oid in enumerate(old_qs)}
    for t in topic:
        t["id"] = pmap.get(t["id"], t["id"])
        t["prerequisites"] = [pmap.get(p, p) for p in t.get("prerequisites") or []]
    for q in qs:
        q["id"] = qmap.get(q["id"], q["id"])
        q["topicId"] = pmap.get(q["topicId"], q["topicId"])
    for d in deps:
        d["from"] = pmap.get(d["from"], d["from"])
        d["to"] = pmap.get(d["to"], d["to"])

    # ② 新增第二单元 4 点
    base_p = max(int(re.sub(r"\D", "", t["id"])) for t in topic if re.match(r"^chi_p\d+$", t["id"]))
    prev = [t["id"] for t in topic if t.get("chapter") == "一年级上册 第一单元 识字"]
    u1_04 = sorted([t["id"] for t in topic if t["chapter"] == "一年级上册 第一单元 识字"])[-1]
    newpts = []
    for i, p in enumerate(PTS):
        pid = f"chi_p{base_p + 1 + i}"
        pre = [u1_04] if i == 0 else [f"chi_p{base_p + i}"]
        newpts.append({
            "id": pid, "name": p["name"], "subject": "chinese", "domain": "识字与写字",
            "grade": 1, "semester": "上", "chapter": "一年级上册 第二单元 汉语拼音",
            "type": "conceptual", "description": p["desc"], "mastery_criteria": p["mastery"],
            "diagnostic_question": p["dq"], "external": False,
            "standards": [dict(p["std"])], "tags": ["识字写字", "汉语拼音", "教材课级"],
            "prerequisites": pre, "curriculumRef": p["std"]["id"], "verified": False,
            "textbookRef": f"人教版语文一年级上册 第{p['page']}页"})

    # ③ 新增 20 题
    qbase = max(int(re.sub(r"\D", "", q["id"])) for q in qs if re.match(r"^chi_q\d+$", q["id"]))
    name2id = {t["name"]: t["id"] for t in newpts}
    newqs, k = [], 0
    for item in QS:
        k += 1
        tname, typ, diff, prompt = item[0], item[1], item[2], item[3]
        rec = {"id": f"chi_q{qbase + k}", "topicId": name2id[tname], "prompt": prompt,
               "question": prompt, "type": typ, "difficulty": diff}
        if typ == "choice":                      # (…, prompt, [(label,text)], answer, explanation)
            rec["options"] = [{"label": l, "text": t} for l, t in item[4]]
            rec["answer"] = item[5]
            rec["explanation"] = item[6]
        elif typ == "fill":                      # (…, prompt, answer, explanation)
            rec["options"] = []
            rec["answer"] = item[4]
            rec["explanation"] = item[5]
        elif typ == "numeric":                   # (…, prompt, answer, verify, explanation)
            rec["options"] = []
            rec["answer"] = item[4]
            rec["verify"] = item[5]
            rec["explanation"] = item[6]
        else:                                    # short-answer (…, prompt, answer, keypoints, explanation)
            rec["options"] = []
            rec["answer"] = item[4]
            rec["keypoints"] = item[5]
            rec["explanation"] = item[6]
        newqs.append(rec)

    newdeps = [{"from": p["prerequisites"][0], "to": p["id"], "type": "hard",
                "reason": "同一册前一课（或上一单元末课）为本课打基础"} for p in newpts]
    print(f"改名：点 {len(pmap)} · 题 {len(qmap)}；新增：点 {len(newpts)} · 题 {len(newqs)} · 边 {len(newdeps)}")
    for a, b in list(pmap.items())[:4]:
        print(f"   {a} → {b}")
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
