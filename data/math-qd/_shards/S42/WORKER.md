# S42 · 八年级下册 题库分片派单

本片知识点 9 个，需写 **66 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p333 | unit | 图形的平移与旋转 | 八年级下册 图形的平移与旋转 | 5 |
| qdm_p334 | lesson | 图形的平移 | 八年级下册 图形的平移与旋转 节 图形的平移 | 8 |
| qdm_p335 | lesson | 图形的旋转 | 八年级下册 图形的平移与旋转 节 图形的旋转 | 8 |
| qdm_p336 | lesson | 图形的中心对称 | 八年级下册 图形的平移与旋转 节 图形的中心对称 | 8 |
| qdm_p337 | unit | 数据的分析 | 八年级下册 数据的分析 | 5 |
| qdm_p338 | lesson | 数据的集中趋势 | 八年级下册 数据的分析 节 数据的集中趋势 | 8 |
| qdm_p339 | lesson | 四分位数与箱线图 | 八年级下册 数据的分析 节 四分位数与箱线图 | 8 |
| qdm_p340 | lesson | 数据的离散程度 | 八年级下册 数据的分析 节 数据的离散程度 | 8 |
| qdm_p341 | lesson | 随机现象的变化趋势 | 八年级下册 数据的分析 节 随机现象的变化趋势 | 8 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS42` + 4 位流水（如 `qdm_qS420001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S42.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S42.json --allow=qdm_p333,qdm_p334,qdm_p335,qdm_p336,qdm_p337,qdm_p338,qdm_p339,qdm_p340,qdm_p341
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S42 / 题数 / 难度分布 / 答案位分布 / checker 末行。
