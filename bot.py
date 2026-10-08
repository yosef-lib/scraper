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
import dex_screener

log = logging.getLogger("bot")

def get_main_keyboard():
    """Mengembalikan custom keyboard (tombol besar di bawah)."""
    return {
        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "🌐 Tren Global"}, {"text": "🐕 Radar Meme Coin"}],
            [{"text": "🤝 Link Referral"}, {"text": "💎 Upgrade VIP"}],
            [{"text": "👤 Status Akun"}],
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
    elif text == "🌐 Tren Global":
        cmd = "/trending"
    elif text == "🐕 Radar Meme Coin":
        cmd = "/meme"
    elif text == "🤝 Link Referral":
        cmd = "/referral"
    elif text == "💎 Upgrade VIP":
        cmd = "/premium"
    elif text == "👤 Status Akun":
        cmd = "/status"

    keyboard = get_main_keyboard()

    if cmd == "/start":
        # Cek referral dari link (format: /start REF_chatid)
        if len(parts) >= 2 and parts[1].startswith("REF"):
            referrer_id = parts[1].replace("REF", "")
            if referrer_id != chat_id:
                if storage.record_referral(referrer_id, chat_id):
                    # Kasih bonus +7 hari VIP ke referrer
                    row = storage.get_subscriber(referrer_id)
                    if row:
                        storage.activate_premium(referrer_id, 7)
                        notifier.send_message(referrer_id, f"🎉 *BONUS REFERRAL!* Teman Anda baru saja bergabung. Anda mendapat *+7 Hari VIP GRATIS!*", parse_mode="Markdown")
        msg = (
            "🚀 *Selamat datang di Whale Crypto VIP!*\n\n"
            "Bot AI sinyal kripto terlengkap di Indonesia:\n"
            "✅ Sinyal Entry + TP + SL Otomatis\n"
            "✅ Radar Smart Money 20 Koin Top\n"
            "✅ Radar Meme Coin DEX (Solana & ETH)\n"
            "✅ Morning Briefing + Fear & Greed Index\n\n"
            "Gunakan tombol menu di bagian bawah layar untuk mulai! 👇"
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

    elif cmd == "/meme":
        if not storage.is_premium(chat_id):
            notifier.send_message(chat_id, "⚠️ Radar Meme Coin hanya untuk Member VIP/Trial. Klik [Klaim Free Trial] untuk mencoba gratis!", reply_markup=keyboard)
            return
        notifier.send_message(chat_id, "⏳ Memindai DEX radar untuk meme coin Solana & ETH...", reply_markup=keyboard)
        dex_screener.run_dex_radar(broadcast=False)
        # Kirim langsung ke user
        sol_pairs = dex_screener.get_trending_pairs("solana")
        eth_pairs = dex_screener.get_trending_pairs("ethereum")
        all_pairs = sol_pairs[:3] + eth_pairs[:2]
        if not all_pairs:
            notifier.send_message(chat_id, "❌ Tidak ada meme coin yang menarik saat ini. Coba lagi nanti!", reply_markup=keyboard)
            return
        for pair in all_pairs:
            msg = dex_screener.format_dex_alert(pair)
            notifier.send_message(chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True)

    elif cmd == "/referral":
        count = storage.get_referral_count(chat_id)
        ref_link = f"https://t.me/WhaleCryptoVIP_bot?start=REF{chat_id}"
        bonus_days = count * 7
        msg = (
            f"🤝 *PROGRAM REFERRAL VIP*\n\n"
            f"Ajak teman Anda bergabung dan dapatkan:\n"
            f"✅ *+7 Hari VIP GRATIS* untuk setiap 1 teman yang join!\n\n"
            f"📊 Statistik Anda:\n"
            f"👥 Total Teman Diajak: *{count} orang*\n"
            f"🎁 Total Bonus: *+{bonus_days} Hari VIP*\n\n"
            f"🔗 *Link Referral Unik Anda:*\n"
            f"{ref_link}\n\n"
            f"_Bagikan link ini ke teman, grup WA, atau postingan Threads Anda!_"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/trending":
        if not storage.is_premium(chat_id):
            notifier.send_message(chat_id, "⚠️ Fitur Tren Global (Pendeteksi Smart Money On-Chain) hanya untuk Member VIP atau Trial. Klik [Klaim Free Trial] untuk mencoba!", reply_markup=keyboard)
            return
            
        notifier.send_message(chat_id, "⏳ Sedang memindai radar global...", reply_markup=keyboard)
        try:
            resp = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=15)
            data = resp.json()
            coins = data.get("coins", [])[:5]
            
            lines = []
            for idx, c in enumerate(coins):
                item = c["item"]
                lines.append(f"{idx+1}. *{item['symbol'].upper()}* ({item['name']})")
                
            msg = "🌐 *TRENDING GLOBAL MINGGU INI* 🌐\n\nIni adalah 5 koin yang paling banyak diakumulasi dan dicari oleh Smart Money di seluruh dunia saat ini:\n\n"
            msg += "\n".join(lines)
            msg += "\n\n_Gunakan perintah /chart <koin> untuk melihat grafiknya!_"
            msg = msg.replace('\n', '\n')
            notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)
        except Exception as e:
            notifier.send_message(chat_id, "❌ Gagal memindai radar global saat ini.", reply_markup=keyboard)

    elif cmd == "/premium":
        msg = """💎 *AKSES PREMIUM WHALE CRYPTO VIP*

Harga Promo: *Rp 50.000* / 30 Hari

───────────────────
💳 *METODE PEMBAYARAN:*

1️⃣ *TRANSFER BANK (Bebas Biaya Admin):*
🏦 Bank Mandiri: `1420019877454`
👤 a.n: YOSEF PASKAH WAHYUTO

2️⃣ *OTOMATIS 24 JAM (QRIS / E-Wallet):*
👉 https://lynk.id/whaleradar
───────────────────

📩 *SETELAH TRANSFER MANUAL:*
Kirim bukti transfer ke Admin untuk mendapatkan Kode Voucher Aktivasi.

Jika sudah menerima kode voucher, ketik di chat ini:
`/aktivasi PREM-XXXX`"""
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

    elif cmd == "/marketing":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return

        prices = sources.fetch_prices()
        top_gainer = max(prices, key=lambda x: x.change_24h) if prices else None
        coin_name = top_gainer.coin.upper() if top_gainer else "BITCOIN"
        coin_gain = top_gainer.change_24h if top_gainer else 5.4

        post1 = (
            f"📱 *DRAFT THREADS #1 (Storytelling)*\n\n"
            f"Awalnya iseng bikin Bot AI buat mantau gerak-gerik Smart Money di kripto.\n"
            f"Eh tadi botnya nge-detect lonjakan volume di {coin_name} pas harganya masih anteng.\n"
            f"Gak sampe beberapa jam langsung naik +{coin_gain:.1f}% 🔥\n\n"
            f"Buat yang mau nyobain tes Bot AI ini GRATIS 24 jam, klik link Telegram di bio ya!\n"
            f"👉 t.me/WhaleCryptoFree 🚀\n\n"
            f"#crypto #bitcoin #investasi #whaleradar"
        )

        post2 = (
            f"📱 *DRAFT THREADS #2 (Edukasi + Fitur)*\n\n"
            f"Beda grup sinyal biasa vs Bot AI Whale Radar:\n"
            f"❌ Grup biasa: Cuma kasih tebakan tanpa Stop Loss.\n"
            f"✅ Bot AI: Kasih titik Entry, Target Profit 1 & 2, plus Stop Loss murni pakai kalkulasi matematika 24 jam.\n\n"
            f"Hari ini sinyal {coin_name} berhasil tembus Target Profit (+{coin_gain:.1f}%)! 🎯\n\n"
            f"Coba gratis 24 jam di Telegram: @WhaleCryptoVIP_bot"
        )

        notifier.send_message(chat_id, "🚀 *DRAFT MARKETING THREADS HARI INI*\n\nCopas teks di bawah ini langsung ke Threads Anda! 👇", parse_mode="Markdown")
        notifier.send_message(chat_id, post1, parse_mode="Markdown")
        notifier.send_message(chat_id, post2, parse_mode="Markdown")

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
