# -*- coding: utf-8 -*-
"""科普版初中地理 · 骨架生成（4 册 16 单元 128 课时）
结构源：① 分课时教学设计 docx 文件名（七上/八上，自证课时名）
        ② 大单元整体教学设计 docx 的「十五、教-学-评一致性课时设计」段（七下/八下）
产出：data/geography-kepu/{_skeleton.json,topics.json,dependencies.json,questions.json}
用法：python3 /tmp/kp/build_skeleton.py [--write]
"""
import glob, json, os, re, sys, collections
from docx import Document

REPO = os.path.expanduser('~/Desktop/cn-k12-dxyc2286')
BUCKET = 'geography-kepu'
OUT = os.path.join(REPO, 'data', BUCKET)
LE = os.path.expanduser('~/Desktop/中小学教材/中小学教材/各学科分课时设计/地理/科普版')
DA = os.path.expanduser('~/Desktop/中小学教材/中小学教材/地理/初中/科普版')
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}

# 单元名（教材顺序）＋ 领域（义教四领域）
UNITS = {
    '七年级上册': [('一', '认识地球探宇宙', '地球与地图'), ('二', '地球运动永不息', '地球与地图'),
                ('三', '海陆分布蕴变迁', '世界地理'), ('四', '气象万千多绚丽', '世界地理'),
                ('五', '多元文化共发展', '世界地理')],
    '七年级下册': [('一', '认识我们所在的大洲', '世界地理'), ('二', '了解特色鲜明的地区', '世界地理'),
                ('三', '走进多种多样的国家', '世界地理')],
    '八年级上册': [('一', '了解祖国的概况', '中国地理'), ('二', '走进祖国的大自然', '中国地理'),
                ('三', '探寻祖国的自然资源', '中国地理'), ('四', '认识祖国的产业特征', '中国地理')],
    '八年级下册': [('一', '认识四大区域', '中国地理'), ('二', '探寻不同尺度的区域', '中国地理'),
                ('三', '走进北京和港澳台', '中国地理'), ('四', '行稳致远的中国', '中国地理')],
}
GRADE = {'七年级上册': (7, '上'), '七年级下册': (7, '下'), '八年级上册': (8, '上'), '八年级下册': (8, '下')}
PROC = re.compile(r'绘制|判读|制作|检测|实验|读图|剖面|模拟|测量|定位|成果展评|项目|辩论|调查')


def from_fenkeshi():
    pat = re.compile(r'科普版初中地理(.+?)·第(\d+)课时\s*(.+?)分课时教学设计')
    got = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in glob.glob(LE + '/**/*.docx', recursive=True):
        m = pat.search(os.path.basename(f))
        if not m:
            continue
        book = '七年级上册' if '七年级上册' in m.group(1) else '八年级上册'
        um = re.search(r'单元([一二三四五])', m.group(1))
        if not um:
            continue  # 跨学科主题学习不出点
        got[book][um.group(1)].append((int(m.group(2)), m.group(3).strip()))
    return got


def from_danyuan():
    got = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in glob.glob(DA + '/*.docx'):
        b = os.path.basename(f)
        m = re.search(r'(七年级下册|八年级下册)单元([一二三四五])', b)
        if not m:
            continue
        book, u = m.group(1), m.group(2)
        ps = [p.text.strip() for p in Document(f).paragraphs if p.text.strip()]
        idx = [i for i, p in enumerate(ps) if '课时设计' in p]
        for s in ps[idx[-1]:] if idx else []:
            mm = re.match(r'（[一二三四五六七八九十]+）第([一二三四五六七八九十]+)课时[:：]\s*(.+)', s)
            if mm:
                got[book][u].append((CN.get(mm.group(1), 0), mm.group(2).strip()))
    return got


