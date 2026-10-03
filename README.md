# VPS Mesin Uang — Sinyal Harga Kripto Berlangganan

Sistem otomatis di VPS yang: mengambil harga kripto → menghitung sinyal →
mengirim ringkasan ke admin dan alert ke pelanggan premium → melayani
langganan via bot Telegram.

## ⚠️ Keamanan (WAJIB duluan)
Token Telegram lama di `scraper.py` sudah bocor (pernah ditulis di kode).
1. Buka @BotFather → `/revoke` → pilih bot → dapatkan token **baru**.
2. Simpan token baru HANYA di file `.env` (jangan pernah di kode/git).
3. File `scraper.py` lama sudah dinonaktifkan dan tidak dipakai lagi.

## Struktur
```
config.py     # baca rahasia dari .env
sources.py    # ambil harga (CoinGecko, gratis tanpa key)
analyzer.py   # hitung sinyal (inti produk)
notifier.py   # kirim ke Telegram
storage.py    # SQLite: riwayat harga + pelanggan
main.py       # siklus terjadwal (cron/systemd timer)
bot.py        # bot berlangganan (long polling)
deploy/       # systemd service + timer + install.sh
```

## Deploy ke GitHub (dari laptop)
```bash
cd "/home/yosef/Dokumen/scraper data"
git init
git add .
git commit -m "Siap deploy: crypto signal bot"
# buat repo kosong di github.com, misal: username/crypto-signal
git remote add origin git@github.com:username/crypto-signal.git
git branch -M main
git push -u origin main
```
Yang dipush aman: `.env` dan `*.sqlite3`/`*.csv`/`logs/` otomatis diabaikan
oleh `.gitignore`. Jangan pernah `git add -f .env`.

## Deploy ke VPS (Ubuntu/Debian)
```bash
# 1. Clone ke path standar
sudo mkdir -p /opt/crypto-signal
sudo chown $USER:$USER /opt/crypto-signal
git clone <URL_REPO_ANDA> /opt/crypto-signal
cd /opt/crypto-signal

# 2. Install + aktifkan service (sekali saja)
sudo bash deploy/install.sh

# 3. Isi rahasia lalu restart service
sudo nano /opt/crypto-signal/.env
# isi: TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, ADMIN_SECRET
# ADMIN_SECRET acak: openssl rand -hex 16
sudo systemctl restart scraper.timer bot.service
```

Isi `.env` minimal:
```
TELEGRAM_BOT_TOKEN=<token-baru-dari-BotFather>
TELEGRAM_ADMIN_CHAT_ID=<id-dari-@userinfobot>
COINS=bitcoin,ethereum,solana
ALERT_PERCENT=3.0
ADMIN_SECRET=<kode-acak-untuk-/aktivasi>
```

## Uji manual
```bash
./.venv/bin/python main.py     # sekali jalan: ambil harga + kirim laporan
./.venv/bin/python bot.py      # jalankan bot (Ctrl+C untuk berhenti)
```

## Operasional systemd
```bash
systemctl list-timers | grep scraper   # cek jadwal
journalctl -u bot.service -f           # lihat log bot
journalctl -u scraper.service --no-pager -n 50  # lihat log scraper
```

## Monetisasi
- Free: 1 koin, tanpa detail persen.
- Premium: semua koin, detail 24j, alert realtime.
- Pembayaran manual dulu (transfer/e-wallet) → admin kirim kode.
  Pelanggan jalankan `/aktivasi <kode>` (kode = `ADMIN_SECRET` di `.env`).
- Langkah lanjut: integrasi Telegram Stars / Midtrans, multi-kode per pelanggan,
  dan upgrade ke webhook untuk skala besar.

## Catatan
- `scraper.py` lama dinonaktifkan sebagai referensi belajar; tidak lagi dipakai.
- Ganti `COINS`, `ALERT_PERCENT`, `VS_CURRENCY` di `.env` sesuai kebutuhan.
