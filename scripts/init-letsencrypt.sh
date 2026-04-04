#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# init-letsencrypt.sh
#
# Issues a Let's Encrypt TLS certificate for the first time using the certbot
# webroot challenge served through nginx.
#
# Run ONCE on a fresh VPS before starting the full stack.
#
# Usage:
#   chmod +x scripts/init-letsencrypt.sh
#   ./scripts/init-letsencrypt.sh <domain> <email>
#
# Example:
#   ./scripts/init-letsencrypt.sh example.com admin@example.com
#
# To test against the Let's Encrypt staging environment (no rate limits):
#   STAGING=1 ./scripts/init-letsencrypt.sh example.com admin@example.com
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

DOMAIN="${1:?Usage: $0 <domain> <email>}"
EMAIL="${2:?Usage: $0 <domain> <email>}"
STAGING="${STAGING:-0}"

CERTBOT_CONF="./certbot/conf"
CERTBOT_WWW="./certbot/www"

echo "──────────────────────────────────────────────────────────────────────"
echo "  Domain : ${DOMAIN}"
echo "  SANs   : www.${DOMAIN}, api.${DOMAIN}"
echo "  Email  : ${EMAIL}"
echo "  Staging: ${STAGING}"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

# ── 1. Create certbot working directories ────────────────────────────────────
mkdir -p "${CERTBOT_CONF}/live/${DOMAIN}" "${CERTBOT_WWW}"

# ── 2. Create a temporary self-signed cert so nginx can start ────────────────
#     (nginx requires the cert files to exist at startup when TLS is configured)
echo "▶ Creating temporary self-signed certificate…"
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
  -keyout "${CERTBOT_CONF}/live/${DOMAIN}/privkey.pem" \
  -out    "${CERTBOT_CONF}/live/${DOMAIN}/fullchain.pem" \
  -subj   "/CN=localhost" 2>/dev/null
echo "  ✓ Temporary certificate created."

# ── 3. Start only the nginx container (needed to serve the ACME challenge) ───
echo "▶ Starting nginx with temporary certificate…"
docker compose -f docker-compose.prod.yml up -d nginx
echo "  ✓ nginx started."
sleep 3

# ── 4. Delete the temporary cert (nginx keeps running from memory) ────────────
echo "▶ Removing temporary certificate…"
rm -rf "${CERTBOT_CONF}/live/${DOMAIN}" \
       "${CERTBOT_CONF}/archive/${DOMAIN}" \
       "${CERTBOT_CONF}/renewal/${DOMAIN}.conf"
echo "  ✓ Temporary certificate removed."

# ── 5. Issue the real Let's Encrypt certificate via certbot webroot ───────────
STAGING_ARG=""
if [ "${STAGING}" != "0" ]; then
  STAGING_ARG="--staging"
  echo "  ⚠ Using Let's Encrypt STAGING environment."
fi

echo "▶ Requesting Let's Encrypt certificate…"
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  ${STAGING_ARG} \
  -d "${DOMAIN}" -d "www.${DOMAIN}" -d "api.${DOMAIN}" \
  --email "${EMAIL}" \
  --rsa-key-size 4096 \
  --agree-tos \
  --no-eff-email \
  --force-renewal
echo "  ✓ Certificate issued."

# ── 6. Reload nginx with the real certificate ─────────────────────────────────
echo "▶ Reloading nginx…"
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
echo "  ✓ nginx reloaded with real certificate."

echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "  TLS certificate ready for ${DOMAIN}!"
echo ""
echo "  Start the full stack:"
echo "    docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "  Certificates auto-renew every 12 h via the certbot container."
echo "──────────────────────────────────────────────────────────────────────"
