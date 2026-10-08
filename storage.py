"""Lapisan penyimpanan SQLite.

Menyimpan:
- riwayat harga (price_history) untuk menghitung sinyal
- daftar subscriber (subscribers) untuk gating free vs premium
- voucher aktivasi (vouchers) untuk sistem langganan unik sekali pakai
"""
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import config


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                price REAL NOT NULL,
                change_24h REAL NOT NULL,
                volume_24h REAL DEFAULT 0,
                recorded_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id TEXT PRIMARY KEY,
                username TEXT,
                plan TEXT NOT NULL DEFAULT 'free',
                premium_until TEXT,
                joined_at TEXT NOT NULL,
                has_trial INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS vouchers (
                code TEXT PRIMARY KEY,
                days INTEGER NOT NULL,
                is_used INTEGER DEFAULT 0,
                used_by TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS referrals (
                referrer_chat_id TEXT NOT NULL,
                referred_chat_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (referrer_chat_id, referred_chat_id)
            );

            CREATE INDEX IF NOT EXISTS idx_price_coin_time
                ON price_history (coin, recorded_at);
            """
        )
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN has_trial INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            conn.execute("""CREATE TABLE IF NOT EXISTS referrals (
                referrer_chat_id TEXT NOT NULL,
                referred_chat_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (referrer_chat_id, referred_chat_id)
            )""")
        except Exception:
            pass

# --- Price History ---
def save_price(coin: str, price: float, change_24h: float, volume_24h: float = 0) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO price_history (coin, price, change_24h, volume_24h, recorded_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (coin, price, change_24h, volume_24h, datetime.now(timezone.utc).isoformat()),
        )

def get_price_history(coin: str, limit: int = 24) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM price_history WHERE coin = ? ORDER BY id DESC LIMIT ?",
            (coin, limit),
        )
        return cur.fetchall()

def cleanup_history(days: int = 30) -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM price_history WHERE recorded_at < ?", (cutoff,)
        )
        return cur.rowcount


# --- Subscriber ---
def upsert_subscriber(chat_id: str, username: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO subscribers (chat_id, username, joined_at) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET username = excluded.username",
            (str(chat_id), username, datetime.now(timezone.utc).isoformat()),
        )

def get_subscriber(chat_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM subscribers WHERE chat_id = ?", (str(chat_id),)
        )
        return cur.fetchone()

def is_premium(chat_id: str) -> bool:
    row = get_subscriber(chat_id)
    if not row or row["plan"] != "premium" or not row["premium_until"]:
        return False
    try:
        until = datetime.fromisoformat(row["premium_until"])
    except ValueError:
        return False
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    
    # Auto-demote jika sudah expired (optional logic, tapi cukup return False di sini)
    return until > datetime.now(timezone.utc)


def activate_premium(chat_id: str, days: int) -> str:
    # Jika sudah premium, tambah harinya
    row = get_subscriber(chat_id)
    now = datetime.now(timezone.utc)
    if row and row["premium_until"]:
        try:
            current_until = datetime.fromisoformat(row["premium_until"])
            if current_until.tzinfo is None:
                current_until = current_until.replace(tzinfo=timezone.utc)
            if current_until > now:
                now = current_until
        except ValueError:
            pass
            
    until = now + timedelta(days=days)
    with get_conn() as conn:
        conn.execute(
            "UPDATE subscribers SET plan = 'premium', premium_until = ? "
            "WHERE chat_id = ?",
            (until.isoformat(), str(chat_id)),
        )
    return until.isoformat()

def all_subscribers(premium_only: bool = False) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM subscribers")
        rows = cur.fetchall()
    if premium_only:
        return [r for r in rows if is_premium(r["chat_id"])]
    return rows

# --- Vouchers ---
def create_voucher(days: int = 30) -> str:
    # PREM- (8 karakter acak)
    code = f"PREM-{uuid.uuid4().hex[:8].upper()}"
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO vouchers (code, days, created_at) VALUES (?, ?, ?)",
            (code, days, datetime.now(timezone.utc).isoformat())
        )
    return code

def claim_voucher(code: str, chat_id: str) -> tuple[bool, str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM vouchers WHERE code = ?", (code,))
        row = cur.fetchone()
        
        if not row:
            return False, "Kode voucher tidak ditemukan."
        if row["is_used"]:
            return False, "Kode voucher sudah pernah digunakan."
            
        # Tandai terpakai
        conn.execute(
            "UPDATE vouchers SET is_used = 1, used_by = ? WHERE code = ?",
            (str(chat_id), code)
        )
        
    # Aktivasi akunnya
    until = activate_premium(chat_id, row["days"])
    return True, until

def claim_trial(chat_id: str) -> tuple[bool, str]:
    upsert_subscriber(chat_id)
    row = get_subscriber(chat_id)
    if row and row.get("has_trial"):
        return False, "Anda sudah pernah mengklaim Free Trial."
        
    until = activate_premium(chat_id, 1)
    with get_conn() as conn:
        conn.execute("UPDATE subscribers SET has_trial = 1 WHERE chat_id = ?", (str(chat_id),))
    return True, until

def get_referral_count(chat_id: str) -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM referrals WHERE referrer_chat_id = ?", (str(chat_id),))
        return cur.fetchone()[0]

def record_referral(referrer_id: str, referred_id: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO referrals (referrer_chat_id, referred_chat_id, created_at) VALUES (?, ?, ?)",
                (str(referrer_id), str(referred_id), __import__("datetime").datetime.utcnow().isoformat())
            )
        return True
    except Exception:
        return False
