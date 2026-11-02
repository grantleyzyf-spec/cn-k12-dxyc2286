#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版数学 题库分片校验（子代必须跑到末行 PASS）。

用法: python3 scripts/check_bsd_bank.py <spec.json> <bank.json>
校验：题量/题型分布/选项/答案位/verify 可复算/字数/无 Markdown/难度三档/知识点覆盖/topicId 精确
       + 一年级不超纲（数值 ≤ 20）
"""
import json, os, re, sys
from collections import Counter

MD_BAD = re.compile(r"\*\*|##|`|\$|\\frac|\\times|\\div")
ABS_OK = re.compile(r"\|[^|\n]{1,14}\|")   # 允许绝对值 |x|、|k|、|a + b|（数学符号不禁）


def has_md(s):
    """只禁 Markdown 记号；竖线仅在「表格分隔」时禁，绝对值成对写法放行。"""
    rest = ABS_OK.sub("", s)
    return bool(MD_BAD.search(rest)) or "|" in rest
Q_TYPES = {"choice", "fill", "numeric", "short-answer"}
DIFFS = {"basic", "standard", "hard"}
fails = []


def ck(name, ok, detail=None):
    if not ok:
        fails.append(f"{name}：{detail}" if detail else name)


def run(spec_p, bank_p):
    spec = json.load(open(spec_p, encoding="utf-8"))
    bank = json.load(open(bank_p, encoding="utf-8"))
    want = [t["id"] for t in spec["topics"]]
    tcontent = {t["id"]: t for t in bank.get("topics", [])}
    qs = bank.get("questions", [])

    # 新流程（内容层已并入 topics.json、工人只写题）不要求 bank 带 topics[]
    if tcontent:
        ck("知识点内容与 spec 一一对应", sorted(tcontent) == sorted(want),
           f"缺 {sorted(set(want) - set(tcontent))} 多 {sorted(set(tcontent) - set(want))}")
        for tid, t in tcontent.items():
            ck(f"{tid} description 40–120 字", 40 <= len(t.get("description", "")) <= 120,
               len(t.get("description", "")))
            ck(f"{tid} mastery_criteria 2–3 条", 2 <= len(t.get("mastery_criteria") or []) <= 3)
            ck(f"{tid} type 合规", t.get("type") in {"conceptual", "procedural", "reasoning",
                                                     "modeling", "application"}, t.get("type"))
            ck(f"{tid} diagnostic_question 有问有答",
               bool((t.get("diagnostic_question") or {}).get("question")) and
               bool((t.get("diagnostic_question") or {}).get("answer")))
    else:
        ck("questions 非空", bool(qs))
        ck("shard 名与 spec 一致", bank.get("shard") in (None, os.path.basename(bank_p)[:-5]),
           bank.get("shard"))
        prefix = spec.get("id_prefix")
        if prefix:
            ck("题 id 前缀与派单一致", all(q["id"].startswith(prefix) for q in qs),
               f"应为 {prefix}xxx，实际 {sorted({q['id'][:9] for q in qs})[:3]}")


    by_topic = Counter(q.get("topicId") for q in qs)
    ck("topicId 无越界", set(by_topic) <= set(want), sorted(set(by_topic) - set(want)))
    need = spec.get("need") or {}
    for tid in want:
        k = need.get(tid, 8)                      # 单元上位点 5 题、课时点 8 题
        ck(f"{tid} 恰好 {k} 题", by_topic.get(tid) == k, by_topic.get(tid))

    ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
    ck("题 id 命名 mbs_qNNNNNN", all(re.fullmatch(r"mbs_q\d{6}", q["id"]) for q in qs))
    ck("题型枚举", all(q.get("type") in Q_TYPES for q in qs),
       sorted({q.get("type") for q in qs}))
    ck("难度三档齐备", {q.get("difficulty") for q in qs} == DIFFS,
       sorted({q.get("difficulty") for q in qs}))

    types = Counter(q.get("type") for q in qs)
    n = len(qs)
    ck("numeric ≥20%", types["numeric"] >= n * 0.2, f"{types['numeric']}/{n}")
    ck("fill ≥18%", types["fill"] >= n * 0.18, f"{types['fill']}/{n}")
    ck("short-answer ≥18%", types["short-answer"] >= n * 0.18, f"{types['short-answer']}/{n}")
    for tid in want:
        kinds = {q["type"] for q in qs if q["topicId"] == tid}
        ck(f"{tid} ≥3 种题型", len(kinds) >= 3, sorted(kinds))

    for q in qs:
        p = q.get("prompt", "")
        ck(f"{q['id']} 题干≥12字", len(p) >= 12, len(p))
        ck(f"{q['id']} question 与 prompt 同值", q.get("question") == p)
        ck(f"{q['id']} 每题必须有 answer(schema required)", bool(q.get("answer")), q.get("type"))
        ck(f"{q['id']} 解析≥20字", len(q.get("explanation", "")) >= 20, len(q.get("explanation", "")))
        ck(f"{q['id']} 无 Markdown 符号", not has_md(p + q.get("explanation", "")), p[:20])
        if q["type"] == "choice":
            opts = q.get("options") or []
            ck(f"{q['id']} 4 选项", len(opts) == 4, len(opts))
            labels = [o.get("label") for o in opts]
            ck(f"{q['id']} 选项文本互异", len({o.get("text") for o in opts}) == len(opts))
            ck(f"{q['id']} answer 是 label", q.get("answer") in labels, q.get("answer"))
        elif q["type"] == "numeric":
            v = q.get("verify")
            ck(f"{q['id']} numeric 带 verify", bool(v))
            if v:
                try:
                    got = eval(v, {"__builtins__": {}}, {})
                    ck(f"{q['id']} verify 可复算且等于 answer",
                       abs(float(got) - float(q["answer"])) < 1e-6, f"{v}={got} vs {q['answer']}")
                except Exception as e:                     # noqa: BLE001
                    ck(f"{q['id']} verify 可复算", False, str(e))
        elif q["type"] == "short-answer":
            ck(f"{q['id']} 简答带 keypoints≥2", len(q.get("keypoints") or []) >= 2)

    # 一年级不超纲：出现 >20 的数字（题号/年份除外）即失败
    if str(spec.get("book", "")).startswith("一年级"):
        for q in qs:
            nums = [int(x) for x in re.findall(r"(?<![\d.])(\d{1,3})(?![\d.])", q.get("prompt", ""))
                    if int(x) > 20]
            ck(f"{q['id']} 一年级数值 ≤20", not nums, nums)

    ch = Counter(q.get("answer") for q in qs if q.get("type") == "choice")
    tot = sum(ch.values()) or 1
    # 四选位均衡只能在 choice ≥4 时成立：8 题/点的单片（numeric/fill/short 各 ≥2 已占 6 题）
    # 最多只有 2 道 choice，要求 A/B/C/D 各 ≥15% 在数学上不可能（需 4 道），这种片在单元合并层配平。
    if tot >= 4:
        ck("选项答案位均衡（各 ≥15%）", all(ch[k] / tot >= 0.15 for k in "ABCD"), dict(ch))
    else:
        ck("choice 少于4道时答案位仍要分散（≥2 种）", len([k for k in "ABCD" if ch[k]]) >= min(tot, 2), dict(ch))

    dup = [p for p, c in Counter(q["prompt"] for q in qs).items() if c > 1]
    ck("片内题干不重复", not dup, dup[:2])

    if fails:
        print(f"FAILED {len(fails)} 项：")
        for f in fails[:25]:
            print("  -", f)
        sys.exit(1)
    print(f"PASS  {spec['book']} 第{spec['unit_no']}单元：点 {len(tcontent)} / 题 {n} "
          f"（choice {types['choice']}·fill {types['fill']}·numeric {types['numeric']}·short {types['short-answer']}）")


def main_shard(bank_p):
    """--shard <_bank_out/片名.json>：自动到同级 _bank_shards/ 找派单。"""
    base = os.path.basename(bank_p)[:-5]
    spec_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(bank_p))),
                          "_bank_shards", base + ".json")
    if not os.path.isfile(spec_p):
        print(f"FAILED 1 项：\n  - 找不到派单 {spec_p}")
        sys.exit(1)
    return run(spec_p, bank_p)


def main():
    if sys.argv[1:2] == ["--shard"]:
        return main_shard(sys.argv[2])
    if len(sys.argv) < 3:
        print("用法：python3 scripts/check_bsd_bank.py <spec.json> <bank.json>\n"
              "  或：python3 scripts/check_bsd_bank.py --shard data/math-bsd/_bank_out/<片名>.json")
        sys.exit(2)
    return run(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
