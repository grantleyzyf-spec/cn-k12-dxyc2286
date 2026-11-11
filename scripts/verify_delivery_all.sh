#!/usr/bin/env bash
# 一点就跑：数学 12 版十链交付件核验（学层 / 讲解合订本 / 试卷 docx / 试卷合订本 /
# 讲解题块 / 逐题对齐 / 答案复算｜讲解↔卷 examId 身份对齐｜讲解答案面锚定｜答案键独立机检）。
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
echo "=== 1/10 技能库七链（学层 / 讲解合订本 / 试卷 docx / 试卷合订本 / 讲解题块 / 逐题对齐 / 答案复算）"
if [ -f "$SKILL/verify_delivery_all.sh" ]; then
  REPO="$REPO" bash "$SKILL/verify_delivery_all.sh" "$@" || rc=1
else
  echo "✗ 找不到技能库门禁：$SKILL/verify_delivery_all.sh（用 SKILL_K12 指定）"; rc=1
fi
echo "=== 8/10 讲解↔卷 examId 身份对齐（孤儿 / 缺讲 / id 笔误）"
"$PY" "$DIR/verify_lecture_exam_id.py" --repo "$REPO" || rc=1
echo "=== 9/10 讲解答案面锚定（题块定位 / 题分 / 结论冲突 / 答案数值落笔）"
"$PY" "$DIR/verify_lecture_answer_anchor.py" --repo "$REPO" --quiet || rc=1
echo "=== 10/10 答案键独立机检（选择结构 / 题干泄答案 / 算式与代值复算）"
"$PY" "$DIR/verify_exam_answer_key.py" --quiet || rc=1
echo "=== 汇总 rc=${rc}（0=全绿）"
exit "$rc"
