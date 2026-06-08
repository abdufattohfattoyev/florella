#!/bin/bash
# Birinchi marta SSL sertifikat olish uchun
# Serverdа bir marta ishga tushiring: bash init-letsencrypt.sh

set -e

DOMAIN="florella-cafe.uz"
EMAIL="abdufattohfattoyev0@gmail.com"
CERTBOT_PATH="./certbot"

echo ">>> Certbot papkalarini yaratish..."
mkdir -p "$CERTBOT_PATH/conf"
mkdir -p "$CERTBOT_PATH/www"

echo ">>> Let's Encrypt tavsiya etilgan sozlamalarni yuklab olish..."
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
    -o "$CERTBOT_PATH/conf/options-ssl-nginx.conf"

curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
    -o "$CERTBOT_PATH/conf/ssl-dhparams.pem"

echo ">>> Vaqtinchalik sertifikat yaratish (nginx ishga tushishi uchun)..."
mkdir -p "$CERTBOT_PATH/conf/live/$DOMAIN"
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "$CERTBOT_PATH/conf/live/$DOMAIN/privkey.pem" \
    -out    "$CERTBOT_PATH/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost" 2>/dev/null

echo ">>> Docker Compose ishga tushirish..."
docker compose up -d web nginx

echo ">>> Vaqtinchalik sertifikatni o'chirish..."
rm -rf "$CERTBOT_PATH/conf/live"

echo ">>> Haqiqiy sertifikat olish..."
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo ">>> Nginx qayta ishga tushirish..."
docker compose exec nginx nginx -s reload

echo ">>> Hammasi tayyor! https://$DOMAIN ochiq."
