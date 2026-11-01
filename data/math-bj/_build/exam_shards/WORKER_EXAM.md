# 北京版数学试卷工位（math-bj · 单元卷）· 契约

你是本片唯一写手。**只写本片的卷**，不碰仓库其它文件。

- 输入：`E<NN>.json`（本片册、单元、课时点、题库索引）
- 输出：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/exams/<册>/<卷名>.json`（每单元一份）
- 自检：`cd /Users/a627692/Desktop/cn-k12-dxyc2286 && python3 scripts/check_math_bj_exam.py data/math-bj/exams/<册>/<卷名>.json`，**每份卷都要末行 PASS**
- 绝对路径：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/_build/exam_shards/`

## 一、卷名与顶层字段

卷名：小学「第X单元测试卷.json」、初中「第X章测试卷.json」（X 为中文序号，与该点 `chapter` 里的单元号一致）。
顶层：

```json
{"book":"一年级上册","kind":"unit","term":"上册","grade":1,"stage":"小学",
 "paper":"第一单元测试卷","duration":40,"fullScore":100,
 "scope":["第一单元 我是小学生"],"examId":"mbj_exam_g1a_u01","sections":[...]}
```

- `duration`/`fullScore`：小学 1–2 年级 40 分/100 分，3–6 年级 60 分/100 分，初中 90 分/120 分。
- `examId`：`mbj_exam_<册码>_u<两位单元号>`（册码见输入 `book_code`，如一上 `g1a`）。
- `scope`：本卷覆盖的单元标题（含单元号）。

## 二、卷面结构（checker 硬断言，不得增删）

| 学段 | 段序（标题须含关键词；题数×分值） |
|---|---|
| 小学1-2 | 直接写得数 10×2 ／ 填空 10×2 ／ 选择 8×2 ／ 操作 4×4 ／ 解决问题 4×7 → 100 分 |
| 小学3-6 | 计算 6×4 ／ 填空 10×2 ／ 选择 8×2 ／ 操作 3×4 ／ 解决问题 4×7 → 100 分 |
| 初中 | 选择 10×3 ／ 填空 6×4 ／ 解答 8 题（分值序列 6,6,8,8,9,9,10,10）→ 120 分 |

无计算的单元（整单元课时点都在图形与几何/统计与概率）可把首段换成「看图作答/看图数一数」，并在顶层写 `"variant":"no-calc"`。

## 三、逐题字段

```json
{"no":1,"type":"fill","difficulty":"basic","topicIds":["mbj_p004"],
 "stem":"直接写得数：3＋2＝（　　）。","answer":"5",
 "analysis":"3＋2＝5：把 3 和 2 合起来一共是 5。","verify":"3+2",
 "score":2,"itemId":"mbj_exam_g1a_u01_q01",
 "prereq":["mbj_p003"],"reteach":[{"qid":"mbj_p004_q1","topicId":"mbj_p004","difficulty":"basic"}]}
```

- `no` 全卷连续 1..N；`itemId` = `<examId>_q<两位>`。
- `topicIds` **必须是本册课时级点**（输入 `topics_all` 里 `level=lesson` 的 id）。
- 单元卷必须让本单元**每个课时点各至少出现 1 次**。
- 题干 `stem` ≥12 字；`analysis` ≥20 字；`choice` 四个选项 `{"label":"A".."D","text"}` 互异且 `answer` 是 label。
- 解答题（初中「解答」段）必须有 `scoreRule`：数组，各项分值和 == 该题 `score`。
- `numeric` 若有 `verify`，必须 `eval(verify)` == `answer`（answer 一律字符串）。
- `reteach`：指向题库里同点题的 `qid`（输入 `bank_index` 给了每个点可用的 qid 列表，取前 2–3 个）。
- `prereq`：本题考点的直接先修点 id（可空数组）。

## 四、原创性红线（checker 硬断言 <0.85）

**卷面题干不得抄题库**：与 `data/math-bj/questions.json` 任一题干相似度必须 <0.85（去空白后 difflib 比）。
题库题只作 `reteach` 引用；卷面题必须**换情境、换数字、换问法**重写。

## 五、内容红线

- 情境用北京版教材口径（小学低年级「一共/还剩/比…多」；初中「解/求证/化简」）。
- 禁 LaTeX、`$`、`^`（幂写「平方」「立方」或 `**` 只在 verify 里）。
- 干扰项必须是真实错法（漏进位、单位不统一、把「第几」当「几个」、量率对应错），严禁「以上都对/与…无关」。
- 数值必须自洽：应用题数据要算得出整数（小数按年级允许）。

## 六、汇报（一行）

```
DONE E<NN> | book=<册> | exams=<卷数> | items=<总题数> | check=PASS
```
