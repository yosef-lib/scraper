import os
import time
import random
import logging
import threading
import datetime
import requests
import config
import sources

log = logging.getLogger(__name__)

MARKETING_TOKEN = os.getenv("MARKETING_BOT_TOKEN")
API_URL = f"{config.TELEGRAM_API}/bot{MARKETING_TOKEN}"
ADMIN_ID = str(config.TELEGRAM_ADMIN_CHAT_ID)

# ─── Keyboards ────────────────────────────────────────────────────────────────
main_keyboard = {
    "keyboard": [
        [{"text": "📱 Draft Threads"}, {"text": "📸 Draft IG Story"}],
        [{"text": "⚔️ Roast Competitor"}],
        [{"text": "📣 Broadcast ke Channel Gratis"}]
    ],
    "resize_keyboard": True,
    "persistent": True
}

broadcast_keyboard = {
    "keyboard": [
        [{"text": "📊 Broadcast: Update Sinyal"}],
        [{"text": "🎁 Broadcast: Promo Free Trial"}],
        [{"text": "🔥 Broadcast: Koin Sedang Terbang!"}],
        [{"text": "🔙 Kembali ke Menu Utama"}]
    ],
    "resize_keyboard": True,
    "persistent": True
}


# ─── Helpers ──────────────────────────────────────────────────────────────────
def send_msg(chat_id, text, reply_markup=None):
    if not MARKETING_TOKEN:
        return
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup if reply_markup else main_keyboard
    }
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=15)
    except Exception:
        pass

def send_photo_msg(chat_id, photo_url, caption, reply_markup=None):
    if not MARKETING_TOKEN:
        return
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "reply_markup": reply_markup if reply_markup else main_keyboard
    }
    try:
        requests.post(f"{API_URL}/sendPhoto", json=payload, timeout=20)
    except Exception:
        pass

def broadcast_to_free(text):
    """Kirim ke Channel Gratis menggunakan bot utama."""
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": config.TELEGRAM_CHANNEL_ID, "text": text}
    try:
        resp = requests.post(url, json=payload, timeout=20)
        return resp.status_code == 200
    except Exception:
        return False

def get_market_data():
    try:
        prices = sources.fetch_prices()
        top_gainer = max(prices, key=lambda x: x.change_24h) if prices else None
        coin_name = top_gainer.coin.upper() if top_gainer else "BITCOIN"
        gain = top_gainer.change_24h if top_gainer else 5.5
        price = top_gainer.price if top_gainer else 0
        return coin_name, gain, price
    except Exception:
        return "BITCOIN", 5.5, 0


# ─── Reminder Scheduler ───────────────────────────────────────────────────────
REMINDER_TIMES = ["07:00", "16:00", "20:00"]
_reminded_today = set()

def reminder_loop():
    """Thread terpisah: kirim pengingat posting ke admin 3x sehari."""
    global _reminded_today
    while True:
        try:
            now = datetime.datetime.now()
            date_key = now.strftime("%Y-%m-%d")
            time_key = now.strftime("%H:%M")

            # Reset harian
            if date_key not in _reminded_today:
                _reminded_today = {date_key}

            reminder_key = f"{date_key}_{time_key}"
            if time_key in REMINDER_TIMES and reminder_key not in _reminded_today:
                _reminded_today.add(reminder_key)
                coin_name, gain, _ = get_market_data()

                if time_key == "07:00":
                    msg = (
                        "🌅 SELAMAT PAGI, BOS!\n\n"
                        f"Data terkini: {coin_name} bergerak +{gain:.1f}% 🔥\n\n"
                        "Waktunya tembak postingan pagi!\n"
                        "👉 Klik [📱 Draft Threads] untuk konten siap pakai."
                    )
                elif time_key == "16:00":
                    msg = (
                        "🌆 PENGINGAT POSTING SORE, BOS!\n\n"
                        f"Pasar sedang panas! {coin_name} +{gain:.1f}% 📈\n\n"
                        "Jam 4-6 sore adalah Golden Hour traffic Threads.\n"
                        "👉 Klik [📱 Draft Threads] atau [⚔️ Roast Competitor]!"
                    )
                else:  # 20:00
                    msg = (
                        "🌙 PENGINGAT POSTING MALAM, BOS!\n\n"
                        f"{coin_name} momen hari ini: +{gain:.1f}% 🎯\n\n"
                        "Orang santai scroll HP malam hari = calon pembeli!\n"
                        "👉 Klik [📸 Draft IG Story] atau [📣 Broadcast ke Channel Gratis]!"
                    )

                if ADMIN_ID:
                    send_msg(ADMIN_ID, msg)

        except Exception as e:
            log.error("Reminder error: %s", e)

        time.sleep(55)


