"""Entrypoint siklus harian/berkala.

Alur:
1. ambil harga dari sumber
2. simpan ke riwayat
3. hitung sinyal (Whale & Price)
4. kirim ringkasan ke admin, dan alert VIP ke subscriber premium
"""
import csv
import logging
import sys
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


def build_summary(signals: list[analyzer.Signal]) -> str:
    header = f"dYT Ringkasan Harga ({datetime.now():%Y-%m-%d %H:%M})\n"
    body = "\n".join(s.format_line() for s in signals)
    alerts = analyzer.only_alerts(signals)
    whales = [s for s in alerts if s.is_whale]
    
    footer = f"\n\ns,? {len(alerts)} sinyal alert ({len(whales)} Whale Detected)."
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
        alert_text = "dYs" *VIP SIGNAL ALERT*\n\n" + "\n\n".join(
            s.format_line() for s in alerts
        )
        for sub in storage.all_subscribers(premium_only=True):
            notifier.send_message(sub["chat_id"], alert_text, parse_mode="Markdown")

    storage.cleanup_history(days=30)
    return 0


if __name__ == "__main__":
    _setup_logging()
    sys.exit(run_once())
