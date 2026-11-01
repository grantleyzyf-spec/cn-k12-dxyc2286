#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""江苏线数学图谱 · 骨架生成器（苏教版 + 苏科版，各自独立学科目录）

用法：
  python3 build_skeleton.py --subject math-sujiao    # 小学苏教版 9 册 + 高中苏教版 4 册
  python3 build_skeleton.py --subject math-suke      # 初中苏科版 5 册

输入：/tmp/msj/<tag>.json（每册目录，由 vision 逐页核读产出）
输出：
  data/<subject>/_skeleton.json            全书结构（册 → 单元 → 节/课时）
  data/<subject>/_shards/<tag>.json        该册派单（结构与空位，子代只读）
  data/<subject>/_deps.json                先修边（单元→课时 hard / 册内顺次 hard / 册际 soft）

口径（与 data/math 人教版一致）：
  单元点 id  <pfx>_{p|h}{序号3位}     chapter = "<册> 第N单元 <单元名>"      题量 5
  课时点 id  <pfx>_{p|h}1{序号3位}    chapter = "<册> 第N单元 <单元名> · <节名>"  题量 8，带 page
  小学/初中 p 系列，高中 h 系列；id 全局唯一、只增不改
  册名统一带版本前缀：苏教版X年级X册 / 苏教版必修第一册 / 苏科版X年级X册
