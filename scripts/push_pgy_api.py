#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 GitHub Git Data API 推送本桶变更（github.com:443 直连不通时的唯一通道）。

做法：远端 head 作 base_tree → 逐文件建 blob → 建 tree → 建 commit → 更新 ref（422 重读 head 再来）。
只覆盖下列显式文件，其余远端文件一律不动。
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

REPO = 'grantleyzyf-spec/cn-k12-dxyc2286'
ROOT = '/Users/a627692/Desktop/cn-k12-dxyc2286'
FILES = [
    'data/physics-bsd-gyy/questions.json',
    'learn/index.json',
    'learn/exam/index.json',
    'diagnose/exam-index.json',
    'learn/exam/data/physics-bsd-gyy-八年级上册.json',
    'learn/exam/data/physics-bsd-gyy-八年级下册.json',
    'learn/exam/data/physics-bsd-gyy-九年级全一册.json',
    'scripts/build_math_exam_docx.py',
    'scripts/build_exam_lecture_docx.py',
    'scripts/build_exam_lecture_booklet.py',
    'scripts/build_pgy_skeleton.py',
    'scripts/gen_pgy_bank_shards.py',
    'scripts/check_pgy_bank.py',
    'scripts/merge_pgy_bank.py',
    'scripts/gen_pgy_exam_specs.py',
    'scripts/check_pgy_exam.py',
    'scripts/gen_pgy_learn_shards.py',
    'scripts/check_pgy_learn.py',
    'scripts/merge_pgy_learn.py',
    'scripts/check_pgy_lecture.py',
    'docs/physics-bsd-gyy.md',
]
MSG = ('feat(physics-bsd-gyy): 北师大版（郭玉英）初中物理桶全链路\n\n'
       '- 结构：3 册 16 章 83 节（目录页视觉逐字抄录），99 点 / 67 先修边\n'
       '- 题库：744 题（一点一片，99 片全 PASS）\n'
       '- 试卷：28 卷（16 章卷 + 3 册期中期末 AB），24 题 120 分\n'
       '- 学层：83 篇 / 190,191 汉字；讲解：28 份\n'
       '- 站点：四处注册 + 三份索引 + 讲解 bundle\n'
       '- 脚本：6 个 pgy 脚本；math 三份 docx 渲染器兼容顶层 items')


def api(path, method='GET', payload=None, raw=False, tries=4):
    tok = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
    url = f'https://api.github.com/repos/{REPO}/{path}'
    last = None
    for i in range(tries):
        try:
            data = json.dumps(payload).encode() if payload is not None else None
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Authorization', f'Bearer {tok}')
            req.add_header('Accept', 'application/vnd.github.raw' if raw else 'application/vnd.github+json')
            if data:
                req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
            return body if raw else json.loads(body.decode() or '{}')
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise SystemExit('API 失败 %s：%s' % (path, last))


def main():
    head = api('git/refs/heads/main')['object']['sha']
    print('远端 head', head[:8])
    entries = []
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print('  ! 缺文件，跳过', rel)
            continue
        b64 = base64.b64encode(open(p, 'rb').read()).decode()
        blob = api('git/blobs', 'POST', {'content': b64, 'encoding': 'base64'})
        entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        print('  blob %-46s %s' % (rel, blob['sha'][:8]))
    tree = api('git/trees', 'POST', {'base_tree': api('git/commits/' + head)['tree']['sha'],
                                     'tree': entries})
    commit = api('git/commits', 'POST', {'message': MSG, 'tree': tree['sha'], 'parents': [head]})
    print('新 commit', commit['sha'][:8])
    for i in range(6):
        try:
            cur = api('git/refs/heads/main')['object']['sha']
            if cur != head:
                print('  远端已前移，重建 tree/commit')
                head = cur
                tree = api('git/trees', 'POST', {'base_tree': api('git/commits/' + head)['tree']['sha'],
                                                 'tree': entries})
                commit = api('git/commits', 'POST', {'message': MSG, 'tree': tree['sha'], 'parents': [head]})
            api('git/refs/heads/main', 'PATCH', {'sha': commit['sha'], 'force': False})
            print('已推送', commit['sha'][:8])
            break
        except SystemExit:
            time.sleep(2)
    else:
        raise SystemExit('推送失败：ref 更新反复冲突')
    check = api('git/refs/heads/main')['object']['sha']
    print('校验：远端 head =', check[:8], '| 一致' if check == commit['sha'] else '| 不一致')


if __name__ == '__main__':
    main()
