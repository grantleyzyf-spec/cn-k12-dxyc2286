#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版（郭玉英）初中物理 题库分片生成器（一点一片）。

口径（与 check_pgy_bank.py 完全一致，改一处必须同步另一处）：
  · 课时点 8 题 / 单元点 5 题（恰好，不是 ≥）
  · 题型配额：8 题片 choice≥3 / fill≥2 / short-answer≥1 / numeric≤1；5 题片 choice≥2 / fill≥1 / short-answer≥1
  · 难度三档 basic / standard / hard 每点必齐
  · 选择题 4 项、选项互异；非选择题 options=[]
  · 解析 ≥25 汉字；题干 ≥12 字；禁 Markdown
id 由本脚本预分配（工位不得自行续号）：pgy_q0001 起，连续。

产物：data/physics-bsd-gyy/_bank_spec/{S01…}.json ＋ 同目录 CONTRACT.md
用法：python3 scripts/gen_pgy_bank_shards.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
SPEC = os.path.join(D, '_bank_spec')
OUT = os.path.join(D, '_bank')

CONTRACT = """# 北师大版（郭玉英）初中物理 · 题库分片合同

## 你要写什么
读本目录下的 `{SID}.json`（作业单），按其中 `items[]` 逐个知识点写题，落盘到：

    {bucket}/_bank/{SID}_out.json

⛔ 只写这一个文件。其他桶（`physics`、`physics-bsd-lcm`、`physics-sk`、`physics-yj`）的同名分片禁止读写。

## 题量（恰好，不多不少）
- `level = "lesson"` 的点：**8 题**
- `level = "unit"` 的点：**5 题**
逐点核对，作业单里 `need` 字段已写明。

## 题型配额（逐点核）
8 题点：`choice ≥ 3`、`fill ≥ 2`、`short-answer ≥ 1`、`numeric ≤ 1`
5 题点：`choice ≥ 2`、`fill ≥ 1`、`short-answer ≥ 1`、`numeric ≤ 1`
`type` 只认：`choice` / `fill` / `short-answer` / `numeric`（写别的直接判红）。

## 难度（逐点核）
`basic` / `standard` / `hard` **每点各 ≥1**，`difficulty` 只认这三个值。

## 字段
```json
{
  "shard": "{SID}",
  "topics": [{"topicId": "pgy_j001", "type": "conceptual",
              "description": "40–90 汉字的实体描述（点名本节概念/规律/实验）",
              "mastery_criteria": ["…", "…"],
              "diagnostic_question": {"question": "…", "answer": "A"}}],
  "questions": [{
    "id": "pgy_q0001",
    "topicId": "pgy_j001",
    "prompt": "题干（≥12 字，完整问句）",
    "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},
                {"label":"C","text":"…"},{"label":"D","text":"…"}],
    "answer": "B",
    "type": "choice",
    "difficulty": "basic",
    "explanation": "解析（≥25 汉字，说清为什么，选择题要点明干扰项错在哪）"
  }]
}
```
- 选择题：`options` 恰好 4 项、文本互异、`answer` 必须是 A/B/C/D 之一。
- 填空/简答/数值题：`options` 写 `[]`；填空题干必须含 `____`；数值题 `answer` 只写数字，另带
  `verify`（**纯算术表达式**，门禁 `eval(verify, {"__builtins__":{}}, {})` 必须等于 answer；
  ⛔ 不许写 `int()`/`round()`/`sqrt()`，根号写 `**0.5`）。
- 简答题 `answer` 用「；」分 2–3 条。
- 物理符号：用 `×` `÷` `＋` `－` `＝`，单位用汉字或标准符号（`N`、`kg/m³`、`Ω`、`V`、`A`、`J`、`W`、`Pa`），
  不写 LaTeX、不写 `$…$`、不写 HTML。
- ⛔ 禁 Markdown：不加 `**`、`##`、表格竖线。
- ⛔ 禁凑数干扰项：「以上都不对」「无法确定」「仅在大学学习」一律不许。
- ⛔ 每点内不得出现两道题干雷同的题（换个数字也算雷同）；也不要抄作业单里 `description` 的原句当题干。

## 自检（落盘后必须跑，把最后一行贴进汇报）
```
python3 scripts/check_pgy_bank.py --shard {bucket}/_bank/{SID}_out.json
```
最后一行必须是 `RESULT: PASS`。红了就地改，不要重派。
"""


def main():
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    os.makedirs(SPEC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    qid = 0
    shards = []
    for i, t in enumerate(topics, 1):
        sid = 'S%03d' % i
        need = 8 if t['level'] == 'lesson' else 5
        ids = []
        for _ in range(need):
            qid += 1
            ids.append('pgy_q%04d' % qid)
        shard = {
            'shard': sid,
            'items': [{
                'topicId': t['id'], 'name': t['name'], 'level': t['level'],
                'chapter': t['chapter'], 'grade': t['grade'], 'domain': t['domain'],
                'description': t['description'], 'mastery_criteria': t['mastery_criteria'],
                'standards': [{'id': s['id'], 'quote': s['quote']} for s in t['standards'][:2]],
                'need': need,
            }],
            'id_range': ids,
            'out': '%s/_bank/%s_out.json' % (D, sid),
        }
        p = os.path.join(SPEC, sid + '.json')
        json.dump(shard, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        shards.append(shard)

    # ⛔ 不用 str.format：合同里有 JSON 花括号
    open(os.path.join(SPEC, 'CONTRACT.md'), 'w', encoding='utf-8').write(
        CONTRACT.replace('{SID}', 'S001').replace('{bucket}', D))
    total = sum(s['items'][0]['need'] for s in shards)
    print('分片 %d 个（lesson %d / unit %d），题位 %d 个'
          % (len(shards), sum(1 for s in shards if s['items'][0]['level'] == 'lesson'),
             sum(1 for s in shards if s['items'][0]['level'] == 'unit'), total))
    print('题号区间：%s … %s' % (shards[0]['id_range'][0], shards[-1]['id_range'][-1]))


if __name__ == '__main__':
    main()
