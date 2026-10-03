"""Konfigurasi terpusat. Semua rahasia dibaca dari file .env (tidak di kode).

Aturan emas: JANGAN pernah menulis token/API key langsung di kode.
Salin .env.example menjadi .env lalu isi nilainya.
"""
import os
from pathlib import Path

# Muat .env bila library python-dotenv tersedia. Kalau tidak ada,
# fallback ke environment variable sistem (dipakai systemd EnvironmentFile).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover - fallback aman
    pass

BASE_DIR = Path(__file__).resolve().parent


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_int(name: str, default: int) -> int:
    raw = _get(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = _get(name, str(default))
    try:
        return float(raw)
    except ValueError:
        return default


def _get_list(name: str, default: str = "") -> list[str]:
    raw = _get(name, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Telegram ---
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = _get("TELEGRAM_ADMIN_CHAT_ID")

# --- Sumber data (CoinGecko, tanpa API key) ---
COINS = _get_list("COINS", "bitcoin,ethereum,solana")
VS_CURRENCY = _get("VS_CURRENCY", "usd")

# --- Sinyal / alert ---
ALERT_PERCENT = _get_float("ALERT_PERCENT", 3.0)
CHECK_INTERVAL_MINUTES = _get_int("CHECK_INTERVAL_MINUTES", 15)

# --- Penyimpanan ---
DB_PATH = _get("DB_PATH", "storage.sqlite3")
if not os.path.isabs(DB_PATH):
    DB_PATH = str(BASE_DIR / DB_PATH)

# --- Monetisasi ---
PREMIUM_PRICE_IDR = _get_int("PREMIUM_PRICE_IDR", 25000)
PREMIUM_DURATION_DAYS = _get_int("PREMIUM_DURATION_DAYS", 30)
ADMIN_SECRET = _get("ADMIN_SECRET")

# --- Endpoint API ---
COINGECKO_API = "https://api.coingecko.com/api/v3"
TELEGRAM_API = "https://api.telegram.org"

LOGS_DIR = BASE_DIR / "logs"


def require_telegram() -> None:
    """Pastikan konfigurasi Telegram ada sebelum mengirim pesan."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN belum diisi. Salin .env.example menjadi .env "
            "dan isi token dari @BotFather."
        )
