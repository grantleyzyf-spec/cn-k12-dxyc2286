# -*- coding: utf-8 -*-
"""鲁教/鲁科学层精讲检查器。

用法：
  python3 scripts/check_chem_editions_learn.py --bucket <桶> --file <篇/片 json>
  python3 scripts/check_chem_editions_learn.py --bucket <桶> --all      # 全桶（成品 learn/*.json）
"""
import argparse, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = ['一、开场', '二、课本原文', '三、费曼翻译', '四、例题精讲', '五、易错点拨', '六、五步学习法', '七、方法锚与自查']
STEPS = ['每天锻炼一个小时', '扎实掌握第一个知识点', '能积微者速成', '对标思维', '杠铃法则']
BAN = ['教学目标', '考点', '命题趋势', '首先', '其次', '综上所述', '总而言之', '由此可见',
       '赋能', '抓手', '闭环', '值得注意的是', '如图', '下图']
_cache = {}


def han(s):
    return len(re.findall(r'[\u4e00-\u9fa5]', str(s)))


def qnorm(s):
    return re.sub(r'[\s\u3000，。、；：“”‘’（）()《》〈〉！？—…·\-\+＝=]', '', str(s))


def book_text(bucket, book):
    key = (bucket, book)
    if key not in _cache:
        p = os.path.join(REPO, 'data', bucket, '_text', book + '.txt')
        _cache[key] = qnorm(open(p, encoding='utf-8').read()) if os.path.exists(p) else ''
    return _cache[key]


def check(les, bucket):
    err = []
    md = les.get('markdown') or ''
    w = han(md)
    if not 1200 <= w <= 2800:
        err.append('字数 %d ∉1200—2800' % w)
    if les.get('words') not in (None, w) and abs((les.get('words') or 0) - w) > 10:
        err.append('words 标注 %s ≠ 实测 %d' % (les.get('words'), w))
    pos = [md.find(s) for s in SEC]
    for s, p in zip(SEC, pos):
        if p < 0:
            err.append('缺节 %s' % s)
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        err.append('七节顺序错乱')
    tail = md.split('六、五步学习法', 1)[-1].split('七、', 1)[0] if '六、五步学习法' in md else ''
    for st in STEPS:
        if st not in tail:
            err.append('五步缺「%s」' % st)
    if tail and not 350 <= han(tail) <= 900:
        err.append('五步节 %d ∉350—900' % han(tail))
    if md.count('- [ ]') < 3:
        err.append('自查勾选 <3 条')
    if md.count('❌') < 2 or md.count('✅') < 2:
        err.append('例题 ❌/✅ 各需 ≥2')
    if len(re.findall(r'例\s*[12１２]', md)) < 2:
        err.append('例题 <2 道')
    if '方法锚' not in md:
        err.append('缺方法锚')
    quotes = re.findall(r'^>\s*(.+)$', md, re.M)
    if len(quotes) < 2:
        err.append('原文引用 <2 处')
    src = book_text(bucket, les.get('book') or '')
    if not src:
        err.append('缺该册 _text 原文（无法回表）')
    else:
        bad = [q for q in quotes if qnorm(q)[:24] not in src]
        if bad:
            err.append('引文失配 %d 处（例：%s）' % (len(bad), bad[0][:28]))
    for b in BAN:
        if b in md:
            err.append('禁词/禁指代 %s' % b)
    if re.search(r'\$[^$]+\$', md):
        err.append('出现 LaTeX')
    if re.search(r'<(?!br\b)[a-zA-Z]+[^>]*>', md):
        err.append('出现 HTML 标签')
    if re.search(r'^\s*\|.*\|\s*$', md, re.M):
        err.append('出现 Markdown 表格')
    if re.search(r'^#{2,3} (?!一、|二、|三、|四、|五、|六、|七、)', md, re.M):
        err.append('出现非规范小节标题')
    if len(re.findall(r'^# ', md, re.M)) > 1:
        err.append('一级标题超过 1 个')
    return err


def lessons_of(obj, default_book=''):
    if isinstance(obj, dict) and 'lessons' in obj:
        bk = obj.get('book') or default_book
        out = []
        for les in obj['lessons']:
            les = dict(les)
            les.setdefault('book', bk)
            out.append(les)
        return out
    les = dict(obj) if isinstance(obj, dict) else {}
    les.setdefault('book', default_book)
    return [les]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--file')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    files = []
    if a.all:
        files = sorted(glob.glob(os.path.join(REPO, 'data', a.bucket, 'learn', '*.json')))
        files = [f for f in files if not os.path.basename(f).startswith('_')]
    elif a.file:
        files = [a.file]
    else:
        print(__doc__)
        return 1
    tot = badn = 0
    for f in files:
        obj = json.load(open(f, encoding='utf-8'))
        for les in lessons_of(obj, os.path.basename(os.path.dirname(f))):
            tot += 1
            err = check(les, a.bucket)
            if err:
                badn += 1
                print('❌ %s · %s · %s · %d 字' % (os.path.basename(f), les.get('topicId'),
                                                  les.get('title'), han(les.get('markdown'))))
                for e in err[:8]:
                    print('   -', e)
    print('共 %d 篇 · 不合格 %d' % (tot, badn))
    print('RESULT: %s' % ('PASS' if badn == 0 and tot else 'FAIL'))
    return 0 if (badn == 0 and tot) else 1


if __name__ == '__main__':
    sys.exit(main())
