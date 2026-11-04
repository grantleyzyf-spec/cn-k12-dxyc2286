#!/usr/bin/env bash
# 连载日更：把已发布章数 +N（默认 5），重新生成章节页并发布到正式站点。
#
#   bash scripts/novel_daily.sh          # 今日 +5 章
#   bash scripts/novel_daily.sh 10       # 本次 +10 章
#   DRY=1 bash scripts/novel_daily.sh    # 只打印将要发布的区间，不改文件
#
# 已发布章数以 novel/xueshen/chapters.json 的 total 为准。
# 源稿不足时生成脚本会停在源稿末章，并提示「需要补写新章节」。
#
# 发布通道（2026-11 起）：
#   主发布 = rsync 到腾讯云 /var/www/k12（正式站点走这台机器）
#   副发布 = git push 到 GitHub（后台尽力而为，失败不影响结果）
#   ⛔ 旧版只认 git push：这台 Mac 到 github.com:443 长期 Empty reply，
#      于是「页面生成成功、站点却没更新」，每天报一次失败——已改。
set -uo pipefail
cd "$(dirname "$0")/.."

STEP="${1:-5}"
HOST="${K12_HOST:-ubuntu@146.56.224.154}"
KEY="${K12_KEY:-$HOME/.ssh/id_k12_deploy}"
REMOTE_ROOT="${K12_ROOT:-/var/www/k12}"
SITE="${K12_SITE:-https://xueketupu.com}"

total() { python3 -c "import json;print(json.load(open('$1',encoding='utf-8'))['total'])" 2>/dev/null || echo 0; }

CUR=$(total novel/xueshen/chapters.json)
TARGET=$(( CUR + STEP ))
echo "连载日更：已发布 ${CUR} 章 → 目标 ${TARGET} 章（+${STEP}）"
[ "${DRY:-0}" = "1" ] && exit 0

python3 scripts/build_novel_pages.py --limit "$TARGET" || { echo "❌ 生成失败"; exit 1; }

NEW=$(total novel/xueshen/chapters.json)
if [ "$NEW" -le "$CUR" ]; then
  echo "⚠️ 实际仍是 ${NEW} 章：源稿已到末章，需要先补写新章节再跑。"
  exit 0
fi
echo "生成完成：${NEW} 章（本次新增 $(( NEW - CUR ))）"

# ---------- 主发布：rsync 到正式站点 ----------
PUBLISHED=0
if [ -f "$KEY" ]; then
  if rsync -a --delete --rsync-path="sudo rsync" \
       -e "ssh -i $KEY -o BatchMode=yes -o ConnectTimeout=12 -o ServerAliveInterval=15" \
       novel/ "$HOST:$REMOTE_ROOT/novel/" 2>/tmp/novel_rsync.err; then
    # 书架页 + 两份 sitemap 一起送（sitemap-novel 里的 URL 也随章数变）
    rsync -a --rsync-path="sudo rsync" \
       -e "ssh -i $KEY -o BatchMode=yes -o ConnectTimeout=12" \
       sitemap-novel.xml "$HOST:$REMOTE_ROOT/" 2>>/tmp/novel_rsync.err || true
    PUBLISHED=1
  else
    echo "⚠️ rsync 失败：$(tail -1 /tmp/novel_rsync.err 2>/dev/null)"
  fi
else
  echo "⚠️ 找不到部署密钥 $KEY（跳过服务器发布）"
fi

# 线上复核：抓 chapters.json 的 total，必须等于 NEW
LIVE=$(curl -s --max-time 20 "$SITE/novel/xueshen/chapters.json?cb=$(date +%s)" \
       | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "-")
echo "线上 chapters.json total = ${LIVE}（期望 ${NEW}）"

# ---------- 本地留痕 + GitHub 副发布 ----------
git add novel sitemap-novel.xml >/dev/null 2>&1
git -c user.name="grantleyzyf-spec" commit -q -m "chore(novel): 日更 ${CUR}→${NEW} 章（$(date +%m-%d)）" 2>/dev/null \
  && echo "本地已提交 ${CUR}→${NEW}"

if [ "$PUBLISHED" = "1" ] && [ "$LIVE" = "$NEW" ]; then
  echo "✅ 已发布 ${NEW} 章 → $SITE/novel/"
  # GitHub 只作备份：后台推，失败写一行提示，绝不改退出码
  ( git push -q origin main >/dev/null 2>&1 && echo "　（GitHub 备份已推送）" \
    || echo "　（GitHub 备份未推送，不影响站点）" ) &
  exit 0
fi

# 服务器通道不通时的兜底：GitHub 能通也行（Pages 仍是备份站）
for i in 1 2 3; do
  if git push -q origin main 2>/dev/null; then
    echo "✅ 服务器通道失败，但已推到 GitHub（${NEW} 章）；建议随后手动 rsync 到 $HOST"
    exit 0
  fi
  sleep 15
done

echo "❌ 发布失败：服务器与 GitHub 两条通道都不通（本地已生成 ${NEW} 章，网络恢复后重跑本脚本即可，不会重复发）"
exit 1
