# 晋教版初中地理 · 内容＋题库工位合同（一片＝一个主题）

> 本文件是 16 个工位共用的**唯一**规则来源。派单卡只写片号，其余照此执行。
> 仓库根：`~/Desktop/cn-k12-dxyc2286`（下文路径都相对它）。

## 一、你的分片

读 `data/geography-jin/_points/T{NN}.json`：

| 字段 | 含义 | 能不能改 |
|---|---|---|
| `book` / `unitLabel` / `chapter` / `domain` / `grade` / `semester` | 册次、主题名、章串、领域、年级、学期 | ⛔ 不许改 |
| `lessons[].id` / `lessons[].name` | 8 个课时点的 id 与课时名 | ⛔ 不许改，`name` 逐字照抄进产物 |
| `unitId` | 本主题的单元点 id | ⛔ 不许改 |

题库槽位在 `data/geography-jin/_bank_spec/T{NN}.json`：9 个点（8 课时 ＋ 1 单元）、每片 **69 题**，
每个槽位已写死 `id / type / difficulty`，选择题还带 `label`（正确项必须在那个字母上）。

## 二、教材原文（唯一权威，不许自造）

`~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中/<册>/整册全文.txt`
（并列有逐页 `ocr/pNNN.txt`）。

定位方法（**只准这一种**）：
```bash
F=~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中/七年级上册/整册全文.txt
grep -n "地球在太阳系" "$F"      # 先找到行号
sed -n '120,190p' "$F"          # 再读那一段
```
⛔ 不准 `search_files`（几万文件的教材仓上必 420 超时）；⛔ 不准通读全册；⛔ 不准按册名猜内容。

## 三、产物 1：`data/geography-jin/_points/T{NN}.json`

```json
{"shard": "T01", "points": [
  {"id": "gjin_j001", "name": "地球在太阳系中的位置", "type": "conceptual",
   "description": "40–120 汉字的实质说明，写这一课时到底讲什么、学生要会什么",
   "mastery_criteria": ["……", "……"],
   "diagnostic_question": {"question": "≥10 字的问句", "answer": "具体答案"}}
]}
```

- 必须恰好 9 条，`id` 集合与 spec 的 9 个 `topicId` 完全一致
- `type` ∈ `conceptual / procedural / reasoning / modeling / application`
  （地理：概念与分布多为 `conceptual`；读图判读、绘图、计算为 `procedural`；区域比较与原因分析为 `reasoning`；
   模拟实验、方案设计为 `modeling`；家乡调查、实地应用为 `application`）
- `description` 汉字数 **40–120**（不足 40 或超 120 一律判红）
- `mastery_criteria` **2–3 条**，每条 ≥8 汉字、互不重复
- 单元点（`unitId`，spec 里 `kind: "unit"`）：`description` 写整个主题的主线，`mastery_criteria` 写 3 条
- 禁 `**`、`##`、`|`、`$`、反斜杠；禁「扫描件/OCR/抽取/切片/文字层/残片/待补/TODO」

## 四、产物 2：`data/geography-jin/_bank/T{NN}.json`

```json
{"shard": "T01", "questions": [
  {"id": "gjin_j001_q02", "topicId": "gjin_j001",
   "prompt": "题干（≥12 字）", "question": "题干必须与 prompt 完全相同",
   "answer": "B", "type": "choice", "difficulty": "basic",
   "explanation": "≥25 汉字的解析，末句写「故选 B」或「故填 …」",
   "options": [{"label": "A", "text": "…"}, {"label": "B", "text": "…"},
               {"label": "C", "text": "…"}, {"label": "D", "text": "…"}],
   "choices": [ /* 与 options 逐项相同 */ ]}
]}
```

字段口径逐字照抄自 `data/geography/questions.json`，要点：

- `question` 必须与 `prompt` **完全相同**（前端两处读不同字段）
- **choice**：`options` 与 `choices` 是**同一份** 4 项（label 恰为 A–D、文本互异），`answer` 是字母，且
  **必须等于 spec 给该槽位的 `label`**（正确项放在指定位置，干扰项要真干扰）
- **fill**：题干含 `____`（4 个半角下划线），`options`/`choices` 为 `[]`，`answer` 是词或短语
- **numeric**：`answer` 是纯数字字符串，`verify` 是可用 `eval` 复算的纯算术式
  （只含数字与 `+ - * / ** ( )`；⛔ `int()`/`round()`/带单位/带「约」都会判红）
- **short-answer**：`answer` 用「；」分 2–3 条要点，总汉字 ≥15
- `explanation` ≥25 汉字，必须给出判断依据，不能只写「见教材」
- 题干 ≥12 字；禁凑数项（以上都不对 / 以上都对 / 仅在大学学习 / 无法确定 这类空选项）
- 禁 Markdown 与 LaTeX（`**`、`##`、`$`、`\frac`、表格竖线）

内容要求（地理特有）：

1. **一题一考点**，题干尽量挂一个具体的区域/数据/现象（如「我国 1 月 0 ℃ 等温线大致沿秦岭—淮河分布」），
   不要写「关于本课内容下列说法正确的是」这种空题干。
2. **不得把教材整句搬来当题干或选项**：教材原句可以改写成自己的表述；整段照抄会在原创性审计里被判雷同。
3. 全片 **69 题题干互不重复**（同一个知识点连出多题时，换角度：分布 / 成因 / 影响 / 判读 / 应用）。
4. 读图类题不依赖看不见的图：把图上的关键信息写进题干文字（「某地年降水量柱状图显示 7 月约 180 毫米」）。

## 五、自检（两条都必须跑，末行必须是 `RESULT: PASS`）

```bash
python3 scripts/check_geo_jin_points.py data/geography-jin/_points/T{NN}.json
python3 scripts/check_geo_jin_bank.py   data/geography-jin/_bank/T{NN}.json
```

判红就地改，**不要重派**。常见红与修法：

| 报错 | 修法 |
|---|---|
| `description 汉字 128（须 40–120）` | 删例子、留结论句 |
| `答案位应为预分配的 C` | 把正确项挪到 C 项，或改题干使 C 项的表述成立（⛔ 不改 `answer`） |
| `verify 复算与 answer 不等` | 改 `verify` 表达式（纯算术），或改 `answer` |
| `题干重复` | 换角度重写其中一题 |
| `含 Markdown/LaTeX 字符` | 去掉 `**`/`|`/`$`，公式写纯文本（`1 500 米`、`约 3/4`） |

## 六、回报格式

一行式：`T{NN} 完成：9 点 / 69 题 / 两个 checker 均 PASS`，再加 3–5 条「教材里查不到、需父代裁定」
的具体要点（没有就写「无」）。

⛔ 不要改技能库文件；⛔ 不要碰别人的分片；⛔ 不要写 `topics.json` / `questions.json`（合并由父代做）。
