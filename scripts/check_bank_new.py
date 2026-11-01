#!/usr/bin/env python3
"""校验题库加深分片文件（data/math/_bank_new/S<NNN>.json）。

用法：
  python3 scripts/check_bank_new.py data/math/_bank_new/S001.json [更多文件…]
  python3 scripts/check_bank_new.py --all

判据见 docs/math-bank-deepening-spec.md。退出码 0 表示全部通过。
"""
import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "math")
JOBS = "/Users/a627692/.hermes/profiles/agent8/cache/scratch/bank_jobs"
TYPES = {"choice", "fill", "numeric", "short-answer"}
DIFFS = {"basic", "standard", "hard"}
BANNED_OPT = ("以上都不对", "以上都对", "以上均", "无法确定", "都不正确")
OPS = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b, ast.Mod: lambda a, b: a % b,
    ast.FloorDiv: lambda a, b: a // b, ast.USub: lambda a: -a, ast.UAdd: lambda a: a,
}


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def safe_eval(expr):
    node = ast.parse(expr.replace("×", "*").replace("÷", "/")
                     .replace("−", "-").replace("^", "**"), mode="eval")

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.operand))
        raise ValueError("unsupported")

    return ev(node)


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


EXISTING_PROMPTS = {re.sub(r"\s+", "", q.get("prompt") or "")
                    for q in load_json(os.path.join(DATA, "questions.json"))}


def check_file(path, errs):
    name = os.path.basename(path)
    shard = name[:-5]
    job_p = os.path.join(JOBS, f"{shard}.json")
    if not os.path.exists(job_p):
        errs.append(f"{shard}: 找不到作业单 {job_p}")
        return 0
    job = load_json(job_p)
    want = {}
    for pt in job["points"]:
        for nq in pt["new"]:
            want[nq["id"]] = (pt["topicId"], nq["type"], nq["difficulty"], pt["existing_prompts"])
    try:
        items = load_json(path)
    except Exception as e:  # noqa: BLE001
        errs.append(f"{shard}: JSON 解析失败 {e}")
        return 0
    if not isinstance(items, list):
        errs.append(f"{shard}: 顶层必须是数组")
        return 0
    got = {}
    for it in items:
        qid = it.get("id")
        got[qid] = it
    miss = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    if miss:
        errs.append(f"{shard}: 缺 {len(miss)} 题 {miss[:4]}")
    if extra:
        errs.append(f"{shard}: 多出计划外 id {extra[:4]}")
    letters = []
    for qid, it in got.items():
        if qid not in want:
            continue
        topic, typ, diff, existing = want[qid]
        tag = f"{shard}/{qid}"
        if it.get("topicId") != topic:
            errs.append(f"{tag}: topicId 应为 {topic}")
        if it.get("subject") != "math":
            errs.append(f"{tag}: subject 应为 math")
        if it.get("type") != typ:
            errs.append(f"{tag}: type 应为 {typ}（实为 {it.get('type')}）")
        if it.get("difficulty") != diff:
            errs.append(f"{tag}: difficulty 应为 {diff}（实为 {it.get('difficulty')}）")
        prompt = (it.get("prompt") or "").strip()
        if prompt != (it.get("question") or "").strip():
            errs.append(f"{tag}: question 必须与 prompt 同值")
        if len(prompt) < 12:
            errs.append(f"{tag}: 题干不足 12 字")
        if prompt in existing:
            errs.append(f"{tag}: 题干与该点已有题重复")
        if han(it.get("explanation")) < 20:
            errs.append(f"{tag}: 解析不足 20 汉字")
        opts = it.get("options") or []
        if typ == "choice":
            labels = [o.get("label") for o in opts]
            texts = [(o.get("text") or "").strip() for o in opts]
            if labels != ["A", "B", "C", "D"]:
                errs.append(f"{tag}: 选项 label 必须为 A/B/C/D（实为 {labels}）")
            if len(set(texts)) != 4 or not all(texts):
                errs.append(f"{tag}: 4 个选项必须互不相同且非空")
            if it.get("answer") not in labels:
                errs.append(f"{tag}: answer 不在选项内")
            if it.get("choices") != opts:
                errs.append(f"{tag}: choices 必须与 options 逐字相同")
            for t in texts:
                if any(b in t for b in BANNED_OPT):
                    errs.append(f"{tag}: 禁用凑数选项「{t[:12]}」")
            letters.append(str(it.get("answer")))
        else:
            if opts or (it.get("choices") or []):
                errs.append(f"{tag}: 非选择题 options/choices 必须为空数组")
            if typ == "fill" and "____" not in prompt:
                errs.append(f"{tag}: 填空题必须含 ____")
            if typ == "numeric":
                v = (it.get("verify") or "").strip()
                if not v:
                    errs.append(f"{tag}: 数值题缺 verify")
                else:
                    try:
                        a = float(re.sub(r"[^\d\.\-]", "", str(it.get("answer"))))
                        if abs(safe_eval(v) - a) > 1e-6:
                            errs.append(f"{tag}: verify={v} → {safe_eval(v)} ≠ answer {a}")
                    except Exception:  # noqa: BLE001
                        errs.append(f"{tag}: verify 不可复算（{v}）")
            if typ == "short-answer" and len(it.get("keypoints") or []) < 2:
                errs.append(f"{tag}: 简答题 keypoints 需 ≥2 条")
    if letters and len(set(letters) & {"A", "B", "C", "D"}) < min(4, len(letters)):
        errs.append(f"{shard}: 选择题答案字母覆盖面不足（{''.join(letters)}）")
    return len(got)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        args = sorted(glob.glob(os.path.join(DATA, "_bank_new", "S*.json")))
    if not args:
        print(__doc__)
        return 2
    errs = []
    total = 0
    for p in args:
        total += check_file(p, errs)
    if errs:
        print(f"❌ {len(errs)} 项不合格（{len(args)} 个文件 / {total} 题）")
        for e in errs[:40]:
            print("  -", e)
        return 1
    print(f"✅ {len(args)} 个文件 · {total} 题 · 不合格 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
