# Fix 1: f-string backslash issue in morning_briefing.py
with open('morning_briefing.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the problematic f-string with concatenation
old_line = "    sep = '\u2500' * 28"
text = text.replace(
    "f\"{'─'*28}\n\"",
    "f\"{'─'*28}\""
).replace(
    "f\"{'─'*28}\n",
    "f\"{'─'*28}\n"
)

# Simpler: replace the whole msg construction
import re
old_msg = '''    msg = (
        f"☀️ *SELAMAT PAGI! — BRIEFING KRIPTO*\\n"
        f"📅 {today}\\n\\n"
        f"{'─'*28}\\n"
        f"{fg_emoji} *Fear & Greed Index:*\\n"
        f"  {fg_text}\\n\\n"
        f"🚀 *Top Gainers 24h:*\\n{gainers_text if gainers_text else '  N/A\\n'}\\n"
        f"📉 *Top Losers 24h:*\\n{losers_text if losers_text else '  N/A\\n'}\\n"
        f"{'─'*28}\\n"
        f"💡 *Tips Hari Ini:*\\n{tips}\\n\\n"
        f"🤖 Ingin sinyal *ENTRY + TP + SL* otomatis?\\n"
        f"👉 Upgrade ke VIP: https://lynk.id/whaleradar\\n"
        f"🎫 Atau coba *GRATIS 24 JAM* langsung di bot: @WhaleCryptoVIP_bot"
    )'''
new_msg = '''    sep = "─" * 28
    gainers_str = gainers_text if gainers_text else "  N/A\\n"
    losers_str = losers_text if losers_text else "  N/A\\n"
    msg = (
        "☀️ *SELAMAT PAGI! — BRIEFING KRIPTO*\\n"
        "📅 " + today + "\\n\\n" +
        sep + "\\n" +
        fg_emoji + " *Fear & Greed Index:*\\n"
        "  " + fg_text + "\\n\\n"
        "🚀 *Top Gainers 24h:*\\n" + gainers_str + "\\n"
        "📉 *Top Losers 24h:*\\n" + losers_str + "\\n" +
        sep + "\\n"
        "💡 *Tips Hari Ini:*\\n" + tips + "\\n\\n"
        "🤖 Ingin sinyal *ENTRY + TP + SL* otomatis?\\n"
        "👉 Upgrade ke VIP: https://lynk.id/whaleradar\\n"
        "🎫 Atau coba *GRATIS 24 JAM* langsung di bot: @WhaleCryptoVIP_bot"
    )'''
text = text.replace(old_msg, new_msg)

with open('morning_briefing.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Fix 2: dex_screener - fix NoneType issue from /trending API endpoint
with open('dex_screener.py', 'r', encoding='utf-8') as f:
    ds = f.read()

old_dex = '''def get_trending_pairs(chain: str = "solana", min_vol_usd: float = 500_000) -> list[dict]:
    \"\"\"Ambil pasangan trading yang sedang trending di chain tertentu.\"\"\"
    try:
        url = f"{DEX_API}/tokens/trending"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        pairs = data.get("pairs", [])'''
new_dex = '''def get_trending_pairs(chain: str = "solana", min_vol_usd: float = 500_000) -> list[dict]:
    \"\"\"Ambil pasangan trading yang sedang trending di chain tertentu.\"\"\"
    try:
        url = f"{DEX_API}/search?q={chain}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return []'''
ds = ds.replace(old_dex, new_dex)

with open('dex_screener.py', 'w', encoding='utf-8') as f:
    f.write(ds)
