# S33 · 七年级下册 题库分片派单

本片知识点 9 个，需写 **66 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p254 | unit | 数据的收集、整理与描述 | 七年级下册 数据的收集、整理与描述 | 5 |
| qdm_p255 | lesson | 数据的收集 | 七年级下册 数据的收集、整理与描述 节 数据的收集 | 8 |
| qdm_p256 | lesson | 数据的整理 | 七年级下册 数据的收集、整理与描述 节 数据的整理 | 8 |
| qdm_p257 | lesson | 数据的描述 | 七年级下册 数据的收集、整理与描述 节 数据的描述 | 8 |
| qdm_p258 | lesson | ° | 七年级下册 数据的收集、整理与描述 节 ° | 8 |
| qdm_p259 | unit | 相交线与平行线 | 七年级下册 相交线与平行线 | 5 |
| qdm_p260 | lesson | 相交线 | 七年级下册 相交线与平行线 节 相交线 | 8 |
| qdm_p261 | lesson | 平行线及其判定 | 七年级下册 相交线与平行线 节 平行线及其判定 | 8 |
| qdm_p262 | lesson | 平行线的性质 | 七年级下册 相交线与平行线 节 平行线的性质 | 8 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS33` + 4 位流水（如 `qdm_qS330001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S33.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S33.json --allow=qdm_p254,qdm_p255,qdm_p256,qdm_p257,qdm_p258,qdm_p259,qdm_p260,qdm_p261,qdm_p262
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S33 / 题数 / 难度分布 / 答案位分布 / checker 末行。
