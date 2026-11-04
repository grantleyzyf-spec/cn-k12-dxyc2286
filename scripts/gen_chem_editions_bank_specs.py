# -*- coding: utf-8 -*-
"""为两个化学版本桶生成题库派单分片（一点一片）。

产物：data/<bucket>/_bank_spec/B<NN>.json ＋ 同目录 CONTRACT.md
用法：python3 scripts/gen_chem_editions_bank_specs.py
"""
import json, os, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
BUCKETS = {
    'chemistry-lujiao': {'unit': 5, 'lesson': 8, 'label': '鲁教版初中化学'},
    'chemistry-luke': {'unit': 5, 'lesson': 8, 'label': '鲁科版高中化学'},
    'chemistry-sujiao': {'unit': 5, 'lesson': 8, 'label': '苏教版高中化学'},
    'chemistry-hukeji': {'unit': 5, 'lesson': 8, 'label': '沪科技版高中化学'},
    'chemistry-yuejiao': {'unit': 5, 'lesson': 8, 'label': '科学粤教版初中化学'},
    'chemistry-kepu': {'unit': 5, 'lesson': 8, 'label': '科普版初中化学'},
    'chemistry-bj': {'unit': 5, 'lesson': 8, 'label': '北京版初中化学'},
}

CONTRACT = """# 化学版本桶题库合同（一点一片，逐字照做）

## 你的任务
读本目录给你的分片 JSON（`B<NN>.json`），为其中**每一个知识点**写指定数量的诊断题，
写成对象形状 `{"shard": "<片号>", "bucket": "<桶名>", "questions": [ … ]}` 落盘到分片里写的 `out` 路径。

## 题量（硬指标，多一道少一道都算不合格）
- `level=unit`（单元/章上位点）：**恰好 5 题**
- `level=lesson`（节/课题）：**恰好 8 题**

## 题型与难度（硬指标）
- choice（选择题）≥3（5 题片 ≥2）、fill（填空题）≥2（5 题片 ≥1）、short-answer ≥1、numeric ≤1
- 三档难度 `basic / standard / hard` **每点各 ≥1 道**
- 选择题必须 4 个选项、`choices` 与 `options` 逐字同构、`answer` 是字母且在 label 内
- 填空题 `answer` 用文字，题干里必须有 `____`（四个下划线）
- numeric 题必须给 `verify`：**纯算术表达式**，只许数字与 + - * / ( ) ** ，⛔ 不许 `int()`/`round()`/单位/文字；`eval(verify)` 的结果必须等于 `answer`
- short-answer 的 `answer` 用「；」分 2–3 条要点

## 字段（逐字照这个键名，不许增删）
```json
{
  "id": "<topicId>_q01",
  "topicId": "<片里给的 topicId>",
  "subject": "<桶名>",
  "type": "choice|fill|short-answer|numeric",
  "difficulty": "basic|standard|hard",
  "prompt": "题干（≥12 字，选择题结尾要有（　））",
  "options": [{"label": "A", "text": "…"}, …]    // 非选择题写 []
  "choices": [{"label": "A", "text": "…"}, …]    // 与 options 完全相同
  "answer": "B 或文字答案",
  "explanation": "解析（≥25 汉字，说明为什么，结尾写「故选 X」或给出答案依据）",
  "verify": "数值题的算式，其它题不写这个键"
}
```
题号 `id` 由父代分配（片里 `id_range` 给出），⛔ 不许自己续号、不许跳号。

## 内容要求
- 只考**本知识点**：`chapter` 与 `description` 写明范围，超纲（考到别的节的内容）算不合格。
- 二年级以上口径：化学方程式、符号、单位写规范；元素符号大小写正确（如 H₂O、CO₂ 用普通文本 H2O、CO2 也可）。
- 干扰项要像真的错的（常见错误、相近概念），⛔ 禁「以上都不对」「无法确定」「仅在大学学习」这类凑数项。
- 禁 Markdown 标记（**、##、表格竖线）；成对绝对值 `|x|` 除外。

## 自检（写完必须跑，输出贴进汇报）
```bash
python3 scripts/check_chem_editions_bank.py --shard <你的 out 路径>
```
必须看到 `RESULT: PASS`。不 PASS 就改到达标，⛔ 不要改 checker。

## 落盘
- 只写自己的 `out` 路径，⛔ 不要动 `topics.json`、`questions.json`、别人的分片、技能库文件。
- 写完在汇报里贴：点数、题数、每题题型分布、三档难度分布、自检末行。
"""


def main():
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    for bucket, cfg in BUCKETS.items():
        if only and bucket not in only:
            continue
        d = os.path.join(DATA, bucket, '_bank_spec')
        os.makedirs(d, exist_ok=True)
        p_topics = os.path.join(DATA, bucket, 'topics.json')
        if not os.path.isfile(p_topics):
            print(f'{bucket} 无 topics.json，跳过')
            continue
        topics = json.load(open(p_topics, encoding='utf-8'))
        io.open(os.path.join(d, 'CONTRACT.md'), 'w', encoding='utf-8').write(CONTRACT)
        n = 0
        for t in topics:
            n += 1
            need = cfg['unit'] if t['level'] == 'unit' else cfg['lesson']
            sid = 'B%02d' % n
            spec = {
                'shard': sid, 'bucket': bucket, 'label': cfg['label'],
                'out': os.path.join(DATA, bucket, '_bank', '%s_out.json' % sid),
                'points': [{
                    'topicId': t['id'], 'name': t['name'], 'level': t['level'],
                    'chapter': t['chapter'], 'domain': t['domain'], 'grade': t['grade'],
                    'description': t['description'], 'mastery_criteria': t['mastery_criteria'],
                    'need': need, 'id_range': ['%s_q%02d' % (t['id'], i) for i in range(1, need + 1)],
                }],
            }
            json.dump(spec, open(os.path.join(d, sid + '.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
        print(bucket, '分片', n, '（unit 片 %d、lesson 片 %d）' % (
            sum(1 for t in topics if t['level'] == 'unit'),
            sum(1 for t in topics if t['level'] == 'lesson')))


if __name__ == '__main__':
    main()
