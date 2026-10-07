"""Bot Telegram berlangganan dengan Reply Keyboard.

Perintah Utama:
  /start - Menampilkan menu tombol
"""
import logging
import time
import requests

import config
import notifier
import sources
import storage

log = logging.getLogger("bot")

def get_main_keyboard():
    """Mengembalikan custom keyboard (tombol besar di bawah)."""
    return {
        "keyboard": [
            [{"text": "💰 Cek Harga"}, {"text": "💎 Beli Premium"}],
            [{"text": "👤 Status Akun"}],
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

HELP_TEXT = (
    "🤖 *Bot Sinyal Harga VIP*\n\n"
    "Gunakan tombol di bawah untuk navigasi, atau ketik manual:\n"
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

    # Map text dari tombol ke command logic
    if text == "💰 Cek Harga":
        cmd = "/harga"
    elif text == "💎 Beli Premium":
        cmd = "/premium"
    elif text == "👤 Status Akun":
        cmd = "/status"

    keyboard = get_main_keyboard()

    if cmd == "/start":
        notifier.send_message(chat_id, HELP_TEXT, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/harga":
        prices = sources.fetch_prices()
        if not prices:
            notifier.send_message(chat_id, "Maaf, gagal mengambil harga.", reply_markup=keyboard)
            return
        
        premium = storage.is_premium(chat_id)
        lines = []
        for p in prices:
            if premium:
                vol_m = p.volume_24h / 1_000_000 if p.volume_24h else 0
                lines.append(f"💎 {p.coin.upper()}: {p.price:,.2f} ({p.change_24h:+.2f}%) | Vol: ${vol_m:,.1f}M")
            else:
                lines.append(f"🟢 {p.coin.upper()}: {p.price:,.2f}")
        
        if premium:
            body = "\n".join(lines)
            notifier.send_message(chat_id, "🤖 *Laporan Premium*\n" + body, parse_mode="Markdown", reply_markup=keyboard)
        else:
            body = "\n".join(lines[:1])
            tail = (
                "\n\n_...Sinyal ini terlambat 15 menit._\n"
                "🚨 *3 Koin lain sedang mengalami lonjakan volume tinggi (Whale Alert)!*\n"
                "👉 Upgrade Premium untuk akses Real-Time & Volume Scanner."
            )
            notifier.send_message(chat_id, body + tail, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/premium":
        msg = (
            f"💎 *Akses Premium*\n\n"
            f"Harga Promo: *Rp 50.000* / 30 hari\n"
            f"Fitur VIP:\n"
            f"✅ Auto-Chart: Otomatis kirim grafik gambar saat ada lonjakan!\n"
            f"✅ Alert Whale & Volume Spike Real-time\n"
            f"✅ Unlock semua koin crypto\n\n"
            f"Cara Bayar: Transfer ke BCA (Hubungi Admin).\n"
            f"Setelah dapat kode voucher, ketik di chat ini:\n`/aktivasi PREM-XXXX`"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/aktivasi":
        if len(parts) < 2:
            notifier.send_message(chat_id, "Format: `/aktivasi <kode_voucher>`", parse_mode="Markdown", reply_markup=keyboard)
            return
        code = parts[1].strip().upper()

        success, msg = storage.claim_voucher(code, chat_id)
        if success:
            notifier.send_message(chat_id, f"💎 *SELAMAT!* Akunmu sudah Premium.\nBerlaku sampai: {msg[:10]}", parse_mode="Markdown", reply_markup=keyboard)
            if config.TELEGRAM_ADMIN_CHAT_ID:
                notifier.send_message(config.TELEGRAM_ADMIN_CHAT_ID, f"💎 Aktivasi Voucher: @{username} (ID:{chat_id}) memakai {code}")
        else:
            notifier.send_message(chat_id, f"❌ Gagal: {msg}", reply_markup=keyboard)

    elif cmd == "/status":
        if storage.is_premium(chat_id):
            row = storage.get_subscriber(chat_id)
            notifier.send_message(chat_id, f"✅ *Status: PREMIUM*\nBerlaku sampai {row['premium_until'][:10]}.", parse_mode="Markdown", reply_markup=keyboard)
        else:
            notifier.send_message(chat_id, "Kamu pengguna FREE. Klik tombol [Beli Premium] untuk upgrade.", reply_markup=keyboard)

    elif cmd == "/generate_voucher":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return
        code = storage.create_voucher(30)
        notifier.send_message(chat_id, f"Voucher 30 hari berhasil dibuat:\n\n`{code}`\n\nKirim kode ini ke pembeli.", parse_mode="Markdown")

    else:
        # Jika bukan command, anggap ngobrol biasa
        if not text.startswith("/"):
            notifier.send_message(chat_id, "Gunakan tombol di bawah untuk menu cepat 👇", reply_markup=keyboard)
        else:
            notifier.send_message(chat_id, "Perintah tidak dikenal.\n\n" + HELP_TEXT, parse_mode="Markdown", reply_markup=keyboard)

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
