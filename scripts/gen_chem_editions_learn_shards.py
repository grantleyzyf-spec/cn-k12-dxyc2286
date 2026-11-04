# -*- coding: utf-8 -*-
"""鲁教/鲁科学层精讲：分片生成 + 合同文档。

用法：python3 scripts/gen_chem_editions_learn_shards.py <chemistry-lujiao|chemistry-luke>
每片 2 篇（同册不跨片），只覆盖 level=lesson 的点；out 目录按册分。
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = sys.argv[1] if len(sys.argv) > 1 else 'chemistry-lujiao'
D = os.path.join(REPO, 'data', BUCKET)
SD = os.path.join(D, '_learn_shards')
os.makedirs(SD, exist_ok=True)

CONTRACT = """# 学层精讲合同（{bucket}）

## 你的任务
分片 JSON 里给了 1–2 个课时点（`lessons[]`），为**每一个点**写一篇学生自己能读懂的精讲，
写成 `{{"book": "<册>", "lessons": [{{"topicId","title","markdown","words"}}]}}`，
落盘到该点自己的 `out` 路径（`learn/_parts/<册>/<topicId>.json`，一片多篇就一题一文件）。

## 七节（标题逐字、顺序固定）
1. `## 一、开场` —— 从学生见过的现象或实验室场景切入，一两句把这一课要解决的问题摆出来。
2. `## 二、课本原文` —— **至少 2 处** `> ` 块引用，**逐字抄本册教材**（每处 ≥8 汉字），
   每处后面紧跟「这句话的意思是……」。⛔ 引文必须能在 `data/<bucket>/_text/<册>.txt` 里逐字命中
   （机检前 24 字），不许改写、不许拼接、不许凭印象编。可先用 `grep` 查原文。
3. `## 三、费曼翻译` —— 「假设你要给同桌讲明白」的口吻，把概念翻成大白话＋一个生活类比；
   写清为什么要这样规定、不这样规定会出什么问题。
4. `## 四、例题精讲` —— **2 道**（「例 1」「例 2」），每道按「审题 → 第一步 → 第二步 → 答案 → 回头看」写，
   每道至少一处 `❌ 常见错法` 与 `✅ 正确做法`。例题优先用本点题库题的同型变式（分片给了 `bank_samples`）。
   化学计算必须**自己复算一遍**数值。
5. `## 五、易错点拨` —— 至少 2 条，每条写「错在哪 → 为什么错 → 怎么防」。
6. `## 六、五步学习法` —— 5 条，条与条之间空一行，顺序固定、每条 ≥25 汉字，且必须结合本知识点具体化：
   ①每天锻炼一个小时 ②扎实掌握第一个知识点 ③能积微者速成 ④运用对标思维突破学习困境 ⑤运用杠铃法则缓解学习疲劳。
   **每条 65–120 汉字**（五条合计须 ≥350，只写一句话会卡在字数门上）。
7. `## 七、方法锚与自查` —— 一句加粗「方法锚」（以后遇到同类题从哪下手）＋ `- [ ]` 自查题 **≥3 条**（可判定）。

## 硬指标（checker 逐条断言）
- 全篇汉字 **1200–2800**；「六、五步学习法」节 **350–900** 汉字；`words` 写实测汉字数（差 ≤10）。
- 例题 ≥2 道、「❌」「✅」各 ≥2 处；七节标题齐全且顺序正确；自查 `- [ ]` ≥3。
- 禁用 LaTeX（`$…$`）、HTML 标签、Markdown 表格（`|`）、「如图／下图」式指代。
- 禁教师语域与套话：教学目标、考点、命题趋势、首先、其次、综上所述、总而言之、由此可见、赋能、抓手、闭环、值得注意的是。
- 只讲本课时，不提前教后面课时的解法（可提一句「后面会学」但不展开）。

## 自检（必须跑到 PASS）
```bash
python3 scripts/check_chem_editions_learn.py --bucket {bucket} --file <你做的那篇 json>
# 期望末行：RESULT: PASS
```
⛔ 不许改 checker；只写自己的 out 路径，不动 topics.json / questions.json / 别人分片。
"""


def main():
    open(os.path.join(SD, 'CONTRACT.md'), 'w', encoding='utf-8').write(CONTRACT.format(bucket=BUCKET))
    T = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    Q = json.load(open(os.path.join(D, 'questions.json'), encoding='utf-8'))
    by_q = {}
    for q in Q:
        by_q.setdefault(q['topicId'], []).append(q)
    by_book = {}
    for t in T:
        if t['level'] == 'lesson':
            by_book.setdefault(t['chapter'].split(' ')[0], []).append(t)
    idx, n = [], 0
    for book, pts in by_book.items():
        for i in range(0, len(pts), 2):
            grp = pts[i:i + 2]
            n += 1
            tag = 'L%02d' % n
            payload = {
                'shard': tag, 'bucket': BUCKET, 'book': book,
                'text_file': 'data/%s/_text/%s.txt' % (BUCKET, book),
                'lessons': [{
                    'topicId': t['id'], 'title': t['name'], 'chapter': t['chapter'],
                    'description': t.get('description', ''),
                    'mastery_criteria': t.get('mastery_criteria', []),
                    'standards': [s.get('quote') for s in (t.get('standards') or [])],
                    'bank_samples': [{'stem': q['prompt'], 'answer': q.get('answer'),
                                      'type': q['type']} for q in by_q.get(t['id'], [])[:3]],
                    'out': 'data/%s/learn/_parts/%s/%s.json' % (BUCKET, book, t['id']),
                } for t in grp],
            }
            json.dump(payload, open(os.path.join(SD, tag + '.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            idx.append({'shard': tag, 'book': book, 'topics': [t['id'] for t in grp]})
    json.dump(idx, open(os.path.join(SD, '_INDEX.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('%s 学层分片 %d / 篇 %d' % (BUCKET, len(idx), sum(len(x['topics']) for x in idx)))


if __name__ == '__main__':
    main()
