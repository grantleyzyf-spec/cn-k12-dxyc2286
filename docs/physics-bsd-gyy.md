# 物理（北师大版·郭玉英）知识图谱桶

## 规模（2026-11-06 建成）

| 层 | 读数 |
|---|---|
| 册 | 3（八年级上册 / 八年级下册 / 九年级全一册） |
| 知识点 | 99 = 16 章级（unit）+ 83 节级（lesson） |
| 先修边 | 67（同章内按节顺链，每章起始课时带 `root_reason`） |
| 领域 | 物质 10 / 运动和相互作用 52 / 能量 17 / 实验探究 8 / 跨学科实践 12 |
| 诊断题 | 744（选择 342 / 填空 200 / 简答 120 / 数值 82；basic 216 / standard 328 / hard 200） |
| 试卷 | 28 卷 / 672 题（16 章卷 + 3 册 × 期中 A/B + 期末 A/B） |
| 学层精讲 | 83 篇 / 190,191 汉字 |
| 试卷讲解 | 28 份 |

## 结构源

三册教材 PDF 均无文字层（541 页）。结构以**目录页视觉逐字抄录**为准（八上 p5–p6、八下 p3–p4、九全 p3–p4），
章号/章名/节号/节名/页码一律以图片为准；`build_pgy_skeleton.py` 里的 `STRUCT` 常量即该抄录结果。
「整理与复习」「附录」「走进物理世界」不建点；设计/制作/调查/探寻/科普行类课时建点并归「跨学科实践」。

## 门禁

```bash
python3 scripts/validate.py physics-bsd-gyy          # 0 error
ajv validate -c ajv-formats -s data/schema-topic.json -d data/physics-bsd-gyy/topics.json
python3 scripts/test_physics_bsd_gyy.py              # 40/40
python3 scripts/check_pgy_bank.py --all              # 99 片
python3 scripts/check_pgy_exam.py --all              # 28 卷
python3 scripts/check_pgy_learn.py --all             # 83 篇
python3 scripts/check_pgy_lecture.py --all           # 28 份
```

## 脚本

- `build_pgy_skeleton.py` — 结构表 → topics / dependencies / _skeleton / _toc
- `gen_pgy_bank_shards.py` + `check_pgy_bank.py` + `merge_pgy_bank.py` — 一点一片的题库产线（题号父代预分配）
- `gen_pgy_exam_specs.py` + `check_pgy_exam.py` — 28 卷规格与逐卷门禁
- `gen_pgy_learn_shards.py` + `check_pgy_learn.py` + `merge_pgy_learn.py` — 学层 83 篇
- `check_pgy_lecture.py` — 讲解门禁（本桶卷面 `items` 在顶层，通用 `check_exam_lecture.py` 不适用）

## 已知瑕疵

- 学层 83 篇里 12 篇的 `excerpt` 切片错位（章首导语/插图标注提到节名导致早切）；成稿引文改从本册同一节取，
  逐字回表仍通过，内容无误。切片器判据待改：命中点后 200 字内不得含 `/页码` 形态。
- 卷面无 `difficulty` 字段，讲解中不写难度分布数字（改按题型结构与分值实述）。
