with open('storage.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix init_db by doing it correctly
def_init = '''def init_db() -> None:
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

            CREATE INDEX IF NOT EXISTS idx_price_coin_time
                ON price_history (coin, recorded_at);
            """
        )
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN has_trial INTEGER DEFAULT 0")
        except Exception:
            pass'''

import re
text = re.sub(r'def init_db\(\) -> None:.*?# --- Price History ---', def_init + '\\n\\n# --- Price History ---', text, flags=re.DOTALL)

with open('storage.py', 'w', encoding='utf-8') as f:
    f.write(text)