"""
import argparse
import json
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = '/tmp/mxj2'

# 小学苏教版/初中苏科版目录只到单元级，课时名从「大单元整体教学设计」docx 的课时设计段抽
KESHI = {}
_kp = os.path.join(SRC, 'keshi.json')
if os.path.isfile(_kp):
    KESHI = json.load(open(_kp, encoding='utf-8'))

EDITIONS = {
    'math-xiangjiao': {
        'edition': '湘教版', 'prefix': 'mxj',
        'vols': [('mxj7a', '初中'), ('mxj7b', '初中'), ('mxj8a', '初中'),
                 ('mxj8b', '初中'), ('mxj9a', '初中'),
                 ('mxjh1', '高中'), ('mxjh2', '高中'), ('mxjh3', '高中')],
        'gap': '小学1–6年级（库中无湘教版小学数学教材）、九下（无 PDF）、选择性必修第二册（库内 PDF 与必修第二册逐页相同，疑为同一册重复入库）、选必三/四（库中未见）',
    },
}

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
CN_NUM = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九',
          10: '十', 11: '十一', 12: '十二', 13: '十三', 14: '十四', 15: '十五', 16: '十六',
          17: '十七', 18: '十八', 19: '十九', 20: '二十'}


def cn_number(s):
    """「十一」→11，「三」→3；阿拉伯数字原样返回。"""
    s = s.strip()
    if s.isdigit():
        return int(s)
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1], 0)
    if '十' in s:
        a, _, b = s.partition('十')
        return CN.get(a, 0) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s, 0)


DOMAIN_RULES_YZ = [
    ('综合与实践', r'综合与实践|实践活动|数学与生活|小小商店|丰收的果园|蒜叶|球的反弹|面积的变化|游戏|活动|连环画|有多大|宝藏|秘密|复习|整理'),
    ('统计与概率', r'统计|数据|条形|折线|扇形|平均数|可能|概率|随机|抽样'),
    ('图形与几何', r'图形|几何|线段|射线|直线|角|三角|长方|正方|平行四边|梯形|圆|周长|面积|体积|容积|位置|方向|平移|旋转|对称|观察物体|表面|展开|勾股|相似|全等|投影|视图'),
]
DOMAIN_RULES_GZ = [
    ('统计与概率', r'统计|概率|随机|抽样|回归|独立性|二项分布|正态'),
    ('几何与代数', r'向量|复数|立体几何|直线|圆|圆锥曲线|空间|平面|解三角形'),
    ('函数', r'集合|逻辑|不等式|函数|指数|对数|三角|数列|导数|幂'),
]

TYPE_RULES = [
    ('procedural', r'计算|运算|解方程|化简|求值|口算|笔算|竖式|乘法|除法|加减|加减法'),
    ('application', r'解决问题|实际问题|应用|百分数|分数除法|比|比例|利息|折扣'),
    ('reasoning', r'探索|规律|猜想|推理|证明'),
]


def domain_of(name, stage):
    rules = DOMAIN_RULES_GZ if stage == '高中' else DOMAIN_RULES_YZ
    for dom, pat in rules:
        if re.search(pat, name):
            return dom
    return '数与代数' if stage != '高中' else '函数'


def type_of(name):
    for t, pat in TYPE_RULES:
        if re.search(pat, name):
            return t
    return 'conceptual'


def norm_name(s):
    s = re.sub(r'第[一二三四五六七八九十\d]+(?:单元|章)', '', s or '')
    return re.sub(r'[\s　·、,，。.「」“”\"\'（）()]', '', s)


def keshi_lessons(book, no, name):
    """按册取课时表：先按单元名匹配，再按单元序号兜底。"""
    key = re.sub(r'^(苏教版|苏科版)', '', book)
    km = KESHI.get(key) or {}
    if not km:
        return [], ''
    tgt = norm_name(name)
    for k, v in km.items():
        kn = norm_name(k)
        if tgt and (tgt in kn or kn.endswith(tgt)):
            return v.get('lessons', []), v.get('how', '')
    if no is not None:
        for k, v in km.items():
            m = re.match(r'^\s*第?([一二三四五六七八九十]+)', k)
            if m and cn_number(m.group(1)) == no:
                return v.get('lessons', []), v.get('how', '')
    return [], ''


def unit_chapter_name(raw):
    """把目录里的单元名规范成「第N单元 X」/「第N章 X」。目录里通常已带序号，原样保留。"""
    s = raw.strip()
    m = re.match(r'^第\s*([一二三四五六七八九十百\d]+)\s*(单元|章)\s*(.*)$', s)
    if not m:
        return None, s
    return cn_number(m.group(1)), f'第{m.group(1)}{m.group(2)} {m.group(3)}'.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', required=True, choices=list(EDITIONS))
    args = ap.parse_args()
    cfg = EDITIONS[args.subject]
    pfx = cfg['prefix']
    OUT = os.path.join(REPO, 'data', args.subject)
    os.makedirs(os.path.join(OUT, '_shards'), exist_ok=True)
    counters = {'p': 0, 'h': 0}
    lesson_counters = {'p': 1000, 'h': 1000}
    volumes = []
    deps = []
    missing = []

    for tag, stage in cfg['vols']:
        p = os.path.join(SRC, f'{tag}.json')
        if not os.path.isfile(p):
            missing.append(tag)
            continue
        d = json.load(open(p, encoding='utf-8'))
        series = 'h' if stage == '高中' else 'p'
        book = d['book']
        # 子代回的容器与键名不统一：units/chapters、unit_no/chapter/no、unit_name/unit/title
        raw_units = d.get('units') or d.get('chapters') or []
        d['units'] = []
        for _u in raw_units:
            if not isinstance(_u, dict):
                continue
            _u = dict(_u)
            _u.setdefault('unit_name', _u.get('unit') or _u.get('title') or _u.get('name') or '')
            _u.setdefault('unit_no', _u.get('chapter') or _u.get('no'))
            secs = []
            for _s in (_u.get('sections') or []):
                if isinstance(_s, dict):
                    secs.append({'sec_no': _s.get('sec_no') or _s.get('no') or '',
                                 'sec_name': _s.get('sec_name') or _s.get('title') or '',
                                 'page': _s.get('page')})
                else:
                    secs.append({'sec_name': str(_s), 'page': None})
            _u['sections'] = secs
            d['units'].append(_u)                      # 苏教版一年级上册 / 苏教版必修第一册
        units_out = []
        prev_lesson_id = None
        for u in d.get('units', []):
            # 子代回的结构键名不统一：unit_name/unit/title/name 与 unit_no/no 都接受
            if 'unit_name' not in u or 'unit_no' not in u:
                u = dict(u)
                u.setdefault('unit_name', u.get('unit') or u.get('title') or u.get('name') or '')
                u.setdefault('unit_no', u.get('no'))
            raw_name = (u.get('unit_name') or '').strip()
            no, uname = unit_chapter_name(raw_name)
            from_name = no is not None          # 目录名里本来就带「第N单元/章」
            if no is None:
                raw_no = u.get('unit_no')
                try:
                    no = int(raw_no)
                except (TypeError, ValueError):
                    rs = str(raw_no or '').strip()
                    if rs[:1] in CN:
                        no = cn_number(rs.lstrip('第'))
                    else:
                        m = re.search(r'\d+', rs)
                        no = int(m.group()) if m else None
                uname = raw_name
            # 统一显示名：小学/人教式「第N单元 名」，高中/苏科式「第N章 名」
            # 注意：目录名自带序号时 unit_chapter_name 已补好，不能再加一遍
            if no is not None and not from_name:
                use_ch = ('章' if (series == 'h' or '苏科' in book or '必修' in book or '湘教' in book) else '单元')
                num = str(no) if use_ch == '章' else CN_NUM.get(no, str(no))
                uname = f'第{num}{use_ch} {uname}'.strip()
            counters[series] += 1
            uid = f'{pfx}_{series}{counters[series]:03d}'
            uchapter = f'{book} {uname}'
            lessons = []
            secs = u.get('sections') or []
            if not secs:
                got, how = keshi_lessons(book, no, uname)
                for g in got:
                    secs.append({'sec_no': f"第{g['no']}课时", 'sec_name': g['title'],
                                 'page': None, '_src': f'大单元课时设计/{how}'})
            secs = [x if isinstance(x, dict) else {'sec_name': str(x), 'page': None}
                    for x in secs]
            # 章末板块（小结/复习题/数学探究/综合与实践/数学建模…）不是课时，不进课时点
            PLATE = re.compile(r'^\s*(小结|本章小结|复习题|复习|整理与复习|总复习|期末复习|数学探究|'
                               r'数学活动|综合与实践|课题学习|探究与拓展|数学建模|阅读|后记|数学文化|数学实验|多知道一点|现代技术应用)')
            secs = [x for x in secs if not PLATE.match((x.get('sec_name') or '').strip())]
            secs = [x for x in secs if (x.get('sec_name') or '').strip()]
            for s in secs:
                lesson_counters[series] += 1
                lid = f'{pfx}_{series}1{lesson_counters[series]-1000:03d}'
                lessons.append({
                    'id': lid,
                    'sec_no': str(s.get('sec_no', '')).strip(),
                    'sec_name': s.get('sec_name', '').strip(),
                    'page': s.get('page'),
                    'chapter': f'{uchapter} · {s.get("sec_name", "").strip()}',
                })
                if prev_lesson_id:
                    deps.append({'from': prev_lesson_id, 'to': lid, 'type': 'hard',
                                 'reason': '同册课时顺次'})
                deps.append({'from': uid, 'to': lid, 'type': 'hard', 'reason': '单元包含课时'})
                prev_lesson_id = lid
            units_out.append({
                'unit_no': no, 'unit_name': uname, 'unit_chapter': uchapter,
                'unit_id': uid, 'domain': domain_of(uname, stage),
                'lessons': lessons,
            })
        volumes.append({
            'tag': tag, 'book': book, 'stage': stage,
            'grade': d.get('grade'), 'semester': d.get('semester'),
            'pdf': d.get('pdf'), 'pages': d.get('pages'), 'toc_pages': d.get('toc_pages'),
            'notes': d.get('notes', ''), 'units': units_out,
        })
        print(f"{tag} {book}: {len(units_out)} 单元 / "
              f"{sum(len(u['lessons']) for u in units_out)} 节")

    skel = {'edition': cfg['edition'], 'subject': 'math', 'generated': 'auto',
            'volumes': volumes, 'missing_volumes': missing, 'known_gap': cfg['gap']}
    json.dump(skel, open(os.path.join(OUT, '_skeleton.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    # 册际 soft 边：上一册最后一个课时 → 下一册第一个单元
    flatin = []
    for v in volumes:
        if v['units']:
            flatin.append((v['tag'], v['units'][0]['unit_id'],
                           v['units'][-1]['lessons'][-1]['id'] if v['units'][-1]['lessons'] else None))
    for i in range(len(flatin) - 1):
        a_tag, _, a_last = flatin[i]
        b_tag, b_first, _ = flatin[i + 1]
        if a_last and b_first:
            deps.append({'from': a_last, 'to': b_first, 'type': 'soft',
                         'reason': f'册际衔接：{a_tag} → {b_tag}'})

    # 每册一份派单（结构 + 空位）
    for v in volumes:
        shard = {
            'tag': v['tag'], 'book': v['book'], 'stage': v['stage'],
            'edition': cfg['edition'],
            'grade': v['grade'], 'semester': v['semester'],
            'units': [{
                'unit_id': u['unit_id'], 'unit_name': u['unit_name'],
                'unit_chapter': u['unit_chapter'], 'domain': u['domain'],
                'lessons': [{'id': l['id'], 'name': l['sec_name'],
                             'chapter': l['chapter'], 'page': l['page']}
                            for l in u['lessons']],
            } for u in v['units']],
        }
        json.dump(shard, open(os.path.join(OUT, '_shards', f"{v['tag']}.json"), 'w',
                              encoding='utf-8'), ensure_ascii=False, indent=1)

    json.dump(deps, open(os.path.join(OUT, '_deps.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    nu = sum(len(v['units']) for v in volumes)
    nl = sum(len(u['lessons']) for v in volumes for u in v['units'])
    print(f"\n[{args.subject}] 合计：{len(volumes)} 册 / {nu} 单元点 / {nl} 课时点 / 边 {len(deps)}")
    if missing:
        print(f"缺目录：{missing}（已知缺口：{cfg['gap']}）")


if __name__ == '__main__':
    main()
