# -*- coding: utf-8 -*-
"""为两个化学版本桶生成「试卷」派单分片（一卷一片）。

卷制（写死在生成器，不现算）：
  初中（九上/九下）：24 题 / 120 分 / 120 分钟
    一、选择题        12 × 3 = 36
    二、填空与简答     6 × 6 = 36
    三、实验探究       2 × 12 = 24
    四、综合计算       2 × 12 = 24
  高中（必修/选择性必修）：21 题 / 150 分 / 150 分钟
    一、单项选择      10 × 4 = 40
    二、不定项选择     3 × 4 = 12
    三、填空与简答     4 × 7 = 28
    四、实验探究       2 × 15 = 30
    五、综合计算       2 × 20 = 40

卷数 ＝ 单元/章数 ＋ 4 × 册数（每册期中 A/B ＋ 期末 A/B）。
产物：data/<bucket>/_exam_spec/<EID>.json ＋ CONTRACT.md
"""
import json, math, os, re, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

BOOK_CODE = {
    '九年级上册': '9a', '九年级下册': '9b',
    '必修第一册': 'b1', '必修第二册': 'b2',
    '选择性必修第一册': 'x1', '选择性必修第二册': 'x2', '选择性必修第三册': 'x3',
}
CN = '零一二三四五六七八九十'
def cn(n):
    if n <= 10: return CN[n]
    if n < 20: return '十' + CN[n - 10]
    return CN[n // 10] + '十' + (CN[n % 10] if n % 10 else '')

STRUCT = {
    'junior': [('一、选择题', 'choice', 12, 3), ('二、填空与简答', 'fill', 6, 6),
               ('三、实验探究', 'experiment', 2, 12), ('四、综合计算', 'calc', 2, 12)],
    'senior': [('一、单项选择', 'choice', 10, 4), ('二、不定项选择', 'multi', 3, 4),
               ('三、填空与简答', 'fill', 4, 7), ('四、实验探究', 'experiment', 2, 15),
               ('五、综合计算', 'calc', 2, 20)],
}
TOTAL = {'junior': (24, 120, 120), 'senior': (21, 150, 150)}

CONTRACT = """# 化学版本桶「试卷」合同（一卷一片）

## 你的任务
读本目录给你的分片 JSON（`<examId>.json`），按其中 `sections` 的结构与分值写**一整份试卷**，
写成对象形状落盘到片内 `out` 路径。

## 卷面结构（逐字照分片的 sections，不许增删题目数、不许改分值）
- 分片里每个 section 给了 `title` / `type` / `count` / `score_each` / `score_total`，
  成品里写成 `{"title": "...", "rule": "每小题 X 分，共 Y 分", "type": "...", "items": [...]}`。
- `items[].no` 从 1 连续编号；`items[].itemId` = `<examId>_qNN`（两位，父代已给范围）。
- 每题必须带 `topicIds`（数组，取自分片 `points` 里的 topicId，1–2 个），`score`、`stem`、`answer`、`analysis`。
- 选择题另带 `options`（A/B/C/D 四项）；`answer` 是字母。多选题 `answer` 用「AB」这种多字母组合。
- 实验探究 / 综合计算题：`answer` 给结论与关键数值，`analysis` 写清步骤，`scoreRule` 可选（写了就必须各步之和＝题分）。

## 覆盖（硬指标）
- 单元卷：本单元**每个课时点至少被 1 道题引用**（`topicIds` 并集 ⊇ 该单元全部 lesson 点）。
- 期中卷：覆盖分片 `scope` 里的单元（每单元 ≥2 题）。
- 期末卷：覆盖全册（每单元 ≥2 题）。

## 原创性
- ⛔ 不许照抄题库题干：与 `questions.json` 里任何题干的相似度必须 < 0.85，同一点换情境、换数据、换设问。

## 字段（逐字照键名）
```json
{
  "examId": "...", "kind": "unit|mid|fin", "paper": "...", "book": "...",
  "stage": "初中|高中", "term": "上|下", "grade": 9或10-12,
  "duration": 120, "fullScore": 120,
  "scope": ["<单元 chapter 串>", ...],
  "sections": [
    {"title": "一、选择题", "rule": "每小题 3 分，共 36 分", "type": "choice",
     "items": [{"no": 1, "itemId": "<examId>_q01", "type": "choice", "difficulty": "basic",
                "topicIds": ["clj_j001"], "score": 3,
                "stem": "题干（≥12 字，选择题结尾（　））",
                "options": [{"label":"A","text":"…"}, …],
                "answer": "B",
                "analysis": "解析（≥25 汉字，说明为什么，结尾「故选 B」）"}]}
  ]
}
```

## 自检（写完必须跑，输出贴进汇报）
```bash
python3 scripts/check_chem_editions_exam.py --exam <你的 out 路径>
```
必须 `RESULT: PASS`。⛔ 不许改 checker。

## 落盘
只写片内 `out`；⛔ 不动 topics.json / questions.json / 别人的卷 / 技能库。
"""


def main():
    targets = [('chemistry-lujiao', 'junior', '初中'),
               ('chemistry-luke', 'senior', '高中'),
               ('chemistry-sujiao', 'senior', '高中'),
               ('chemistry-yuejiao', 'junior', '初中'),
               ('chemistry-kepu', 'junior', '初中'),
               ('chemistry-hukeji', 'senior', '高中'),
               ('chemistry-bj', 'junior', '初中')]
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
        targets = [x for x in targets if x[0] == only]
    for bucket, stage_key, stage_name in targets:
        if not os.path.isfile(os.path.join(DATA, bucket, 'topics.json')):
            print(bucket, '无 topics.json，跳过')
            continue
        d = os.path.join(DATA, bucket, '_exam_spec')
        os.makedirs(d, exist_ok=True)
        io.open(os.path.join(d, 'CONTRACT.md'), 'w', encoding='utf-8').write(CONTRACT)
        topics = json.load(open(os.path.join(DATA, bucket, 'topics.json'), encoding='utf-8'))
        books = {}
        for t in topics:                      # 按册分组，保持册内顺序
            book = t['chapter'].split(' ')[0]
            books.setdefault(book, []).append(t)
        n = 0
        made = []
        for book, ts in books.items():
            grade = ts[0]['grade']; sem = ts[0]['semester']
            pre = {'chemistry-lujiao': 'clj_exam_', 'chemistry-luke': 'clk_exam_',
                   'chemistry-sujiao': 'csj_exam_', 'chemistry-kepu': 'ckp_exam_',
                   'chemistry-yuejiao': 'cyj_exam_', 'chemistry-hukeji': 'chk_exam_',
                   'chemistry-bj': 'cbj_exam_'}[bucket]
            code = BOOK_CODE.get(book) or ('k%02d' % (len(made) + 1))
            units = []
            for t in ts:
                if t['level'] == 'unit':
                    m = re.search(r'第(\d+)(单元|章|专题)', t['chapter'])
                    units.append((int(m.group(1)) if m else len(units) + 1, t))
            made.append((ts, book, grade, sem, units, pre, code))
        for ts, book, grade, sem, units, pre, code in made:
            jobs = []
            for no, topic in units:
                jobs.append(('unit', (no, topic), None))
            half = math.ceil(len(units) / 2)
            for kind, sc_units in (('mid', units[:half]), ('fin', units)):
                for letter in ('A', 'B'):
                    jobs.append((kind, sc_units, letter))
            for kind, u, letter in jobs:
                n += 1
                if kind == 'unit':
                    eid = '%s%s_u%02d' % (pre, code, u[0])
                    paper = u[1]['chapter'].split(' ', 1)[1] + ' 测试卷'
                    scope = [u[1]['chapter']]
                    owners = [x for x in ts if x['chapter'] == u[1]['chapter']
                              or x['chapter'].startswith(u[1]['chapter'] + ' · ')]
                else:
                    eid = '%s%s_%s%s' % (pre, code, 'qz' if kind == 'mid' else 'qm', letter.lower())
                    paper = ('期中' if kind == 'mid' else '期末') + '测试卷' + letter
                    scope = [x[1]['chapter'] for x in u]
                    owners = [x for x in ts if any(x['chapter'] == sc or x['chapter'].startswith(sc + ' · ')
                                                   for sc in scope)]
                tn, fs, dur = TOTAL[stage_key]
                secs = []
                q = 0
                for title, typ, cnt, each in STRUCT[stage_key]:
                    secs.append({'title': title, 'type': typ, 'count': cnt,
                                 'score_each': each, 'score_total': cnt * each,
                                 'id_range': ['%s_q%02d' % (eid, q + i + 1) for i in range(cnt)]})
                    q += cnt
                spec = {
                    'examId': eid, 'kind': kind, 'paper': paper, 'book': book,
                    'stage': stage_name, 'term': sem, 'grade': grade,
                    'duration': dur, 'fullScore': fs, 'scope': scope,
                    'out': os.path.join(DATA, bucket, 'exams', book, paper + '.json'),
                    'sections': secs,
                    'points': [{'topicId': x['id'], 'name': x['name'], 'level': x['level'],
                                'chapter': x['chapter'], 'description': x['description']}
                               for x in owners],
                    'must_cover': [x['id'] for x in owners if x['level'] == 'lesson'] if kind == 'unit'
                                  else [x['id'] for x in owners],
                }
                json.dump(spec, open(os.path.join(d, eid + '.json'), 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=1)
        print(bucket, '卷数', n)


if __name__ == '__main__':
    main()
