# 北京版数学题库工位（math-bj）· 契约

你是本片唯一写手。**只写本片**，不碰仓库其它文件。

- 输入：`S<NN>.json`（本片知识点清单，含 `std_candidates`）
- 输出：`../_bank/S<NN>.json`（唯一产物）
- 自检：`python3 check_bank.py S<NN>` 必须跑到末行 `PASS`
- 绝对路径：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/_shards/`
  `_bank/` 目录不存在就建。

## 一、每点必须产出（点数与 S 文件一致，不多不少）

```json
{
  "topicId": "mbj_p001",
  "description": "60–140 字，教材口径：学什么、学到什么程度；不写出答案",
  "mastery_criteria": ["1–3 条，每条 ≤50 字，行为动词开头、可计数"],
  "misconceptions": ["2–3 条，每条 ≤40 字，写学生真实错法（不是口号）"],
  "std": {"id": "mat-2022:1.NR.05", "quote": "……"} ,   // 或 null
  "questions": [ ... ]
}
```

- `std`：**只能**从本片 `std_candidates` 里选 1 条最贴合的，`quote` 必须与候选项**逐字相同**（含标点），`id` 用候选项的 id。
  确实无对应表述 → `null`（宁可留空，不许自造 id、不许改写 quote）。
- 学段：`grade 1–2 → 学段 1`，`3–4 → 2`，`5–6 → 3`，`7–9 → 4`。

## 二、题量（按点的 `level`）

- `level: "unit"`（单元/章）：**5 题**
- `level: "lesson"`（课时/节）：**8 题**

## 三、每题字段

| 字段 | 要求 |
|---|---|
| `id` | `<topicId>_q1` … `_q5/_q8`，按序 |
| `topicId` | 同点 id |
| `prompt` | ≥12 字，学生向；不用「以上都对/与…无关」；不含 LaTeX、`$`、`^`（用「平方」「根号」等文字） |
| `question` | 与 `prompt` 同值（兼容别名） |
| `type` | `choice` / `numeric` / `fill` / `short-answer` 之一 |
| `difficulty` | `basic` / `standard` / `hard` 三档，**不许 easy/medium** |
| `options` | `choice` 必填：4 项 `{label:"A".."D", text}`；**干扰项必须是学生的真实错法**（错位、漏0、符号反、概念混），禁止「仅在大学学习」「不属于本课程」这类凑数项 |
| `answer` | `choice`→label；`fill`/`numeric`→字符串答案；`short-answer`→要点式参考答案（≥30 字） |
| `explanation` | ≥20 字，讲清「为什么」，不是复述答案 |
| `verify` | **numeric 必填**：可直接 `eval` 的纯算术表达式，且其计算结果 == `answer`（如 answer "24"、verify "6*4"） |
| `subject` | 固定 `"math-bj"` |

## 四、同点要求（逐条自检）

1. 同点的 5/8 题**不得问同一件事**（覆盖不同侧面：概念判断、计算、应用、辨析、表述）。
2. 难度配比：`basic` 约 40%、`standard` 约 40%、`hard` 约 20%，**每点三档至少各 1 题**。
3. `choice` 的答案位：全片 A/B/C/D **各 ≥2 次**，不许全 A。
4. 数值答案必须真算对；应用题数据要自洽（不要出现「每人 5 个、3 人共 20 个」）。
5. 语言用教材口径（一年级用「一共」「还剩」，初中用「解」「求证」），不用抽象学术腔。

## 五、汇报（只有一行，不要长篇）

```
DONE S<NN> | points=<n> | q=<题总数> | choice=<n>/numeric=<n>/fill=<n>/short=<n> | std=<已挂标点数>/<n> | check=PASS
```
