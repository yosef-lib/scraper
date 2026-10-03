"""Bot Telegram berlangganan (long polling sederhana, tanpa framework).

Perintah:
  /start      - daftar & info paket
  /harga      - harga terbaru (semua pengguna, versi ringkas)
  /premium    - cara berlangganan
  /aktivasi <kode> - aktivasi premium (kode = ADMIN_SECRET di .env)
  /status     - cek status langganan

Gating: pengguna free dapat ringkasan terbatas; premium dapat detail + alert.
"""
import logging
import time

import requests

import config
import notifier
import sources
import storage

log = logging.getLogger("bot")

HELP_TEXT = (
    "🪙 *Bot Sinyal Harga*\n\n"
    "/harga - Lihat harga terbaru\n"
    "/premium - Info & harga langganan\n"
    "/status - Cek status langgananmu\n"
    "/aktivasi <kode> - Aktifkan premium\n"
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

    if cmd == "/start":
        notifier.send_message(chat_id, HELP_TEXT, parse_mode="Markdown")

    elif cmd == "/harga":
        prices = sources.fetch_prices()
        if not prices:
            notifier.send_message(chat_id, "Maaf, gagal mengambil harga.")
            return
        premium = storage.is_premium(chat_id)
        lines = []
        for p in prices:
            if premium:
                lines.append(f"{p.coin.upper()}: {p.price:,.2f} ({p.change_24h:+.2f}%)")
            else:
                # free: hanya 1 koin + tanpa detail persen penuh
                lines.append(f"{p.coin.upper()}: {p.price:,.2f}")
        body = "\n".join(lines[: (len(lines) if premium else 1)])
        tail = "" if premium else "\n\n🔒 Upgrade ke premium untuk detail lengkap."
        notifier.send_message(chat_id, body + tail)

    elif cmd == "/premium":
        msg = (
            f"💎 *Premium*\n"
            f"Harga: Rp{config.PREMIUM_PRICE_IDR:,} / {config.PREMIUM_DURATION_DAYS} hari\n"
            f"Fitur: alert sinyal realtime, semua koin, detail persen.\n\n"
            f"Setelah bayar, kirim: /aktivasi <kode>"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown")

    elif cmd == "/aktivasi":
        if len(parts) < 2:
            notifier.send_message(chat_id, "Format: /aktivasi <kode>")
            return
        secret = config.ADMIN_SECRET
        if not secret:
            notifier.send_message(chat_id, "Aktivasi belum dikonfigurasi admin.")
            return
        if parts[1] == secret:
            until = storage.activate_premium(chat_id, config.PREMIUM_DURATION_DAYS)
            notifier.send_message(chat_id, f"✅ Premium aktif sampai {until[:10]}.")
        else:
            notifier.send_message(chat_id, "❌ Kode salah.")

    elif cmd == "/status":
        if storage.is_premium(chat_id):
            row = storage.get_subscriber(chat_id)
            notifier.send_message(
                chat_id, f"✅ Premium sampai {row['premium_until'][:10]}."
            )
        else:
            notifier.send_message(chat_id, "Kamu pengguna FREE. Kirim /premium.")

    else:
        notifier.send_message(chat_id, "Perintah tidak dikenal.\n\n" + HELP_TEXT, parse_mode="Markdown")


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
                username = chat.get("username")
                text = message.get("text", "")
                if text:
                    handle_command(chat_id, username, text)
        except requests.RequestException as exc:
            log.warning("Error polling: %s", exc)
            time.sleep(5)
        except Exception as exc:  # jaga bot tetap hidup
            log.exception("Kesalahan tak terduga: %s", exc)
            time.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_polling()
