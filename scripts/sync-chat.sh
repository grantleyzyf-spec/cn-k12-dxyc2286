#!/usr/bin/env bash
# 本机（Mac）运行：把客服相关文件同步到服务器并远程安装。
#   bash scripts/sync-chat.sh            # 默认 ubuntu@146.56.224.154
#   HOST=1.2.3.4 USER_=ubuntu bash scripts/sync-chat.sh
# 会提示输入 SSH 密码（没有装密钥）。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST_="${HOST:-146.56.224.154}"
U="${USER_:-ubuntu}"
DEST="${DEST:-/var/www/k12}"

echo "== 1/2 同步文件到 $U@$HOST_:$DEST =="
rsync -avz --no-perms --no-owner --no-group \
  "$ROOT/chat/" "$U@$HOST_:$DEST/chat/"
rsync -avz --no-perms --no-owner --no-group \
  "$ROOT/assets/chat-widget.js" "$ROOT/assets/chat-widget.css" "$U@$HOST_:$DEST/assets/"
rsync -avz --no-perms --no-owner --no-group \
  "$ROOT/deploy/chat/" "$U@$HOST_:$DEST/deploy/chat/"
rsync -avz --no-perms --no-owner --no-group \
  "$ROOT/scripts/deploy-chat.sh" "$U@$HOST_:$DEST/scripts/"

echo "== 2/2 远程安装 =="
ssh -o ServerAliveInterval=30 "$U@$HOST_" "sudo bash $DEST/scripts/deploy-chat.sh"
