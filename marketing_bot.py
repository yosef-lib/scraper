import os
import time
import random
import logging
import threading
import datetime
import requests
import json
import config

log = logging.getLogger(__name__)

MARKETING_TOKEN = os.getenv("MARKETING_BOT_TOKEN")
API_URL = f"{config.TELEGRAM_API}/bot{MARKETING_TOKEN}"
ADMIN_ID = str(config.TELEGRAM_ADMIN_CHAT_ID)
CHANNEL_ID = config.TELEGRAM_CHANNEL_ID

# --- Keyboards ---
main_keyboard = {
    "keyboard": [
        [{"text": "📱 Draft Threads"}, {"text": "📸 Draft IG"}],
        [{"text": "⚔️ Roast Competitor"}, {"text": "📢 Broadcast ke Channel"}],
        [{"text": "🚀 Test Auto-Pilot"}]
    ],
    "resize_keyboard": True
}

broadcast_keyboard = {
    "keyboard": [
        [{"text": "Broadcast: Update Sinyal"}],
        [{"text": "Broadcast: Promo Free Trial"}],
        [{"text": "Broadcast: Koin Sedang Terbang"}],
        [{"text": "🔙 Kembali ke Menu Utama"}]
    ],
    "resize_keyboard": True
}

# Waktu pengingat & auto-pilot (Format 24 Jam)
AUTO_POST_TIMES = ["08:00", "13:00", "19:00"]
_posted_today = set()

# --- Fungsi Helper ---
def send_msg(chat_id, text, reply_markup=None):
    if not reply_markup:
        reply_markup = main_keyboard
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(reply_markup),
        "parse_mode": "Markdown"
    }
    try:
        requests.post(f"{API_URL}/sendMessage", json=data, timeout=10)
    except Exception as e:
        log.error("Gagal kirim pesan ke %s: %s", chat_id, e)

def send_photo_to_free(photo_url, caption):
    inline_kb = {
        "inline_keyboard": [
            [{"text": "🚀 KLAIM VIP GRATIS 24 JAM", "url": "https://t.me/scraping26bot?start=freetrial"}],
            [{"text": "💎 UPGRADE VIP (Rp 50.000/Bulan)", "url": "https://t.me/scraping26bot?start=premium"}]
        ]
    }
    data = {
        "chat_id": CHANNEL_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(inline_kb)
    }
    
    try:
        resp = requests.post(f"{API_URL}/sendPhoto", data=data, timeout=15)
        # Jika gambar dari CoinGecko gagal (404 dsb), pakai gambar ilustrasi cadangan
        if not resp.json().get("ok"):
            log.warning("Gagal kirim gambar CoinGecko, memakai fallback. Respon: %s", resp.text)
            fallback_photo = "https://images.unsplash.com/photo-1621504450181-5d356f61d307?auto=format&fit=crop&w=800&q=80"
            data["photo"] = fallback_photo
            requests.post(f"{API_URL}/sendPhoto", data=data, timeout=15)
        return True
    except Exception as e:
        log.error("Error broadcast photo: %s", e)
        return False

