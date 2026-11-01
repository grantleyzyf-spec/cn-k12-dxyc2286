# S28 · 六年级上册 题库分片派单

本片知识点 10 个，需写 **59 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p209 | lesson | 分数四则混合运算 | 六年级上册 第二单元 走进乡村看小康 信息窗4 分数四则混合运算 | 8 |
| qdm_p210 | unit | 劳动实践长学问 | 六年级上册 第三单元 劳动实践长学问 | 5 |
| qdm_p211 | lesson | 比的意义和基本性质 | 六年级上册 第三单元 劳动实践长学问 信息窗1 比的意义和基本性质 | 8 |
| qdm_p212 | lesson | 按比例分配 | 六年级上册 第三单元 劳动实践长学问 信息窗2 按比例分配 | 8 |
| qdm_p213 | unit | 主题活动·“黄金比”之美 | 六年级上册 主题活动·“黄金比”之美 | 5 |
| qdm_p214 | unit | 四 | 六年级上册 四 | 5 |
| qdm_p215 | unit | 五 | 六年级上册 五 | 5 |
| qdm_p216 | unit | 六 | 六年级上册 六 | 5 |
| qdm_p217 | unit | 项目学习·制订家庭节水方案 | 六年级上册 项目学习·制订家庭节水方案 | 5 |
| qdm_p218 | unit | 七 | 六年级上册 七 | 5 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS28` + 4 位流水（如 `qdm_qS280001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S28.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S28.json --allow=qdm_p209,qdm_p210,qdm_p211,qdm_p212,qdm_p213,qdm_p214,qdm_p215,qdm_p216,qdm_p217,qdm_p218
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S28 / 题数 / 难度分布 / 答案位分布 / checker 末行。
