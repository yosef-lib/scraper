"""Entrypoint siklus harian/berkala.

Alur:
1. ambil harga dari sumber
2. simpan ke riwayat
3. hitung sinyal (Whale & Price)
4. kirim ringkasan ke admin, dan alert VIP (beserta Auto-Chart) ke subscriber premium
"""
import csv
import logging
import sys
import json
import urllib.parse
from datetime import datetime

import analyzer
import config
import notifier
import sources
import storage


def _setup_logging() -> None:
    config.LOGS_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(config.LOGS_DIR / "app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def generate_chart_url(coin: str, prices: list[float]) -> str:
    """Menggunakan QuickChart.io untuk Auto-Chart."""
    # Ambil 50 data poin terakhir biar grafik ga terlalu padat
    if len(prices) > 50:
        prices = prices[-50:]
        
    chart_config = {
        "type": "line",
        "data": {
            "labels": [""] * len(prices),
            "datasets": [{
                "label": coin.upper(),
                "data": prices,
                "borderColor": "rgba(46, 204, 113, 1)" if prices[-1] >= prices[0] else "rgba(231, 76, 60, 1)",
                "backgroundColor": "rgba(46, 204, 113, 0.2)" if prices[-1] >= prices[0] else "rgba(231, 76, 60, 0.2)",
                "fill": True,
                "borderWidth": 3,
                "pointRadius": 0
            }]
        },
        "options": {
            "plugins": {"legend": {"display": False}},
            "scales": {"x": {"display": False}, "y": {"display": True}},
            "layout": {"padding": 10}
        }
    }
    encoded_json = urllib.parse.quote(json.dumps(chart_config))
    return f"https://quickchart.io/chart?w=500&h=300&c={encoded_json}"

def build_summary(signals: list[analyzer.Signal]) -> str:
    header = f"🤖 Ringkasan Harga ({datetime.now():%Y-%m-%d %H:%M})\n"
    body = "\n".join(s.format_line() for s in signals)
    alerts = analyzer.only_alerts(signals)
    whales = [s for s in alerts if s.is_whale]
    
    footer = f"\n\n⚠️ {len(alerts)} sinyal alert ({len(whales)} Whale Detected)."
    return f"{header}\n{body}{footer}"

def export_csv(signals: list[analyzer.Signal]) -> str:
    filename = config.BASE_DIR / "hasil_harga.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["coin", "price", "change_24h", "volume_24h", "currency", "waktu"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for s in signals:
            writer.writerow(
                [s.coin, s.price, f"{s.change_24h:.2f}", f"{s.volume_24h:.2f}", config.VS_CURRENCY, now]
            )
    return str(filename)

def run_once() -> int:
    log = logging.getLogger("main")
    storage.init_db()

    prices = sources.fetch_prices()
    if not prices:
        log.warning("Tidak ada harga yang berhasil diambil.")
        return 1

    # Simpan history harga DAN volume untuk analisis anomali
    for p in prices:
        storage.save_price(p.coin, p.price, p.change_24h, p.volume_24h)

    signals = analyzer.analyze(prices)
    summary = build_summary(signals)
    log.info("Sinyal: %s", [f"{s.coin}={s.change_24h:+.2f}%" for s in signals])

    # Ringkasan + CSV ke admin
    if config.TELEGRAM_ADMIN_CHAT_ID:
        notifier.send_message(config.TELEGRAM_ADMIN_CHAT_ID, summary)
        csv_path = export_csv(signals)
        notifier.send_document(
            config.TELEGRAM_ADMIN_CHAT_ID, csv_path, caption="Data harga terbaru"
        )
    else:
        log.info("TELEGRAM_ADMIN_CHAT_ID kosong, laporan hanya di log.")

    # Alert detail VIP hanya ke premium
    alerts = analyzer.only_alerts(signals)
    if alerts:
        subs = storage.all_subscribers(premium_only=True)
        for s in alerts:
            alert_text = f"🚨 *VIP SIGNAL ALERT*\n\n{s.format_line()}"
            # Fetch chart
            chart_data = sources.fetch_market_chart(s.coin, days=1)
            if chart_data:
                chart_url = generate_chart_url(s.coin, chart_data)
                for sub in subs:
                    # Send photo with caption
                    notifier.send_photo(sub["chat_id"], chart_url, caption=alert_text, parse_mode="Markdown")
            else:
                for sub in subs:
                    notifier.send_message(sub["chat_id"], alert_text, parse_mode="Markdown")

    storage.cleanup_history(days=30)
    return 0

if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_once())
