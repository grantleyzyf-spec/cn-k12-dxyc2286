#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 data/mappings/ 下的教材版本映射文件。

规则：
- 跳过 README.md / *.template.json / schema-mapping.json / volume-map.json
- subject 目录内 topics.json 必须存在
- 每个 topicId 必须能在该学科 topics.json 中找到
- confidence ∈ exact/partial/inferred；volumes 非空（模板除外）
- 同一 topicId 不跨两个版本文件重复（允许 partial/合并时重复，但要在报告里列出）

用法：python3 scripts/validate_mappings.py [--all]
"""
import glob, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
SKIP = {'README.md', 'schema-mapping.json', 'volume-map.json', 'example.template.json'}
CONF = {'exact', 'partial', 'inferred'}


def main():
    files = [p for p in sorted(glob.glob(os.path.join(DATA, 'mappings', '*.json')))
             if os.path.basename(p) not in SKIP]
    if not files:
        print('data/mappings/ 下暂无填充的版本映射（只有 volume-map.json 与模板），跳过。')
        return 0

    errors = []
    seen = defaultdict(list)
    for p in files:
        name = os.path.basename(p)
        try:
            m = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            errors.append(f'{name}: JSON 解析失败 {e}')
            continue
        sub = m.get('subject')
        for k in ('subject', 'edition', 'volumes'):
            if k not in m:
                errors.append(f'{name}: 缺字段 {k}')
        tp = os.path.join(DATA, sub or '', 'topics.json')
        if not os.path.exists(tp):
            errors.append(f'{name}: 学科 {sub} 的 topics.json 不存在')
            continue
        ids = {t['id'] for t in json.load(open(tp, encoding='utf-8'))}
        if not m.get('volumes') and 'template' not in name:
            errors.append(f'{name}: volumes 为空（没有依据就不要交）')
        for v in m.get('volumes') or []:
            for c in v.get('chapters') or []:
                conf = c.get('confidence')
                if conf not in CONF:
                    errors.append(f'{name}: confidence 非法 {conf!r}')
                tids = c.get('topicIds') or []
                if not tids:
                    errors.append(f"{name}: {v.get('volume')}/{c.get('chapter')} 没有 topicIds")
                for t in tids:
                    if t not in ids:
                        errors.append(f'{name}: topicId {t} 不存在于 {sub}')
                    seen[t].append(name)
                if conf == 'inferred' and not c.get('reviewed'):
                    print(f"  ⚠ {name}: {t}. 待教师复核".replace('{t}', '') if False else f"  ⚠ {name}: {c.get('chapter')} 标为 inferred，待教师复核")

    dup = {k: v for k, v in seen.items() if len(set(v)) > 1}
    if dup:
        print(f"  ℹ {len(dup)} 个 topicId 在多个版本文件中出现（合并/拆分场景允许，确认是否标注 partial）")

    if errors:
        print(f'❌ {len(errors)} 处错误：')
        for e in errors[:30]:
            print('  -', e)
        return 1
    print(f'✓ {len(files)} 个版本映射文件校验通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
