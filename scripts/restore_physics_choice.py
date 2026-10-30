# -*- coding: utf-8 -*-
"""恢复被误转为 fill 的 103 道物理选择题为 4 选项选择题（原始 A/B/C 取自 git HEAD，D 为新增干扰项）。"""
import json, subprocess, sys
from pathlib import Path

P = Path('data/physics/questions.json')
cur = json.loads(P.read_text(encoding='utf-8'))
head = json.loads(subprocess.check_output(['git', 'show', 'HEAD:data/physics/questions.json']))
HM = {q['id']: q for q in head}

D = {
 'phy_q001': '运动还是静止与参照物无关',
 'phy_q002': '读数时要估读到分度值的下一位',
 'phy_q003': '2.5m/s',
 'phy_q004': '弹簧测力计和刻度尺',
 'phy_q005': '声音在液体中不能传播',
 'phy_q006': '频率不同',
 'phy_q007': '用听诊器探测病人心肺情况',
 'phy_q008': '把房间的门窗关紧',
 'phy_q009': '0℃表示没有温度',
 'phy_q010': '塑料',
 'phy_q011': '把粮食装入密封罐中',
 'phy_q012': '夏天冰棍周围冒白气',
 'phy_q013': '日食和月食的形成',
 'phy_q014': '120°',
 'phy_q015': '先变大后不变',
 'phy_q016': '平面镜中看到自己的脸',
 'phy_q017': '除红光外的其他色光',
 'phy_q018': '先会聚后发散',
 'phy_q019': '正立等大的虚像',
 'phy_q020': '凸面镜',
 'phy_q021': '把铁块加热到高温',
 'phy_q022': '铁块切去一半后密度变为原来的一半',
 'phy_q023': '一个物体也能产生力的作用',
 'phy_q024': '500N',
 'phy_q025': '做加速直线运动',
 'phy_q026': '给自行车轴承加滚珠',
 'phy_q027': '图钉的尖端做得很尖',
 'phy_q028': '液体压强只与液体的体积有关',
 'phy_q029': '伽利略斜面实验',
 'phy_q030': '沿水平方向',
 'phy_q031': '0.1N',
 'phy_q032': '密度与水的密度无关',
 'phy_q033': '举着杠铃静止不动',
 'phy_q034': '3:2',
 'phy_q035': '动能减小，势能增大',
 'phy_q036': '天平',
 'phy_q037': '减小提升的物重',
 'phy_q038': '秋天树叶飘落',
 'phy_q039': '用火炉烤手',
 'phy_q040': '2.1×10⁴J',
 'phy_q041': '先带负电后带正电',
 'phy_q042': '电路中有电压且有开关',
 'phy_q043': '串联或并联都互不影响',
 'phy_q044': '36V',
 'phy_q045': '导体的电阻与它两端的电压成正比',
 'phy_q046': '0.05Ω',
 'phy_q047': '其他形式能转化为机械能的过程',
 'phy_q048': '10kW·h',
 'phy_q049': '电流的机械效应',
 'phy_q050': '磁体的中间',
 'phy_q051': '楞次定律',
 'phy_q052': '闭合电路的一部分导体在磁场中静止',
 'phy_q053': '3×10⁶m/s',
 'phy_q054': '天然气',
 'phy_q055': '研究地球自转时，地球可看作质点',
 'phy_q056': '路程是矢量，位移是标量',
 'phy_q057': '平均速率是平均速度的大小',
 'phy_q058': '加速度为零，速度一定为零',
 'phy_q059': '4m/s',
 'phy_q060': '1m',
 'phy_q061': '5m',
 'phy_q062': '只有弹簧才能产生弹力',
 'phy_q063': '滑动摩擦力大小与物体运动速度成正比',
 'phy_q064': '7N',
 'phy_q065': '1.5m/s²',
 'phy_q066': '作用力大于反作用力',
 'phy_q067': '曲线运动的加速度一定为零',
 'phy_q068': '匀速圆周运动',
 'phy_q069': '速度的大小和方向都不变',
 'phy_q070': '沿半径方向背离圆心',
 'phy_q071': '4倍',
 'phy_q072': '3.0×10⁵km/s',
 'phy_q073': '只要有位移就一定有力做功',
 'phy_q074': '合外力做的功等于动量的变化',
 'phy_q075': '物体在粗糙斜面上加速下滑',
 'phy_q076': '电荷量可以凭空产生',
 'phy_q077': '16倍',
 'phy_q078': '电场中某点的场强与该点的试探电荷有关',
 'phy_q079': '负电荷在电势高处电势能大',
 'phy_q080': '电容与两极板间的距离无关',
 'phy_q081': '动量相同的物体，速度一定相同',
 'phy_q082': '在光滑水平面上做匀速圆周运动的小球',
 'phy_q083': '简谐运动的加速度大小不变',
 'phy_q084': '机械波的频率由介质决定',
 'phy_q085': '7m/s',
 'phy_q086': '周期不变但频率改变',
 'phy_q087': '光从光疏介质射入光密介质且入射角大于临界角',
 'phy_q088': '两列波的波长相同',
 'phy_q089': '磁感线是客观存在的曲线',
 'phy_q090': '安培力方向与磁场方向相同',
 'phy_q091': '静止的电荷在磁场中也受洛伦兹力',
 'phy_q092': '磁通量的单位是特斯拉',
 'phy_q093': '感应电动势与线圈匝数无关',
 'phy_q094': '交变电流的频率越高，有效值越大',
 'phy_q095': '匝数之比的平方',
 'phy_q096': '分子之间的引力和斥力不能同时存在',
 'phy_q097': '先增大后减小',
 'phy_q098': '物体对外做功，内能一定减少',
 'phy_q099': '热机的效率可以达到100%',
 'phy_q100': '原子核由质子和电子组成',
 'phy_q101': '光电子的最大初动能与入射光强度成正比',
 'phy_q102': 'γ射线在电场中会发生偏转',
 'phy_q103': '质量亏损说明核反应前后质量数减少',
}

targets = [q for q in cur if q.get('type') == 'fill' and q.get('options') == [] and q.get('answer') in ('A', 'B', 'C')]
print(f'① 目标条数: {len(targets)}  (D 表条数: {len(D)})')

changed = 0
for q in targets:
    o = HM[q['id']]['options']
    assert [x['label'] for x in o] == ['A', 'B', 'C'], q['id']
    assert HM[q['id']]['answer'] == q['answer'], q['id']
    new = [{'label': 'A', 'text': o[0]['text']},
           {'label': 'B', 'text': o[1]['text']},
           {'label': 'C', 'text': o[2]['text']},
           {'label': 'D', 'text': D[q['id']]}]
    q['options'] = new
    q['type'] = 'choice'
    changed += 1

print(f'   实际改数: {changed}')

# 自检 ②
bad = []
for q in cur:
    if q['id'] in D:
        lab = [x['label'] for x in q['options']]
        texts = [x['text'] for x in q['options']]
        if lab != ['A', 'B', 'C', 'D'] or q['answer'] not in lab or len(set(texts)) != 4 \
           or any(not t.strip() for t in texts) or q['type'] != 'choice':
            bad.append(q['id'])
print(f'② 四选项/标签/answer ∈ labels 违规条数: {len(bad)} {bad[:10]}')

from collections import Counter
c = Counter(q.get('type') for q in cur)
print(f'③ 全库 {len(cur)} 题 type 分布: {dict(c)}')

P.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding='utf-8')
print('写回完成:', P)
