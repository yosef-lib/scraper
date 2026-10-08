import re

with open('storage.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add referral table to schema
schema_old = '''            CREATE INDEX IF NOT EXISTS idx_price_coin_time
                ON price_history (coin, recorded_at);'''
schema_new = '''            CREATE TABLE IF NOT EXISTS referrals (
                referrer_chat_id TEXT NOT NULL,
                referred_chat_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (referrer_chat_id, referred_chat_id)
            );

            CREATE INDEX IF NOT EXISTS idx_price_coin_time
                ON price_history (coin, recorded_at);'''
text = text.replace(schema_old, schema_new)

# Also add migration for referrals table
migration_old = '''        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN has_trial INTEGER DEFAULT 0")
        except Exception:
            pass'''
migration_new = '''        try:
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
            pass'''
text = text.replace(migration_old, migration_new)

# Add referral functions at end
referral_funcs = '''
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
'''
text += referral_funcs

with open('storage.py', 'w', encoding='utf-8') as f:
    f.write(text)
