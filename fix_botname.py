import os

files = [
    'bot.py',
    'marketing_bot.py',
    'promo.py',
    'morning_briefing.py',
    'weekly_report.py',
    'dex_screener.py',
]

replacements = [
    ('WhaleCryptoVIP_bot', 'scraping26bot'),
    ('https://t.me/scraping26bot?start=REF', 'https://t.me/scraping26bot?start=REF'),  # already correct after above
    ('https://lynk.id/whaleradar', 'Bank Mandiri: 1420019877454 a.n YOSEF PASKAH WAHYUTO'),
    ('link Lynk.id', 'bot @scraping26bot'),
    ('https://lynk.id/whaleradar\\n', 'Bank Mandiri: 1420019877454\\n'),
]

for fname in files:
    if not os.path.exists(fname):
        print(f"SKIP: {fname} not found")
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()

    original = text
    text = text.replace('WhaleCryptoVIP_bot', 'scraping26bot')
    text = text.replace('https://lynk.id/whaleradar', 'Bank Mandiri: 1420019877454 a.n YOSEF PASKAH WAHYUTO')
    text = text.replace('link Lynk.id', 'bot @scraping26bot')
    text = text.replace('nanti kalau ada yang nanya di komentar, arahin ke link Lynk.id', 'arahin ke @scraping26bot')

    if text != original:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"FIXED: {fname}")
    else:
        print(f"NO CHANGE: {fname}")
