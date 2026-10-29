#!/usr/bin/env bash
# 部署静态站到腾讯云轻量应用服务器（Lighthouse）/ CVM（Nginx 托管）
#   前置：本机可 ssh 到服务器；服务器已装 nginx
#   用法：
#     HOST=1.2.3.4 bash scripts/deploy-tencent.sh              # root 用户
#     HOST=1.2.3.4 USER=ubuntu bash scripts/deploy-tencent.sh  # 普通用户（需 sudo 权限）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${HOST:-146.56.224.154}"   # 腾讯云轻量 · 南京
USER_="${USER:-root}"
DEST="${DEST:-/var/www/k12}"

echo "== 1/3 本地打包 =="
bash "$ROOT/scripts/build-dist.sh" "$ROOT/dist"

echo "== 2/3 上传到 $USER_@$HOST:$DEST =="
ssh "$USER_@$HOST" "sudo mkdir -p '$DEST' && sudo chown -R \$(id -un) '$DEST'"
rsync -avz --delete "$ROOT/dist/" "$USER_@$HOST:$DEST/"

echo "== 3/3 装 Nginx 配置并 reload =="
scp "$ROOT/deploy/k12-common.conf" "$USER_@$HOST:/tmp/k12-common.conf"
scp "$ROOT/deploy/nginx-k12.conf" "$USER_@$HOST:/tmp/nginx-k12.conf"
ssh "$USER_@$HOST" "sudo mkdir -p /etc/nginx/snippets \
  && sudo cp /tmp/k12-common.conf /etc/nginx/snippets/k12-common.conf \
  && sudo cp /tmp/nginx-k12.conf /etc/nginx/conf.d/k12.conf \
  && sudo nginx -t && sudo systemctl reload nginx"

echo "完成：http://$HOST/  （备案通过后把域名 A 记录指到该 IP 即可）"
