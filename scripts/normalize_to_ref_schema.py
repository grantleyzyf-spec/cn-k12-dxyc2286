#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 17 个学科的数据规范化到参考节点结构（cn-math-taxonomy 口径）。

参考节点结构（topics）：
  id, name, domain, grade, semester(上/下), chapter, type, description,
  mastery_criteria[], diagnostic_question{question,answer}, external,
  standards[{id,confidence}]  —— 另保留本库扩展字段 subject/tags/prerequisites/curriculumRef/verified

参考题目结构（questions）：
  id, topicId, difficulty, type, prompt, answer, explanation, verify?, options?

用法：
  python3 scripts/normalize_to_ref_schema.py --check     # 只体检，不落盘
  python3 scripts/normalize_to_ref_schema.py --write     # 就地规范化 + 汇总 data/*.json
"""
import argparse, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

SEM_MAP = {'fall': '上', 'spring': '下', '上': '上', '下': '下', '': '上', None: '上'}
TYPE_OK = {'conceptual', 'procedural', 'reasoning', 'modeling', 'application'}
QUESTION_TYPES = {'choice', 'fill', 'short-answer', 'numeric'}


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def dump(p, obj):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def split_criteria(desc, name):
    """从 description 派生 1–3 条可检测的掌握标准（不改写原意，只切分）。"""
    if not desc:
        return []
    parts = [s.strip(' 。；;，,') for s in re.split(r'[；;。]', desc) if s.strip(' 。；;，,')]
    out = []
    for s in parts:
        if len(s) >= 4 and s not in out:
            out.append(s)
        if len(out) == 3:
            break
    return out


def norm_question(q, subject):
    out = {}
    out['id'] = q.get('id') or ''
    _qtid = q.get('topicId') or q.get('topic_id') or ''
    out['topicId'] = q.get('topicId') or q.get('topic_id') or ''
    prompt = q.get('prompt') or q.get('question') or q.get('stem') or ''
    out['prompt'] = prompt
    out['question'] = prompt                       # 兼容旧前端
    opts = q.get('options') or []
    norm_opts = []
    for i, o in enumerate(opts):
        if isinstance(o, dict):
            lab = str(o.get('label') or chr(65 + i))
            txt = o.get('text') or o.get('label') or ''
            item = {'label': lab, 'text': txt}
            if o.get('correct'):
                item['correct'] = True
            norm_opts.append(item)
        else:  # "A. ß" / "A、ß" / "ß"
            raw = str(o).strip()
            m = re.match(r'^([A-Da-d])\s*[.、．)）:：]?\s*(.*)$', raw)
            if m:
                norm_opts.append({'label': m.group(1).upper(), 'text': m.group(2).strip()})
            else:
                norm_opts.append({'label': chr(65 + i), 'text': raw})
    if norm_opts:
        out['options'] = norm_opts
    ans = str(q.get('answer') or '').strip()
    if not ans:
        for o in norm_opts:
            if o.get('correct'):
                ans = o['label']
                break
    out['answer'] = ans
    # 题型/难度别名纠正：历史学科曾把 difficulty 的值写进 type
    raw_type = (q.get('type') or '').strip()
    DIFFS = {'easy', 'medium', 'hard', 'basic', 'standard'}
    if raw_type in QUESTION_TYPES:
        out['type'] = raw_type
    elif raw_type in DIFFS:
        out['type'] = 'choice' if opts else 'short-answer'
        if not q.get('difficulty'):
            out['difficulty'] = raw_type
    else:
        out['type'] = 'choice' if opts else 'short-answer'
    diff = str(q.get('difficulty') or '').strip()
    if diff in DIFFS:
        out['difficulty'] = diff
    else:
        if len(diff) > 12 and not q.get('explanation'):
            out['explanation'] = diff
        out['difficulty'] = 'standard'
    if q.get('explanation'):
        out['explanation'] = q['explanation']
    if q.get('verify'):
        out['verify'] = q['verify']
    if q.get('subject'):
        out['subject'] = q['subject']
    if not out['id']:
        out['id'] = f"{_qtid}_q{abs(hash(prompt)) % 1000:03d}"
    return out


def norm_topic(t, subject, qmap):
    t = dict(t)
    t['subject'] = t.get('subject') or subject
    t['semester'] = SEM_MAP.get(t.get('semester'), '上')
    t['chapter'] = t.get('chapter') or '未分章'
    t['tags'] = t.get('tags') or []
    t['prerequisites'] = t.get('prerequisites') or []
    t['domain'] = t.get('domain') or t.get('dimension_name') or (t['tags'][0] if t['tags'] else '综合')
    t['type'] = t['type'] if t.get('type') in TYPE_OK else 'conceptual'
    t['mastery_criteria'] = t.get('mastery_criteria') or split_criteria(t.get('description', ''), t.get('name', ''))
    dq = t.get('diagnostic_question')
    if not dq:
        q = qmap.get(t.get('id'))
        if q:
            dq = {'question': q['prompt'], 'answer': str(q.get('answer', ''))}
        else:
            dq = {'question': '', 'answer': ''}
    t['diagnostic_question'] = dq
    t['external'] = bool(t.get('external', False))
    std = t.get('standards')
    if not std:
        ref = t.get('curriculumRef')
        std = [{'id': ref, 'confidence': 'exact'}] if ref else []
    t['standards'] = std
    t.setdefault('verified', bool(t.get('verified', False)))
    # 字段顺序按参考结构
    order = ['id', 'name', 'subject', 'domain', 'grade', 'semester', 'chapter', 'type',
             'description', 'mastery_criteria', 'diagnostic_question', 'external',
             'standards', 'tags', 'prerequisites', 'curriculumRef', 'verified']
    out = {k: t[k] for k in order if k in t}
    for k, v in t.items():                     # 保留额外字段（dimension 等）
        if k not in out:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    subjects = sorted(d for d in os.listdir(DATA) if os.path.isdir(os.path.join(DATA, d)))
    n_topics = n_q = n_deps = 0
    report = []
    all_topics, all_qs, all_deps = [], [], []

    for sub in subjects:
        tp = os.path.join(DATA, sub, 'topics.json')
        qp = os.path.join(DATA, sub, 'questions.json')
        dp = os.path.join(DATA, sub, 'dependencies.json')
        if not os.path.exists(tp):
            continue
        topics = load(tp)
        qs = load(qp) if os.path.exists(qp) else []
        deps = load(dp) if os.path.exists(dp) else []
        qmap = {}
        nq = [norm_question(q, sub) for q in qs]
        for q in nq:
            qmap.setdefault(q['topicId'], q)
        nt = [norm_topic(t, sub, qmap) for t in topics]
        ids = {t['id'] for t in nt}
        nd = [d for d in deps if d.get('from') in ids and d.get('to') in ids]
        # 先修边规范化：type 只留 hard/soft（参考仓库口径），别名归并
        DEP_ALIAS = {'prerequisite': 'hard', 'required': 'hard', 'strong': 'hard',
                     'suggested': 'soft', 'related': 'soft', 'weak': 'soft'}
        fixed = []
        for d in nd:
            t = (d.get('type') or 'hard').strip().lower()
            t = DEP_ALIAS.get(t, t)
            if t not in ('hard', 'soft'):
                t = 'hard'
            fixed.append({'from': d['from'], 'to': d['to'], 'type': t})
        nd = fixed
        filled = sum(1 for t in nt if t['mastery_criteria'] and t['diagnostic_question'].get('question'))
        report.append((sub, len(nt), len(nq), len(nd), filled))
        n_topics += len(nt); n_q += len(nq); n_deps += len(nd)
        all_topics += nt; all_qs += nq; all_deps += nd
        if a.write:
            dump(tp, nt)
            if qs:
                dump(qp, nq)
            if deps:
                dump(dp, nd)

    print(f"{'学科':<22}{'知识点':>6}{'题目':>6}{'先修边':>7}{'结构完整':>8}")
    for r in report:
        print(f"{r[0]:<22}{r[1]:>6}{r[2]:>6}{r[3]:>7}{r[4]:>8}")
    print(f"{'合计':<22}{n_topics:>6}{n_q:>6}{n_deps:>7}")

    if a.write:
        dump(os.path.join(DATA, 'topics.json'), all_topics)
        dump(os.path.join(DATA, 'questions.json'), all_qs)
        dump(os.path.join(DATA, 'dependencies.json'), all_deps)
        print(f"已写汇总：topics {len(all_topics)} / questions {len(all_qs)} / dependencies {len(all_deps)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
