# -*- coding: utf-8 -*-
"""subject_typo 的判据测试（对应 docs/typo-spec.md §3 八条判据 + 各学科正反例）。

运行：python3 scripts/test_subject_typo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subject_typo as T  # noqa: E402

fail = []
n = 0


def check(name, cond, detail=""):
    global n
    n += 1
    if not cond:
        fail.append(f"{name} {detail}")


def kinds(text, subject):
    return [(k, v) for k, v, _ in T.segments(text, subject)]


def has(text, subject, kind, value=None):
    return any(k == kind and (value is None or v == value) for k, v in kinds(text, subject))


def no(text, subject, kind):
    return not any(k == kind for k, v in kinds(text, subject))


# ---------- 数学（不得回归） ----------
check("数学·根号", has("长是 2√6 米", "math", "rad", "6"))
check("数学·分数", has("用了 3/8 张纸", "math", "frac", ("3", "8")))
check("数学·向量", has("与向量OA共线", "math", "vec", "OA"))
check("数学·纯字母比不转", no("比值 a/b 大于 1", "math", "frac"))
check("数学·日期不转", no("2026/11/01 统计", "math", "frac"))

# ---------- 化学 ----------
check("化学·化学式识别", has("生成 H2O 分子", "chemistry", "chem", "H2O"))
check("化学·带系数", has("反应 2H2O2 分解", "chemistry", "chem", "2H2O2"))
check("化学·非元素不转", no("这是 ATP 分子", "chemistry", "chem"))
check("化学·单元素不转", no("只有 O 一种元素", "chemistry", "chem"))
check("化学·箭头", has("2H2 + O2 -> 2H2O", "chemistry", "rxn"))
check("化学·条件置上", has("CaCO3 ->[高温] CaO + CO2", "chemistry", "rxn", ("→", "高温")),
      str(kinds("CaCO3 ->[高温] CaO + CO2", "chemistry")))
check("化学·可逆箭头保留", has("N2 + 3H2 <=> 2NH3", "chemistry", "rxn", ("⇌", None)))
check("化学·电荷", has("溶液中有 SO4^2- 离子", "chemistry", "chem"))
toks = T.chem_tokens("2H2O2")
check("化学·拆分顺序", toks[0] == ("coef", "2") and toks[1] == ("el", "H") and toks[2] == ("sub", "2"),
      str(toks[:3]))
check("化学·电荷转上标", ("sup", "2−") in T.chem_tokens("SO4^2-"), str(T.chem_tokens("SO4^2-")))
check("化学·OMML 下标", "<m:sSub>" in T.omml_chem("H2O"))
check("化学·OMML 条件", "<m:limUpp>" in T.omml_rxn("点燃"))

# ---------- 物理 ----------
check("物理·单位正体", has("车速 3 m/s 前进", "physics", "unit", "m/s"))
check("物理·单位幂", has("加速度 9.8 m/s^2", "physics", "unit"))
check("物理·复合单位", has("做的功 10 N·m 很大", "physics", "unit"))
check("物理·量符号斜体", has("v＝3 m/s", "physics", "qty", "v"))
check("物理·缩写不斜体", no("测得 DNA 长度", "physics", "qty")
      and not has("pH＝7", "physics", "qty", "p"))
check("物理·非单位不误判", no("走了 3 步 就停", "physics", "unit"))
check("物理·单位链校验", not T._unit_ok("km/hz") and T._unit_ok("km/h") and T._unit_ok("N·m"))

# ---------- 生物 ----------
check("生物·基因斜体", has("TP53 基因突变", "biology", "gene", "TP53"))
check("生物·p53 斜体", has("p53 表达升高", "biology", "gene", "p53"))
check("生物·缩写不斜体", no("DNA 复制发生在间期", "biology", "gene"))
check("生物·普通大写不误判", no("选项 A 正确", "biology", "gene"))

# ---------- 跨学科隔离（关键：不能串味） ----------
check("隔离·数学不转化学式", no("水是 H2O", "math", "chem"))
check("隔离·化学不转物理单位", no("速度 3 m/s", "chemistry", "unit"))
# 分数/根号属通用规则，任何学科都该转（生物里也有 3/8 概率）
check("隔离·生物也转分数", has("占 3/8", "biology", "frac", ("3", "8")))
check("隔离·生物不转化学式", no("水是 H2O", "biology", "chem"))

# ---------- 渲染输出 ----------
html = T.html_inline("反应 2H2O2 ->[△] 2H2O + O2↑", lambda s: s.replace("<", "&lt;"), "chemistry")
check("HTML·下标", "<sub>2</sub>" in html, html)
check("HTML·条件置顶", 'class="cond"' in html, html)
html_m = T.html_inline("长 2√6，分数 3/8，向量OA", lambda s: s, "math")
check("HTML·数学三件套", 'class="rad"' in html_m and 'class="frac"' in html_m and 'class="vec"' in html_m)
docx = T.docx_segments("测得 v＝3 m/s，H2O 与 TP53", "physics")
check("docx·斜体标记", any(k == "text" and v == "v" and it for k, v, it in docx), str(docx))

print(f"{n - len(fail)}/{n} 通过")
if fail:
    for f in fail:
        print("  ❌", f)
    sys.exit(1)
print("TYPО SPEC PASSED".replace("О", "O"))
