# -*- coding: utf-8 -*-
"""历史（history）题库门禁：核对「每点题量 + 题目硬约束」。

用法：
  python3 scripts/check_history_bank.py --book 八年级上册       # 按册核量（历史课级点一律 8 题）
  python3 scripts/check_history_bank.py --shard /tmp/his_g8a/out/S1.json  # 核一个分片（子代自查）
  python3 scripts/check_history_bank.py --all                   # 全库硬约束（不看题量）

判据（与 data-model-and-gates.md 一致）：
  · answer 必须是字符串；choice 四个互异选项、answer ∈ labels、禁「以上都不对/都对」凑数项
  · 题干 ≥12 字；explanation ≥20 汉字；fill 的填空处用 ____
  · 全库题干不重复；同点题干不做近似判重（语文同课多题天然相似，改由父代人工抽检）
  · 点级题量：历史一课一点，一律 ≥8（骨架见 _skeleton.json；活动课不建点）
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "history")
HAN = re.compile(r"[\u4e00-\u9fa5]")
BAN = ("以上都不对", "以上都对", "以上都可以", "都不正确", "都正确")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


TARGET = 8          # 历史一课一点，统一 8 题（四档掌握度要区分 basic/standard/hard）


def target_of(topic):
    return TARGET


def check_question(q, seen_prompts, errs):
    qid = q.get("id", "?")
    tp = q.get("type")
    if not isinstance(q.get("answer"), str):
        errs.append(f"{qid}: answer 必须是字符串（现为 {type(q.get('answer')).__name__}）")
    prompt = q.get("prompt") or ""
    if len(prompt) < 12:
        errs.append(f"{qid}: 题干不足 12 字（{len(prompt)}）")
    if prompt in seen_prompts:
        errs.append(f"{qid}: 题干与 {seen_prompts[prompt]} 完全重复")
    seen_prompts.setdefault(prompt, qid)
    if len(HAN.findall(q.get("explanation") or "")) < 20:
        errs.append(f"{qid}: 解析不足 20 个汉字")
    if q.get("question") and q["question"] != prompt:
        errs.append(f"{qid}: question 别名与 prompt 不同值")
    if tp == "choice":
        opts = q.get("options") or []
        if len(opts) != 4:
            errs.append(f"{qid}: 选择题须 4 个选项（现 {len(opts)}）")
        labels = [o.get("label") for o in opts]
        texts = [(o.get("text") or "").strip() for o in opts]
        if len(set(texts)) != len(texts):
            errs.append(f"{qid}: 选项文本有重复")
        if q.get("answer") not in labels:
            errs.append(f"{qid}: answer 不在选项 label 内")
        if any(b in t for t in texts for b in BAN):
            errs.append(f"{qid}: 出现「以上都不对」类凑数选项")
        if q.get("choices") and [c.get("text") for c in q["choices"]] != texts:
            errs.append(f"{qid}: choices 与 options 不一致")
    else:
        if q.get("options"):
            errs.append(f"{qid}: 非选择题不应带 options")
        if tp == "fill" and "____" not in prompt:
            errs.append(f"{qid}: fill 题干缺 ____ 空位")
        if tp == "short-answer" and len(q.get("keypoints") or []) < 2:
            errs.append(f"{qid}: short-answer 应有 ≥2 条 keypoints")
        for kp in q.get("keypoints") or []:
            if len(kp) < 4:
                errs.append(f"{qid}: keypoint「{kp}」不足 4 字（schema minLength=4，CI 会红）")
        if tp == "numeric":
            v = q.get("verify")
            if not v:
                errs.append(f"{qid}: numeric 缺 verify")
            else:
                try:
                    if abs(float(eval(v)) - float(q["answer"])) > 1e-9:
                        errs.append(f"{qid}: verify 复算值与 answer 不一致")
                except Exception as e:
                    errs.append(f"{qid}: verify 无法复算（{e}）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--shard")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--count", action="store_true", help="只看题量，不跑存量题硬约束")
    ap.add_argument("--strict", action="store_true", help="存量题硬约束不合规也算失败")
    ap.add_argument("--allow", help="白名单：本片允许写的 topicId，逗号分隔（越界即失败）")
    a = ap.parse_args()

    errs = []
    topics = load(os.path.join(D, "topics.json"))
    T = {t["id"]: t for t in topics}
    questions = load(os.path.join(D, "questions.json"))
    bank_cnt = Counter(q.get("topicId") for q in questions)
    seen = {}

    allow = {x.strip() for x in a.allow.split(",") if x.strip()} if a.allow else None

    if a.shard:
        qs = load(a.shard)
        for q in qs:
            if q.get("topicId") not in T:
                errs.append(f"{q.get('id')}: topicId {q.get('topicId')} 不存在")
            elif allow and q.get("topicId") not in allow:
                errs.append(f"{q.get('id')}: topicId {q.get('topicId')} 不在本片白名单（越界）")
            check_question(q, seen, errs)
        per = Counter(q.get("topicId") for q in qs)
        print(f"分片题目 {len(qs)} 道，覆盖 {len(per)} 点")
        for tid, n in sorted(per.items()):
            # 分片是「增量」文件：题量 = 题库已有 + 分片内
            need = target_of(T[tid]) - bank_cnt.get(tid, 0) - n
            if need > 0:
                errs.append(f"{tid}（{T[tid]['name']}）还缺 {need} 题（题库已有 {bank_cnt.get(tid, 0)}）")
            elif need < 0:
                print(f"   ⚠ {tid}（{T[tid]['name']}）超量 {-need} 题（题库 {bank_cnt.get(tid, 0)} + 分片 {n} > {target_of(T[tid])}）")
    else:
        if a.book:
            scope = [t for t in topics if (t.get("chapter") or "").startswith(a.book)]
        elif a.all:
            scope = topics
        else:
            scope = topics
        ids = {t["id"] for t in scope}
        qs = [q for q in questions if q.get("topicId") in ids]
        legacy = []
        if not a.count:
            for q in qs:
                check_question(q, seen, legacy)
            if legacy:
                print(f"\n【存量题硬约束】{len(legacy)} 项不合规（属存量返修范围，默认不影响退出码；--strict 才算失败）")
                for e in legacy[:12]:
                    print("  ·", e)
                if len(legacy) > 12:
                    print(f"  …… 另有 {len(legacy)-12} 项")
                if a.strict:
                    errs.extend(legacy)
        if a.book:
            per = Counter(q.get("topicId") for q in qs)
            short = []
            for t in scope:
                need = target_of(t) - per.get(t["id"], 0)
                if need > 0:
                    short.append((t["id"], t["name"], per.get(t["id"], 0), target_of(t), need))
            if short:
                print(f"{a.book}：{len(short)} 个点题量不足")
                for s in sorted(short, key=lambda x: -x[4])[:20]:
                    print("   ", s[0], s[1], f"{s[2]}/{s[3]} 缺{s[4]}")
                errs.append(f"{a.book} 共 {len(short)} 点未达题量")
            else:
                print(f"{a.book}：{len(scope)} 点全部达到题量（课级 8）")
        # 答案位分布（仅 choice）
        ch = [q for q in qs if q.get("type") == "choice"]
        if ch:
            c = Counter(q["answer"] for q in ch)
            tot = sum(c.values())
            low = {k: round(v / tot * 100, 1) for k, v in c.items() if v / tot < 0.15}
            print(f"选择题 {tot} 道，答案位分布 " + " ".join(f"{k}:{v}({v/tot*100:.1f}%)" for k, v in sorted(c.items())))
            if low:
                print("   ⚠ 低于 15% 的答案位:", low, "（建议新题优先换位）")

    if errs:
        print(f"\n❌ {len(errs)} 项不合规：")
        for e in errs[:40]:
            print("  -", e)
        if len(errs) > 40:
            print(f"  …… 另有 {len(errs)-40} 项")
        return 1
    print("\n✅ HISTORY BANK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
