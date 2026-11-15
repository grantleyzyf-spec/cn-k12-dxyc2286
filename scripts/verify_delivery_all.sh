#!/usr/bin/env bash
# 一点就跑：数学 12 版十三链交付件核验（学层 / 讲解合订本 / 试卷 docx / 试卷合订本 /
# 讲解题块 / 逐题对齐 / 答案复算｜讲解↔卷 examId 身份对齐｜讲解答案面锚定｜答案键独立机检｜
# 讲解 docx 同源＋合订本版式指纹｜学层 docx 同源＋合订本版式指纹｜试卷 docx 同源＋版式指纹｜
# 试卷合订本同源＋版式指纹｜合订本渲染面（真转 PDF：页码/空白页/页数下限/字体内嵌））。
# 任一链 FAIL ⇒ 退出码 1。
#
# 为什么这层壳：前六+第七链的脚本随技能库走（k12-knowledge-graph-repo/scripts），
# 而 /tmp 里的临时门禁会被系统清理（2026-11-09 的门禁脚本已丢失）；
# 本文件把「技能库七链 + 仓库新增第八链」固化成仓库内可复跑入口。
#
# 用法:
#   bash scripts/verify_delivery_all.sh                 # 全 12 版
#   bash scripts/verify_delivery_all.sh 苏教版 math-sujiao   # 只核一版（版本名 桶名成对传）
#   SKILL_K12=/path/to/skill/scripts bash scripts/verify_delivery_all.sh   # 换技能库路径
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
REPO="${REPO:-$(dirname "$DIR")}"
SKILL="${SKILL_K12:-$HOME/.hermes/profiles/agent2/skills/education/k12-knowledge-graph-repo/scripts}"
rc=0
echo "=== 1/13 技能库七链（学层 / 讲解合订本 / 试卷 docx / 试卷合订本 / 讲解题块 / 逐题对齐 / 答案复算）"
if [ -f "$SKILL/verify_delivery_all.sh" ]; then
  REPO="$REPO" bash "$SKILL/verify_delivery_all.sh" "$@" || rc=1
else
  echo "✗ 找不到技能库门禁：$SKILL/verify_delivery_all.sh（用 SKILL_K12 指定）"; rc=1
fi
echo "=== 8/13 讲解↔卷 examId 身份对齐（孤儿 / 缺讲 / id 笔误）"
"$PY" "$DIR/verify_lecture_exam_id.py" --repo "$REPO" || rc=1
echo "=== 9/13 讲解答案面锚定（题块定位 / 题分 / 结论冲突 / 答案数值落笔）"
"$PY" "$DIR/verify_lecture_answer_anchor.py" --repo "$REPO" --quiet || rc=1
echo "=== 10/13 答案键独立机检（选择结构 / 题干泄答案 / 算式与代值复算 / 答案句算式链 / 解析结论句）"
"$PY" "$DIR/verify_exam_answer_key.py" --quiet || rc=1
echo "=== 11/13 讲解 docx ↔ 现役讲解 JSON 同源（12 版逐份 Jaccard / 汉字比 / 题块头 / 合订本重建 / 旧稿残留 / 合订本版式指纹）"
# 必须带 --all-editions：本链默认只核苏教+苏科两版，而壳声明的是 12 版（11-15 发现的口径缺口）
"$PY" "$DIR/verify_lecture_docx_samesource.py" --all-editions --quiet || rc=1
echo "=== 12/13 学层 docx ↔ 现役学层 JSON 同源（缺件/多余件 / 逐份 Jaccard / 汉字比 / 小标题覆盖 / 合订本正文 / 合订本版式指纹）"
"$PY" "$DIR/verify_learn_docx_samesource.py" --repo "$REPO" --quiet || rc=1
echo "=== 13/13 试卷 docx ↔ 现役卷 JSON 同源（缺件/多余件 / 重渲逐份比对 / 版式指纹零容差 / 合订本目录正文＋合订本版式指纹）"
"$PY" "$DIR/verify_exam_docx_samesource.py" --repo "$REPO" --quiet || rc=1
echo "=== 14/14 合订本渲染面（520 本真转 PDF：页码逐页在位 / 无空白页 / 页数≥分页符+1 / 字体内嵌）"
# 属性指纹证不了「页码真的排出来了」「版面真的没空页」⇒ 这一链真转 PDF（LibreOffice）再判。
# PDF_GATE=0 可跳过（波峰只做轻活时用）；整链约 10–11 分钟。
if [ "${PDF_GATE:-1}" != "0" ]; then
  "$PY" "$DIR/verify_docx_pdf_render.py" --jobs 3 || rc=1
else
  echo "（PDF_GATE=0：跳过渲染面核验）"
fi
echo "=== 汇总 rc=${rc}（0=全绿）"
exit "$rc"
