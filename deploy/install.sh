#!/usr/bin/env bash
# Installer VPS untuk crypto-signal. Jalankan sekali di VPS sebagai root.
# Cara pakai di VPS:
#   sudo bash deploy/install.sh
# Asumsi: kode sudah di-clone ke /opt/crypto-signal
set -euo pipefail

APP_DIR="/opt/crypto-signal"
SERVICE_DIR="/etc/systemd/system"

echo "[1/5] Cek direktori $APP_DIR"
if [ ! -f "$APP_DIR/main.py" ]; then
  echo "ERROR: $APP_DIR/main.py tidak ditemukan."
  echo "Clone dulu, misal:"
  echo "  sudo mkdir -p /opt/crypto-signal"
  echo "  sudo chown \$USER:\$USER /opt/crypto-signal"
  echo "  git clone <URL_REPO_ANDA> /opt/crypto-signal"
  exit 1
fi

echo "[2/5] Buat venv + install deps"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "[3/5] Siapkan .env"
if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo "WAJIB: edit $APP_DIR/.env lalu isi TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, ADMIN_SECRET"
  echo "  sudo nano $APP_DIR/.env"
  echo "  # buat ADMIN_SECRET acak: openssl rand -hex 16"
else
  echo ".env sudah ada, dilewati."
fi

echo "[4/5] Install systemd service + timer"
cp "$APP_DIR/deploy/scraper.service" "$APP_DIR/deploy/scraper.timer" "$APP_DIR/deploy/bot.service" "$APP_DIR/deploy/marketing.service" "$SERVICE_DIR/"
systemctl daemon-reload
systemctl enable --now scraper.timer bot.service marketing.service

echo "[5/5] Status"
systemctl list-timers | grep -i scraper || true
systemctl is-active bot.service || journalctl -u bot.service --no-pager -n 20 || true
systemctl is-active marketing.service || journalctl -u marketing.service --no-pager -n 20 || true

echo ""
echo "Selesai. Uji manual:"
echo "  $APP_DIR/.venv/bin/python $APP_DIR/main.py"
echo "Lihat log:"
echo "  journalctl -u bot.service -f"
echo "  journalctl -u marketing.service -f"
echo "  journalctl -u scraper.service --no-pager -n 50"
