#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版物理桶：6 处卷面硬错 + 1 处模板解析 + 课时 id 前缀统一。

A 部分改卷面（exams/*.json），每处都断言命中，命中不到直接退出；
B 部分把 phy_hNNN / phy_pNNN 统一成 phys_h1NN / phys_p1NN（物理桶内全局替换 + 文件改名），
  映射偏移 +100，避开已有的 phys_h001…phys_h071。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics')


def load_exam(book, paper):
    f = os.path.join(D, 'exams', book, paper + '.json')
    return f, json.load(open(f, encoding='utf-8'))


def items_of(d):
    return {it['no']: it for s in d['sections'] for it in s['items']}


def save(f, d):
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def sub(old, new, text, tag):
    assert old in text, '未命中：%s' % tag
    return text.replace(old, new, 1)


def fix_exams():
    n = 0

    # 1 必修三 第11章 Q24 scoreRule：分流电阻该增大
    f, d = load_exam('必修第三册', '第11章 电路及其应用 测试卷')
    q = items_of(d)[24]
    q['scoreRule'][2] = sub('适当减小并联的分流电阻', '读数偏小说明分流过多，应适当增大并联的分流电阻',
                            q['scoreRule'][2], 'pb3_u03 给分点')
    assert sum(int(re.search(r'(\d+)\s*分$', r).group(1)) for r in q['scoreRule']) == 16
    save(f, d); n += 1
    print('✔ 必修三·11章 Q24 给分点改「增大」')

    # 2 必修三 第13章 Q24(3)：转动与拉出都是磁通量减小，方向相同
    f, d = load_exam('必修第三册', '第13章 电磁感应与电磁波初步 测试卷')
    q = items_of(d)[24]
    q['answer'] = sub('且电流方向与拉出磁场时相反。',
                      '且电流方向与拉出磁场时相同——两种情况下磁通量都在减小，感应电流都要维持原来的磁场方向。',
                      q['answer'], 'pb3_u05 answer(3)')
    q['analysis'] = sub('判断感应电流的统一标准是穿过闭合回路的磁通量是否变化',
                        '判断感应电流的统一标准是穿过闭合回路的磁通量是否变化：拉出与转至平行，磁通量都是减小，感应电流方向因此相同',
                        q['analysis'], 'pb3_u05 analysis')
    save(f, d); n += 1
    print('✔ 必修三·13章 Q24(3) 方向改「相同」')

    # 3 选必一 期中A Q3：Δp = 0 - m(-5) = +1.0 N·s，方向向上 → A
    f, d = load_exam('选择性必修第一册', '期中测试卷A')
    q = items_of(d)[3]
    assert q['answer'] == 'C'
    q['answer'] = 'A'
    q['analysis'] = ('取竖直向上为正方向，落地前速度 v0 = -5 m/s，静止后 v = 0。'
                     '由动量定理，合力的冲量等于动量变化量：I = Δp = 0 - 0.2×(-5) = +1.0 N·s，'
                     '正号表示方向竖直向上，与选项 A 一致。'
                     '这个冲量是重力冲量与地面作用力冲量共同贡献的结果，单个力的冲量不能代表合力冲量。')
    save(f, d); n += 1
    print('✔ 选必一·期中A Q3 答案 C→A（解析按向上为正重写）')

    # 4 选必二 第1章 Q6：解析算出 8.5×10⁻⁵ m，答案应为 A
    f, d = load_exam('选择性必修第二册', '第1章 安培力与洛伦兹力 测试卷')
    q = items_of(d)[6]
    assert q['answer'] == 'C'
    q['answer'] = 'A'
    save(f, d); n += 1
    print('✔ 选必二·1章 Q6 答案 C→A')

    # 5 选必一 第1章 Q24(2)：碰后同速同向 = 完全非弹性碰撞
    f, d = load_exam('选择性必修第一册', '第1章 动量守恒定律 测试卷')
    q = items_of(d)[24]
    q['answer'] = sub('碰后两滑块速度不相等，动能又有损失，属于非弹性碰撞。',
                      '碰后两滑块速度相同且同向（vA = vB = 2.0 m/s，实际已粘在一起运动），动能由 18 J 减为 6 J，'
                      '属于完全非弹性碰撞。',
                      q['answer'], 'px1_u01 answer(2)')
    save(f, d); n += 1
    print('✔ 选必一·1章 Q24(2) 改为完全非弹性碰撞')

    # 6 必二 期末A Q9：倾斜路面 N = mg/cosθ > mg，选项 C 需改成错误项
    f, d = load_exam('必修第二册', '期末测试卷A')
    q = items_of(d)[9]
    for o in q['options']:
        if o['label'] == 'C':
            o['text'] = '汽车对路面的压力小于汽车的重力'
    q['analysis'] = ('路面倾斜后，重力与支持力的合力水平指向弯道圆心，恰好提供转弯所需的向心力，此时轮胎不受侧向摩擦。'
                     '竖直方向平衡：N·cosθ = mg，故支持力 N = mg/cosθ，略大于重力；由牛顿第三定律，汽车对路面的压力大小等于 N，'
                     '同样略大于重力，所以选项 C 说「压力小于重力」是错的。')
    save(f, d); n += 1
    print('✔ 必二·期末A Q9 选项 C 与解析按 N = mg/cosθ 改正')

    # 9 选必三 期末B：19–24 六题解析原为同一句模板，按题改写
    ANALYSES = {
        19: '本题考查阿伏加德罗常数的换算：先由摩尔质量求单个分子的质量，再由总体积与分子体积的关系估算分子直径，'
            '注意 1 cm³ 水的质量取 1 g、结果是数量级估算。',
        20: '本题考查气体实验定律的选择：判断状态参量中哪个不变（等温用玻意耳、等压用盖-吕萨克），'
            '温度一律换成热力学温度，再用 pV/T 检验结果是否自洽。',
        21: '本题考查热力学第一定律 ΔU = W + Q 的符号规则：外界对气体做功 W 取正，气体吸热 Q 取正，'
            '先定符号再代数，最后按 ΔU 的正负判断内能增减。',
        22: '本题考查热力学第二定律的方向性：热量不能自发地从低温物体传到高温物体，效率不可能达到 100%，'
            '与能量守恒并不矛盾。',
        23: '本题考查光电效应：由 Ek = hν - W0 求逸出功与遏止电压，注意遏止电压对应最大初动能，'
            '光强只影响饱和电流、不改变遏止电压。',
        24: '本题考查核反应方程的配平与质量亏损：先由质量数、电荷数守恒定粒子，再由 ΔE = Δm·c² 求释放能量，'
            '其中 1 u 对应 931.5 MeV。',
    }
    f, d = load_exam('选择性必修第三册', '期末测试卷B')
    its = items_of(d)
    for no, txt in ANALYSES.items():
        assert no in its, '缺第 %d 题' % no
        its[no]['analysis'] = txt
    save(f, d); n += 1
    print('✔ 选必三·期末B 第 19–24 题解析按题改写')
    return n


PHY = re.compile(r'\bphy_([hp])(\d{3})\b')


def new_id(m):
    kind, num = m.group(1), int(m.group(2))
    return 'phys_%s%03d' % (kind, num + 100)


def unify_prefix():
    files = []
    for pat in ('**/*.json', '**/*.md', '**/*.txt'):
        files += glob.glob(os.path.join(D, pat), recursive=True)
    files = [f for f in files if '/_text/' not in f]     # 教材原文不动
    changed = 0
    for f in files:
        try:
            s = open(f, encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        if 'phy_h' not in s and 'phy_p' not in s:
            continue
        s2 = PHY.sub(new_id, s)
        if s2 != s:
            open(f, 'w', encoding='utf-8').write(s2)
            changed += 1
    print('内容替换文件数', changed)

    renamed = 0
    for f in glob.glob(os.path.join(D, '**', '*'), recursive=True):
        if not os.path.isfile(f):
            continue
        b = os.path.basename(f)
        nb = PHY.sub(new_id, b)
        if nb != b:
            os.rename(f, os.path.join(os.path.dirname(f), nb))
            renamed += 1
    print('改名文件数', renamed)

    left = 0
    for f in glob.glob(os.path.join(D, '**', '*'), recursive=True):
        if os.path.isfile(f) and '/_text/' not in f and f.endswith(('.json', '.md')):
            if PHY.search(open(f, encoding='utf-8', errors='ignore').read()):
                left += 1
    print('残留 phy_ 引用文件数', left)
    return left


if __name__ == '__main__':
    n = fix_exams()
    left = unify_prefix()
    print('\n卷面修正 %d 处；id 前缀统一后残留 %d 个文件' % (n, left))
    sys.exit(0 if left == 0 else 1)
