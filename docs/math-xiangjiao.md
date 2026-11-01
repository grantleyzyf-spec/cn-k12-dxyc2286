# 数学（湘教版）`math-xiangjiao`

湖南教育出版社义务教育教科书·数学（初中）与普通高中教科书·数学（湘教版）的知识图谱切片，独立学科代码 `math-xiangjiao`，知识点 id 前缀 `mxj_`。与人教版 `math`、北师大版 `math-bsd` 并列，互不覆盖。

## 规模（现算）

| 项 | 数 |
|---|---|
| 册 | 8（初中 5 + 高中 3） |
| 章／单元点 | 37 |
| 节／课时点 | 161 |
| 知识点合计 | **198** |
| 先修边 | 321（hard 314 · soft 7） |
| 诊断题 | **1,473**（选择 766 · 数值 299 · 填空 247 · 简答 161） |
| 难度 | basic 457 · standard 648 · hard 368 |
| 带课标引用 | 197/198（逐字 quote，去空白后回表 197/197） |

## 册次与分布

| 册 | 点 | 章 | 节 |
|---|---|---|---|
| 湘教版七年级上册 | 26 | 4 | 22 |
| 湘教版七年级下册 | 27 | 6 | 21 |
| 湘教版八年级上册 | 26 | 5 | 21 |
| 湘教版八年级下册 | 27 | 4 | 23 |
| 湘教版九年级上册 | 25 | 4 | 21 |
| 湘教版必修第一册 | 27 | 6 | 21 |
| 湘教版必修第二册 | 17 | 4 | 13 |
| 湘教版选择性必修第一册 | 23 | 4 | 19 |

（每册点数 = 章数 + 节数；上表「点」即 单元点 + 课时点。）

## 口径

- **章号按册内重新编号**（湘教版初中各册从第 1 章起），因此 `chapter` 一律写成 `湘教版七年级上册 第1章 有理数 · 认识负数`，册名不可从 `grade` 拼出。
- **节 = 教材小节**（`1.1`、`3.5` 这类编号），一章末的「小结与评价」「复习题」「数学文化」「数学实验」「多知道一点」「现代技术应用」「综合与实践」**不入点**。
- **领域**：义教段用课标四领域（数与代数 76 · 图形与几何 44 · 统计与概率 24），高中段用主线（函数 35 · 几何与代数 19 · 统计与概率并入 24）——两套口径按学段并存，不强行归一。
- **题型**：conceptual 81 · procedural 60 · reasoning 32 · application 14 · modeling 11。
- 册内「章包含节」与「节顺次」为 hard 边；册际衔接为 soft 边（7 条，覆盖 8 册首尾）。

## 已知缺口（不编造）

1. **小学 1–6 年级**：教材库中无湘教版小学数学，全部未建。
2. **九下**：库中无 PDF。
3. **选择性必修第二册**：库内 PDF（`9787553939704_…选择性必修第二册`）与必修第二册（`9787553972190_…必修第二册`）**逐页渲染像素完全相同**，判为同一册重复入库，未重复建点。
4. **选必三/四**：库中未见该社对应册。
5. **`mxj_p1022` 「角」** 无机读课标句可对（课标该处以「角」单字成词，2-gram 打分无命中），`standards` 留空。
6. **高中三册无逐页文本层**：PDF 使用自定义字形编码，`get_text()` 出来是 ASCII 乱码；目录由视觉模型逐页抄录（`/tmp/mxj/vlm/*_merged.json`），正文靠本地 RapidOCR 逐页识别（`/tmp/mxj2/mxjh*/ocr/`）供校对。

## 自检与生成链

```bash
cd ~/Desktop/cn-k12-dxyc2286

# 1 目录（初中：按字号识别正文标题；高中：vision 目录页）
python3 /tmp/mxj_extract_chuzhong_v7.py        # → /tmp/mxj/toc_chuzhong.json
python3 /tmp/mxj_high_to_skeleton.py           # → /tmp/mxj2/mxjh*.json
python3 /tmp/mxj_to_skeleton_input.py          # → /tmp/mxj2/mxj7a…mxj9a.json
python3 /tmp/mxj_textpack.py mxj7a mxj7b mxj8a mxj8b mxj9a   # 逐页文本包

# 2 结构
python3 data/math-xiangjiao/_scripts/build_skeleton.py --subject math-xiangjiao

# 3 内容与题库（每册一个工位，规范见 _scripts/WORKER.md）
python3 data/math-xiangjiao/_scripts/check_bank_sj.py mxj7a --subject math-xiangjiao

# 4 合并 + 课标回表
python3 data/math-xiangjiao/_scripts/merge_bank.py --subject math-xiangjiao
python3 data/math-xiangjiao/_scripts/map_standards.py --subject math-xiangjiao

# 5 聚合与索引
python3 /tmp/mxj_merge_aggregate.py
python3 scripts/build_standards_index.py

# 6 门禁
python3 scripts/validate.py math-xiangjiao     # Total Errors: 0
python3 scripts/test_math_xiangjiao.py         # 37/37 PASSED
```

## 页面用法

- 浏览：`/explore/?subject=math-xiangjiao`（下拉「📐 数学（湘教版）」）
- 诊断：`/diagnose/?subject=math-xiangjiao&topic=mxj_p1001`
- 册次筛选：`?book=湘教版七年级上册`（册名直接来自 `chapter`，不再由 `grade` 拼字符串）

## 备注

- 题量与难度在册内**每点三档齐备**（basic/standard/hard 各至少 1 题），单元点 5 题、课时点 8 题。
- 高中三册的题目在本地 OCR 完成后做过一轮「情境与结论是否见于教材」的抽查；凡教材无依据的表述已改，不改者删除。
