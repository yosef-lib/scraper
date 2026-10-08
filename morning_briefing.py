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
        fg_text = f"{fear_val} — *Extreme Greed*"
        tips = "⚠️ Pasar sangat serakah. Waspada koreksi. Pertimbangkan ambil profit sebagian!"
    elif fear_val >= 55:
        fg_emoji = "😏"
        fg_text = f"{fear_val} — *Greed*"
        tips = "✅ Momentum bagus. Smart Money sedang aktif. Pantau sinyal lonjakan volume!"
    elif fear_val >= 45:
        fg_emoji = "😐"
        fg_text = f"{fear_val} — *Neutral*"
        tips = "🔍 Pasar sedang konsolidasi. Tunggu konfirmasi breakout sebelum entry."
    elif fear_val >= 25:
        fg_emoji = "😨"
        fg_text = f"{fear_val} — *Fear*"
        tips = "💡 Pasar takut = Peluang. Kumpulkan koin bagus saat orang panik!"
    else:
        fg_emoji = "😱"
        fg_text = f"{fear_val} — *Extreme Fear*"
        tips = "🛒 *Extreme Fear* seringkali adalah sinyal BUY terbaik! Serok pelan-pelan."

    gainers_text = ""
    for p in gainers:
        gainers_text += f"  🟢 *{p.coin.upper()}* {p.change_24h:+.2f}%\n"

    losers_text = ""
    for p in losers:
        losers_text += f"  🔴 *{p.coin.upper()}* {p.change_24h:+.2f}%\n"

    msg = (
        f"☀️ *SELAMAT PAGI! — BRIEFING KRIPTO*\n"
        f"📅 {today}\n\n"
        f"{'─'*28}\n"
        f"{fg_emoji} *Fear & Greed Index:*\n"
        f"  {fg_text}\n\n"
        f"🚀 *Top Gainers 24h:*\n{gainers_text if gainers_text else '  N/A\n'}\n"
        f"📉 *Top Losers 24h:*\n{losers_text if losers_text else '  N/A\n'}\n"
        f"{'─'*28}\n"
        f"💡 *Tips Hari Ini:*\n{tips}\n\n"
        f"🤖 Ingin sinyal *ENTRY + TP + SL* otomatis?\n"
        f"👉 Upgrade ke VIP: https://lynk.id/whaleradar\n"
        f"🎫 Atau coba *GRATIS 24 JAM* langsung di bot: @WhaleCryptoVIP_bot"
    )

    notifier.send_message(channel_id, msg, parse_mode="Markdown")
    log.info("Morning briefing berhasil dikirim.")
    return 0

if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_morning_briefing())
