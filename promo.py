"""Bot Promosi Otomatis (Marketing Manager)

Skrip ini bertugas:
1. Mengambil koin dengan performa terbaik hari ini.
2. Mengirim pesan promosi (FOMO) ke Channel Gratis.
3. Mengirimkan draf postingan Threads/Twitter ke Admin.
"""
import logging
import sys
import random

import config
import notifier
import sources
from main import generate_chart_url

log = logging.getLogger("promo")

def _setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_best_coin():
    prices = sources.fetch_prices()
    if not prices:
        return None
    # Cari koin dengan kenaikan (change_24h) tertinggi
    best_coin = max(prices, key=lambda c: c.change_24h)
    return best_coin

def send_promo_to_channel(coin_data) -> bool:
    channel_id = config._get("TELEGRAM_CHANNEL_ID", "")
    if not channel_id:
        log.info("TELEGRAM_CHANNEL_ID kosong. Melewati broadcast ke channel gratis.")
        return False
        
    vol_m = coin_data.volume_24h / 1_000_000 if coin_data.volume_24h else 0
    emoji = "🚀" if coin_data.change_24h > 0 else "📉"
    
    templates = [
        f"🔥 *MARKET UPDATE*\\n\\n{coin_data.coin.upper()} sedang bergejolak {emoji}\\nPerubahan: *{coin_data.change_24h:+.2f}%*\\nVolume 24j: *${vol_m:,.1f}M*\\n\\n💎 *Member VIP* sudah mendapatkan notifikasi & grafik otomatis dari pergerakan ini lebih awal!\\n\\nJangan sampai ketinggalan momentum besar berikutnya.\\n👉 *Upgrade VIP 24 Jam Non-stop:* https://lynk.id/whaleradar",
        
        f"🚨 *SMART MONEY TERDETEKSI BERGERAK*\\n\\nPerhatian pada koin {coin_data.coin.upper()}! Volume transaksi harian mencapai *${vol_m:,.1f}M*.\\n\\nDi channel gratis ini sinyal selalu *delay*. Ingin tahu koin apa lagi yang sedang diakumulasi bandar secara Real-Time?\\n\\n🤖 *Gunakan AI Smart Radar VIP sekarang!*\\n👉 Klik: https://lynk.id/whaleradar"
    ]
    
    msg = random.choice(templates)
    msg = msg.replace('\\n', '\n')
    
    # Generate Chart for the promo!
    chart_data = sources.fetch_market_chart(coin_data.coin, days=1)
    if chart_data:
        chart_url = generate_chart_url(coin_data.coin, chart_data)
        return notifier.send_photo(channel_id, chart_url, caption=msg, parse_mode="Markdown")
    else:
        return notifier.send_message(channel_id, msg, parse_mode="Markdown")

def send_threads_draft_to_admin(coin_data) -> bool:
    if not config.TELEGRAM_ADMIN_CHAT_ID:
        return False
        
    emoji = "🔥" if coin_data.change_24h > 0 else "👀"
    
    msg = (
        f"🤖 *ASISTEN MARKETING VIP*\\n\\n"
        f"Bos, ini draf untuk diposting di Threads atau Twitter hari ini. Tinggal *Copy-Paste* aja biar kelihatan natural & mancing pembeli!\\n\\n"
        f"👇👇👇\\n\\n"
        f"Gila sih pergerakan bandar kripto hari ini, diam-diam ngumpul di {coin_data.coin.upper()} {emoji}. "
        f"Untung aja AI radar VIP gue udah bunyi ngasih alert. Emang paling bener trading dibantu robot, cuan ngalir saat tidur. Kalian pada serok apa nih hari ini? #KriptoIndonesia #Cuan\\n\\n"
        f"👆👆👆\\n\\n"
        f"*(Jangan lupa nanti kalau ada yang nanya di komentar, arahin ke link Lynk.id kita)*"
    )
    msg = msg.replace('\\n', '\n')
    return notifier.send_message(config.TELEGRAM_ADMIN_CHAT_ID, msg, parse_mode="Markdown")

def run_promo():
    best_coin = get_best_coin()
    if not best_coin:
        log.error("Gagal mendapatkan data koin.")
        return 1
        
    log.info(f"Koin terbaik hari ini: {best_coin.coin}")
    
    # 1. Kirim ke Channel Publik
    send_promo_to_channel(best_coin)
    
    # 2. Kirim draf ke Admin
    send_threads_draft_to_admin(best_coin)
    
    return 0

if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_promo())
