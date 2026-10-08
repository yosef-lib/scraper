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
from main import generate_chart_url

log = logging.getLogger("bot")

def get_main_keyboard():
    """Mengembalikan custom keyboard (tombol besar di bawah)."""
    return {
        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "💎 Upgrade VIP"}, {"text": "👤 Status Akun"}],
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

HELP_TEXT = (
    "🤖 *Bot Sinyal Harga VIP*\n\n"
    "Gunakan tombol di bawah untuk navigasi cepat."
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
    if text == "🎫 Klaim Free Trial":
        cmd = "/trial"
    elif text == "📈 Cek Grafik Koin":
        cmd = "/helpchart"
    elif text == "💎 Upgrade VIP":
        cmd = "/premium"
    elif text == "👤 Status Akun":
        cmd = "/status"

    keyboard = get_main_keyboard()

    if cmd == "/start":
        msg = (
            "🚀 *Selamat datang di Whale Crypto VIP!*\n\n"
            "Gunakan tombol menu di bagian bawah layar untuk mulai menggunakan fitur bot."
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/trial":
        success, msg = storage.claim_trial(chat_id)
        if success:
            notifier.send_message(chat_id, f"🎉 *SELAMAT!*\nAnda telah mengaktifkan **Free Trial 24 Jam**.\nBerlaku sampai: {msg[:10]}\n\nAnda sekarang memiliki akses penuh ke fitur On-Demand Chart dan notifikasi Real-Time!", parse_mode="Markdown", reply_markup=keyboard)
            if config.TELEGRAM_ADMIN_CHAT_ID:
                notifier.send_message(config.TELEGRAM_ADMIN_CHAT_ID, f"🔔 *TRIAL DIKLAIM* oleh @{username} (ID:{chat_id})", parse_mode="Markdown")
        else:
            notifier.send_message(chat_id, f"❌ {msg}", reply_markup=keyboard)

    elif cmd == "/helpchart":
        msg = (
            "📈 *FITUR ON-DEMAND CHART*\n\n"
            "Untuk memanggil grafik secara Real-Time, ketik perintah `/chart` diikuti simbol koinnya.\n\n"
            "Contoh:\n"
            "`/chart btc`\n"
            "`/chart sol`\n"
            "`/chart pepe`"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/chart":
        if not storage.is_premium(chat_id):
            notifier.send_message(chat_id, "⚠️ Fitur On-Demand Chart hanya untuk Member VIP atau Trial. Klik [Klaim Free Trial] untuk mencoba!", reply_markup=keyboard)
            return
            
        if len(parts) < 2:
            notifier.send_message(chat_id, "Format salah. Gunakan: `/chart btc`", parse_mode="Markdown", reply_markup=keyboard)
            return
            
        coin_input = parts[1].lower()
        # Pemetaan sederhana
        coin_map = {
            "btc": "bitcoin", "eth": "ethereum", "sol": "solana", "bnb": "binancecoin", 
            "xrp": "ripple", "ada": "cardano", "avax": "avalanche-2", "doge": "dogecoin", 
            "trx": "tron", "dot": "polkadot", "link": "chainlink", "matic": "polygon", 
            "ton": "toncoin", "shib": "shiba-inu", "ltc": "litecoin", "pepe": "pepe", 
            "near": "near", "apt": "aptos", "arb": "arbitrum", "sui": "sui"
        }
        coin_id = coin_map.get(coin_input, coin_input)
        
        notifier.send_message(chat_id, f"⏳ Sedang memproses grafik untuk {coin_id.upper()}...")
        chart_data = sources.fetch_market_chart(coin_id, days=1)
        
        if chart_data:
            chart_url = generate_chart_url(coin_id, chart_data)
            notifier.send_photo(chat_id, chart_url, caption=f"📊 Grafik 24 Jam: *{coin_id.upper()}*", parse_mode="Markdown", reply_markup=keyboard)
        else:
            notifier.send_message(chat_id, f"❌ Gagal mendapatkan data untuk koin {coin_id.upper()}. Pastikan nama koin valid (contoh: btc, sol, ethereum).", reply_markup=keyboard)

    elif cmd == "/premium":
        msg = (
            f"💎 *Akses Premium VIP*\n\n"
            f"Harga Promo: *Rp 50.000* / 30 hari\n"
            f"Fitur VIP:\n"
            f"✅ Auto-Chart: Kirim grafik saat volume melonjak!\n"
            f"✅ On-Demand Chart: Bebas minta grafik 24 jam!\n"
            f"✅ Akses Real-Time Top 20 Koin\n\n"
            f"👉 *Beli Otomatis 24 Jam:*\n"
            f"Klik link: https://lynk.id/whaleradar\n\n"
            f"Setelah bayar via QRIS/GoPay, Anda akan mendapat kode voucher.\n"
            f"Ketik kodenya di chat ini:\n`/aktivasi PREM-XXXX`"
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
            notifier.send_message(chat_id, f"👤 *Status: PREMIUM/TRIAL*\nBerlaku sampai {row['premium_until'][:10]}.", parse_mode="Markdown", reply_markup=keyboard)
        else:
            notifier.send_message(chat_id, "Anda pengguna FREE. Klik tombol [Klaim Free Trial] untuk mencoba fitur VIP.", reply_markup=keyboard)

    elif cmd == "/generate_voucher":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return
        code = storage.create_voucher(30)
        notifier.send_message(chat_id, f"Voucher 30 hari berhasil dibuat:\n\n`{code}`\n\nKirim kode ini ke pembeli.", parse_mode="Markdown")

    else:
        # Jika bukan command, anggap ngobrol biasa
        if not text.startswith("/"):
            notifier.send_message(chat_id, "Gunakan tombol menu cepat di bawah ini 👇", reply_markup=keyboard)
        else:
            notifier.send_message(chat_id, "Perintah tidak dikenal.", parse_mode="Markdown", reply_markup=keyboard)

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
