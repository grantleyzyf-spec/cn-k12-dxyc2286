#!/usr/bin/env bash
# 站点验收：四页 200 + 数据可解析 + 缓存头 + HTTPS（缺项只报不退出，便于备案期用 IP 跑）
#   用法：bash scripts/verify-site.sh [BASE_URL]
#   例：  bash scripts/verify-site.sh http://1.2.3.4
#         bash scripts/verify-site.sh https://xueketupu.com
set -uo pipefail
BASE="${1:-https://xueketupu.com}"
BASE="${BASE%/}"
fail=0
p() { printf "%-46s %s\n" "$1" "$2"; }

code() { curl -sS -o /dev/null -w '%{http_code}' -m 20 "$1" 2>/dev/null || echo 000; }

echo "=== 1. 页面（应为 200） ==="
for u in / /explore/ /diagnose/ /children/; do
  c=$(code "$BASE$u"); [ "$c" = 200 ] || fail=$((fail+1)); p "$u" "$c"
done

echo "=== 2. 数据（应能 json.load） ==="
tmp=$(mktemp -d)
for f in data/stats.json data/math/topics.json data/math/questions.json; do
  if curl -sS -m 90 -o "$tmp/x.json" "$BASE/$f" 2>/dev/null && /usr/bin/python3 -c "
import json,sys
d=json.load(open('$tmp/x.json'))
n=len(d) if isinstance(d,list) else len(d.keys())
print(n)" >/dev/null 2>&1; then
    n=$(/usr/bin/python3 -c "
import json
d=json.load(open('$tmp/x.json'))
print(len(d) if isinstance(d,list) else len(d.keys()))")
    p "$f" "OK（$n 条）"
  else
    p "$f" "★ 取不到或非 JSON"; fail=$((fail+1))
  fi
done

echo "=== 3. 缓存头 ==="
hdr=$(curl -sSI -m 20 "$BASE/data/stats.json" 2>/dev/null | tr -d '\r' | grep -i '^cache-control' || true)
p "data/stats.json cache-control" "${hdr:-（无，属正常：GitHub Pages/部分托管不设）}"
hdr2=$(curl -sSI -m 20 "$BASE/sw.js" 2>/dev/null | tr -d '\r' | grep -i '^cache-control' || true)
p "sw.js cache-control" "${hdr2:-（无）}"

echo "=== 4. HTTPS / 证书 ==="
case "$BASE" in
  https://*)
    if curl -sSI -m 20 "$BASE/" >/dev/null 2>&1; then p "TLS 握手" "OK"; else p "TLS 握手" "★ 失败"; fail=$((fail+1)); fi
    exp=$(echo | openssl s_client -servername "${BASE#https://}" -connect "${BASE#https://}:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    p "证书到期" "${exp:-未知}"
    ;;
  *) p "HTTPS" "跳过（当前是 http，备案期正常）" ;;
esac

echo
[ "$fail" = 0 ] && echo "✅ 全部通过" || echo "❌ 有 $fail 项不通过"
