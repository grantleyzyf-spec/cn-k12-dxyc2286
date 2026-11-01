# 湘教版数学 · 分册内容与题库工位（WORKER）

你是「湘教版数学知识图谱」的**一册工人**。父代只负责结构，内容与题目全部由你产出。

## 输入（只读）

- `data/math-xiangjiao/_shards/<tag>.json` —— 该册结构：`units[].unit_id/unit_name/unit_chapter/domain`、`units[].lessons[].id/name/chapter/page`
- `/tmp/mxj2/<tag>/textpack.txt` —— 该册逐页正文，页头形如 `<<<PDF 12 / 印5>>>`；**题材依据只能来自这里**，某处是图/表就写「教材该处为图/表」，不编造
- 课标：初中用
  `~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt`；
  高中用 `…/高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt`
- 教材 PDF（只在 textpack 缺页时才开）：`~/Desktop/中小学教材/中小学教材/数学/{初中,高中}/湘教版/`

## 输出（唯一）

`data/math-xiangjiao/_bank/<tag>.json`

```json
{
  "tag": "mxj7a", "book": "湘教版七年级上册",
  "unit_points": [
    {"id": "mxj_p001", "description": "…（≥12 汉字）",
     "mastery_criteria": ["…（≥8 汉字，1–3 条）"],
     "type": "conceptual", "questions": [ 5 道 ]}
  ],
  "lesson_points": [
    {"id": "mxj_p1001", "page": 14, "description": "…", "mastery_criteria": ["…"],
     "misconceptions": ["…", "…（≥2 条）"], "type": "conceptual", "questions": [ 8 道 ]}
  ]
}
```

- **单元点 5 题、课时点 8 题**，数量必须正好；`id` 只能用派单里的 id，一个不多一个不少；`page` 与派单一致。
- `type` ∈ `conceptual / procedural / reasoning / modeling / application`（按节内容如实判定：讲定义概念→conceptual，讲算法运算→procedural，讲推理证明→reasoning，建模应用→modeling/application）

## 题目字段

```json
{"id":"mxj_p1001_q1","topicId":"mxj_p1001","prompt":"…","question":"…（与 prompt 相同）",
 "options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "answer":"B","type":"choice","difficulty":"basic","explanation":"…（≥15 汉字）"}
```

- `type` ∈ `choice / numeric / fill / short-answer`
  - `choice`：4 个选项 A–D，`answer` 是单个字母且在选项内
  - `numeric`：必带 `verify`，格式 `{"type":"num","value":12.5}` 或
    `{"type":"op","op":"mul","values":[{"type":"num","value":3},{"type":"num","value":4}]}`
    （`op` ∈ `op/sub/mul/div/pow`；**不许写 ^，幂写 pow**）
  - `fill / short-answer`：`answer` 写学生应填的答案文本
- `difficulty` ∈ `basic / standard / hard`，**每点三档都要出现**
- 单点内选择题答案位同一字母 ≤40%（8 题里同一字母最多 3 次）
- 题干 ≥8 汉字、解析 ≥15 汉字；**全文禁用 Markdown 符号** `* _ ` # [ ] |`（乘方写「的平方」）

## 学科红线

1. 题目必须能在该节 textpack 文本里找到依据；找不到依据的题不写，也不写「教材没有但一般会考」的。
2. 不编造教材页码、单元号、活动名；不出现人教版独有栏目名（如「数学广角」）。
3. 初中题不超纲：本节未学的运算/符号不用（如未学二次根式就用整数与有理数）。
4. 应用题情境取真实生活（购物、测量、行程、体育），避免广告与品牌。
5. 事实性错误零容忍：数与运算、几何结论、单位换算一律自行复核一遍。

## 自检（必须跑到末行 PASS 才回报）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 data/math-xiangjiao/_scripts/check_bank_sj.py <tag> --subject math-xiangjiao
```

末行须为 `== 小结：通过 1/1 ==`。报错就改 `_bank/<tag>.json` 重跑，直到全绿。

## 回报（一句话）

`<tag> <册名>：单元点 N / 课时点 M / 题 K（choice x / numeric y / fill z / short-answer w）· check PASS`
