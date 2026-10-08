import re

with open('promo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add imports for chart generation
import_str = "import sources\nfrom main import generate_chart_url\n"
text = text.replace("import sources\n", import_str)

new_func = '''def send_promo_to_channel(coin_data) -> bool:
    channel_id = config._get("TELEGRAM_CHANNEL_ID", "")
    if not channel_id:
        log.info("TELEGRAM_CHANNEL_ID kosong. Melewati broadcast ke channel gratis.")
        return False
        
    vol_m = coin_data.volume_24h / 1_000_000 if coin_data.volume_24h else 0
    emoji = "🚀" if coin_data.change_24h > 0 else "📉"
    
    templates = [
        f"🔥 *MARKET UPDATE*\\n\\n{coin_data.coin.upper()} sedang bergejolak {emoji}\\nPerubahan: *{coin_data.change_24h:+.2f}%*\\nVolume 24j: *${vol_m:,.1f}M*\\n\\n💎 *Member VIP* sudah mendapatkan notifikasi & grafik otomatis dari pergerakan ini lebih awal!\\n\\nJangan sampai ketinggalan momentum besar berikutnya.\\n👉 *Upgrade VIP 24 Jam Non-stop:* https://lynk.id/whaleradar",
        
        f"🚨 *SMART MONEY TERDETEKSI BERGERAK*\\n\\nPerhatian pada koin {coin_data.coin.upper()}! Volume transaksi harian mencapai *${vol_m:,.1f}M*.\\n\\nDi channel gratis ini sinyal selalu *delay*. Ingin tahu koin apa lagi yang sedang diakumulasi bandar secara Real-Time?\\n\\n🤖 *Gunakan AI Smart Radar VIP sekarang!*\\n👉 Klik: https://lynk.id/whaleradar"
    ]
    
    msg = random.choice(templates)
    
    # Generate Chart for the promo!
    chart_data = sources.fetch_market_chart(coin_data.coin, days=1)
    if chart_data:
        chart_url = generate_chart_url(coin_data.coin, chart_data)
        return notifier.send_photo(channel_id, chart_url, caption=msg, parse_mode="Markdown")
    else:
        return notifier.send_message(channel_id, msg, parse_mode="Markdown")
'''

text = re.sub(r'def send_promo_to_channel.*?return notifier.send_message\(channel_id, msg, parse_mode="Markdown"\)', new_func, text, flags=re.DOTALL)

# Fix mojibake in send_threads_draft_to_admin
text = re.sub(r'f"dY - \*ASISTEN', r'f"🤖 *ASISTEN', text)
text = re.sub(r'f"dY`.*?\\n\\n"', r'f"👇👇👇\\n\\n"', text)
text = re.sub(r'f"dY`\+.*?\\n\\n"', r'f"👆👆👆\\n\\n"', text)

with open('promo.py', 'w', encoding='utf-8') as f:
    f.write(text)
