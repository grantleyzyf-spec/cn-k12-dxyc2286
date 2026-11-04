# -*- coding: utf-8 -*-
"""科普版地理 4 册 PDF → 文本包（rapidocr）。用法：python3 ocr_kepu.py <册名>"""
import os, sys, re, json, glob
import fitz
from rapidocr_onnxruntime import RapidOCR

BOOKS = {'七上': '七年级_上册', '七下': '七年级_下册', '八上': '八年级_上册', '八下': '八年级_下册'}
OUT = os.path.expanduser('~/Desktop/cn-k12-dxyc2286/data/geography-kepu/_text')
PDF = os.environ.get('KEPU_PDF_DIR', '/tmp/kp') + '/{}.pdf'

def main(tag):
    book = BOOKS[tag]
    os.makedirs(OUT, exist_ok=True)
    ocr = RapidOCR()
    doc = fitz.open(PDF.format(book))
    pages = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=200)
        png = f'/tmp/kp/_{tag}_{os.getpid()}.png'
        pix.save(png)
        try:
            res, _ = ocr(png)
            txt = '\n'.join(x[1] for x in (res or []))
        except Exception as e:  # noqa: BLE001
            txt = ''
            print('page', i, 'err', e, flush=True)
        txt = re.sub(r'[ \t\u3000]+', '', txt)
        pages.append(txt)
        if i % 20 == 0:
            print(book, i, '/', len(doc), flush=True)
    open(f'{OUT}/{book}.txt', 'w', encoding='utf-8').write('\n\n'.join(pages))
    print(book, 'done', sum(len(p) for p in pages), '字符', flush=True)

if __name__ == '__main__':
    main(sys.argv[1])
