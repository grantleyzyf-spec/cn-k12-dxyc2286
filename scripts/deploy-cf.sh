#!/usr/bin/env bash
# 把 cn-k12-dxyc2286 打包成 Cloudflare Pages 可直传的静态目录，并（可选）部署。
#   用法：
#     bash scripts/deploy-cf.sh --dry                 # 只打包，打印体积与文件数（不联网）
#     bash scripts/deploy-cf.sh                       # 打包 + 部署到 Pages 项目 cn-k12-site
#     PROJECT=cn-k12-site bash scripts/deploy-cf.sh   # 指定项目名
#   前置：npx wrangler login（或 export CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=...）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${PROJECT:-cn-k12-site}"
DIST="${TMPDIR:-/tmp}/cn-k12-pages-dist.$$"
mkdir -p "$DIST/data"
trap 'rm -rf "$DIST"' EXIT

# ---- 1. 静态壳 ----
cp "$ROOT/index.html" "$ROOT/sw.js" "$ROOT/manifest.webmanifest" "$DIST/"
cp -a "$ROOT/assets" "$ROOT/explore" "$ROOT/diagnose" "$ROOT/children" "$DIST/"

# ---- 2. 前端真正 fetch 的数据（按学科拆分，不传归档 *_grade*.json）----
cp "$ROOT/data/stats.json" "$ROOT/data/cn-curriculum-standards.json" "$DIST/data/"
[ -f "$ROOT/data/id-aliases.json" ] && cp "$ROOT/data/id-aliases.json" "$DIST/data/"
for d in "$ROOT"/data/*/; do
  name="$(basename "$d")"
  [[ "$name" == "mappings" ]] && continue
  [[ -f "$d/topics.json" ]] || continue
  mkdir -p "$DIST/data/$name"
  for f in topics.json dependencies.json questions.json; do
    [[ -f "$d/$f" ]] && cp "$d/$f" "$DIST/data/$name/$f"
  done
done

# ---- 3. 缓存策略（Pages 读顶层 _headers）----
cat > "$DIST/_headers" <<'EOF'
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/data/*
  Cache-Control: public, max-age=300, must-revalidate
/*.html
  Cache-Control: public, max-age=0, must-revalidate
/sw.js
  Cache-Control: public, max-age=0, must-revalidate
EOF

# ---- 4. 体积体检 ----
echo "dist: $(du -sh "$DIST" | awk '{print $1}')  files: $(find "$DIST" -type f | wc -l | tr -d ' ')"
echo "最大单文件: $(find "$DIST" -type f -exec ls -l {} + | sort -k5 -rn | head -1 | awk '{printf "%.1fMB %s", $5/1048576, $9}')"
for f in index.html explore/index.html diagnose/index.html children/index.html data/stats.json sw.js; do
  [[ -f "$DIST/$f" ]] && echo "  ✔ $f" || echo "  ✘ 缺 $f"
done

[[ "${1:-}" == "--dry" ]] && { echo "（--dry：未部署）"; exit 0; }

# ---- 5. 部署 ----
npx --yes wrangler@4 pages deploy "$DIST" \
  --project-name "$PROJECT" \
  --branch main \
  --commit-dirty=true
echo "完成：https://$PROJECT.pages.dev/"
