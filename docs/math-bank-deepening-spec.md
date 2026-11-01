# 数学题库加深规范 V1.0（每课时点 5 → 8 题）

> 目的：现有 1044 个知识点各 **恰好 5 题**，自适应诊断要判「四档掌握度」样本不足。
> 本轮把 **529 个课时点** 各加深 3 题（+1587 题），单元点保持 5 题不变（单元点只作图谱展示与上册总览）。

## 一、谁写、写到哪里

- 写手只写自己的分片文件：`data/math/_bank_new/<分片号>.json`
- **⛔ 不得修改** `data/math/questions.json`、`topics.json`、`exams/`、`learn/`、`exam_lectures/`、`docs/`、`scripts/`
- 合并入库由父代统一执行

分片作业单：`/Users/a627692/.hermes/profiles/agent8/cache/scratch/bank_jobs/S<NNN>.json`，
内含 4–5 个课时点（`topicId` / `name` / `chapter` / `description` / `mastery_criteria` / `existing_prompts`）与每题**指定的 `id`、`type`、`difficulty`**。

## 二、输出格式

`data/math/_bank_new/S<NNN>.json` 是一个**数组**，元素数 = 作业单里所有 `new` 条目之和（通常 15）。每个元素：

```json
{
  "id": "mat_p1000_q6",
  "topicId": "mat_p1000",
  "prompt": "题干（与 question 同值）",
  "question": "题干（与 prompt 同值）",
  "options": [{"label": "A", "text": "…"}, {"label": "B", "text": "…"},
              {"label": "C", "text": "…"}, {"label": "D", "text": "…"}],
  "answer": "B",
  "type": "choice",
  "difficulty": "basic",
  "explanation": "解析（≥20 汉字，说清「为什么」）",
  "subject": "math",
  "choices": [ …与 options 完全相同… ],
  "verify": "",
  "keypoints": []
}
```

字段规则：

| 字段 | choice | fill | numeric | short-answer |
|---|---|---|---|---|
| `options` / `choices` | 4 个，`choices` 必须与 `options` **逐字相同** | `[]` | `[]` | `[]` |
| `answer` | 正确项 label（A–D） | 答案文本 | 数值（字符串或数字，不带单位） | 参考答案文本 |
| `verify` | `""` | `""` | **纯 ASCII 算式**，`eval(verify) == float(answer)` | `""` |
| `keypoints` | `[]` | `[]` | `[]` | **≥2 条**字符串 |

- `id` / `type` / `difficulty` **必须照作业单给定值原样使用**（这三项由父代统一分配，用于避免 id 冲突与保持全库题型占比 40/20/20/20）。
- `subject` 恒为 `"math"`。

## 三、质量铁律

1. **数学必须算对**：每道数值题、每道解答要点都用 python 复算一遍再落盘，不得凭感觉。
2. **题干 ≥12 字**；`fill` 的填空处用 `____`（四个下划线）。
3. **解析 ≥20 汉字**，写清依据与易错点，禁止「显然」「易知」式空话。
4. **选择题**：4 个选项互不相同、只有一个正确；**禁用**「以上都不对 / 以上都对 / 无法确定」类凑数项；干扰项要像真错（常见错误、少一步、符号反、单位漏）。
5. **不得与已有 5 题重复或近似**：同一点内题干相似度 >0.88 且差异不足 6 字即判不合格（`test_math.py` 会拦）。同一点的三道新题之间也要互相避开。
6. **答案位置无偏置**：一个分片里 6 道选择题的正确答案要覆盖 A、B、C、D **各至少一次**。
7. **公式纯文本**（渲染层负责排版，禁止自己画符号）：
   - 根号 `√3`、`√(a+b)`；分数 `3/8`；幂 `x^2`；向量 `向量OA` 或 `OA→` 以外的写法一律用「向量OA」
   - 单位与数字之间留一个空格：`5 cm`、`3.5 kg`、`20 m/s`；算式里的 `4m`（代数式）不算单位
   - 禁止 LaTeX（`$…$`）、禁止 HTML 标签、禁止 Markdown 表格

## 四、难度口径

- `basic`：单步、直接套用定义或公式
- `standard`：两步以上，需要选方法或做一次转化
- `hard`：需要构造、分类讨论或综合两个知识点

难度由作业单指定，**不得自行更改**。

## 五、自检（必须跑到 exit 0）

```bash
cd /Users/a627692/Desktop/cn-k12-dxyc2286
python3 scripts/check_bank_new.py data/math/_bank_new/S<NNN>.json
```

门禁内容：字段齐全、类型/难度与作业单一致、id 与作业单一致且全库唯一、题干 ≥12 字、解析 ≥20 字、
选择题 4 选项互异且答案在项内、`choices == options`、数值题 `verify` 可复算且等于答案、简答题 `keypoints ≥2`、
不与已有题干重复、选择题答案字母覆盖 A–D。

## 六、汇报格式（一行，≤120 字）

```
S<NNN> | 15 题 | checker 末行
```
