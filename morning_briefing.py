"""Morning Briefing Otomatis.

Mengirim laporan cuaca kripto setiap jam 07:00 WIB ke Channel Gratis & VIP.
Termasuk:
- Fear & Greed Index
- Top 3 Gainers & Losers hari ini
- Tips strategi berdasarkan kondisi pasar
"""
import logging
import sys
import requests
from datetime import datetime, timezone, timedelta

import config
import notifier
import sources
import storage

log = logging.getLogger("morning_briefing")

def _setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_fear_greed():
    """Ambil Fear & Greed Index dari API alternative.me"""
    try:
        resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        data = resp.json()
        value = int(data["data"][0]["value"])
        label = data["data"][0]["value_classification"]
        return value, label
    except Exception:
        return None, None

def get_market_snapshot():
    """Ambil ringkasan harga & hitung gainer/loser hari ini."""
    prices = sources.fetch_prices()
    if not prices:
        return [], []
    gainers = sorted([p for p in prices if p.change_24h > 0], key=lambda x: x.change_24h, reverse=True)[:3]
    losers  = sorted([p for p in prices if p.change_24h < 0], key=lambda x: x.change_24h)[:3]
    return gainers, losers

def run_morning_briefing():
    channel_id = config._get("TELEGRAM_CHANNEL_ID", "")
    if not channel_id:
        log.error("TELEGRAM_CHANNEL_ID kosong.")
        return 1

    wib = timezone(timedelta(hours=7))
    today = datetime.now(wib).strftime("%A, %d-%m-%Y")

    fear_val, fear_label = get_fear_greed()
    gainers, losers = get_market_snapshot()

    # Tentukan emoji & tips berdasarkan Fear & Greed
    if fear_val is None:
        fg_text = "N/A"
        tips = "Pantau pasar dengan hati-hati hari ini."
        fg_emoji = "❓"
    elif fear_val >= 75:
        fg_emoji = "🤑"
        fg_text = str(fear_val) + " — Extreme Greed (Sangat Serakah)"
        tips = "⚠️ Pasar sangat serakah. Waspada koreksi. Pertimbangkan ambil profit sebagian!"
    elif fear_val >= 55:
        fg_emoji = "😏"
        fg_text = str(fear_val) + " — Greed (Serakah)"
        tips = "✅ Momentum bagus. Smart Money sedang aktif. Pantau sinyal lonjakan volume!"
    elif fear_val >= 45:
        fg_emoji = "😐"
        fg_text = str(fear_val) + " — Neutral"
        tips = "🔍 Pasar sedang konsolidasi. Tunggu konfirmasi breakout sebelum entry."
    elif fear_val >= 25:
        fg_emoji = "😨"
        fg_text = str(fear_val) + " — Fear (Takut)"
        tips = "💡 Pasar takut = Peluang. Kumpulkan koin bagus saat orang panik!"
    else:
        fg_emoji = "😱"
        fg_text = str(fear_val) + " — Extreme Fear (Sangat Takut)"
        tips = "🛒 *Extreme Fear* seringkali adalah sinyal BUY terbaik! Serok pelan-pelan."

    gainers_text = ""
    for p in gainers:
        gainers_text += f"  🟢 *{p.coin.upper()}* {p.change_24h:+.2f}%\n"

    losers_text = ""
    for p in losers:
        losers_text += f"  🔴 *{p.coin.upper()}* {p.change_24h:+.2f}%\n"

    sep = "─" * 28
    gainers_str = gainers_text if gainers_text else "  N/A\n"
    losers_str = losers_text if losers_text else "  N/A\n"
    msg = (
        "☀️ *SELAMAT PAGI! — BRIEFING KRIPTO*\n"
        "📅 " + today + "\n\n" +
        sep + "\n" +
        fg_emoji + " *Fear & Greed Index:*\n"
        "  " + fg_text + "\n\n"
        "🚀 *Top Gainers 24h:*\n" + gainers_str + "\n"
        "📉 *Top Losers 24h:*\n" + losers_str + "\n" +
        sep + "\n"
        "💡 *Tips Hari Ini:*\n" + tips + "\n\n"
        "🤖 Ingin sinyal *ENTRY + TP + SL* otomatis?\n"
        "👉 Upgrade ke VIP: Bank Mandiri: 1420019877454 a.n YOSEF PASKAH WAHYUTO\n"
        "🎫 Atau coba *GRATIS 24 JAM* langsung di bot: @scraping26bot"
    )

    notifier.send_message(channel_id, msg, parse_mode="Markdown")
    log.info("Morning briefing berhasil dikirim.")
    return 0

if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_morning_briefing())
