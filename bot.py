"""Bot Telegram berlangganan.

Perintah:
  /start      - daftar & info paket
  /harga      - harga terbaru (semua pengguna, versi ringkas)
  /premium    - cara berlangganan
  /aktivasi <kode> - aktivasi premium dengan voucher unik
  /status     - cek status langganan
  
Admin:
  /generate_voucher - buat kode unik (hanya admin)
"""
import logging
import time
import requests

import config
import notifier
import sources
import storage

log = logging.getLogger("bot")

HELP_TEXT = (
    "🤖 *Bot Sinyal Harga VIP*\n\n"
    "/harga - Lihat harga terbaru\n"
    "/premium - Info & harga langganan\n"
    "/status - Cek status langgananmu\n"
    "/aktivasi <kode> - Aktifkan premium\n"
)

def _api(method: str, **params):
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/{method}"
    resp = requests.post(url, json=params, timeout=40)
    return resp.json()

def _get_updates(offset: int | None):
    return _api("getUpdates", offset=offset, timeout=30)

def handle_command(chat_id: str, username: str | None, text: str) -> None:
    storage.upsert_subscriber(chat_id, username)
    parts = text.strip().split()
    cmd = parts[0].lower() if parts else ""

    if cmd == "/start":
        notifier.send_message(chat_id, HELP_TEXT, parse_mode="Markdown")

    elif cmd == "/harga":
        prices = sources.fetch_prices()
        if not prices:
            notifier.send_message(chat_id, "Maaf, gagal mengambil harga.")
            return
        
        premium = storage.is_premium(chat_id)
        lines = []
        for p in prices:
            if premium:
                # Premium melihat volume dan persen lengkap
                vol_m = p.volume_24h / 1_000_000 if p.volume_24h else 0
                lines.append(f"💎 {p.coin.upper()}: {p.price:,.2f} ({p.change_24h:+.2f}%) | Vol: ${vol_m:,.1f}M")
            else:
                # free: hanya 1 koin tanpa detail
                lines.append(f"🟢 {p.coin.upper()}: {p.price:,.2f}")
        
        if premium:
            body = "\n".join(lines)
            notifier.send_message(chat_id, "🤖 *Laporan Premium*\n" + body, parse_mode="Markdown")
        else:
            body = "\n".join(lines[:1])
            tail = (
                "\n\n_...Sinyal ini terlambat 15 menit._\n"
                "🚨 *3 Koin lain sedang mengalami lonjakan volume tinggi (Whale Alert)!*\n"
                "💎 Upgrade ke Premium (Rp 25.000/bln) untuk akses Real-Time & Volume Scanner. Ketik /premium"
            )
            notifier.send_message(chat_id, body + tail, parse_mode="Markdown")

    elif cmd == "/premium":
        msg = (
            f"💎 *Akses Premium*\n\n"
            f"Harga Promo: *Rp 25.000* / 30 hari\n"
            f"Fitur VIP:\n"
            f"✅ Alert Whale & Volume Spike Real-time\n"
            f"✅ Unlock semua koin crypto\n"
            f"✅ Analisis persentase detail\n\n"
            f"Cara Bayar: Transfer ke BCA / GoPay (Hubungi Admin @UsernameAdmin).\n"
            f"Setelah dapat kode, kirim: `/aktivasi PREM-XXXX`"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown")

    elif cmd == "/aktivasi":
        if len(parts) < 2:
            notifier.send_message(chat_id, "Format: /aktivasi <kode_voucher>")
            return
        code = parts[1].strip().upper()
        
        # Dukungan legacy untuk ADMIN_SECRET lama, jika terpaksa
        if config.ADMIN_SECRET and code == config.ADMIN_SECRET.upper():
            until = storage.activate_premium(chat_id, config.PREMIUM_DURATION_DAYS)
            notifier.send_message(chat_id, f"✅ [LEGACY] Premium aktif sampai {until[:10]}. Segera gunakan sistem voucher baru.")
            return

        success, msg = storage.claim_voucher(code, chat_id)
        if success:
            notifier.send_message(chat_id, f"💎 *SELAMAT!* Akunmu sudah Premium.\nBerlaku sampai: {msg[:10]}", parse_mode="Markdown")
            # Beritahu admin ada yang aktivasi
            if config.TELEGRAM_ADMIN_CHAT_ID:
                notifier.send_message(config.TELEGRAM_ADMIN_CHAT_ID, f"💎 Aktivasi Voucher: @{username} (ID:{chat_id}) memakai {code}")
        else:
            notifier.send_message(chat_id, f"❌ Gagal: {msg}")

    elif cmd == "/status":
        if storage.is_premium(chat_id):
            row = storage.get_subscriber(chat_id)
            notifier.send_message(chat_id, f"✅ *Status: PREMIUM*\nBerlaku sampai {row['premium_until'][:10]}.", parse_mode="Markdown")
        else:
            notifier.send_message(chat_id, "Kamu pengguna FREE. Ketik /premium untuk upgrade.")

    elif cmd == "/generate_voucher":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return
        code = storage.create_voucher(30)
        notifier.send_message(chat_id, f"Voucher 30 hari berhasil dibuat:\n\n`{code}`", parse_mode="Markdown")

    else:
        notifier.send_message(chat_id, "Perintah tidak dikenal.\n\n" + HELP_TEXT, parse_mode="Markdown")

def run_polling() -> None:
    config.require_telegram()
    storage.init_db()
    log.info("Bot polling dimulai.")
    offset = None
    while True:
        try:
            updates = _get_updates(offset)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                message = upd.get("message") or upd.get("edited_message")
                if not message:
                    continue
                chat = message.get("chat", {})
                chat_id = str(chat.get("id"))
                username = chat.get("username", "Unknown")
                text = message.get("text", "")
                if text:
                    handle_command(chat_id, username, text)
        except requests.RequestException as exc:
            log.warning("Error polling: %s", exc)
            time.sleep(5)
        except Exception as exc:
            log.exception("Kesalahan tak terduga: %s", exc)
            time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_polling()
