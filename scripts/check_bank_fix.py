#!/usr/bin/env python3
"""校验「题库改写分片」data/math/_bank_fix/<册>.json。

背景：题库加深后，有 120 道题库题与卷面题（179 卷 5037 题）相似度 >0.85，触发
check_math_exam_json 的原创性门禁。修法是**只改题库那一侧**（卷面是学生可见成品，
动它要连带重做讲解与 docx），改后题库题与卷面题脱钩。

用法：
  python3 scripts/check_bank_fix.py data/math/_bank_fix/七年级上册.json [更多…]
  python3 scripts/check_bank_fix.py --all

判据：
 1 覆盖：必须包含作业单 COL_<册>.json 里的全部 bankId，不多不少
 2 字段：id/topicId/type/difficulty 与原题一致；prompt==question；题干 ≥12 字
 3 选择题：4 选项 A–D 互异、answer 在项内、choices==options、无凑数项
 4 数值题：verify 可复算且等于 answer；简答题 keypoints ≥2
 5 解析 ≥20 汉字
 6 脱钩：与作业单里点名的卷面题相似度 <0.80（去空白标点后）
 7 唯一：题干不与题库其他题重复
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
BANNED = ("以上都不对", "以上都对", "以上都可以", "无法确定", "无法判断")
OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
       ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
       ast.Pow: lambda a, b: a ** b, ast.Mod: lambda a, b: a % b,
       ast.FloorDiv: lambda a, b: a // b, ast.USub: lambda a: -a, ast.UAdd: lambda a: a}


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def norm(s):
    return re.sub(r"[\s，。？、；：（）()【】\[\]\"“”]", "", s or "")


def safe_eval(expr):
    node = ast.parse(expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**"), mode="eval")

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


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


QS = {q["id"]: q for q in load(os.path.join(DATA, "questions.json"))}
ALL_PROMPTS = {norm(q.get("prompt")): q["id"] for q in QS.values()}


def check_file(path, errs):
    book = os.path.basename(path)[:-5]
    job_p = os.path.join(JOBS, f"COL_{book}.json")
    if not os.path.exists(job_p):
        errs.append(f"{book}: 缺作业单 {job_p}")
        return 0
    job = load(job_p)
    want = {it["bankId"]: it for it in job["items"]}
    try:
        items = load(path)
    except Exception as e:  # noqa: BLE001
        errs.append(f"{book}: JSON 解析失败 {e}")
        return 0
    if not isinstance(items, list):
        errs.append(f"{book}: 顶层必须是数组")
        return 0
    got = {it.get("id"): it for it in items}
    miss = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    if miss:
        errs.append(f"{book}: 缺 {len(miss)} 题 {miss[:4]}")
    if extra:
        errs.append(f"{book}: 多出计划外 id {extra[:4]}")

    for qid, it in got.items():
        if qid not in want:
            continue
        spec = want[qid]
        orig = QS.get(qid, {})
        tag = f"{book}/{qid}"
        if it.get("topicId") != orig.get("topicId"):
            errs.append(f"{tag}: topicId 与原题不一致")
        if it.get("type") != orig.get("type"):
            errs.append(f"{tag}: type 必须与原题一致（{orig.get('type')}）")
        if it.get("difficulty") != orig.get("difficulty"):
            errs.append(f"{tag}: difficulty 必须与原题一致（{orig.get('difficulty')}）")
        if it.get("subject") != "math":
            errs.append(f"{tag}: subject 应为 math")
        p = (it.get("prompt") or "").strip()
        if p != (it.get("question") or "").strip():
            errs.append(f"{tag}: question 必须与 prompt 同值")
        if len(p) < 12:
            errs.append(f"{tag}: 题干不足 12 字")
        if han(it.get("explanation")) < 20:
            errs.append(f"{tag}: 解析不足 20 汉字")
        opts = it.get("options") or []
        if orig.get("type") == "choice":
            labels = [o.get("label") for o in opts]
            texts = [(o.get("text") or "").strip() for o in opts]
            if labels != ["A", "B", "C", "D"]:
                errs.append(f"{tag}: 选项 label 必须 A/B/C/D")
            if len(set(texts)) != 4 or not all(texts):
                errs.append(f"{tag}: 4 选项必须互异且非空")
            if it.get("answer") not in labels:
                errs.append(f"{tag}: answer 不在选项内")
            if it.get("choices") != opts:
                errs.append(f"{tag}: choices 必须与 options 逐字相同")
            for t in texts:
                if any(b in t for b in BANNED):
                    errs.append(f"{tag}: 禁用凑数选项")
        else:
            if opts or (it.get("choices") or []):
                errs.append(f"{tag}: 非选择题 options/choices 必须为空数组")
            if orig.get("type") == "numeric":
                v = (it.get("verify") or "").strip()
                try:
                    a = float(re.sub(r"[^\d\.\-]", "", str(it.get("answer"))))
                    if abs(safe_eval(v) - a) > 1e-6:
                        errs.append(f"{tag}: verify 复算 ≠ answer")
                except Exception:  # noqa: BLE001
                    errs.append(f"{tag}: verify 缺失或不可复算")
            if orig.get("type") == "short-answer" and len(it.get("keypoints") or []) < 2:
                errs.append(f"{tag}: 简答题 keypoints 需 ≥2 条")
        # 与点名的卷面题脱钩
        import difflib
        r = difflib.SequenceMatcher(None, norm(p), norm(spec["exam"]["stem"])).ratio()
        if r >= 0.80:
            errs.append(f"{tag}: 与卷面题 {spec['exam']['paper']}#{spec['exam']['no']} 仍相似 {r:.2f}（要求 <0.80）")
        owner = ALL_PROMPTS.get(norm(p))
        if owner and owner != qid:
            errs.append(f"{tag}: 题干与题库 {owner} 重复")
    return len(got)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        args = sorted(glob.glob(os.path.join(DATA, "_bank_fix", "*.json")))
    if not args:
        print(__doc__)
        return 2
    errs, total = [], 0
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
