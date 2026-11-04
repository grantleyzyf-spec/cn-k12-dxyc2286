#!/usr/bin/env bash
# 部署静态站到腾讯云轻量应用服务器（Lighthouse）/ CVM（Nginx 托管）
#   前置：本机可 ssh 到服务器；服务器已装 nginx
#   用法：
#     bash scripts/deploy-tencent.sh                                   # 默认 root@146.56.224.154
#     DEPLOY_USER=ubuntu SSH_KEY=~/.ssh/id_k12_deploy bash scripts/deploy-tencent.sh
#   注意：不要用 USER= 传账号 —— macOS 的 USER 是本地登录名（实测会变成 a627692@… 被拒）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${HOST:-146.56.224.154}"        # 腾讯云轻量 · 南京
DEPLOY_USER_="${DEPLOY_USER:-root}"   # 部署账号（不是本地 $USER）
DEST="${DEST:-/var/www/k12}"
SSH_KEY="${SSH_KEY:-}"

SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new)
if [ -n "$SSH_KEY" ]; then
  SSH_OPTS+=(-i "$SSH_KEY" -o IdentitiesOnly=yes)
fi
SSH_CMD="ssh ${SSH_OPTS[*]}"

echo "== 1/3 本地打包 =="
bash "$ROOT/scripts/build-dist.sh" "$ROOT/dist"

echo "== 2/3 上传到 $DEPLOY_USER_@$HOST:$DEST =="
$SSH_CMD "$DEPLOY_USER_@$HOST" "sudo mkdir -p '$DEST' && sudo chown -R \$(id -un) '$DEST'"
rsync -az --delete -e "$SSH_CMD" "$ROOT/dist/" "$DEPLOY_USER_@$HOST:$DEST/"
# 校验：线上 index.html 必须与本地产物逐字节一致
$SSH_CMD "$DEPLOY_USER_@$HOST" "md5sum '$DEST/index.html'" | awk '{print "  线上 index.html md5:", $1}'
md5 -q "$ROOT/dist/index.html" | awk '{print "  本地 index.html md5:", $1}'

echo "== 3/3 装 Nginx 配置并 reload =="
scp ${SSH_KEY:+-i "$SSH_KEY"} "${SSH_OPTS[@]}" "$ROOT/deploy/k12-common.conf" "$DEPLOY_USER_@$HOST:/tmp/k12-common.conf"
scp ${SSH_KEY:+-i "$SSH_KEY"} "${SSH_OPTS[@]}" "$ROOT/deploy/nginx-k12.conf" "$DEPLOY_USER_@$HOST:/tmp/nginx-k12.conf"
$SSH_CMD "$DEPLOY_USER_@$HOST" "sudo mkdir -p /etc/nginx/snippets \
  && sudo cp /tmp/k12-common.conf /etc/nginx/snippets/k12-common.conf \
  && sudo cp /tmp/nginx-k12.conf /etc/nginx/conf.d/k12.conf \
  && sudo nginx -t && sudo systemctl reload nginx"

echo "完成：https://xueketupu.com/  (IP ${HOST})"