# ─── Command Handler ───────────────────────────────────────────────────────────
def handle_command(chat_id, text):
    if str(chat_id) != ADMIN_ID:
        send_msg(chat_id, "Akses ditolak. Bot ini khusus internal Whale Crypto.")
        return

    coin_name, gain, price = get_market_data()

    # ── Menu Utama ──
    if text in ["/start", "🔙 Kembali ke Menu Utama"]:
        send_msg(chat_id,
            "🎯 WHALE MARKETING CENTER\n\n"
            "Pilih senjata promosi Anda:\n"
            "📱 Draft konten untuk Threads\n"
            "📸 Draft konten untuk IG Story\n"
            "⚔️ Teks serangan vs kompetitor\n"
            "📣 Broadcast langsung ke Channel Gratis"
        )

    # ── Draft Threads ──
    elif "Draft Threads" in text or text == "/draft_threads":
        templates = [
            f"Iseng bikin Bot AI pelacak pergerakan Smart Money di kripto.\n\nPagi tadi bunyi di {coin_name} pas masih sepi, eh sekarang beneran terbang +{gain:.1f}%! Mau nyobain botnya gratis 24 jam?\n\nCek link di bio ya!\n\n#crypto #bitcoin #cuan #investasi",
            f"Stop trading pakai firasat!\n\nAI kita nangkap sinyal {coin_name} sebelum naik. Hasilnya? Langsung terbang +{gain:.1f}% dalam beberapa jam.\n\nTes keakuratan AI kita GRATIS 24 jam, klik link di bio!\n\n#whaleradar #cryptoid #bitcoin #cuan",
            f"Dulu trading sering nyangkut karena fomo grup abal-abal. Sekarang pakai Bot AI pelacak anomali volume.\n\nHari ini {coin_name} sukses hit profit +{gain:.1f}% dengan presisi!\n\nMau nyicip botnya gratis? Link di bio!\n\n#crypto #trading #sinyal #investasi",
        ]
        chart_url = f"https://www.coingecko.com/chart/images/{coin_name.lower()}/large.png"
        caption = random.choice(templates)
        send_msg(chat_id, "✅ DRAFT THREADS SIAP:\n\n" + caption)

    # ── Draft IG Story ──
    elif "Draft IG" in text or text == "/draft_ig":
        templates = [
            f"🔥 {coin_name} NAIK +{gain:.1f}% HARI INI! 🔥\n\nMember VIP sudah cuan dari pagi.\nYang masih manual pasti ketinggalan!\n\nFREE TRIAL 24 Jam ada di link bio 🚀\n\n#crypto #bitcoin",
            f"Sinyal {coin_name} sukses hit TP!\n+{gain:.1f}% ✅\n\nSemua murni dari AI, bukan tebak-tebakan.\nCoba gratis di link bio!\n\n#whaleradar #cuan",
            f"AI nggak tidur, nggak baper, nggak salah Entry.\n\n{coin_name} +{gain:.1f}% tadi sudah dideteksi dari pagi!\n\nFree Trial 24 Jam, link di bio 👇\n\n#cryptoindonesia #tradingbot",
        ]
        send_msg(chat_id, "✅ DRAFT IG STORY SIAP:\n\n" + random.choice(templates))

    # ── Roast Competitor ──
    elif "Roast Competitor" in text or text == "/roast_competitor":
        templates = [
            f"Capek ikut grup VIP Crypto yang adminnya lepas tangan pas koin nyungsep? 📉\n\nTinggalkan cara lama. AI Whale Radar hitung Entry sampai Stop Loss pakai matematika, bukan firasat.\n\nHari ini terbukti di {coin_name} (+{gain:.1f}%). Coba gratis 24 jam di link bio!",
            f"Beda grup biasa vs Whale Crypto AI:\n❌ Grup biasa: Tebakan tanpa Stop Loss\n✅ Whale AI: Entry, TP1, TP2, dan SL matematis\n\nHari ini {coin_name} tembus +{gain:.1f}% dengan presisi.\nCoba gratis di link bio!",
            f"Banyak grup VIP isinya admin yang beli duluan lalu suruh member beli (pom-pom dump).\n\nHindari jebakan itu. AI kami murni melacak Smart Money di exchange, 100% transparan.\n\nBuktinya hari ini: {coin_name} +{gain:.1f}%. Free Trial 24 Jam link di bio!",
        ]
        send_msg(chat_id, "✅ TEKS ROAST SIAP:\n\n" + random.choice(templates))

    # ── Broadcast Menu ──
    elif "Broadcast ke Channel" in text:
        send_msg(chat_id,
            "📣 PILIH TEMPLATE BROADCAST:\n\nPilih template atau ketik pesan custom Anda dengan:\n`/bom_free <pesan Anda>`",
            broadcast_keyboard
        )

    # ── Broadcast: Update Sinyal ──
    elif "Broadcast: Update Sinyal" in text:
        pesan = (
            f"📊 MARKET UPDATE — {coin_name}\n\n"
            f"Koin {coin_name} menunjukkan pergerakan signifikan hari ini!\n"
            f"Lonjakan volume terdeteksi oleh AI Whale Radar (+{gain:.1f}%).\n\n"
            f"Ingin sinyal lengkap dengan Entry, TP & Stop Loss?\n"
            f"👉 Klaim FREE TRIAL 24 Jam: @WhaleCryptoVIP_bot"
        )
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast 'Update Sinyal' berhasil dikirim ke Channel Gratis!" if ok else "❌ Gagal broadcast. Coba lagi.")

    # ── Broadcast: Promo Free Trial ──
    elif "Broadcast: Promo Free Trial" in text:
        pesan = (
            "🎁 PROMO TERBATAS!\n\n"
            "Dapatkan akses GRATIS ke Bot AI Whale Crypto selama 24 Jam!\n\n"
            "Pantau sinyal Smart Money + Entry + Target Profit otomatis.\n\n"
            "Caranya gampang:\n"
            "1. Buka @WhaleCryptoVIP_bot\n"
            "2. Klik tombol [Klaim Free Trial]\n"
            "3. Nikmati sinyal VIP 24 Jam GRATIS!\n\n"
            "Jangan sampai ketinggalan 🚀"
        )
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast 'Promo Free Trial' berhasil dikirim!" if ok else "❌ Gagal broadcast.")

    # ── Broadcast: Koin Terbang ──
    elif "Broadcast: Koin Sedang Terbang" in text:
        pesan = (
            f"🔥 SMART MONEY TERDETEKSI BERGERAK!\n\n"
            f"Radar AI mendeteksi lonjakan volume anomali pada {coin_name}!\n"
            f"Pergerakan hari ini: +{gain:.1f}%\n\n"
            f"Anggota VIP sudah menerima sinyal Entry & Target Profit-nya sejak awal.\n\n"
            f"Mau ikut next signal?\n"
            f"👉 Coba GRATIS 24 Jam di @WhaleCryptoVIP_bot"
        )
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Broadcast 'Koin Terbang' berhasil dikirim!" if ok else "❌ Gagal broadcast.")

    # ── Broadcast Custom ──
    elif text.lower().startswith("/bom_free"):
        pesan = text[len("/bom_free"):].strip()
        if not pesan:
            send_msg(chat_id, "Format: /bom_free <pesan Anda>")
            return
        ok = broadcast_to_free(pesan)
        send_msg(chat_id, "✅ Pesan custom berhasil dikirim ke Channel Gratis!" if ok else "❌ Gagal broadcast.")

    else:
        send_msg(chat_id, "Gunakan tombol menu di bawah ya, Bos 👇")


# ─── Main Loop ─────────────────────────────────────────────────────────────────
def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Marketing Bot v2 started with reminders & broadcast templates")

    # Jalankan reminder di thread terpisah
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
