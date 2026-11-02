#!/bin/bash
# 沪教版 Word 交付全量产出（重负载）——只在波谷跑
# 波峰 09:00–12:00 / 14:00–18:00；波谷 12:00–14:00 / 18:00–次日 09:00
set -uo pipefail
cd "$HOME/Desktop/cn-k12-dxyc2286" || exit 1

if ! /usr/bin/python3 scripts/offpeak.py --quiet; then
  echo "[skip] 当前处于波峰（09–12 / 14–18），本轮不启动重负载；下一个波谷见 scripts/offpeak.py"
  exit 0
fi

export MATH_BUCKET=math-hujiao
export MATH_EDITION=沪教版
LOG="/tmp/hj_docx_$(date +%m%d_%H%M).log"
: > "$LOG"

run() {
  local name="$1"; shift
  echo "=== $name ===" | tee -a "$LOG"
  /usr/bin/python3 "$@" 2>&1 | tail -3 | tee -a "$LOG"
}

run "原创试卷 41 卷 × 2 份" scripts/build_math_exam_docx.py
run "试卷讲解 41 份"        scripts/build_exam_lecture_docx.py
run "学层精讲 80 篇"        scripts/build_math_learn_docx.py

OUT="$HOME/Desktop/学科图谱相关资料"
echo "--- 产出清点 ---" | tee -a "$LOG"
for d in 学科图谱原创试卷 试卷讲解 学层精讲; do
  n=$(find "$OUT/$d/数学/沪教版" -name "*.docx" ! -name ".~*" 2>/dev/null | wc -l | tr -d ' ')
  echo "$d: $n 份" | tee -a "$LOG"
done
echo "日志：$LOG"
