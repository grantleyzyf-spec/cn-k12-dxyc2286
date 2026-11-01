# S32 · 七年级上册 题库分片派单

本片知识点 8 个，需写 **61 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p246 | unit | 基本的几何图形 | 七年级上册 基本的几何图形 | 5 |
| qdm_p247 | lesson | 图形的认识 | 七年级上册 基本的几何图形 节 图形的认识 | 8 |
| qdm_p248 | lesson | 线段、射线和直线 | 七年级上册 基本的几何图形 节 线段、射线和直线 | 8 |
| qdm_p249 | lesson | 线段的比较与运算 | 七年级上册 基本的几何图形 节 线段的比较与运算 | 8 |
| qdm_p250 | lesson | 角 | 七年级上册 基本的几何图形 节 角 | 8 |
| qdm_p251 | lesson | 角的比较与运算 | 七年级上册 基本的几何图形 节 角的比较与运算 | 8 |
| qdm_p252 | lesson | 余角和补角 | 七年级上册 基本的几何图形 节 余角和补角 | 8 |
| qdm_p253 | lesson |  | 七年级上册 基本的几何图形 节 | 8 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS32` + 4 位流水（如 `qdm_qS320001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S32.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S32.json --allow=qdm_p246,qdm_p247,qdm_p248,qdm_p249,qdm_p250,qdm_p251,qdm_p252,qdm_p253
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S32 / 题数 / 难度分布 / 答案位分布 / checker 末行。
