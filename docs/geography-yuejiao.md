# 地理（粤教粤人版）知识图谱桶说明

> 桶名：`geography-yuejiao`｜版本：粤教粤人版（广东教育出版社·广东人民出版社，2024–2025 版）
> 学段：初中 七、八年级（本社高中地理教材不在教材库内，本桶不覆盖高中）
> 结构源：`~/Desktop/中小学教材/中小学教材/地理/初中/粤教粤人版/` 下 19 份「大单元整体教学设计」docx 的第十五部分（课时设计），并与已产出的分课时 docx 逐条核对

## 1. 规模

| 层 | 数量 | 说明 |
| --- | ---: | --- |
| 知识点 | **171** | 19 个单元点 + 152 个课时点（每单元 8 课时） |
| 诊断题 | **1311** | 课时点 8 题/点、单元点 5 题/点 |
| 先修边 | 133 | 同单元课时链（hard），单元点不挂先修 |
| 试卷 | **35** | 19 单元卷 + 每册期中 A/B、期末 A/B（4 册 × 4 = 16） |
| 学层精讲 | **152** | 逐课时一篇 |
| 试卷讲解 | **35** | 逐卷一份 |

按册：

| 册 | 单元 | 课时 | 点 | 题 | 卷 | 学层 | 讲解 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 七年级上册 | 5 | 40 | 45 | 345 | 9 | 40 | 9 |
| 七年级下册 | 4 | 32 | 36 | 276 | 8 | 32 | 8 |
| 八年级上册 | 5 | 40 | 45 | 345 | 9 | 40 | 9 |
| 八年级下册 | 5 | 40 | 45 | 345 | 9 | 40 | 9 |

## 2. 单元与领域

| 册 | 单元 | 领域 |
| --- | --- | --- |
| 七上 | 一 地理工具与地理实践 / 二 地球的宇宙环境 / 三 地球的运动 | 地球与地图 |
| 七上 | 四 自然地理环境 / 五 人文地理环境 | 世界地理 |
| 七下 | 六 区域位置与特征 / 七 区域资源与经济 / 八 区域联系与合作 / 九 区域可持续发展 | 世界地理 |
| 八上 | 一 屹立世界的中国 / 二 自然环境与生态保护 / 三 自然资源与合理利用 / 四 产业分布与产业发展 / 五 灿烂的中华文化 | 中国地理 |
| 八下 | 六 中国的区域划分 / 七 区域位置与特征 / 八 区域资源与经济 / 九 区域联系与合作 / 十 建设美丽中国 | 中国地理 |

领域只用《义务教育地理课程标准（2022 年版 2025 年修订）》的四个名称（地球与地图 / 世界地理 / 中国地理 / 乡土地理）。
分布：地球与地图 27、世界地理 54、中国地理 90、乡土地理 0 —— 本套教材未单设乡土地理单元，**这是教材事实，不是缺口**。

## 3. 口径

- `chapter`：单元点写「<册> 第N单元 <单元名>」；课时点同串再 ` · <课时名>`。册名与「第N单元」之间**一个空格**，单元号用中文数字。
- 课标挂标：每点 3–5 条，`id` 沿 `geo-2022:4.NR.xx` 体系；引文逐字取自课标 TXT，`test_geo_yuejiao.py` 做去空白子串回表，**100% 命中**。本桶新起 19 条 `geo-2022:4.NR.66–84`（宇宙环境、太空探索、文化景观等义教课标有原文但既有桶未收录的条目）。
- 题量：课时点**恰好 8 题**（4 选择 + 2 填空 + 1 简答 + 1 数值）、单元点**恰好 5 题**（2 选择 + 1 填空 + 1 数值 + 1 简答）；难度三档全覆盖；数值题带纯算术 `verify`。
- 试卷：初中 **120 分 / 120 分钟**，24 题 = 选择 18×3 + 综合 6×11；单元卷覆盖本单元 9 个点各 ≥1 次；与题库题干相似度 < 0.85；答案位 A–D 各 ≥15%。
- 学层：七段固定标题（开场 / 课本原文 / 费曼翻译 / 例题精讲 / 易错点拨 / 五步学习法 / 自查清单），1200–2800 汉字，`> ` 引文逐字回表，五步学习法五条固定说法。
- 讲解：六段（这份卷在考什么 / 考点地图 / 逐题精讲 / 整卷复盘 / 五步学习法 / 自查清单），4000–7800 汉字，24 题逐题四要素（思路 / 关键一步 / 易错）。

## 4. 门禁

```bash
cd ~/Desktop/cn-k12-dxyc2286

python3 scripts/test_geo_yuejiao.py                                   # 32 项不变量
python3 scripts/check_geo_yuejiao_bank.py data/geography-yuejiao/_bank/GYJ_B01.json
python3 scripts/check_geo_yuejiao_exam.py --all                       # 35 卷
python3 scripts/check_geo_yuejiao_learn.py --dir data/geography-yuejiao/learn
python3 scripts/check_exam_lecture.py --subject geography-yuejiao     # 35 份
```

## 5. 复现

```bash
python3 scripts/build_geo_yuejiao_outline.py          # docx → _outline.json
python3 scripts/build_geo_yuejiao_skeleton.py         # → topics / dependencies / _skeleton
python3 scripts/gen_geo_yuejiao_bank_shards.py        # 19 片
python3 scripts/gen_geo_yuejiao_exam_shards.py        # 35 卷 / 19 片
python3 scripts/gen_geo_yuejiao_learn_shards.py       # 38 片 / 152 篇

python3 scripts/merge_geo_yuejiao_bank.py             # 题库 + 点位正文回写
python3 scripts/merge_geo_yuejiao_learn.py            # 学层并按册合并

MATH_BUCKET=geography-yuejiao SUBJECT_NAME=地理 MATH_EDITION=粤教粤人版 python3 scripts/build_math_exam_docx.py
MATH_BUCKET=geography-yuejiao SUBJECT_NAME=地理 MATH_EDITION=粤教粤人版 python3 scripts/build_math_learn_docx.py
MATH_BUCKET=geography-yuejiao SUBJECT_NAME=地理 MATH_EDITION=粤教粤人版 python3 scripts/build_math_learn_booklet.py
MATH_BUCKET=geography-yuejiao SUBJECT_NAME=地理 MATH_EDITION=粤教粤人版 python3 scripts/build_exam_lecture_docx.py
```

## 6. 交付件

| 产物 | 路径 | 份数 |
| --- | --- | ---: |
| 试卷（卷 + 答案） | `~/Desktop/学科图谱相关资料/学科图谱原创试卷/地理/粤教粤人版/<册>/` | 70 |
| 学层精讲 | `~/Desktop/学科图谱相关资料/学层精讲/地理/粤教粤人版/<册>/` | 152 |
| 学层合订本 | 同上 `_合订本/` | 4 |
| 试卷讲解 | `~/Desktop/学科图谱相关资料/试卷讲解/地理/粤教粤人版/<册>/` | 35 |

## 7. 已知边界

- 无高中册：教材库 `地理/高中/` 下没有粤教粤人版，故本桶只到八年级。
- 无乡土地理独立单元：见 §2。
- 「主题活动」并入所属单元最后一个课时（教材体例如此），不单独建点、不单独出卷。
