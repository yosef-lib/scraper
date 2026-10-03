"""Lapisan penyimpanan SQLite.

Menyimpan:
- riwayat harga (price_history) untuk menghitung sinyal
- daftar subscriber (subscribers) untuk gating free vs premium
"""
import sqlite3
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
                recorded_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id TEXT PRIMARY KEY,
                username TEXT,
                plan TEXT NOT NULL DEFAULT 'free',
                premium_until TEXT,
                joined_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_price_coin_time
                ON price_history (coin, recorded_at);
            """
        )


def save_price(coin: str, price: float, change_24h: float) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO price_history (coin, price, change_24h, recorded_at) "
            "VALUES (?, ?, ?, ?)",
            (coin, price, change_24h, datetime.now(timezone.utc).isoformat()),
        )


def last_price(coin: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM price_history WHERE coin = ? ORDER BY id DESC LIMIT 1",
            (coin,),
        )
        return cur.fetchone()


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
    return until > datetime.now(timezone.utc)


def activate_premium(chat_id: str, days: int) -> str:
    until = datetime.now(timezone.utc) + timedelta(days=days)
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
