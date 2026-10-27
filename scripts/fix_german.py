# -*- coding: utf-8 -*-
"""德语（german）学科收口 · 数据归一（幂等）

修的东西（每一项都可在 audit 里复验）：
 1. chapter：由「未分章」改为「课程类型 领域」——依据《普通高中德语课程标准
    （2017年版2020年修订）》表 1（必修／选择性必修／选修 三类课程）。
 2. prerequisites：由 dependencies.json 双向镜像回 topics（原来 60 条边全部未镜像，
    导致 100 个知识点全被当成根节点）。
 3. root_reason：镜像后仍无先修的知识点补写根节点依据。
 4. tags：补 [领域, 主题] 两级标签（原来 100 个全空）。
 5. mastery_criteria：ger_h058 / ger_h060 原来为空；同时把「关键词式」描述改写成
    可测量的掌握标准。
 6. description：61 条过短（最短 3 字，前端详情卡读起来像残句）改写为完整表述。
 7. difficulty：原来 100 题全是 standard，按知识点难度重新分 basic/standard/hard 三档。
 8. prompt：46 条短题干（最短 6 字）补足语境；ger_h086 原题干与 ger_h064 完全重复
    （连解析都一样），整体重写为「连接词运用」的题。
 9. type：拼读／构词／变位／词尾／语序这类「规则运用」知识点细分为 procedural。

用法：python3 scripts/fix_german.py [--check]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "german")

# ---------------------------------------------------------------- 册次（课标表1）
BOOK = {
    10: "必修",                    # 综合德语，6 学分，高中第 1—2 学期
    11: "选择性必修",              # 文化与科学／社会与世界 专题，8 学分，第 3—4 学期
    12: "选修",                    # 兴趣型／加强型，第 5—6 学期及自选
}
BOOK_NOTE = {
    "必修": "必修（综合德语，高中第1—2学期）",
    "选择性必修": "选择性必修（文化与科学／社会与世界，高中第3—4学期）",
    "选修": "选修（兴趣型／加强型，高中第5—6学期）",
}

# ---------------------------------------------------------------- 描述与掌握标准改写
# id -> (description, [mastery_criteria...])
ENRICH = {
    "ger_h003": ("ä/ö/ü 三个变元音的圆唇发音、长短音与书写形式（含 ae/oe/ue 替代写法）。",
                 ["能正确发出 ä/ö/ü 的圆唇音并区分长短音",
                  "能在无变音符号的键盘上写出 ae/oe/ue 替代形式"]),
    "ger_h005": ("德语多音节词划分音节、判断词重音位置的规则：词重音多落在首音节，be-/ge-/ver-/ent- 等前缀不重读。",
                 ["能把多音节单词正确划分音节并标出重音位置"]),
    "ger_h007": ("字母与音素（Graphem-Phonem）的对应关系，覆盖 ch、sch、sp/st、v、z 等常考拼读规则。",
                 ["能按拼读规则读出未见过的德语单词"]),
    "ger_h008": ("德语口语中词尾 e 的省音（hab' ich）与相邻音的自然连读现象。",
                 ["能识别并模仿口语中的连读与省音形式"]),
    "ger_h009": ("英语、法语外来词进入德语后的读音德语化规律（Team、Restaurant、Chance 等）。",
                 ["能按德语化读音读常见外来词"]),
    "ger_h010": ("通过听音辨词建立语音与拼写的对应关系，减少变元音与特殊字符的拼写错误。",
                 ["能听写出包含变元音与 ß 的单词"]),
    "ger_h013": ("家庭成员称谓（Oma/Großmutter、Tante、Cousin 等）及用第一格、第二格描述亲属关系。",
                 ["能用德语称谓介绍自己的家庭成员及关系"]),
    "ger_h015": ("食物饮料词汇、点餐常用语（ich möchte…、die Rechnung）与餐馆场景交际句式。",
                 ["能在餐馆场景完成点餐与结账的基本对话"]),
    "ger_h016": ("交通工具、方向表达与问路用语（Wie komme ich zum Bahnhof?）。",
                 ["能用德语问路并说明前往某地的交通方式"]),
    "ger_h017": ("身体部位名称、常见疾病症状与就医表达（Kopfschmerzen、zum Arzt gehen）。",
                 ["能描述身体不适并完成简单的就医表达"]),
    "ger_h018": ("职业名称（含女性形式 -in）、工作场所与职业选择的常用表达。",
                 ["能介绍自己或他人的职业与工作场所"]),
    "ger_h019": ("商店类型、价格询问（Was kostet das?）与付款方式的词汇和句套。",
                 ["能在商店完成询价与付款的基本交际"]),
    "ger_h020": ("天气现象（es schneit/regnet）、四季名称与天气预报句式。",
                 ["能描述不同季节的天气状况"]),
    "ger_h021": ("房间名称、家具陈设与租房（eine Wohnung mieten）场景词汇。",
                 ["能介绍自己的住处与房间布置"]),
    "ger_h022": ("运动、娱乐、度假类爱好词汇，以及表达喜好的句型（gern、lieber）。",
                 ["能说明自己的爱好并询问他人的爱好"]),
    "ger_h023": ("情绪词汇与性格形容词（glücklich、fröhlich、ruhig、fleißig 等）。",
                 ["能用形容词描述人物性格与当前情绪"]),
    "ger_h024": ("自然现象与环保主题词汇（Umweltschutz、Mülltrennung、erneuerbare Energie）。",
                 ["能用德语谈论环保措施与自然现象"]),
    "ger_h025": ("互联网、手机、社交媒体相关词汇（Smartphone、soziale Medien、herunterladen）。",
                 ["能描述常用数字设备与网络行为的德语表达"]),
    "ger_h026": ("国家政体、公民权利与社会议题词汇（Bundesrepublik、Bürgerrecht、Wahl）。",
                 ["能用德语表述基本政治制度与社会议题"]),
    "ger_h027": ("德语复合词的构成方式与拆解方法：末词决定词性与性数格（Haus+tür → Haustür）。",
                 ["能把长复合词拆成词素并判断词性"]),
    "ger_h028": ("前缀（be-、ver-、ent-、er-、ge-）与后缀（-ung、-heit、-keit、-lich）构成的派生词及词性变化。",
                 ["能通过前缀后缀判断派生词的词性与含义"]),
    "ger_h029": ("常见近义词组的语义与语用差别（fast/bald、wissen/kennen、lernen/studieren）。",
                 ["能在语境中辨析近义词并选词正确"]),
    "ger_h030": ("动词＋介词的固定搭配与常用短语（aufpassen auf、sich interessieren für）。",
                 ["能正确搭配动词与介词并用于造句"]),
    "ger_h036": ("第一格作主语与表语（sein/werden 之后）的用法，以及在句中的位置。",
                 ["能识别句中作主语或表语的第一格名词"]),
    "ger_h037": ("第四格作直接宾语，以及 durch/für/gegen/ohne/um 等介词后的第四格用法。",
                 ["能把直接宾语与方向性介词后的名词变到第四格"]),
    "ger_h038": ("第三格作间接宾语，以及 aus/bei/mit/nach/zu 等介词后的第三格与静态位置表达。",
                 ["能把间接宾语与静态位置名词变到第三格"]),
    "ger_h039": ("第二格表示所属关系，以及 wegen/trotz/während 等介词后的第二格用法。",
                 ["能用第二格表达所属关系"]),
    "ger_h040": ("动词原形、词干（Stamm）的切分方法，以及不定式在句末的位置。",
                 ["能从变位形式还原动词原形并切出词干"]),
    "ger_h041": ("规则动词（弱变化）现在时的人称词尾变位规则，以及词干以 -t/-d 结尾时插入 e 的处理。",
                 ["能写出规则动词六个人称的现在时形式"]),
    "ger_h042": ("强变化（不规则）动词现在时的词干元音换音（a→ä）与变音（e→i/ie）。",
                 ["能正确写出 sprechen、fahren 等强变化动词的 du/er 形式"]),
    "ger_h043": ("可分前缀动词在主句中前缀后置、在从句与不定式中重新合并的句式规则。",
                 ["能正确安排可分动词在各类句式中的位置"]),
    "ger_h050": ("用 hatte/war ＋ 第二分词表示先于过去某一时点发生的动作，即“过去的过去”。",
                 ["能用过去完成时表达先于过去动作的事件"]),
    "ger_h053": ("虚拟式 I 的构成及其在间接引语中的用法（er sei、er habe）。",
                 ["能用虚拟式 I 转述他人的话"]),
    "ger_h055": ("形容词原级形式及其作表语、定语时的基本用法。",
                 ["能使用形容词原级作表语与定语"]),
    "ger_h056": ("比较级的构成（-er）与比较句 als 的用法，以及 gut/viel/gern 的不规则比较级。",
                 ["能写出比较级并构造 als 比较句"]),
    "ger_h058": ("定冠词（der/die/das）后形容词的弱变化词尾：单数第一格与阴中性用 -e，其余格位用 -en。",
                 ["能写出定冠词后形容词在各格位的正确词尾"]),
    "ger_h059": ("不定冠词（ein/eine）后形容词的混合变化词尾：随性数格在 -e、-er、-en 之间切换。",
                 ["能写出不定冠词后形容词在各格位的正确词尾"]),
    "ger_h060": ("无冠词时形容词的强变化词尾：由形容词自身承担示格任务（guter Wein、frisches Brot）。",
                 ["能写出无冠词时形容词在各格位的强变化词尾"]),
    "ger_h061": ("陈述句主句中变位动词固定在第二位的规则（Verbzweitstellung）。",
                 ["能正确安排主句中变位动词的位置"]),
    "ger_h066": ("快速通读短文、概括中心思想（Hauptaussage）并为其选择恰当标题。",
                 ["能概括短文主旨并选出匹配的标题"]),
    "ger_h067": ("用题干关键词扫描全文、定位具体事实与数据的阅读策略。",
                 ["能按题干关键词定位文中的具体信息"]),
    "ger_h068": ("依据上下文、构词与语篇线索推测生词含义，不急于查词典。",
                 ["能在不查词的情况下推断生词大意"]),
    "ger_h070": ("识别 zuerst/dann/danach/schließlich 等时间标记，梳理事件发生的先后顺序。",
                 ["能按时间标记排出事件的先后顺序"]),
    "ger_h071": ("识别 weil/denn/deshalb/daher 等因果标记，区分原因与结果。",
                 ["能判断句间或段间的因果关系"]),
    "ger_h072": ("通过评价性形容词、情态词与语气判断作者或人物对事件的态度。",
                 ["能从措辞中判断作者的态度与立场"]),
    "ger_h073": ("识别段落之间的并列、递进、转折、因果等逻辑关系与总—分—总结构。",
                 ["能画出篇章的逻辑结构"]),
    "ger_h076": ("诗歌、小说片段的意象、修辞与情感基调的赏析方法。",
                 ["能说出文学片段的主要意象与情感基调"]),
    "ger_h077": ("从表格、柱状图、折线图的标题、图例与数据趋势中提取德语信息。",
                 ["能依据图表数据回答具体问题"]),
    "ger_h078": ("德语主—谓—宾基本句型，以及状语在句中位置的构句方式。",
                 ["能按德语语序造出正确的简单句"]),
    "ger_h079": ("以主题句（Topic sentence）统领、用支撑句展开的段落结构。",
                 ["能围绕主题句写出含支撑句的段落"]),
    "ger_h080": ("叙述事件的六要素（时间、地点、人物、起因、经过、结果）与过去时叙述方式。",
                 ["能写出结构完整的德语记叙短文"]),
    "ger_h081": ("用形容词、比喻与感官细节描写人物、景物与事物的写法。",
                 ["能写出含细节描写的德语短文"]),
    "ger_h082": ("解释事物原理与操作流程的写作方式，常用被动语态与序数连接词。",
                 ["能写出条理清楚的德语说明短文"]),
    "ger_h083": ("以论点、论据、论证三要素展开的议论性写作，含让步与反驳句式。",
                 ["能写出含论点与论据的德语议论段落"]),
    "ger_h084": ("正式书信（Sehr geehrte Damen und Herren）与非正式书信、邮件的格式差别。",
                 ["能按格式写出德语正式邮件"]),
    "ger_h085": ("用第一人称记录个人经历与感受的书面表达，含日期与地点的标注习惯。",
                 ["能写出一则格式规范、语句连贯的德语日记"]),
    "ger_h087": ("从语法、拼写、搭配到表达得体性的分层自查与润色方法。",
                 ["能自查并改正文稿中的语法与拼写错误"]),
    "ger_h089": ("德国 16 个联邦州的名称与首府，以及柏林、汉堡、不来梅三个城市州的特殊地位。",
                 ["能说出主要联邦州及其首府"]),
    "ger_h097": ("德国在欧洲联盟中的角色、欧盟主要机构与总部所在地布鲁塞尔。",
                 ["能说明德国在欧盟中的地位与作用"]),
    "ger_h098": ("德语国家见面礼节、称谓（Sie/du）与日常交往中的礼仪和禁忌。",
                 ["能在跨文化场景中选择恰当的礼节与称谓"]),
    "ger_h099": ("从歌德、席勒到当代德语文学的代表作家与代表作品脉络。",
                 ["能举出德语文学各时期的代表作家与作品"]),
}

# ---------------------------------------------------------------- 题干补足（46 条 <12 字）
PROMPTS = {
    "ger_h004": "德语单词 ich 中的字母组合 ch 应发什么音？",
    "ger_h010": "德语语音阶段的听写（Diktat）训练，主要培养的是哪一项能力？",
    "ger_h012": "在德语中，表示「星期三」的单词是下列哪一个？",
    "ger_h013": "在德语的亲属称谓中，表示「祖母」的单词是哪一个？",
    "ger_h017": "在德语中，表示「头痛」这一症状的单词是哪一个？",
    "ger_h021": "在德语的住房词汇中，表示「客厅」的单词是哪一个？",
    "ger_h022": "在德语中，表示「游泳」这一运动爱好的单词是哪一个？",
    "ger_h023": "德语中表示「高兴的」，与 froh 含义最接近的形容词是哪一个？",
    "ger_h025": "在德语的媒体与科技词汇中，「智能手机」的正确表达是哪一个？",
    "ger_h036": "在德语的四个格中，第一格（主格）承担的语法功能是什么？",
    "ger_h038": "德语第三格（Dativ）在句子中通常用来表示什么人？",
    "ger_h044": "德语动词前缀 be-（如 besuchen、beginnen）属于哪一类前缀？",
    "ger_h050": "德语过去完成时（Plusquamperfekt）的构成方式是哪一种？",
    "ger_h051": "德语第一分词（Partizip I）按「不定式＋哪个字母」构成？",
    "ger_h052": "构成德语被动语态（Vorgangspassiv）时使用的助动词是哪一个？",
    "ger_h053": "德语中用来转述他人原话（间接引语）的虚拟式是哪一种？",
    "ger_h054": "表达与现实相反的假设「如果我有钱」，德语应使用哪种形式？",
    "ger_h057": "形容词 schön 的最高级形式「最漂亮」在德语中写作？",
    "ger_h061": "在德语的陈述性主句中，变位动词固定位于哪个位置？",
    "ger_h063": "德语中要否定一个带不定冠词或无冠词的名词，应使用哪个否定词？",
    "ger_h068": "德语阅读中遇到不认识的生词时，第一步应当采取的策略是？",
    "ger_h071": "下列各组连接词中，用于表达原因与结果关系的是哪一组？",
    "ger_h074": "阅读德语广告类篇章时，最需要抓住的关键信息是哪一类？",
    "ger_h075": "德语新闻报道的导语部分通常集中交代哪些信息？",
    "ger_h077": "阅读带图表的德语篇章时，首先应当关注图表中的哪类信息？",
    "ger_h078": "德语陈述句最基本的语序结构是哪一种？",
    "ger_h079": "组织德语段落时，整段内容必须围绕哪个成分展开？",
    "ger_h080": "德语记叙文写作通常包含六个要素，下列哪一项不属于其中？",
    "ger_h081": "德语描写文写作中最常用来刻画对象的语言手法是哪一种？",
    "ger_h082": "德语说明文写作的主要目的是向读者传达什么？",
    "ger_h083": "德语议论文写作必须具备的三个基本要素是哪些？",
    "ger_h084": "写作德语正式书信时，开头的称呼语应当使用哪种形式？",
    "ger_h085": "德语日记中标注日期与地点时习惯采用的格式是？",
    "ger_h087": "修改德语作文时，第一步应当首先检查哪一方面？",
    "ger_h089": "德国由多少个联邦州组成（其中包含三个城市州）？",
    "ger_h090": "统一后的德意志联邦共和国首都是哪一座城市？",
    "ger_h091": "德国高中毕业时参加的考试及其文凭被称为什么？",
    "ger_h092": "德国慕尼黑每年举办、最著名的民间节日是哪一个？",
    "ger_h093": "德国人传统早餐的典型内容是下列哪一种？",
    "ger_h094": "德国高速公路（Autobahn）区别于多数国家的特点是？",
    "ger_h095": "德国文学名著《浮士德》的作者是哪一位作家？",
    "ger_h096": "两德实现统一、成立统一德国的年份是哪一年？",
    "ger_h097": "欧洲联盟主要机构总部所在的城市是哪一座？",
    "ger_h098": "德语国家的人们初次见面时通常采用的礼节是？",
    "ger_h099": "歌德最著名的代表作是下列哪一部作品？",
    "ger_h100": "TestDaF 属于下列哪一类考试？",
    "ger_h086": "下列各组连接词中，全部表示转折或对立关系的是哪一组？",
}

# ger_h086 原题与 ger_h064 完全重复（题干与解析都一样），按「连接词运用」重写
# 另：ger_h011 原选项 A/C 文本完全相同（等于只有 3 个真选项）；h035/h055/h090 解析<10 字
Q_FIX = {
    "ger_h086": {
        "options": [
            {"label": "A", "text": "aber, sondern, jedoch"},
            {"label": "B", "text": "und, außerdem, sowie"},
            {"label": "C", "text": "weil, da, denn"},
            {"label": "D", "text": "deshalb, daher, also"},
        ],
        "answer": "A",
        "explanation": "aber／jedoch 表转折，sondern 用于否定句之后的更正（nicht…, sondern…）；"
                       "und／außerdem／sowie 表并列递进，weil／da／denn 表原因，deshalb／daher／also 表结果。",
    },
    "ger_h011": {
        "options": [
            {"label": "A", "text": "zwölf"},
            {"label": "B", "text": "zwolf"},
            {"label": "C", "text": "zwelf"},
            {"label": "D", "text": "zwölfe"},
        ],
        "answer": "A",
        "explanation": "12 的德语是 zwölf：必须写变元音 ö，且词尾不加 -e；zwolf 漏变元音，zwelf 元音错，"
                       "zwölfe 是错误加尾。",
    },
    "ger_h035": {
        "explanation": "德语四格中直接宾语用第四格（Akkusativ），间接宾语用第三格（Dativ），"
                       "所属关系用第二格（Genitiv），主语与表语用第一格。",
    },
    "ger_h055": {
        "explanation": "gut 是原级，besser 是比较级，am besten 是最高级；guter 只是带词尾的变格形式，"
                       "不是另一个级。",
    },
    "ger_h090": {
        "explanation": "柏林（Berlin）自 1990 年两德统一后成为德国首都；汉堡、慕尼黑、法兰克福"
                       "虽为重要城市，但不是首都。",
    },
}

# ---------------------------------------------------------------- 难度三档
BASIC = set("""
ger_h001 ger_h002 ger_h003 ger_h004 ger_h005 ger_h006 ger_h007 ger_h010
ger_h011 ger_h012 ger_h013 ger_h014 ger_h015 ger_h016 ger_h019 ger_h020
ger_h031 ger_h032 ger_h033 ger_h034 ger_h035 ger_h036 ger_h037
ger_h040 ger_h041 ger_h045 ger_h055 ger_h061 ger_h062 ger_h063
ger_h066 ger_h067 ger_h078 ger_h088 ger_h089 ger_h090 ger_h092
""".split())
HARD = set("""
ger_h029 ger_h030 ger_h050 ger_h052 ger_h053 ger_h054 ger_h058 ger_h059
ger_h060 ger_h065 ger_h073 ger_h077 ger_h083
""".split())
# 规则运用型（procedural）
PROCEDURAL = set("""
ger_h007 ger_h027 ger_h028 ger_h041 ger_h042 ger_h043 ger_h058 ger_h059
ger_h060 ger_h061
""".split())

# ---------------------------------------------------------------- 主题标签（领域＋子技能）
# 标签取「领域 + 子技能」，与语文学科的 ['识字写字','拼音'] 同一口径；
# 子技能按领域内关键词判定，避免跨领域误标（如「名词的性」不应落到「词汇」）。
SUB_RULES = {
    "语音基础": [("拼写与听写", r"听写|拼音"), ("拼读规则", r"拼读|外来词|连读|字母表"), ("发音", r".")],
    "词汇": [("构词法", r"构词"), ("词义辨析", r"近义|辨析"), ("固定搭配", r"搭配|短语"), ("主题词汇", r".")],
    "语法": [("句法", r"语序|从句|否定|疑问|句"), ("词法", r".")],
    "阅读理解": [("文体阅读", r"广告|新闻|文学|图表"), ("阅读策略", r".")],
    "写作": [("文体写作", r"记叙|描写|说明|议论"), ("应用文", r"书信|日记"), ("写作基础", r".")],
    "文化常识": [("国情文化", r".")],
}

ROOT_REASON = {
    "语音基础": "语音第一环：{name} 是德语语音与拼读体系的入门知识点，图谱内无更早前置；课标必修课程从字母与发音要求起步。",
    "词汇": "主题词群入口：{name} 是「{name}」主题词群的起始项，语义上不依赖其他词汇知识点，故列为根节点。",
    "语法": "语法体系入口：{name} 是德语语法入门的第一个知识点，先修只需字母与发音（语音不计入本图谱连边）。",
    "阅读理解": "阅读策略入口：{name} 属策略性知识，不依赖具体语法点，故图谱内无先修。",
    "写作": "写作技能入口：{name} 是写作训练的第一项技能，先修只需基础句型，图谱内无更早前置。",
    "文化常识": "文化常识独立项：{name} 属文化知识，与语言知识点之间无先修依赖，作为独立根节点。",
}

DEFAULT_DESC = "本知识点覆盖德语{name}的基本要求，对应课标{book}阶段的{domain}培养目标。"


def sub_of(name, domain):
    for kw, pat in SUB_RULES.get(domain, [("综合", r".")]):
        if re.search(pat, name):
            return kw
    return "综合"


def main():
    check = "--check" in sys.argv
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    deps = json.load(open(os.path.join(D, "dependencies.json"), encoding="utf-8"))
    questions = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))

    parents = {}
    for e in deps:
        parents.setdefault(e["to"], []).append(e["from"])

    qmap = {q["topicId"]: q for q in questions}
    changed = {"chapter": 0, "prereq": 0, "root_reason": 0, "tags": 0,
               "desc": 0, "criteria": 0, "type": 0, "prompt": 0, "difficulty": 0}

    for t in topics:
        tid = t["id"]
        book = BOOK.get(t.get("grade"), "选修")
        domain = t.get("domain") or t.get("dimension_name") or "综合"

        # 1. 册次
        ch = "%s %s" % (book, domain)
        if t.get("chapter") != ch:
            t["chapter"] = ch
            changed["chapter"] += 1

        # 2. 先修镜像
        pre = sorted(set(parents.get(tid, [])))
        if t.get("prerequisites") != pre:
            t["prerequisites"] = pre
            changed["prereq"] += 1

        # 3. 根节点依据
        if not pre:
            reason = ROOT_REASON.get(domain, "入门知识点：{name} 图谱内无更早前置。").format(name=t["name"])
            if t.get("root_reason") != reason:
                t["root_reason"] = reason
                changed["root_reason"] += 1
        elif "root_reason" in t:
            del t["root_reason"]

        # 4. 描述与掌握标准
        if tid in ENRICH:
            desc, crit = ENRICH[tid]
            if t.get("description") != desc:
                t["description"] = desc
                changed["desc"] += 1
            if t.get("mastery_criteria") != crit:
                t["mastery_criteria"] = crit
                changed["criteria"] += 1
        elif not t.get("mastery_criteria"):
            t["mastery_criteria"] = [t["name"] + "的基本要求"]
            changed["criteria"] += 1

        # 5. 标签
        tags = []
        for x in [domain, sub_of(t["name"], domain)]:
            if x and x not in tags:
                tags.append(x)
        if t.get("tags") != tags:
            t["tags"] = tags
            changed["tags"] += 1

        # 6. 知识点类型
        want = "procedural" if tid in PROCEDURAL else t.get("type", "conceptual")
        if want not in ("conceptual", "procedural", "reasoning", "modeling", "application"):
            want = "conceptual"
        if t.get("type") != want:
            t["type"] = want
            changed["type"] += 1

        # 7. 难度
        q = qmap.get(tid)
        if q:
            diff = "basic" if tid in BASIC else ("hard" if tid in HARD else "standard")
            if q.get("difficulty") != diff:
                q["difficulty"] = diff
                changed["difficulty"] += 1
            # 8. 题干
            if tid in PROMPTS:
                new_prompt = PROMPTS[tid]
                if q.get("prompt") != new_prompt:
                    q["prompt"] = new_prompt
                    changed["prompt"] += 1
                q["question"] = q["prompt"]
            for k, v in Q_FIX.get(tid, {}).items():
                q[k] = v
            # diagnostic_question 与题库同源
            dq = {"question": q["prompt"], "answer": str(q.get("answer", ""))}
            if t.get("diagnostic_question") != dq:
                t["diagnostic_question"] = dq

    print("变更统计:", changed)
    if check:
        return 0

    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(os.path.join(D, "topics.json"), "a", encoding="utf-8").write("\n")
    json.dump(questions, open(os.path.join(D, "questions.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(os.path.join(D, "questions.json"), "a", encoding="utf-8").write("\n")
    print("已写回 data/german/{topics,questions}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
