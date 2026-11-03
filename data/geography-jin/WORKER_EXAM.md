# 晋教版初中地理 · 出卷工位合同（一片＝一册 4 卷）

> 16 个工位共用。派单卡只给你片号；其余照此执行。仓库根 `~/Desktop/cn-k12-dxyc2286`。

## 一、你的派单

读 `data/geography-jin/_exam_shards/E{NN}.json`：`book / grade / term / stage / duration / fullScore` 已定，
`papers[]` 每项给出 `examId / kind / paper / scope / topicIds`。

**卷面口径写死，不许改数字**：

| 段 | rule 文本（逐字） | 题数 | 题型 | 每题分 |
|---|---|---|---|---|
| 一 | `每小题 3 分，共 54 分` | 18 | `choice` | 3 |
| 二 | `每小题 11 分，共 66 分` | 6 | `short` | 11 |

全卷 24 题、120 分、120 分钟。

## 二、产物

每卷一个文件：`data/geography-jin/exams/<册>/<paper>.json`

```json
{"book": "七年级上册", "kind": "unit", "term": "上", "grade": 7, "stage": "初中",
 "paper": "七年级上册 主题一 探寻人类的太空家园 测试卷",
 "duration": 120, "fullScore": 120, "examId": "gjin_exam_j7a_u01",
 "scope": ["七年级上册 主题一 探寻人类的太空家园"],
 "sections": [
   {"rule": "每小题 3 分，共 54 分", "items": [ /* 18 题 choice */ ]},
   {"rule": "每小题 11 分，共 66 分", "items": [ /* 6 题 short */ ]}
 ]}
```

题字段（逐字照此，`no` 全卷连续 1–24）：

```json
{"no": 1, "itemId": "gjin_exam_j7a_u01_q01", "type": "choice", "difficulty": "basic",
 "topicIds": ["gjin_j001"], "score": 3,
 "stem": "题干（≥12 字）",
 "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "answer": "B", "analysis": "≥20 汉字，含「故选 B」"}

{"no": 19, "itemId": "gjin_exam_j7a_u01_q19", "type": "short", "difficulty": "standard",
 "topicIds": ["gjin_j002"], "score": 11,
 "stem": "材料 ＋ 三小问（1）（2）（3）",
 "options": [], "answer": "① … ② … ③ …（与 scoreRule 步数对应）",
 "analysis": "≥20 汉字，讲清每一步怎么来的",
 "scoreRule": ["① …，3 分", "② …，4 分", "③ …，4 分"]}
```

- `itemId` 必须是 `<examId>_qNN`（NN 与 `no` 对齐，两位）
- `short` 题的 `scoreRule` 是**字符串数组**，每条末尾写「N 分」，各条分值之和必须等于 11
- `choice` 题的 `options` 为 4 项、label 恰为 A–D、文本互异；`answer` 是字母
- `options` 在 `short` 题里写 `[]`

## 三、内容要求

1. **覆盖**：`kind == "unit"` 的卷必须覆盖 `scope[0]` 这个主题下的**全部 8 个课时点**（`topicIds` 里每个课时点 ≥1 次）；
   期中卷覆盖前两个主题的 16 个点、期末卷覆盖全册 32 个点 —— 一个题可以挂 2 个 `topicIds`，但每个点至少出现 1 次。
2. **难度**：每卷 `basic` 约 8 题、`standard` 约 12 题、`hard` 约 4 题；6 道综合题里至少 1 道 `hard`。
3. **答案位**：18 道选择题里 A、B、C、D 各 ≥3 题（各 ≥15%），别一律选 B。
4. **原创性**：与题库 `data/geography-jin/questions.json` 的题干相似度必须 <0.85（改写情境、换数据、换问法）。
5. **地理味**：题干带真实区域/数据/现象；读图题把图上关键信息写进文字（学生看不到原图）。
6. 综合题要「材料 ＋ 若干小问」，小问数与 `scoreRule` 条数一致，答案与 `scoreRule` 一一对应。

## 四、自检（末行必须 `RESULT: PASS`）

```bash
python3 scripts/check_geo_jin_exam.py data/geography-jin/exams/<册>/<卷名>.json
# 或者整片一次过：
python3 scripts/check_geo_jin_exam.py --book <册>
```

常见红与修法：

| 报错 | 修法 |
|---|---|
| `单元卷未覆盖 N 个课时点` | 给某道题补上缺的 `topicId`，并让题干真的考到那个点 |
| `与题库 xxx 雷同 0.8x` | 换情境与数据，别只改一个数字 |
| `答案位偏低 {'D': 11.1}` | 把某题正确项挪到 D 项（交换选项文本，改 `analysis` 里的「故选」） |
| `第N题 scoreRule 合计 10 ≠ 题分 11` | 调某一步分值（3/4/4 或 2/4/5） |
| `分值和 118 ≠ 满分 120` | 逐段核 score，必须 54 + 66 |

## 五、回报

一行式：`E0N 完成：4 卷 / 逐卷 checker PASS`，附 3 条以内「卷面踩到的坑或需父代裁定的点」。

⛔ 不改技能库；⛔ 不动 `topics.json`/`questions.json`/别人的卷；⛔ 不改卷面口径里的数字。
