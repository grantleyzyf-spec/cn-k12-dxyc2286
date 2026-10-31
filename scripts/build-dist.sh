#!/usr/bin/env bash
# 打包静态站到 ./dist（Cloudflare Pages / 腾讯云 / GitHub Pages 通用）
#   用法：bash scripts/build-dist.sh [输出目录，默认 ./dist]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist}"
rm -rf "$OUT"; mkdir -p "$OUT/data"

cp "$ROOT/index.html" "$ROOT/sw.js" "$ROOT/manifest.webmanifest" "$OUT/"
for f in robots.txt sitemap.xml; do [ -f "$ROOT/$f" ] && cp "$ROOT/$f" "$OUT/"; done
cp -a "$ROOT/assets" "$ROOT/explore" "$ROOT/diagnose" "$ROOT/learn" "$ROOT/children" "$ROOT/contact" "$OUT/"

cp "$ROOT/data/stats.json" "$ROOT/data/cn-curriculum-standards.json" "$OUT/data/"
[ -f "$ROOT/data/site-config.json" ] && cp "$ROOT/data/site-config.json" "$OUT/data/"
[ -f "$ROOT/data/id-aliases.json" ] && cp "$ROOT/data/id-aliases.json" "$OUT/data/"

for d in "$ROOT"/data/*/; do
  name="$(basename "$d")"
  [[ "$name" == "mappings" ]] && continue
  [[ -f "$d/topics.json" ]] || continue
  mkdir -p "$OUT/data/$name"
  for f in topics.json dependencies.json questions.json; do
    [[ -f "$d/$f" ]] && cp "$d/$f" "$OUT/data/$name/$f"
  done
  # 学层讲解正文（课时讲解页要 fetch）：data/<学科>/learn/<册>.json
  [[ -d "$d/learn" ]] && cp -a "$d/learn" "$OUT/data/$name/learn"
done

# 缓存头：Nginx 与 Pages 共用同一份口径说明（Nginx 见 deploy/nginx-k12.conf）
cat > "$OUT/_headers" <<'EOF'
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/data/*
  Cache-Control: public, max-age=300, must-revalidate
/*.html
  Cache-Control: public, max-age=0, must-revalidate
/sw.js
  Cache-Control: public, max-age=0, must-revalidate
EOF

echo "dist → $OUT"
echo "  体积 $(du -sh "$OUT" | awk '{print $1}')｜文件 $(find "$OUT" -type f | wc -l | tr -d ' ')｜最大 $(find "$OUT" -type f -exec ls -l {} + | sort -k5 -rn | head -1 | awk '{printf "%.1fMB", $5/1048576}')"
