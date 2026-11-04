# -*- coding: utf-8 -*-
"""把鲁教/鲁科化学教材 PDF 抽成 _text/<册>.txt（供学层引文逐字回表）。

用法：python3 scripts/build_chem_editions_text.py [chemistry-lujiao|chemistry-luke]
每页前加 `[[p<PDF页>]]` 标记，便于写手核对页码；行内不删字符，只把软换行并成段。
"""
import glob, os, re, sys

import fitz

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '/Users/a627692/Desktop/中小学教材/中小学教材/化学'
SRC = {
    'chemistry-sujiao': {
        '必修第一册': ('高中/苏教版', '必修第一册'),
        '必修第二册': ('高中/苏教版', '必修第二册'),
        '选择性必修第一册': ('高中/苏教版', '选择性必修第一册'),
        '选择性必修第二册': ('高中/苏教版', '选择性必修第二册'),
        '选择性必修第三册': ('高中/苏教版', '选择性必修第三册'),
    },
    'chemistry-lujiao': {
        '九年级上册': ('初中/鲁教版', '九年级_上册'),
        '九年级下册': ('初中/鲁教版', '九年级_下册'),
    },
    'chemistry-luke': {
        '必修第一册': ('高中/鲁科版', '必修第一册'),
        '必修第二册': ('高中/鲁科版', '必修第二册'),
        '选择性必修第一册': ('高中/鲁科版', '选择性必修第一册'),
        '选择性必修第二册': ('高中/鲁科版', '选择性必修第二册'),
        '选择性必修第三册': ('高中/鲁科版', '选择性必修第三册'),
    },
}


def find_pdf(sub, key):
    hits = [f for f in glob.glob(os.path.join(BASE, sub, '*.pdf'))
            if ('_' + key + '_') in os.path.basename(f)]
    assert len(hits) == 1, (sub, key, hits)
    return hits[0]


def build(bucket):
    out = os.path.join(REPO, 'data', bucket, '_text')
    os.makedirs(out, exist_ok=True)
    for book, (sub, key) in SRC[bucket].items():
        pdf = find_pdf(sub, key)
        doc = fitz.open(pdf)
        chunks = []
        for i, page in enumerate(doc, 1):
            t = page.get_text('text')
            lines = [ln.strip() for ln in t.splitlines()]
            chunks.append('[[p%d]]\n' % i + '\n'.join(ln for ln in lines if ln))
        txt = '\n\n'.join(chunks)
        dst = os.path.join(out, book + '.txt')
        open(dst, 'w', encoding='utf-8').write(txt)
        print('%-16s %-4s 页 %3d 字符 %6d → %s' % (bucket, book, len(doc), len(txt), dst))


if __name__ == '__main__':
    for b in (sys.argv[1:] or ['chemistry-lujiao', 'chemistry-luke']):
        build(b)
