#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学层精讲分片生成器（83 个课时点，一篇一文件）。

每片自带：
  · lessons[]：topicId / title / chapter / grade / standards / **excerpt**（本册 OCR 全文里该节的节选）
  · txt：本册 OCR 全文绝对路径（回表用）
  · out：落盘路径 _learn_parts/L###.json
产物：data/physics-bsd-gyy/_learn_parts/L001.json … ＋ _CONTRACT.md
用法：python3 scripts/gen_pgy_learn_shards.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
PARTS = os.path.join(D, '_learn_parts')
MAXLEN = 3800

CONTRACT = """# 北师大版（郭玉英）初中物理 · 学层精讲合同

落盘：`{D}/_learn_parts/L###_out.json`（只写你自己那一个文件）
形状：`{"shard": "L001", "topicId": "pgy_j002", "markdown": "……", "words": 1650}`

## 七段标题（逐字照抄，不许改写同义标题）
```
## 一、开场
## 二、课本原文
## 三、费曼翻译
## 四、例题精讲
## 五、易错点拨
## 六、五步学习法
## 七、方法锚与自查
```

## 内容硬指标（checker 逐条查）
- 全篇 **1200–2600 汉字**（`words` 字段填实测值，必须与正文汉字数相等）
- 第二节「课本原文」：**逐字**引用本片 `excerpt` 里≥2 处完整句子，每处另起一行写「这句话的意思是……」把它翻成人话
  ⛔ 引文必须是 `excerpt` 里连续出现的原句（不得改字、不得拼接）；⛔ 不要引用 excerpt 之外的段落
- 第四节「例题精讲」：**2 道**例题，每道都要写「❌ 常见错解」与「✅ 正确思路」两行（各自用这两个符号开头）
- 第六节「五步学习法」：五条，序号 ①②③④⑤，每条 **72–88 汉字**（整节 350–700）
  五条主题依次为：①每天锻炼一个小时 ②扎实掌握第一个知识点 ③能积微者速成 ④运用对标思维 ⑤运用杠铃法则
  ⛔ 导语与正文里不要写「五步学习法」这四个字以外的自造标题
- 第七节「方法锚与自查」：给一个可复用的"方法锚"（一句话口诀）＋ **≥3 条** `- [ ]` 自查项
- ⛔ 禁 Markdown 表格、禁 LaTeX、禁 HTML；公式用文字或 `p＝F/S` 这种纯文本写法
- ⛔ 禁「扫描件/OCR/抽取/残片」这类元话语；素材里的乱码字符视为不存在，不解释

## 自检（落盘后必跑）
```
python3 scripts/check_pgy_learn.py --shard {D}/_learn_parts/L###_out.json
```
末行须 `RESULT: PASS`。
"""


def norm(s):
    return re.sub(r'\s+', '', s or '')


def main():
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    os.makedirs(PARTS, exist_ok=True)
    src = {}
    for book in ('八年级上册', '八年级下册', '九年级全一册'):
        p = os.path.join(D, '_text', book + '.txt')
        src[book] = norm(open(p, encoding='utf-8').read()) if os.path.exists(p) else ''

    lessons = [t for t in topics if t['level'] == 'lesson']
    for i, t in enumerate(lessons, 1):
        book = t['chapter'].split(' ')[0]
        text = src.get(book, '')
        name = norm(t['name'])
        # 目录页也含节名（后面紧跟 /页码），必须跳过：取全文 6% 之后的首次出现
        cut = int(len(text) * 0.06)
        idx = text.find(name, cut)
        if idx < 0:
            idx = text.find(name)          # 兜底
        excerpt = text[idx: idx + MAXLEN] if idx >= 0 else ''
        shard = {
            'shard': 'L%03d' % i,
            'txt': os.path.join(D, '_text', book + '.txt'),
            'out': os.path.join(PARTS, 'L%03d_out.json' % i),
            'lessons': [{
                'topicId': t['id'], 'title': t['name'], 'chapter': t['chapter'],
                'grade': t['grade'], 'domain': t['domain'],
                'standards': [{'id': s['id'], 'quote': s['quote']} for s in t['standards'][:2]],
                'excerpt': excerpt,
            }],
        }
        json.dump(shard, open(os.path.join(PARTS, 'L%03d.json' % i), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    open(os.path.join(PARTS, '_CONTRACT.md'), 'w', encoding='utf-8').write(CONTRACT.replace('{D}', D))
    empty = [i for i, t in enumerate(lessons, 1)
             if not src.get(t['chapter'].split(' ')[0]) or
             norm(t['name']) not in src.get(t['chapter'].split(' ')[0], '')]
    print('学层分片 %d 个；节选缺失 %d 个：%s' % (len(lessons), len(empty), empty[:6]))


if __name__ == '__main__':
    main()
