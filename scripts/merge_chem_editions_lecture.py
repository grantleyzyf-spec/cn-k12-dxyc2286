# -*- coding: utf-8 -*-
"""把 exam_lectures/<册>/*.json 汇总成 exam_lectures/_INDEX.json（站内索引用）。

用法：python3 scripts/merge_chem_editions_lecture.py <chemistry-lujiao|chemistry-luke>
"""
import glob, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = sys.argv[1] if len(sys.argv) > 1 else 'chemistry-lujiao'
D = os.path.join(REPO, 'data', BUCKET)
rows, words = [], 0
for f in sorted(glob.glob(os.path.join(D, 'exam_lectures', '*', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    rows.append({'examId': d.get('examId'), 'book': d.get('book'), 'paper': d.get('paper'),
                 'kind': d.get('kind'), 'words': d.get('words'),
                 'path': os.path.relpath(f, os.path.join(REPO, 'data'))})
    words += d.get('words') or 0
json.dump({'bucket': BUCKET, 'count': len(rows), 'words': words, 'items': rows},
          open(os.path.join(D, 'exam_lectures', '_INDEX.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('%s 讲解 %d 份 / 汉字 %d' % (BUCKET, len(rows), words))
