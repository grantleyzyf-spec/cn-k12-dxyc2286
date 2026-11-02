import os, sys, glob
from multiprocessing import Pool
sys.path.insert(0, "/Users/a627692/Desktop/中小学教材/义务教育对应学科大单元教学设计V1.0全套执行标准2026")
import fitz
from ocr_helper import ocr_page

BASE = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/高中/鄂教版"
OUT = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-ejiao/_src"
os.makedirs(OUT, exist_ok=True)

TAGS = [("h1", "数学必修第一册"), ("h2", "数学必修第二册"), ("h3", "数学必修第三册"),
        ("h4", "数学必修第四册"), ("h5", "数学选择性必修第一册"),
        ("h6", "数学选择性必修第二册"), ("h7", "数学选择性必修第三册")]

BOOKS = {}
for p in glob.glob(os.path.join(BASE, "*.pdf")):
    n = os.path.basename(p).replace(" ", "")
    for tag, key in TAGS:
        if key in n:
            BOOKS[tag] = p


def work(a):
    tag, i = a
    cache = os.path.join(OUT, f"p_{tag}_{i:03d}.txt")
    if os.path.exists(cache) and os.path.getsize(cache) > 0:
        return tag, i, -1
    d = fitz.open(BOOKS[tag])
    t = ocr_page(d[i - 1], dpi=180)
    d.close()
    open(cache, "w", encoding="utf-8").write(t)
    return tag, i, len(t)


if __name__ == "__main__":
    jobs = []
    for tag, p in BOOKS.items():
        n = fitz.open(p).page_count
        jobs += [(tag, i) for i in range(1, n + 1)]
    print("books", len(BOOKS), "pages", len(jobs), flush=True)
    with Pool(10) as pool:
        for tag, i, n in pool.imap_unordered(work, jobs):
            if n >= 0:
                print(f"{tag} p{i} {n}", flush=True)
    for tag, p in BOOKS.items():
        n = fitz.open(p).page_count
        parts = []
        for i in range(1, n + 1):
            c = os.path.join(OUT, f"p_{tag}_{i:03d}.txt")
            parts.append(open(c, encoding="utf-8").read() if os.path.exists(c) else "")
        open(os.path.join(OUT, f"{tag}_full.txt"), "w", encoding="utf-8").write("\n\n".join(parts))
        print(f"{tag} 合并 {n} 页", flush=True)
    print("ALLDONE")
