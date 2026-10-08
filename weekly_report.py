import sqlite3
import datetime
import logging
import sys

import config
import notifier

log = logging.getLogger("weekly")

def _setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_weekly_stats():
    # Menghitung jumlah sinyal potensial dalam 7 hari terakhir
    try:
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        
        cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).isoformat()
        
        # Cari koin dengan lonjakan > 3% di minggu ini
        cur = conn.execute(
            "SELECT coin, MAX(change_24h) as max_change, MAX(volume_24h) as max_vol "
            "FROM price_history WHERE recorded_at >= ? AND change_24h >= ? GROUP BY coin ORDER BY max_change DESC LIMIT 3",
            (cutoff, config.ALERT_PERCENT)
        )
        top_coins = cur.fetchall()
        
        # Hitung total deteksi
        cur = conn.execute(
            "SELECT COUNT(DISTINCT id) FROM price_history WHERE recorded_at >= ? AND change_24h >= ?",
            (cutoff, config.ALERT_PERCENT)
        )
        total_alerts = cur.fetchone()[0]
        
        conn.close()
        return total_alerts, top_coins
    except Exception as e:
        log.error(f"Error DB: {e}")
        return 0, []

def run_weekly_report():
    channel_id = config._get("TELEGRAM_CHANNEL_ID", "")
    if not channel_id:
        log.error("Channel ID tidak ditemukan.")
        return 1
        
    total_alerts, top_coins = get_weekly_stats()
    
    if total_alerts == 0 or not top_coins:
        log.info("Tidak ada data yang cukup untuk report minggu ini.")
        return 0
        
    coins_text = ""
    for idx, row in enumerate(top_coins):
        vol_m = row['max_vol'] / 1_000_000 if row['max_vol'] else 0
        coins_text += f"{idx+1}. *{row['coin'].upper()}* (🚀 +{row['max_change']:.2f}%) - Vol: ${vol_m:.1f}M\\n"
        
    msg = (
        f"🏆 *REKAP KINERJA MINGGUAN WHALE RADAR* 🏆\\n\\n"
        f"Selama 7 hari terakhir, AI Radar kami telah berhasil mendeteksi *{total_alerts} Pergerakan Smart Money* sebelum harganya meroket!\\n\\n"
        f"Top 3 Koin Paling Cuan Minggu Ini:\\n{coins_text}\\n"
        f"Para **Member VIP** kami sudah mendapatkan notifikasi koin-koin di atas *jauh sebelum* publik menyadarinya.\\n\\n"
        f"Masih mau jadi penonton minggu depan? 👀\\n"
        f"💎 *Upgrade VIP Sekarang:* Bank Mandiri: 1420019877454 a.n YOSEF PASKAH WAHYUTO"
    )
    
    msg = msg.replace('\\n', '\n')
    notifier.send_message(channel_id, msg, parse_mode="Markdown")
    log.info("Weekly report berhasil dikirim.")
    return 0

if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_weekly_report())
