# 数学课时级建点：内容层工位说明书（V1.0）

> 目标：把数学图谱从「单元级」扩到「**课时级**」——教材每一条课时名对一个知识点、每点 5 题。
> 本文件是**唯一契约**。写手只产出 `data/math/ke_json/<册>.json`，不碰任何其他数据文件。

## 1 输入（每个工位只做一册）

| 材料 | 路径 |
|---|---|
| 课时清单（单元\|课时名\|印刷页） | `data/math/ke_json/_toc/<册>.txt` |
| 教材 PDF | 小学 `…/数学/小学/人教版/*.pdf`；初中 `…/数学/初中/人教版/*.pdf`；高中 `…/数学/高中/人教版（A版）/*.pdf`（按册名匹配） |
| 课标引用表（**唯一允许的课标来源**） | `docs/math-std-quotes.md` 的**本册**小节 |

读教材用 `fitz`（PyMuPDF，系统 Python 已装）。印刷页 → PDF 页序偏移：小学 **−5**、初中共用目录页标注、高中 **+7**（必修）/ **+5**（选必）；清单里的页码是教材印刷页。

## 2 输出

`data/math/ke_json/<册>.json`，UTF-8、`ensure_ascii=False`：

```json
{
  "book": "一年级上册",
  "keshi": [
    {
      "name": "1～5的认识",
      "unit": "第一单元",
      "unit_name": "5以内数的认识和加、减法",
      "page": 14,
      "domain": "数与代数",
      "type": "conceptual",
      "tags": ["数与代数", "教材课时", "数与运算"],
      "description": "≥20 字，说清本课时学什么、到什么程度",
      "mastery_criteria": ["可观测的达成标准，1–3 条，每条 ≥10 字"],
      "standards": [{"id": "mat-2022:1.XY.01", "confidence": "exact",
                     "quote": "逐字照抄 docs/math-std-quotes.md 本册条目", "sourceLine": 732}],
      "questions": [ 5 题 ]
    }
  ]
}
```

- `unit` 写「第一单元」这种序号＋`unit_name` 单独给名字（照清单原样，**不许自己改名**）。
- `domain` 只能取课标四领域：`数与代数` / `图形与几何` / `统计与概率` / `综合与实践`；`tags` 首位必须＝domain，且必须含 `"教材课时"`。
- `type` 取 `conceptual` / `procedural` / `reasoning` / `modeling` / `application`。
- `standards`：只能从**本册**引用表里挑，`quote` 与 `sourceLine` 原样照抄，改一个字都会被自检器拦下。

## 3 五题配比（硬约束）

每课时固定 **2 choice + 1 fill + 1 numeric + 1 short-answer**：

| 题型 | 字段要点 |
|---|---|
| `choice` ×2 | `options` 4 个，`label` 必须 A B C D；`choices` 与 `options` 同值；4 个选项文本互不相同；`answer` 是某个 label |
| `fill` ×1 | 填空，`prompt` 里用 `____` 表示空位；`answer` 给标准答案（简短） |
| `numeric` ×1 | 数值答案；**必须带 `verify`**，且 `eval(verify) == float(answer)`（容差 1e-6），如 `"answer": 7, "verify": "2+5"` |
| `short-answer` ×1 | 必须带 `keypoints` ≥2 条，每条 ≥4 字（供自动判读）；**还必须带 `answer`**（要点式参考答案，可直接由 keypoints 拼「；」）——缺 answer 会被 schema 门禁拦下 |

每题还需：`type`、`difficulty`（`basic`/`standard`/`hard`）、`explanation`（**≥20 字**，讲清为什么）。

## 4 内容质量铁律

1. **数学必须算对**。numeric 题的 `verify` 要能独立复算出答案；分数写 `Fraction`/小数均可，但要与 `answer` 一致。
   ⛔ **伪 verify 一律不收**：`verify` 写 `5`、`0*1`、`1+1`、`1*答案` 这种只是把答案抄一遍的，自检器会判死。
   计数题写成 `len([1,2,3,4,5])` 或 `len([x for x in range(-50,51) if ...])`，能真算出来才算过。
2. **同一课时的 `standards` 不许重复同一 id**（写两次等于只写了一条），挑两条就挑两条不同的。
3. **题干 ≥12 字**，且必须能看出考什么（不要「计算下面各题」这种脱离教材的干题）。
4. **题干全域唯一**：`data/math/questions.json` 已有题干不得重复使用（自检器会查），本册内部也不许重复。
5. 选择题干扰项要**像真的错**：不得用「以上都不对」「与本题无关」「只有高中才学」凑数；4 个选项同一量纲、同一问法。
6. 答案标签分散：全册 choice 里任一 label 占比 ≤45%。
7. 难度配比：每册约 basic 55–65%、standard 30–40%、hard ≤10%（hard 用在本册确实有综合性的课时，不要硬凑）。
8. 题目必须**落在教材这一页的内容范围内**：先读该课时页码对应的 PDF 页，再写题；不许写这一课时没教的解法。
9. 严禁自造概念名、严禁把下一课时内容提前考、严禁出现教材里的具体人物/插图编号等不可复算信息。

## 5 交付前自检（必须自己跑过，exit 0 才算交）

```bash
cd ~/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/check_math_ke_json.py data/math/ke_json/<册>.json
```

## 6 禁止事项

- ⛔ 不修改 `data/math/{topics,questions,dependencies}.json`、`scripts/`、`docs/` 里的任何文件；
- ⛔ 不修改其他册的 `ke_json`；
- ⛔ 不跑 `build_math_ke_points.py`（合并由父工位统一做）；
- ⛔ 课时清单里没有的课时不要自己加；清单里有的不要漏（插图单元缺名时按 PDF 实读补名并注明）。

## 7 父工位合并与门禁

```bash
/usr/bin/python3 scripts/build_math_ke_points.py --book <册>
/usr/bin/python3 scripts/rebuild_aggregates_only.py
/usr/bin/python3 scripts/test_math.py && /usr/bin/python3 scripts/validate.py math
```

id 由合并器统一分配（小学/初中 `mat_p` 从 1000 起、高中 `mat_h` 从 300 起），写手**不要写 id**。
chapter 由合并器拼成 `<册> <单元> <单元名> · <课时名>`，先修边自动连到同单元单元级点（hard）与本单元上一课时（soft）。