def build():
    lessons = from_fenkeshi()
    for b, v in from_danyuan().items():
        lessons[b].update(v)
    units, topics, deps, seq = [], [], [], 0
    prev_tail = None
    for book, ulist in UNITS.items():
        grade, sem = GRADE[book]
        for u, uname, domain in ulist:
            lst = sorted(set(lessons[book].get(u, [])))
            assert lst, f'缺课时：{book} 单元{u}'
            seq += 1
            uid = f'gkp_p{seq:03d}'
            chap = f'{book} 第{u}单元 {uname}'
            units.append({'id': uid, 'book': book, 'unit': u, 'name': uname,
                          'chapter': chap, 'domain': domain, 'lessons': len(lst)})
            topics.append({
                'id': uid, 'name': uname, 'subject': BUCKET, 'domain': domain,
                'grade': grade, 'semester': sem, 'chapter': chap, 'level': 'unit',
                'type': 'conceptual',
                'description': f'本单元围绕「{uname}」展开，共 {len(lst)} 课时，梳理该单元的主干概念、读图方法与区域认知路径。',
                'mastery_criteria': [f'能说出本单元「{uname}」的主干概念与读图方法',
                                     f'能把本单元知识迁移到{domain}的真实情境中'],
                'diagnostic_question': {'question': f'关于「{uname}」，下列说法正确的是？', 'answer': ''},
                'external': False, 'standards': [], 'tags': [domain, uname],
                'prerequisites': [], 'root_reason': '单元上位点，不设先修课时',
                'curriculumRef': '', 'verified': False})
            first_id = None
            for n, name in lst:
                seq += 1
                lid = f'gkp_p{seq:03d}'
                lchap = f'{chap} · {name}'
                topics.append({
                    'id': lid, 'name': name, 'subject': BUCKET, 'domain': domain,
                    'grade': grade, 'semester': sem, 'chapter': lchap, 'level': 'lesson',
                    'type': 'procedural' if PROC.search(name) else 'conceptual',
                    'description': f'理解「{name}」的核心内容，掌握其读图与分析方法，能结合实例说明。',
                    'mastery_criteria': [f'能说明「{name}」的基本内容',
                                         f'能运用相关知识解释{domain}中的具体现象'],
                    'diagnostic_question': {'question': f'关于「{name}」，下列叙述正确的是？', 'answer': ''},
                    'external': False, 'standards': [], 'tags': [domain, uname],
                    'prerequisites': [], 'curriculumRef': '', 'verified': False})
                topics[-1]['prereqUpper'] = uid
                if first_id is None:
                    first_id = lid
                    if prev_tail:
                        topics[-1]['prerequisites'] = [prev_tail]
                        deps.append({'from': prev_tail, 'to': lid, 'type': 'hard'})
                    else:
                        topics[-1]['root_reason'] = '起始课时，无先修'
                else:
                    prev_id = topics[-2]['id']
                    topics[-1]['prerequisites'] = [prev_id]
                    deps.append({'from': prev_id, 'to': lid, 'type': 'hard'})
                prev_tail = lid
            if first_id is None:
                prev_tail = uid
    return units, topics, deps


REF_MAP = {
    '七年级上册 第1单元': ['七年级上册 第一章 地球', '七年级上册 第二章 地图'],
    '七年级上册 第2单元': ['七年级上册 第一章 地球'],
    '七年级上册 第3单元': ['七年级上册 第三章 陆地和海洋'],
    '七年级上册 第4单元': ['七年级上册 第四章 天气与气候'],
    '七年级上册 第5单元': ['七年级上册 第五章 居民与文化', '七年级上册 第六章 发展与合作'],
    '七年级下册 第1单元': ['七年级下册 第七章 我们生活的大洲——亚洲'],
    '七年级下册 第2单元': ['七年级下册 第九章 东半球其他的地区和国家', '七年级下册 第十一章 极地地区'],
    '七年级下册 第3单元': ['七年级下册 第八章 我们邻近的地区和国家', '七年级下册 第十章 西半球的国家'],
    '八年级上册 第1单元': ['八年级上册 第一章 从世界看中国'],
    '八年级上册 第2单元': ['八年级上册 第二章 中国的自然环境'],
    '八年级上册 第3单元': ['八年级上册 第三章 中国的自然资源'],
    '八年级上册 第4单元': ['八年级上册 第四章 中国的经济发展'],
    '八年级下册 第1单元': ['八年级下册 第六章 中国的地理差异'],
    '八年级下册 第2单元': ['八年级下册 第七章 北方地区', '八年级下册 第十一章 奋进中的中国'],
    '八年级下册 第3单元': ['八年级下册 第七章 北方地区', '八年级下册 第八章 南方地区'],
    '八年级下册 第4单元': ['八年级下册 第十一章 奋进中的中国'],
}


def borrow_standards(topics):
    """按单元映射从 data/geography（人教版）借同一课标条目：quote 逐字沿用，confidence 降 partial。"""
    ref = json.load(open(os.path.expanduser('~/Desktop/cn-k12-dxyc2286/data/geography/topics.json'), encoding='utf-8'))
    pool = {}
    for t in ref:
        pool.setdefault(t['chapter'], []).extend(t.get('standards') or [])
    for t in topics:
        head = t['chapter'].split(' · ')[0]
        m = re.match(r'^(\S+?) 第([一二三四五六七八九十]+)单元', head)
        key = f'{m.group(1)} 第{CN[m.group(2)]}单元'
        got, seen = [], set()
        for chap in REF_MAP.get(key, []):
            for st in pool.get(chap, []):
                q = st.get('quote') or ''
                if not q or q in seen:
                    continue
                seen.add(q)
                got.append({'id': st['id'], 'confidence': 'partial', 'quote': q,
                            'sourceLine': st.get('sourceLine', 0)})
        if got:
            t['standards'] = got[:3]
            t['curriculumRef'] = got[0]['id']
    return topics


if __name__ == '__main__':
    units, topics, deps = build()
    topics = borrow_standards(topics)
    print(f'单元 {len(units)} · 课时点 {sum(1 for t in topics if t["level"]=="lesson")} · 总点 {len(topics)} · 边 {len(deps)}')
    for u in units:
        print(f'  {u["chapter"]}（{u["domain"]}）{u["lessons"]} 课时')
    if '--write' in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        json.dump(units, open(f'{OUT}/_skeleton.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(topics, open(f'{OUT}/topics.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(deps, open(f'{OUT}/dependencies.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        q = f'{OUT}/questions.json'
        if not os.path.exists(q):
            json.dump([], open(q, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('已写入', OUT)
