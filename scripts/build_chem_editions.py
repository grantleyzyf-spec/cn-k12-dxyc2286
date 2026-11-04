# -*- coding: utf-8 -*-
"""生成鲁教版初中化学 / 鲁科版高中化学两个版本桶（可复现，脚本入库）：_skeleton.json / topics.json / dependencies.json

用法：python3 /tmp/chem/build.py [--write]
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chem_lujiao_cz_data as CZ
import chem_luke_gz_data as GZ
import chem_yuejiao_cz_data as YJ
import chem_bj_cz_data as BJ

ROOT = '/Users/a627692/Desktop/cn-k12-dxyc2286'
POOL = json.load(open(os.path.join(ROOT, 'data', '_chem_std_pool.json'), encoding='utf-8'))

# 引文借用：按关键词把课标条目挂到最贴切的知识点（宁缺毋滥）
KW = [
    (('物质的量', '摩尔', '气体摩尔体积'), '物质的量'),
    (('离子反应', '电解质', '电离'), '离子反应'),
    (('氧化还原',), '氧化还原'),
    (('元素周期', '原子结构', '元素性质'), '元素周期'),
    (('化学键', '共价键', '离子键', '分子间作用力', '杂化'), '化学键'),
    (('铁', '亚铁'), '铁'),
    (('硫', '二氧化硫', '硫酸'), '硫'),
    (('氮', '氨', '硝酸'), '氮'),
    (('钠', '氯'), '钠'),
    (('金属', '合金', '腐蚀', '锈蚀'), '金属'),
    (('酸', '碱', 'pH', '中和'), '酸碱'),
    (('溶液', '溶解度', '溶质'), '溶液'),
    (('有机物', '烃', '醇', '酚', '醛', '羧酸', '酯', '糖', '蛋白质'), '有机'),
    (('晶体', '晶胞'), '晶体'),
    (('反应速率', '平衡', '限度', '方向'), '速率平衡'),
    (('原电池', '电解', '电池', '电能'), '电化学'),
    (('热效应', '焓变', '盖斯'), '反应热'),
    (('空气', '氧气', '二氧化碳'), '空气'),
    (('实验', '探究', '仪器', '操作'), '实验'),
    (('材料', '能源', '环境', '社会'), 'STSE'),
]

import chem_std_map as std_map

def pick_std(name, is_yijiao):
    table = std_map.YIJIAO if is_yijiao else std_map.GAOZHONG
    keys = table.get(name, [])
    out, seen = [], set()
    for k in keys:
        for p in POOL:
            if k in p['quote'] and p['quote'] not in seen:
                if (is_yijiao and p['id'].startswith('che-2022')) or ((not is_yijiao) and p['id'].startswith('che-2017')):
                    seen.add(p['quote'])
                    out.append({'id': p['id'], 'confidence': 'partial', 'quote': p['quote'],
                                'sourceLine': p['sourceLine'] if isinstance(p['sourceLine'], int) else 1})
                    break
    return out[:2]


def build(books, prefix, subject, out_dir):
    topics, deps, skeleton = [], [], []
    uid = lid = 0
    prev_last = None            # 上一节（跨单元、跨册都不清空，保证整桶成链）
    first_of_bucket = True
    for book, grade, sem, unit_word, pdf, units in books:
        sk_book = {'book': book, 'pdf': pdf, 'grade': grade, 'semester': sem, 'units': []}
        for no, uname, domain, lessons in units:
            uid += 1
            unit_id = '%s_u%03d' % (prefix, uid)
            chapter = '%s 第%d%s %s' % (book, no, unit_word, uname)
            up = re.sub(r'「.*?」', uname, uname)
            topics.append({
                'id': unit_id, 'name': uname, 'subject': subject, 'domain': domain,
                'grade': grade, 'semester': sem, 'chapter': chapter, 'level': 'unit',
                'type': 'conceptual',
                'description': '%s本%s围绕「%s」组织，含 %d 个课题，覆盖%s的核心内容与方法。' % (
                    chapter.split(' ')[0] + '，', unit_word, uname, len(lessons), domain),
                'mastery_criteria': ['能说出「%s」的主线与本%s各课题之间的关系' % (uname, unit_word),
                                     '能综合运用本%s知识解决一个实际问题' % unit_word],
                'tags': [domain, uname], 'standards': [],
                'prerequisites': [], 'root_reason': '%s上位点，不设先修' % unit_word,
            })
            sk_book['units'].append({'no': no, 'name': uname, 'unitId': unit_id,
                                     'lessons': [l[0] for l in lessons]})
            for lname, desc, c1, c2 in lessons:
                lid += 1
                tid = '%s_j%03d' % (prefix, lid)
                topics.append({
                    'id': tid, 'name': lname, 'subject': subject, 'domain': domain,
                    'grade': grade, 'semester': sem,
                    'chapter': '%s · %s' % (chapter, lname), 'level': 'lesson',
                    'type': 'conceptual', 'description': desc,
                    'mastery_criteria': [c1, c2], 'tags': [domain, lname],
                    'standards': pick_std(lname, grade <= 9),
                    'prerequisites': [prev_last] if prev_last else [],
                    'prereqUpper': [unit_id],
                })
                if prev_last:
                    deps.append({'from': prev_last, 'to': tid, 'type': 'hard'})
                prev_last = tid
                first_of_bucket = False
        skeleton.append(sk_book)
    if not topics[0].get('prerequisites'):
        topics[0]['root_reason'] = '本版本第一册第一%s，作为先修链起点' % unit_word
    # 首个 unit 点本来就带 root_reason；首个 lesson 点（prerequisites 空）也要有
    for t in topics:
        if t['level'] == 'lesson' and not t['prerequisites'] and 'root_reason' not in t:
            t['root_reason'] = '本册第一节，作为本教材先修链起点'
    os.makedirs(out_dir, exist_ok=True)
    json.dump(topics, open(os.path.join(out_dir, 'topics.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(out_dir, 'dependencies.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(skeleton, open(os.path.join(out_dir, '_skeleton.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return topics, deps


if __name__ == '__main__':
    write = '--write' in sys.argv
    for books, prefix, subject, d in [
        (CZ.BOOKS, 'clj', 'chemistry-lujiao', os.path.join(ROOT, 'data', 'chemistry-lujiao')),
        (GZ.BOOKS, 'clk', 'chemistry-luke', os.path.join(ROOT, 'data', 'chemistry-luke')),
        (YJ.BOOKS, 'cyj', 'chemistry-yuejiao', os.path.join(ROOT, 'data', 'chemistry-yuejiao')),
        (BJ.BOOKS, 'cbj', 'chemistry-bj', os.path.join(ROOT, 'data', 'chemistry-bj')),
    ]:
        t, e = build(books, prefix, subject, d)
        st = sum(1 for x in t if x['standards'])
        print('%s：点 %d（单元/章 %d、节 %d）｜先修边 %d｜挂课标 %d（%.0f%%）' % (
            subject, len(t), sum(1 for x in t if x['level'] == 'unit'),
            sum(1 for x in t if x['level'] == 'lesson'), len(e), st, 100.0 * st / len(t)))
