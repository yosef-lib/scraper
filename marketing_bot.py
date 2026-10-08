import os
import time
import random
import logging
import requests
import config
import sources

log = logging.getLogger(__name__)

MARKETING_TOKEN = os.getenv("MARKETING_BOT_TOKEN")
API_URL = f"{config.TELEGRAM_API}/bot{MARKETING_TOKEN}"

def send_msg(chat_id, text, parse_mode=None):
    if not MARKETING_TOKEN:
        return
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    requests.post(f"{API_URL}/sendMessage", json=payload)

def handle_command(chat_id, text):
    if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
        send_msg(chat_id, "Akses ditolak. Bot ini khusus internal tim marketing Whale Crypto.")
        return

    cmd = text.split()[0].lower()
    
    try:
        prices = sources.fetch_prices()
        top_gainer = max(prices, key=lambda x: x.change_24h) if prices else None
    except:
        top_gainer = None

    coin_name = top_gainer.coin.upper() if top_gainer else "BITCOIN"
    gain = top_gainer.change_24h if top_gainer else 5.5

    if cmd == "/start":
        msg = (
            "🎯 *WHALE MARKETING CONTROL CENTER* 🎯\n\n"
            "Pilih amunisi promosi Anda hari ini:\n"
            "👉 `/draft_threads` - Hook & Storytelling\n"
            "👉 `/draft_ig` - Singkat, padat (IG Story)\n"
            "👉 `/roast_competitor` - Serang kelemahan grup VIP sebelah\n"
            "👉 `/bom_free <pesan>` - Broadcast instan ke Channel Gratis"
        )
        send_msg(chat_id, msg, "Markdown")

    elif cmd == "/draft_threads":
        templates = [
            f"Iseng bikin Bot AI pelacak pergerakan Smart Money (Whale) di kripto. Pagi tadi bunyi di {coin_name}, eh sekarang beneran terbang +{gain:.1f}%. Mau nyobain botnya gratis 24 jam? Cek link di bio ya!",
            f"Stop trading pakai firasat. Tadi pagi AI nangkap sinyal {coin_name} pas masih sepi, sekarang udah meroket +{gain:.1f}%. Tes keakuratan AI kita GRATIS 24 jam, klik link di bio!",
            f"Dulu capek trading sering nyangkut karena fomo grup. Sekarang murni pakai Bot AI pelacak anomali volume. Hari ini {coin_name} sukses hit profit +{gain:.1f}%. Mau nyicip keakuratan botnya gratis? Link di bio!"
        ]
        send_msg(chat_id, random.choice(templates) + "\n\n#crypto #bitcoin #cuan")

    elif cmd == "/draft_ig":
        templates = [
            f"🔥 {coin_name} NAIK +{gain:.1f}% HARI INI! 🔥\n\nMember VIP udah cuan dari pagi berkat radar AI. Yang masih manual pasti ketinggalan.\n\nKlik link di bio buat FREE TRIAL 24 Jam! 🚀",
            f"Sinyal {coin_name} sukses hit Target Profit (+{gain:.1f}%)! 🎯\nTrading gampang kalau ngikutin pergerakan Uang Besar.\n\nLink di bio untuk coba bot gratis."
        ]
        send_msg(chat_id, random.choice(templates))

    elif cmd == "/roast_competitor":
        templates = [
            f"Capek ikut grup VIP Crypto yang adminnya suka lepas tangan pas koin nyungsep? 📉 Tinggalkan cara lama. Saatnya beralih ke AI Whale Radar. Kita hitung titik Entry sampai Stop Loss pakai matematika, bukan firasat. Hari ini terbukti di {coin_name} (+{gain:.1f}%). Coba gratis 24 jam botnya di bio!",
            f"Beda grup biasa vs Whale Crypto AI:\n❌ Grup biasa cuma kasih tebakan tanpa Stop Loss.\n✅ Whale AI ngasih Entry, TP, dan SL matematis.\n\nHari ini {coin_name} tembus +{gain:.1f}% dengan presisi. Coba gratis di link bio!",
            f"Banyak grup VIP isinya cuma admin yang beli duluan lalu suruh member beli (pom-pom). Hindari jebakan itu. AI kami murni melacak Smart Money di exchange. Buktikan sendiri akurasinya hari ini ({coin_name} +{gain:.1f}%), Free Trial 24 Jam link di bio!"
        ]
        send_msg(chat_id, random.choice(templates))

    elif cmd.startswith("/bom_free"):
        pesan = text.replace("/bom_free", "").strip()
        if not pesan:
            send_msg(chat_id, "Format salah. Gunakan:\n`/bom_free Halo semua ini update terbaru...`", "Markdown")
            return
        
        # Kirim pakai bot utama agar seolah-olah dikirim oleh Whale Crypto VIP
        url_main = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": config.TELEGRAM_CHANNEL_ID, "text": pesan}
        try:
            resp = requests.post(url_main, json=payload, timeout=20)
            if resp.status_code == 200:
                send_msg(chat_id, "✅ Pesan berhasil dibombardir ke Channel Gratis!")
            else:
                send_msg(chat_id, f"❌ Gagal mengirim: {resp.text}")
        except Exception as e:
            send_msg(chat_id, f"❌ Error: {e}")

    else:
        send_msg(chat_id, "Perintah tidak dikenal. Ketik /start untuk melihat menu.")

def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Marketing Bot started")
    offset = None
    while True:
        try:
            if not MARKETING_TOKEN:
                log.error("MARKETING_BOT_TOKEN belum diset!")
                time.sleep(10)
                continue
                
            resp = requests.get(f"{API_URL}/getUpdates", params={"timeout": 30, "offset": offset}, timeout=40)
            data = resp.json()
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if msg and msg.get("text"):
                    handle_command(msg["chat"]["id"], msg["text"])
        except Exception as e:
            time.sleep(5)

if __name__ == '__main__':
    run()
