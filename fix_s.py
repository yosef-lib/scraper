import re
with open('storage.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '        conn.executescript("""\\n            CREATE INDEX IF NOT EXISTS idx_price_coin_time',
    '        conn.executescript("""\\n            CREATE INDEX IF NOT EXISTS idx_price_coin_time'
) # This was just a test. I will re-download the clean version or just fix the specific syntax.

