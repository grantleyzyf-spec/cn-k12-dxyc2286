# -*- coding: utf-8 -*-
"""鲁教/鲁科试卷讲解检查器。

用法：
  python3 scripts/check_chem_editions_lecture.py --bucket <桶> --file <讲解 json>
  python3 scripts/check_chem_editions_lecture.py --bucket <桶> --all
关键闸门：题号必须逐个出现，且 `**第 N 题（X 分）**` 的 X 与卷面该题 score 完全相等。
"""
import argparse, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = ['一、这份卷在考什么', '二、考点地图', '三、逐题精讲', '四、整卷复盘', '五、五步学习法', '六、自查清单']
STEPS = ['每天锻炼一个小时', '扎实掌握第一个知识点', '能积微者速成', '对标思维', '杠铃法则']
BAN = ['教学目标', '命题趋势', '首先', '其次', '综上所述', '总而言之', '由此可见',
       '赋能', '抓手', '闭环', '值得注意的是', '如图', '下图']


def han(s):
    return len(re.findall(r'[\u4e00-\u9fa5]', str(s)))


def load_exam(bucket, exam_id):
    for f in glob.glob(os.path.join(REPO, 'data', bucket, 'exams', '*', '*.json')):
        d = json.load(open(f, encoding='utf-8'))
        if d.get('examId') == exam_id:
            return d
    return None


def check(lec, bucket):
    err = []
    md = lec.get('markdown') or ''
    w = han(md)
    if not 2500 <= w <= 7500:
        err.append('字数 %d ∉2500—7500' % w)
    if lec.get('words') not in (None, w) and abs((lec.get('words') or 0) - w) > 10:
        err.append('words 标注 %s ≠ 实测 %d' % (lec.get('words'), w))
    pos = [md.find(s) for s in SEC]
    for s, p in zip(SEC, pos):
        if p < 0:
            err.append('缺节 %s' % s)
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        err.append('六段顺序错乱')
    exam = load_exam(bucket, lec.get('examId'))
    if not exam:
        err.append('找不到卷面 %s' % lec.get('examId'))
        return err
    if lec.get('paper') != exam.get('paper'):
        err.append('paper 与卷面不一致')
    items = [it for s in exam.get('sections') or [] for it in s.get('items') or []]
    hit = re.findall(r'\*\*第\s*(\d+)\s*题[（(](\d+(?:\.\d+)?)\s*分[）)]\*\*', md)
    seen = {}
    for no, sc in hit:
        seen.setdefault(int(no), []).append(float(sc))
    for it in items:
        no, sc = it['no'], float(it['score'])
        if no not in seen:
            err.append('题号第 %d 题未出现' % no)
        elif sc not in seen[no]:
            err.append('第 %d 题分值写成 %s，卷面是 %s' % (no, seen[no], sc))
    extra = [n for n in seen if n not in {it['no'] for it in items}]
    if extra:
        err.append('出现卷面没有的题号 %s' % extra[:3])
    need = int(len(items) * 0.7)
    for tag in ['**思路**', '**关键一步**', '**易错**']:
        if md.count(tag) < need:
            err.append('%s 出现 %d 次 < %d（题数 %d 的 70%%）' % (tag, md.count(tag), need, len(items)))
    tail = md.split('五、五步学习法', 1)[-1].split('六、', 1)[0] if '五、五步学习法' in md else ''
    for st in STEPS:
        if st not in tail:
            err.append('五步缺「%s」' % st)
    ncb = md.count('- [ ]')
    if not 6 <= ncb <= 8:
        err.append('自查清单 %d 条 ∉6—8' % ncb)
    for b in BAN:
        if b in md:
            err.append('禁词/禁指代 %s' % b)
    if re.search(r'\$[^$]+\$', md):
        err.append('出现 LaTeX')
    if re.search(r'<(?!br\b)[a-zA-Z]+[^>]*>', md):
        err.append('出现 HTML 标签')
    if re.search(r'^\s*\|.*\|\s*$', md, re.M):
        err.append('出现 Markdown 表格')
    if re.search(r'^#{2,3} (?!一、|二、|三、|四、|五、|六、)', md, re.M):
        err.append('出现非规范小节标题')
    return err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--file')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    files = []
    if a.all:
        files = sorted(f for f in glob.glob(os.path.join(REPO, 'data', a.bucket, 'exam_lectures', '*', '*.json'))
                       if not os.path.basename(f).startswith('_'))
    elif a.file:
        files = [a.file]
    else:
        print(__doc__)
        return 1
    tot = badn = 0
    for f in files:
        lec = json.load(open(f, encoding='utf-8'))
        tot += 1
        err = check(lec, a.bucket)
        if err:
            badn += 1
            print('❌ %s · %s · %d 字' % (os.path.basename(f), lec.get('examId'), han(lec.get('markdown'))))
            for e in err[:8]:
                print('   -', e)
    print('共 %d 份 · 不合格 %d' % (tot, badn))
    print('RESULT: %s' % ('PASS' if badn == 0 and tot else 'FAIL'))
    return 0 if (badn == 0 and tot) else 1


if __name__ == '__main__':
    sys.exit(main())
