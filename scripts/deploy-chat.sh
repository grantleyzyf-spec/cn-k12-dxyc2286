#!/usr/bin/env bash
# 在服务器上安装站内客服（systemd + nginx 反代 + 全站自动注入）。需 sudo。
#   用法（服务器上）：bash /var/www/k12/scripts/deploy-chat.sh
#   前置：/etc/xkt-chat.env 里写好 CHAT_API_KEY（首次运行会生成模板后退出）
set -euo pipefail
ROOT="${ROOT:-/var/www/k12}"
ENVF=/etc/xkt-chat.env
NG=/etc/nginx/conf.d/k12.conf

echo "== 1/6 环境文件 =="
if [ ! -f "$ENVF" ]; then
  sudo tee "$ENVF" >/dev/null <<'EOF'
# xueketupu.com 客服环境变量（600 权限，勿入库）
CHAT_API_KEY=
CHAT_API_BASE=https://api.deepseek.com
CHAT_MODEL=deepseek-chat
PORT=8091
CHAT_DAILY_BUDGET=500
CHAT_IP_DAILY=6
CHAT_MAX_TURNS=12
EOF
  echo "已生成 $ENVF"
  echo "→ 把 CHAT_API_KEY 填进去（DeepSeek 控制台新建的 key），然后重跑本脚本"
  exit 0
fi
if ! sudo grep -q '^CHAT_API_KEY=.\+' "$ENVF"; then
  echo "!! $ENVF 里 CHAT_API_KEY 还是空的，填好再跑"; exit 1
fi
sudo chmod 600 "$ENVF"

echo "== 2/6 知识库 =="
cd "$ROOT"
env -u PYTHONPATH python3 chat/build_kb.py "$ROOT"
sudo mkdir -p chat/state chat/logs
sudo chown -R www-data:www-data chat/state chat/logs

echo "== 3/6 systemd =="
sudo cp deploy/chat/xkt-chat.service /etc/systemd/system/xkt-chat.service
sudo systemctl daemon-reload
sudo systemctl enable --now xkt-chat
sleep 1
sudo systemctl is-active xkt-chat

echo "== 4/6 nginx =="
sudo cp deploy/chat/chat.conf /etc/nginx/snippets/k12-chat.conf
if ! grep -q 'k12-chat.conf' "$NG"; then
  sudo /usr/bin/python3 - "$NG" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
if 'k12-chat.conf' not in s:
    if 'include snippets/k12-common.conf;' in s:
        s = s.replace('include snippets/k12-common.conf;',
                      'include snippets/k12-common.conf;\n    include snippets/k12-chat.conf;', 1)
    else:
        s = s.replace('server {', 'server {\n    include snippets/k12-chat.conf;', 1)
    open(p, 'w').write(s)
    print('patched', p)
PY
fi
sudo nginx -t
sudo systemctl reload nginx

echo "== 5/6 验收 =="
curl -fsS -m 5 http://127.0.0.1:8091/api/chat/health; echo
curl -fsS -m 8 https://xueketupu.com/api/chat/health; echo
curl -fsS -m 8 https://xueketupu.com/ | grep -c 'chat-widget.js' | sed 's/^/首页注入行数: /'

echo "== 6/6 试问一句 =="
curl -sS -m 40 -X POST https://xueketupu.com/api/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"这个网站是做什么的？"}]}' | head -4

echo
echo "完成：https://xueketupu.com/ 右下角出现「客服」按钮"