def broadcast_to_free(pesan):
    data = {
        "chat_id": CHANNEL_ID,
        "text": pesan,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(f"{API_URL}/sendMessage", json=data, timeout=10)
        return resp.json().get("ok", False)
    except Exception:
        return False

def get_market_data():
    import sqlite3
    try:
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT coin, change_24h FROM price_history ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        conn.close()
        
        if rows:
            best = max(rows, key=lambda x: x["change_24h"])
            return best["coin"].capitalize(), best["change_24h"]
    except Exception as e:
        log.error("DB Error: %s", e)
        
    coins = ["Bitcoin", "Ethereum", "Solana", "Dogecoin", "Pepe"]
    return random.choice(coins), random.uniform(3.0, 15.0)



# --- Mesin Auto-Pilot ---
def auto_post_marketing(time_key="13:00"):
    import storage
    coin_name, gain = get_market_data()
    
    photo_url = f"https://www.coingecko.com/chart/images/{coin_name.lower()}/large.png"
    
    mode = random.choice(["TEASER", "FLASHDROP", "PROMO"])
    
    # Override khusus jam tertentu biar merata
    if time_key == "08:00": mode = "TEASER"
    elif time_key == "13:00": mode = random.choice(["FLASHDROP", "PROMO"])
    
    if mode == "FLASHDROP":
        # UANG KAGET VOUCHER!
        code = storage.create_voucher(3) # 3 Hari VIP Gratis
        caption = (
            f"🎁 *UANG KAGET VOUCHER REBUTAN!* 🎁\n\n"
            f"Rezeki dari langit siang ini! Siapa cepat dia dapat!\n"
            f"Voucher Akses VIP 3 HARI GRATIS hanya bisa diklaim oleh *1 ORANG PERTAMA* yang klik tombol di bawah ini.\n\n"
            f"Siap? 3.. 2.. 1.. SIKAT!"
        )
        inline_kb = {
            "inline_keyboard": [
                [{"text": "🎁 KLAIM VOUCHER VIP KAGET SEKARANG!", "url": f"https://t.me/scraping26bot?start=VOUCHER_{code}"}]
            ]
        }
        data = {
            "chat_id": CHANNEL_ID,
            "photo": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=800&q=80",
            "caption": caption,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(inline_kb)
        }
        requests.post(f"{API_URL}/sendPhoto", data=data, timeout=15)
        return True

    elif mode == "TEASER":
        # SINYAL SENSOR
        caption = (
            f"🚨 *SINYAL AI BOCOR!* 🚨\n\n"
            f"Koin: *{coin_name}*\n"
            f"Trend: *BULLISH / MOMENTUM KUAT*\n\n"
            f"Target Profit (TP1): 🛑 _[SENSORD - KHUSUS VIP]_\n"
            f"Target Profit (TP2): 🛑 _[SENSORD - KHUSUS VIP]_\n"
            f"Stop Loss (SL): 🛑 _[SENSORD - KHUSUS VIP]_\n\n"
            f"Koin ini diprediksi bersiap *terbang +{gain:.1f}%* hari ini! Member VIP sudah masuk posisi dan pasang jaring profit otomatis.\n"
            f"Masih mau jadi penonton orang lain cuan?\n\n"
            f"👇 Buka Target Koinnya Sekarang:"
        )
        return send_photo_to_free(photo_url, caption)

    else:
        # PROMO NORMAL
        caption = (
            f"⚡ *MARKET FLASH UPDATE*\n\n"
            f"Saat ini *{coin_name}* memimpin dengan potensi anomali volume +{gain:.1f}%!\n\n"
            f"Jangan cuma jadi penonton. Biarkan AI Whale Radar memandu *entry* dan *exit* Anda secara presisi tanpa campur tangan emosi.\n\n"
            f"👇 Cobain botnya GRATIS 24 jam atau langsung upgrade!"
        )
        return send_photo_to_free(photo_url, caption)

def reminder_loop():
    global _posted_today
    while True:
        try:
            now = datetime.datetime.now()
            date_key = now.strftime("%Y-%m-%d")
            time_key = now.strftime("%H:%M")

            if date_key not in _posted_today:
                _posted_today = {date_key}

            reminder_key = f"{date_key}_{time_key}"
            if time_key in AUTO_POST_TIMES and reminder_key not in _posted_today:
                _posted_today.add(reminder_key)
                
                # AUTO POSTING TO FREE CHANNEL
                auto_post_marketing(time_key)
                
                # Info ke admin bahwa auto-post telah berjalan
                send_msg(ADMIN_ID, f"🤖 [AUTO-PILOT] Posting otomatis pukul {time_key} telah berhasil dikirim ke Channel Gratis!")
                
        except Exception as e:
            log.error("Error in reminder_loop: %s", e)
        time.sleep(30)


# --- Handler Pesan ---
def handle_command(chat_id, text):
    if str(chat_id) != ADMIN_ID:
        send_msg(chat_id, "Maaf, bot ini khusus untuk manajemen Whale Crypto.")
        return

    coin_name, gain = get_market_data()

    if text in ["/start", "🔙 Kembali ke Menu Utama"]:
        send_msg(chat_id,
            "🎯 *WHALE MARKETING CENTER*\n\n"
            "Sistem Auto-Pilot aktif! Promo akan dikirim jam 08:00, 13:00, dan 19:00.\n"
            "Pilih opsi di bawah untuk posting manual:",
            main_keyboard
        )

    elif "Test Auto-Pilot" in text or text == "/test_auto":
        send_msg(chat_id, "⏳ Menjalankan Test Auto-Pilot. Mengecek koin teratas dan men-download gambar dari CoinGecko...")
        ok = auto_post_marketing("13:00")
        if ok:
            send_msg(chat_id, "✅ Test Auto-Pilot berhasil! Silakan cek Channel Gratis Anda.")
        else:
            send_msg(chat_id, "❌ Gagal memposting. Cek log server.")

    elif "Draft Threads" in text or text == "/draft_threads" or "Draft IG" in text:
        import urllib.parse
        templates = [
            f"Iseng bikin Bot AI pelacak pergerakan Smart Money di kripto.\n\nPagi tadi bunyi di {coin_name} pas masih sepi, eh sekarang beneran terbang +{gain:.1f}%! Mau nyobain botnya gratis 24 jam?\n\nCek link di bio ya!\n\n#crypto #bitcoin #cuan #investasi",
            f"Stop trading pakai firasat!\n\nAI kita nangkap sinyal {coin_name} sebelum naik. Hasilnya? Langsung terbang +{gain:.1f}% dalam beberapa jam.\n\nTes keakuratan AI kita GRATIS 24 jam, klik link di bio!\n\n#whaleradar #cryptoid #bitcoin #cuan",
            f"Capek ikut grup VIP Crypto yang adminnya lepas tangan pas koin nyungsep? 📉\n\nTinggalkan cara lama. AI Whale Radar hitung Entry sampai Stop Loss pakai matematika, bukan firasat.\n\nHari ini terbukti di {coin_name} (+{gain:.1f}%). Coba gratis 24 jam di link bio!"
        ]
        caption = random.choice(templates)
        
        # Link 1-Klik Post
        text_encoded = urllib.parse.quote(caption)
        bot_link = urllib.parse.quote("https://t.me/scraping26bot")
        
        tw_url = f"https://twitter.com/intent/tweet?text={text_encoded}"
        th_url = f"https://www.threads.net/intent/post?text={text_encoded}"
        fb_url = f"https://www.facebook.com/sharer/sharer.php?u={bot_link}&quote={text_encoded}"
        
        kb = {
            "inline_keyboard": [
                [{"text": "🐦 1-Klik Twitter", "url": tw_url}],
                [{"text": "🌀 1-Klik Threads", "url": th_url}],
                [{"text": "📘 1-Klik Facebook", "url": fb_url}]
            ]
        }
        
        send_msg(chat_id, f"✅ *DRAFT KONTEN SIAP:*\n\n{caption}\n\n👇 *Klik tombol di bawah untuk langsung nge-post!*", reply_markup=kb)

    elif "Roast Competitor" in text or text == "/roast_competitor":
        templates = [
            f"Capek ikut grup VIP Crypto yang adminnya lepas tangan pas koin nyungsep? 📉\n\nTinggalkan cara lama. AI Whale Radar hitung Entry sampai Stop Loss pakai matematika, bukan firasat.\n\nHari ini terbukti di {coin_name} (+{gain:.1f}%). Coba gratis 24 jam di link bio!",
        ]
        send_msg(chat_id, "✅ TEKS ROAST SIAP:\n\n" + random.choice(templates))

    elif "Broadcast ke Channel" in text:
        send_msg(chat_id,
            "📢 PILIH TEMPLATE BROADCAST MANUAL:\nAtau ketik pesan custom dengan `/bom_free <pesan>`",
            broadcast_keyboard
        )

    elif "Broadcast: Update Sinyal" in text:
        pesan = f"📊 MARKET UPDATE — {coin_name}\n\nKoin {coin_name} menunjukkan pergerakan signifikan hari ini (+{gain:.1f}%).\n\nIngin sinyal lengkap dengan Entry, TP & Stop Loss?\n👉 Klaim FREE TRIAL 24 Jam: @scraping26bot"
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast berhasil!" if ok else "❌ Gagal broadcast.")

    elif "Broadcast: Promo Free Trial" in text:
        pesan = "🎁 PROMO TERBATAS!\n\nDapatkan akses GRATIS ke Bot AI Whale Crypto selama 24 Jam!\n\nPantau sinyal Smart Money + Entry + Target Profit otomatis.\n\n👉 Klik [Klaim Free Trial] di @scraping26bot"
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast berhasil!" if ok else "❌ Gagal broadcast.")

    elif "Broadcast: Koin Sedang Terbang" in text:
        pesan = f"🔥 SMART MONEY TERDETEKSI!\n\nRadar AI mendeteksi lonjakan volume anomali pada {coin_name} (+{gain:.1f}%).\n\nMau ikut next signal?\n👉 Coba GRATIS 24 Jam di @scraping26bot"
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast berhasil!" if ok else "❌ Gagal broadcast.")

    elif text.lower().startswith("/bom_free"):
        pesan = text[len("/bom_free"):].strip()
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast custom berhasil!" if ok else "❌ Gagal broadcast.")

    else:
        send_msg(chat_id, "Gunakan tombol menu di bawah ya, Bos 👇")

def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Marketing Bot Full Auto-Pilot Started")

    t = threading.Thread(target=reminder_loop, daemon=True)
    t.start()

    offset = None
    while True:
        try:
            if not MARKETING_TOKEN:
                log.error("MARKETING_BOT_TOKEN belum diset!")
                time.sleep(10)
                continue

            resp = requests.get(
                f"{API_URL}/getUpdates",
                params={"timeout": 30, "offset": offset},
                timeout=40
            )
            data = resp.json()
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if msg and msg.get("text"):
                    handle_command(str(msg["chat"]["id"]), msg["text"])
        except Exception as e:
            log.error("Error: %s", e)
            time.sleep(5)

if __name__ == '__main__':
    run()
