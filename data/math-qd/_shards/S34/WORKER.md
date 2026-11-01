# S34 · 七年级下册 题库分片派单

本片知识点 9 个，需写 **66 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p263 | unit | 二元一次方程组 | 七年级下册 二元一次方程组 | 5 |
| qdm_p264 | lesson | 认识二元一次方程组 | 七年级下册 二元一次方程组 节 认识二元一次方程组 | 8 |
| qdm_p265 | lesson | 解二元一次方程组 | 七年级下册 二元一次方程组 节 解二元一次方程组 | 8 |
| qdm_p266 | lesson | 二元一次方程组与实际问题 | 七年级下册 二元一次方程组 节 二元一次方程组与实际问题 | 8 |
| qdm_p267 | unit | 整式的乘法与除法 | 七年级下册 整式的乘法与除法 | 5 |
| qdm_p268 | lesson | 幂的运算 | 七年级下册 整式的乘法与除法 节 幂的运算 | 8 |
| qdm_p269 | lesson | 整式的乘法 | 七年级下册 整式的乘法与除法 节 整式的乘法 | 8 |
| qdm_p270 | lesson | 乘法公式 | 七年级下册 整式的乘法与除法 节 乘法公式 | 8 |
| qdm_p271 | lesson | 整式的除法 | 七年级下册 整式的乘法与除法 节 整式的除法 | 8 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS34` + 4 位流水（如 `qdm_qS340001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S34.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S34.json --allow=qdm_p263,qdm_p264,qdm_p265,qdm_p266,qdm_p267,qdm_p268,qdm_p269,qdm_p270,qdm_p271
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S34 / 题数 / 难度分布 / 答案位分布 / checker 末行。
