# S10 · 二年级上册 题库分片派单

本片知识点 10 个，需写 **65 道题**（课时点每点 8 题、单元点每点 5 题）。

| topicId | level | 名称 | 教材位置 | 题数 |
| --- | --- | --- | --- | --- |
| qdm_p058 | unit | 智慧广场·分类数图形 | 二年级上册 智慧广场·分类数图形 | 5 |
| qdm_p059 | unit | 多彩的社团 | 二年级上册 第三单元 多彩的社团 | 5 |
| qdm_p060 | lesson | 7的乘法口诀 | 二年级上册 第三单元 多彩的社团 信息窗1 7的乘法口诀 | 8 |
| qdm_p061 | lesson | 8的乘法口诀 | 二年级上册 第三单元 多彩的社团 信息窗2 8的乘法口诀 | 8 |
| qdm_p062 | lesson | 9的乘法口诀 | 二年级上册 第三单元 多彩的社团 信息窗3 9的乘法口诀 | 8 |
| qdm_p063 | unit | 主题活动·我们的校园 | 二年级上册 主题活动·我们的校园 | 5 |
| qdm_p064 | unit | 传统节日 | 二年级上册 第四单元 传统节日 | 5 |
| qdm_p065 | lesson | 平均分 | 二年级上册 第四单元 传统节日 信息窗1 平均分 | 8 |
| qdm_p066 | lesson | 除法的认识 | 二年级上册 第四单元 传统节日 信息窗2 除法的认识 | 8 |
| qdm_p067 | unit | 教室里的测量 | 二年级上册 第五单元 教室里的测量 | 5 |

## 题目要求

1. 全部 `choice`，4 个选项，字段：`{"id","topicId","prompt","question","answer","type":"choice","difficulty","explanation","options":[{"label":"A","text":"…"},…]}`。
2. `prompt` 与 `question` 同值；≥12 个汉字；写真实情境题干（不要「关于「X」，下列说法正确的是」）。
3. 4 个选项都要实质内容，3 个错项必须是学生真实错法（多算/少算/符号看错/单位漏写/概念混淆），⛔ 禁「与本题无关」「不知道」「以上都不是」。
4. `answer` 只能是 A/B/C/D；全片四字母分布接近均匀（单字母 ≤40%）。
5. 难度三档齐全：basic（直接套用）/ standard（一步情境或辨析）/ hard（多步、逆向、易错边界）。
6. `explanation` ≥15 个汉字，写清「为什么对」并点出典型错因。
7. 题面与解析内不出现 Markdown 记号（**、反引号、#、行首 - ）。
8. 计算题请自己先用算式核一遍答案（数值题的正确项文字里要含该数值），避免算术错误。
9. `id` 用 `qdm_qS10` + 4 位流水（如 `qdm_qS100001`）；`topicId` 只能取本片清单内的 id。

## 产出与自检（必须跑到末行 PASS）

把题目数组写到 `/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S10.json`（顶层就是数组），然后运行：

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/scripts/qd_check_bank.py /Users/a627692/Desktop/cn-k12-dxyc2286/data/math-qd/_bank/S10.json --allow=qdm_p058,qdm_p059,qdm_p060,qdm_p061,qdm_p062,qdm_p063,qdm_p064,qdm_p065,qdm_p066,qdm_p067
```

有 FAIL 就按提示改 JSON 再跑，直到末行打印 `PASS`。

## 汇报（一句话）

分片 S10 / 题数 / 难度分布 / 答案位分布 / checker 末行。
