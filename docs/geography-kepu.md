# 地理 · 科普版（`geography-kepu`）

科学普及出版社（北京市仁爱教育研究所编著）义务教育教科书·地理，2024 版（2025.7 重印），初中四册。

## 规模（2026-11-04 实测）

| 项 | 数 |
|---|---|
| 册 | 4（七上 / 七下 / 八上 / 八下） |
| 单元 | 16 |
| 课时点 | 128 |
| 知识点合计 | 144（单元 16 ＋ 课时 128） |
| 先修边 | 255（同单元串联 ＋ 跨单元接上一单元末课时） |
| 题库 | 1104 题（课时点 8 题、单元点 5 题） |
| 试卷 | 32 卷（16 单元卷 ＋ 4 册 × 期中 A/B、期末 A/B） |
| 学层精讲 | 128 篇 |
| 试卷讲解 | 32 份 |
| 课标 | 144/144 挂标（借人教版同条课标句，confidence=partial，回表 100%） |

## 结构源

- 七上 / 八上：`各学科分课时设计/地理/科普版/初中/<册>/*分课时教学设计*.docx`（文件名自证课时名）
- 七下 / 八下：`地理/初中/科普版/*大单元整体教学设计*.docx` 的「十五、教-学-评一致性课时设计」段（取最后一次出现）
- 教材正文：四册为扫描件，用 macOS Vision OCR（`pdf_pages_vision_ocr.py`，300dpi）抽文本包到 `_text/<册>.txt`

## 单元表

| 册 | 单元 | 领域 |
|---|---|---|
| 七年级上册 | 一 认识地球探宇宙 / 二 地球运动永不息 | 地球与地图 |
| 七年级上册 | 三 海陆分布蕴变迁 / 四 气象万千多绚丽 / 五 多元文化共发展 | 世界地理 |
| 七年级下册 | 一 认识我们所在的大洲 / 二 了解特色鲜明的地区 / 三 走进多种多样的国家 | 世界地理 |
| 八年级上册 | 一 了解祖国的概况 / 二 走进祖国的大自然 / 三 探寻祖国的自然资源 / 四 认识祖国的产业特征 | 中国地理 |
| 八年级下册 | 一 认识四大区域 / 二 探寻不同尺度的区域 / 三 走进北京和港澳台 / 四 行稳致远的中国 | 中国地理 |

⛔ 领域只用义教地理四领域（地球与地图 / 世界地理 / 中国地理 / 乡土地理），不写「地球与宇宙」「地图与地理工具」这类内容标题当领域。
教材的「跨学科主题学习 编制二十四节气绘本」（2 课时）**不建点、不出卷**，与活动课同口径。

## 门禁

```bash
python3 scripts/test_geo_kepu.py                       # 数据不变量（31 项）
python3 scripts/validate.py geography-kepu              # schema 校验
python3 scripts/check_geo_kepu_bank.py <分片>           # 题库分片
python3 scripts/check_geo_kepu_exam.py --all            # 32 卷
python3 scripts/check_geo_kepu_learn.py --dir data/geography-kepu/learn/_parts
python3 scripts/check_exam_lecture.py --subject geography-kepu
```

## 管线脚本（克隆自湘教版，改桶名/前缀/章→单元）

`build_skeleton.py`（在 `/tmp/kp/`，可按需重建骨架）、`gen_geo_kepu_bank_shards.py`、`merge_geo_kepu_bank.py`、
`gen_geo_kepu_exam_shards.py`、`gen_geo_kepu_learn_shards.py`、`merge_geo_kepu_learn.py`、`gen_geo_kepu_lecture_shards.py`、
`check_geo_kepu_{bank,exam,learn}.py`、`test_geo_kepu.py`。

## 交付件

`~/Desktop/学科图谱相关资料/{学层精讲,学科图谱原创试卷,试卷讲解}/地理/科普版/<册>/`

## 已知口径

- 试卷 `scoreRule` 必须是**字符串数组**（`"答出……，4 分"`），对象型会让 checker 与站点渲染崩。
- 讲解考点地图按 `items[].score` 现算；一题挂多点导致各行相加超满分时，须写明「一题挂多点，看单行就行」。
- 教材 OCR 有形近误字（钓/吹洲/准河 等），学层引文只取连续干净整句，⛔ 不照抄错字、也不自造原文。
