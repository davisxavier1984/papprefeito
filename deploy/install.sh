#!/usr/bin/env bash
#
# Instala papprefeito (backend + frontend + túnel maispap) como serviços systemd.
# Rode como root:  sudo bash deploy/install.sh
#
set -euo pipefail

REPO=/home/davi/python/MG/papprefeito-dev
DEPLOY="$REPO/deploy"
CF_DIR=/home/davi/.cloudflared
ENV_FILE="$REPO/backend/.env"
TUNNEL_ID=7265903e-6db2-44d1-9cf7-24075d472dbb

if [[ $EUID -ne 0 ]]; then
  echo "Precisa de root. Rode: sudo bash deploy/install.sh" >&2
  exit 1
fi

echo "==> 1/5 Pré-condições"
for f in "$CF_DIR/$TUNNEL_ID.json" "$REPO/backend/.venv/bin/uvicorn" "$REPO/frontend/dist/index.html"; do
  [[ -e "$f" ]] || { echo "FALTA: $f" >&2; exit 1; }
done
for porta in 8000 5173; do
  if ss -ltn "sport = :$porta" | grep -q LISTEN; then
    echo "Porta $porta já está ocupada. Libere antes de instalar." >&2
    exit 1
  fi
done
echo "    ok"

echo "==> 2/5 SECRET_KEY do backend"
# config.py traz um default inseguro ("your-secret-key-here-change-in-production").
# Gera uma chave real se o .env não tiver uma, ou se ainda estiver no placeholder.
PLACEHOLDER='your-secret-key-here-change-in-production'
touch "$ENV_FILE"
if grep -q "^SECRET_KEY=${PLACEHOLDER}\$" "$ENV_FILE"; then
  NOVA=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')
  sed -i "s|^SECRET_KEY=${PLACEHOLDER}\$|SECRET_KEY=${NOVA}|" "$ENV_FILE"
  echo "    placeholder substituído por chave nova (tokens JWT antigos ficam inválidos)"
elif grep -q '^SECRET_KEY=' "$ENV_FILE"; then
  echo "    SECRET_KEY já definida no .env — mantida como está"
else
  NOVA=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')
  [[ -s "$ENV_FILE" && -n "$(tail -c1 "$ENV_FILE")" ]] && printf '\n' >> "$ENV_FILE"
  printf 'SECRET_KEY=%s\n' "$NOVA" >> "$ENV_FILE"
  echo "    SECRET_KEY gerada e gravada (tokens JWT antigos ficam inválidos)"
fi
chown davi:davi "$ENV_FILE"
chmod 600 "$ENV_FILE"

echo "==> 3/5 Config do túnel"
install -o davi -g davi -m 644 "$DEPLOY/config-maispap.yml" "$CF_DIR/config-maispap.yml"
runuser -u davi -- /usr/local/bin/cloudflared --config "$CF_DIR/config-maispap.yml" tunnel ingress validate

echo "==> 4/5 Units systemd"
install -m 644 "$DEPLOY/papprefeito-backend.service"  /etc/systemd/system/
install -m 644 "$DEPLOY/papprefeito-frontend.service" /etc/systemd/system/
install -m 644 "$DEPLOY/cloudflared-maispap.service"  /etc/systemd/system/
systemctl daemon-reload

echo "==> 5/5 Subindo serviços"
systemctl enable --now papprefeito-backend.service papprefeito-frontend.service
sleep 2
systemctl enable --now cloudflared-maispap.service
sleep 3

echo
systemctl --no-pager --lines=0 status \
  papprefeito-backend.service \
  papprefeito-frontend.service \
  cloudflared-maispap.service || true

echo
echo "Pronto. Verifique:"
echo "  curl -s https://api-maispap.dasix.site/health"
echo "  curl -sI https://maispap.dasix.site"
