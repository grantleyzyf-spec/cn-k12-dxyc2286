#!/usr/bin/env bash
# 备案通过后「域名开通」一键脚本 —— 在**服务器上**以 root 执行
#
#   sudo bash /var/www/k12/scripts/server-launch-domain.sh
#
# 做的事（顺序不能换）：
#   1. 确认域名已解析到本机公网 IP（没解析就别往下走，否则 certbot 必失败）
#   2. git pull 取最新站点（含已填好备案号的 data/site-config.json）
#   3. certbot 以 webroot 方式签发 LE 证书（不改 nginx 配置，配置由仓库管）
#   4. 拷贝 deploy/*.conf（此时 443 块才有证书可引用）
#   5. nginx -t && reload，最后自测 http→https 跳转与备案号展示
#
# 前置：腾讯云防火墙已放行 TCP 80 / 443（来源 0.0.0.0/0）
set -euo pipefail

DOMAIN="${DOMAIN:-xueketupu.com}"
REPO="${REPO:-/var/www/k12}"
EMAIL="${EMAIL:-grantleyzyf@gmail.com}"

say() { printf '\n== %s ==\n' "$*"; }

say "0/6 前置检查"
[ "$(id -u)" = "0" ] || { echo "请用 sudo 执行"; exit 1; }
MYIP=$(curl -s --max-time 10 https://api.ipify.org || true)
echo "本机公网 IP: ${MYIP:-未知}"
DNSIP=$(dig +short A "$DOMAIN" @223.5.5.5 | tail -1)
echo "$DOMAIN A 记录: ${DNSIP:-（空）}"
if [ -z "$DNSIP" ]; then
  echo "★ 域名还没解析：先到 DNSPod 加 A 记录 @ / www → 本机 IP，等 1–10 分钟再跑本脚本。"
  exit 1
fi
if [ -n "$MYIP" ] && [ "$DNSIP" != "$MYIP" ]; then
  echo "★ A 记录 $DNSIP ≠ 本机 IP $MYIP，解析错了，先改正。"
  exit 1
fi

say "1/6 拉取站点"
cd "$REPO"
sudo -u "${SUDO_USER:-root}" git pull --ff-only || git pull --ff-only
grep -o '渝ICP备[0-9]*号-[0-9]' data/site-config.json || echo "⚠ site-config.json 里还没有备案号"

say "2/6 安装 certbot"
if ! command -v certbot >/dev/null 2>&1; then
  apt-get update -qq && apt-get install -y certbot
fi
certbot --version

say "3/6 签发证书（webroot，不动 nginx 配置）"
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  echo "证书已存在，跳过签发"
else
  mkdir -p "$REPO/.well-known/acme-challenge"
  certbot certonly --webroot -w "$REPO" \
    -d "$DOMAIN" -d "www.$DOMAIN" \
    --email "$EMAIL" --agree-tos --no-eff-email --non-interactive
fi

say "4/6 安装 nginx 配置"
mkdir -p /etc/nginx/snippets
cp "$REPO/deploy/k12-common.conf" /etc/nginx/snippets/k12-common.conf
cp "$REPO/deploy/nginx-k12.conf"  /etc/nginx/conf.d/k12.conf
rm -f /etc/nginx/sites-enabled/default

say "5/6 校验并 reload"
nginx -t
systemctl reload nginx

say "6/6 自测"
C() { curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" --max-time 15 "$1"; }
echo -n "http://$DOMAIN/      → "; C "http://$DOMAIN/"
echo -n "https://$DOMAIN/     → "; curl -s -o /dev/null -w "%{http_code}\n" --max-time 20 "https://$DOMAIN/"
echo -n "https://www.$DOMAIN/ → "; C "https://www.$DOMAIN/"
echo -n "证书到期: "; echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null \
  | openssl x509 -noout -enddate | cut -d= -f2
echo -n "首页备案号: "; curl -s --max-time 20 "https://$DOMAIN/data/site-config.json"

say "续期"
systemctl list-timers 'certbot*' --no-pager | head -3 || true
echo "certbot 自带 systemd timer，无需手工续期；也可 certonly 后 --dry-run 验证："
echo "  sudo certbot renew --dry-run"
