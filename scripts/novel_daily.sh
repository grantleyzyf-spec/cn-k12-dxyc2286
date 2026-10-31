#!/usr/bin/env bash
# 连载日更：把已发布章数 +N（默认 5），重新生成章节页并推送。
#
#   bash scripts/novel_daily.sh          # 今日 +5 章
#   bash scripts/novel_daily.sh 10       # 本次 +10 章
#   DRY=1 bash scripts/novel_daily.sh    # 只打印将要发布的区间，不改文件
#
# 已发布章数以 novel/xueshen/chapters.json 的 total 为准。
# 源稿不足时生成脚本会停在源稿末章，并提示「需要补写新章节」。
set -uo pipefail
cd "$(dirname "$0")/.."

STEP="${1:-5}"
CUR=$(python3 -c "import json;print(json.load(open('novel/xueshen/chapters.json',encoding='utf-8'))['total'])" 2>/dev/null || echo 0)
TARGET=$(( CUR + STEP ))
echo "连载日更：已发布 ${CUR} 章 → 目标 ${TARGET} 章（+${STEP}）"
[ "${DRY:-0}" = "1" ] && exit 0

python3 scripts/build_novel_pages.py --limit "$TARGET" || { echo "❌ 生成失败"; exit 1; }

NEW=$(python3 -c "import json;print(json.load(open('novel/xueshen/chapters.json',encoding='utf-8'))['total'])")
if [ "$NEW" -le "$CUR" ]; then
  echo "⚠️ 实际仍是 ${NEW} 章：源稿已到末章，需要先补写新章节再跑。"
  exit 0
fi

git add novel sitemap-novel.xml
git -c user.name="grantleyzyf-spec" commit -q -m "chore(novel): 日更 ${CUR}→${NEW} 章（$(date +%m-%d)）" || echo "（没有变更可提交）"

# 远端可能被其他会话推进：先 rebase（自动暂存别人的未提交改动），失败也不阻断
git -c rebase.autoStash=true pull --rebase -q origin main >/dev/null 2>&1 || true

OK=0
for i in 1 2 3 4 5; do
  if git push -q origin main 2>/dev/null; then OK=1; break; fi
  sleep 20
done
if [ "$OK" = "1" ]; then
  echo "✅ 已推送：连载已发布 ${NEW} 章（https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/novel/）"
else
  echo "❌ 推送失败（本地已提交 ${CUR}→${NEW} 章，网络恢复后手动 git push 即可）"
  exit 1
fi
