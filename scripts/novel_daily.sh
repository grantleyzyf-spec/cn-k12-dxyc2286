#!/usr/bin/env bash
# 连载日更：把已发布章数 +N（默认 5），重新生成章节页并推送。
#
#   bash scripts/novel_daily.sh          # 今日 +5 章
#   bash scripts/novel_daily.sh 10       # 本次 +10 章
#   DRY=1 bash scripts/novel_daily.sh    # 只打印将要发布的区间，不改文件
#
# 已发布章数以 novel/xueshen/chapters.json 的 total 为准。
# 源稿不足时生成脚本会停在源稿末章，并在输出里显示实际发布数——看到数字没涨就是需要补写新章节。
set -euo pipefail
cd "$(dirname "$0")/.."

STEP="${1:-5}"
CUR=$(python3 -c "import json;print(json.load(open('novel/xueshen/chapters.json',encoding='utf-8'))['total'])" 2>/dev/null || echo 0)
TARGET=$(( CUR + STEP ))
echo "已发布 ${CUR} 章 → 目标 ${TARGET} 章（本次 +${STEP}）"
[ "${DRY:-0}" = "1" ] && exit 0

python3 scripts/build_novel_pages.py --limit "$TARGET"

NEW=$(python3 -c "import json;print(json.load(open('novel/xueshen/chapters.json',encoding='utf-8'))['total'])")
if [ "$NEW" -le "$CUR" ]; then
  echo "⚠️ 实际发布仍是 ${NEW} 章：源稿已到末章，需要先补写新章节再跑。"
  exit 0
fi

git add novel sitemap-novel.xml
git -c user.name="grantleyzyf-spec" commit -q -m "chore(novel): 日更 ${CUR}→${NEW} 章（$(date +%m-%d)）" || { echo "没有变更可提交"; exit 0; }
for i in 1 2 3; do
  git push -q origin main 2>/dev/null && { echo "已推送：已发布 ${NEW} 章"; break; }
  sleep 10
done
