# 人教版物理 · 题库分片合同（PHYS_B01–B26）

> 只读本文件 ＋ 你自己的分片 JSON。**不许改仓库数据、脚本、别人的分片**；只写自己 `out` 指定的那个文件。

## 0. 输入输出

`data/physics/_bank_shards/PHYS_Bnn.json`：`topics[]`（点清单）、`slots[]`（每点题数 `count`、题号 `idRange`、题型配额 `quota`）、`txt`（本册教材全文）、`out`（落盘路径）。

落盘必须是**对象**：

```json
{"shard": "PHYS_B01",
 "topics": [{"id": "phys_p102", "description": "…40–90 汉字…", "mastery_criteria": ["…","…"], "type": "conceptual"}],
 "questions": [{"id": "phy_q0001", "topicId": "phys_p102", "type": "choice", "difficulty": "basic",
                "stem": "…", "options": [{"label":"A","text":"…"}], "choices": [同 options 四项],
                "answer": "B", "analysis": "…25 汉字以上…"}]}
```

## 1. 题量与题号
- 每个 slot 题数**恰好** `count`（课时点 8、章点 5），题号**逐字**取 `idRange`，⛔ 不自己续号。

## 2. 题型配额（按 slot.quota）
| 题型 | 硬要求 |
|---|---|
| `choice` | 4 选项 A–D，`answer` ∈ label，`choices` 与 `options` 同构 |
| `fill` | 题干含 `____`，`answer` 字符串，`options=[]` |
| `short-answer` | `answer` 用「；」分 2–3 条，`options=[]` |
| `numeric` | `answer` 数字字符串（如 `"2.5"`），`verify` **纯算术**表达式（`"0.5*5"`），禁 `int()/round()`；`options=[]` |

## 3. 难度
课时点 8 题**三档齐**（basic/standard/hard 各 ≥1）；章点 5 题至少两档。

## 4. 题干与解析
- 题干 ≥12 汉字；解析 ≥25 汉字，结尾写「故选 X」或「答案为 …」。
- 禁 Markdown（`**`、`##`、`|`、`$`、`\frac`）。
- 物理量用普通文本：`v=s/t`、`F=ma`、`ρ=m/V`、`P=UI`、`W=Fs`、`g 取 10 N/kg`；⛔ 不用下标字符（`v₀`）、不写公式对象。
- 数值题必须**带单位**，且 `verify` 复算等于 `answer`；单位与数量级要合理（速度 m/s、密度 kg/m³、功率 W）。
- 同一片内题干不得重复。

## 5. topics[] 内容
- `description` 40–90 汉字，写本点**具体**在讲什么（物理量、规律、实验、单位），⛔ 不写「理解本课核心内容」。
- `mastery_criteria` 1–3 条：能说出…／能写出公式…／能计算…／能解释…。
- `type`：`conceptual / procedural / reasoning / modeling / application` 之一。
- ⛔ 不写 `standards`（父代挂）。

## 6. 自检
```bash
python3 scripts/check_phys_bank.py <你的 out>
```
必须 `RESULT: PASS`。报错改自己的文件，⛔ 不改 checker。

## 7. 汇报
```
DONE PHYS_Bnn | topics=K | questions=N | selfcheck=PASS
```
