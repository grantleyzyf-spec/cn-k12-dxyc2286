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
set -uo pipefail

DOMAIN="${DOMAIN:-xueketupu.com}"
REPO="${REPO:-/var/www/k12}"
EMAIL="${EMAIL:-grantleyzyf@gmail.com}"

say() { printf '\n== %s ==\n' "$*"; }
die() { echo "★ $*"; exit 1; }

say "0/6 前置检查"
[ "$(id -u)" = "0" ] || die "请用 sudo 执行：sudo bash $REPO/scripts/server-launch-domain.sh"
[ -f "$REPO/index.html" ] || die "找不到站点目录 $REPO"

MYIP=$(curl -s --max-time 10 https://api.ipify.org || true)
echo "本机公网 IP: ${MYIP:-未知}"

# dig 不一定装（Ubuntu 最小镜像没有）；依次退到 host / getent
resolve() {
  if command -v dig >/dev/null 2>&1; then
    dig +short A "$1" @223.5.5.5 | tail -1
  elif command -v host >/dev/null 2>&1; then
    host -t A "$1" 119.29.29.29 2>/dev/null | awk '/has address/{print $NF; exit}'
  else
    getent ahostsv4 "$1" | awk 'NR==1{print $1}'
  fi
}
DNSIP=$(resolve "$DOMAIN")
echo "$DOMAIN A 记录: ${DNSIP:-（空）}"
[ -z "$DNSIP" ] && die "域名还没解析。先到 DNSPod 给 @ 和 www 各加一条 A 记录指向本机 IP，等 1–10 分钟再跑。"
if [ -n "$MYIP" ] && [ "$DNSIP" != "$MYIP" ]; then
  die "A 记录 $DNSIP ≠ 本机 IP $MYIP，解析指错了，先改正。"
fi

say "1/6 拉取站点"
cd "$REPO" || die "进不去 $REPO"
git pull --ff-only || echo "⚠ git pull 失败（网络或本地改动），继续用现有文件"
grep -o '渝ICP备[0-9]*号-[0-9]' data/site-config.json || echo "⚠ site-config.json 里还没有备案号"

say "2/6 准备 certbot"
if ! command -v certbot >/dev/null 2>&1; then
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y certbot ca-certificates
fi
certbot --version || die "certbot 安装失败"

say "3/6 签发证书（webroot，不动 nginx 配置）"
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  echo "证书已存在，跳过签发"
else
  mkdir -p "$REPO/.well-known/acme-challenge"
  certbot certonly --webroot -w "$REPO" \
    -d "$DOMAIN" -d "www.$DOMAIN" \
    --email "$EMAIL" --agree-tos --no-eff-email --non-interactive \
    || die "签发失败：确认 80 端口对公网开放（腾讯云防火墙）、且 http://$DOMAIN/ 能打开。"
fi

say "4/6 安装 nginx 配置"
mkdir -p /etc/nginx/snippets
[ -f "$REPO/deploy/k12-common.conf" ] || die "缺 deploy/k12-common.conf"
[ -f "$REPO/deploy/nginx-k12.conf" ]  || die "缺 deploy/nginx-k12.conf（仓库还没 pull 到最新）"
cp "$REPO/deploy/k12-common.conf" /etc/nginx/snippets/k12-common.conf
cp "$REPO/deploy/nginx-k12.conf"  /etc/nginx/conf.d/k12.conf
rm -f /etc/nginx/sites-enabled/default

say "5/6 校验并 reload"
nginx -t || die "nginx 配置校验失败，未 reload（站点仍跑在旧配置上）"
systemctl reload nginx

say "6/6 自测"
echo -n "http://$DOMAIN/      → "
curl -s -o /dev/null -w "%{http_code} → %{redirect_url}\n" --max-time 15 "http://$DOMAIN/"
echo -n "https://$DOMAIN/     → "
curl -s -o /dev/null -w "%{http_code}\n" --max-time 20 "https://$DOMAIN/"
echo -n "https://www.$DOMAIN/ → "
curl -s -o /dev/null -w "%{http_code} → %{redirect_url}\n" --max-time 15 "https://www.$DOMAIN/"
echo -n "证书到期: "
echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null \
  | openssl x509 -noout -enddate | cut -d= -f2
echo -n "备案号数据: "
curl -s --max-time 20 "https://$DOMAIN/data/site-config.json"; echo

say "续期"
systemctl list-timers 'certbot*' --no-pager 2>/dev/null | head -3 || true
echo "certbot 自带 systemd timer 自动续期；想现在验证就：sudo certbot renew --dry-run"
