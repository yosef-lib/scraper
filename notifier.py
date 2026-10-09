"""Pengirim pesan/berkas ke Telegram. Token dibaca dari config (via .env)."""
import logging
import requests
import config

log = logging.getLogger(__name__)

def send_message(chat_id: str, text: str, parse_mode: str | None = None, reply_markup: dict | None = None) -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN belum diisi, pesan tidak dikirim.")
        return False
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code != 200:
            log.error("Gagal kirim pesan ke %s: %s", chat_id, resp.text)
            return False
        return True
    except requests.RequestException as exc:
        log.error("Error jaringan saat kirim pesan: %s", exc)
        return False

def send_photo(chat_id: str, photo: str, caption: str = "", parse_mode: str | None = None, reply_markup: dict | None = None) -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN belum diisi, foto tidak dikirim.")
        return False
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo, "caption": caption}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            log.error("Gagal kirim foto ke %s: %s", chat_id, resp.text)
            return False
        return True
    except requests.RequestException as exc:
        log.error("Error jaringan saat kirim foto: %s", exc)
        return False

def send_document(chat_id: str, file_path: str, caption: str = "") -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        return False
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id, "caption": caption}
            resp = requests.post(url, data=data, files=files, timeout=60)
        return resp.status_code == 200
    except (requests.RequestException, OSError) as exc:
        return False

def forward_message(chat_id: str, from_chat_id: str, message_id: int) -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        return False
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/forwardMessage"
    payload = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
    try:
        resp = requests.post(url, json=payload, timeout=20)
        return resp.status_code == 200
    except requests.RequestException:
        return False
