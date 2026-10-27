#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「艺术（美术）课标回表」用的文本底本（可复算）。

背景：《义务教育艺术课程标准（2022 年版）》官方 PDF 是**扫描版**（131 页，无文字层），
仓库的 `2025修订课程标准TXT /义务教育/` 目录里也没有它的 TXT 快照，
所以 test_art.py 的「quote 逐字回表」无法像物理/语文那样直接读 TXT。
本脚本把该 PDF 渲染成图片后 OCR，拼成 /tmp/art_yijiao_ocr.txt 作为回表底本；
同时把高中美术课标 TXT（GB18030 编码）转存为 UTF-8 的 /tmp/gaozhong_meishu.txt。

用法:
    python3 scripts/ocr_art_standards.py            # 生成两份底本（约 3–5 分钟）
    python3 scripts/test_art.py                     # 回表即可 26/26 通过

依赖: pdftoppm（poppler）、tesseract + chi_sim。
CI 上没有这两个依赖也不会红：test_art.py 发现底本缺失时跳过回表（与 test_physics.py 同款约定）。
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

PDF = "/Users/a627692/Desktop/中小学教材/中小学教材/2025修订课程标准/义务教育2022课程标准/义务教育艺术课程课程标准（2022年版）.pdf"
GAOZHONG_TXT = ("/Users/a627692/Desktop/中小学教材/中小学教材/2025修订课程标准/"
                "普通高中课程方案及20科课程标准（2017年版2020年修订)/"
                "普通高中美术课程标准（2017年版2020年修订）.txt")
OUT_YIJIAO = "/tmp/art_yijiao_ocr.txt"
OUT_GAOZHONG = "/tmp/gaozhong_meishu.txt"
DPI = "200"
JOBS = "8"


def need(bin_name):
    if not shutil.which(bin_name):
        sys.exit(f"缺少依赖 {bin_name}（brew install poppler / tesseract tesseract-lang）")


def ocr_pdf(pdf, out_txt):
    need("pdftoppm")
    need("tesseract")
    tmp = tempfile.mkdtemp(prefix="art_ocr_")
    try:
        subprocess.run(["pdftoppm", "-r", DPI, "-png", pdf, os.path.join(tmp, "pg")], check=True)
        pngs = sorted(glob.glob(os.path.join(tmp, "pg-*.png")))
        print(f"  渲染 {len(pngs)} 页 → OCR（-P {JOBS}）")
        subprocess.run(
            "ls " + os.path.join(tmp, "pg-*.png") + " | xargs -P " + JOBS +
            ' -I{} sh -c \'tesseract "{}" "' + os.path.join(tmp, "$(basename {} .png)") + '" -l chi_sim 2>/dev/null\'',
            shell=True, check=True)
        txts = sorted(glob.glob(os.path.join(tmp, "pg-*.txt")))
        with open(out_txt, "w", encoding="utf-8") as f:
            for p in txts:
                f.write(open(p, encoding="utf-8", errors="ignore").read() + "\n")
        print(f"  {out_txt}  {os.path.getsize(out_txt)} 字节 / {len(txts)} 页")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def convert_gaozhong(src, out_txt):
    raw = open(src, "rb").read()
    for enc in ("utf-8", "gb18030"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        sys.exit("高中美术课标 TXT 解码失败（既非 UTF-8 也非 GB18030）")
    # 该 TXT 实为 GB18030，用 UTF-8 硬读会得到乱码；只有当解出的文本里出现「美术」才算成功
    if txt.count("美术") < 10:
        txt = raw.decode("gb18030")
    open(out_txt, "w", encoding="utf-8").write(txt.replace("\r\n", "\n"))
    print(f"  {out_txt}  {os.path.getsize(out_txt)} 字节")


def main():
    if os.path.exists(PDF):
        print("义务教育艺术课标（扫描版）→ OCR")
        ocr_pdf(PDF, OUT_YIJIAO)
    else:
        print(f"⚠️ 找不到 {PDF}，跳过义教底本")
    if os.path.exists(GAOZHONG_TXT):
        print("高中美术课标 TXT → UTF-8")
        convert_gaozhong(GAOZHONG_TXT, OUT_GAOZHONG)
    else:
        print(f"⚠️ 找不到 {GAOZHONG_TXT}，跳过高中底本")
    print("完成。接着跑 python3 scripts/test_art.py")


if __name__ == "__main__":
    main()
