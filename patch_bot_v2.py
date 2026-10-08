import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add imports
old_import = 'from main import generate_chart_url'
new_import = '''from main import generate_chart_url
import dex_screener'''
text = text.replace(old_import, new_import)

# 2. Update keyboard - add Referral and Meme buttons
old_kb = '''        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "🌐 Tren Global"}, {"text": "💎 Upgrade VIP"}],
            [{"text": "👤 Status Akun"}],
        ],'''
new_kb = '''        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "🌐 Tren Global"}, {"text": "🐕 Radar Meme Coin"}],
            [{"text": "🤝 Link Referral"}, {"text": "💎 Upgrade VIP"}],
            [{"text": "👤 Status Akun"}],
        ],'''
text = text.replace(old_kb, new_kb)

# 3. Add button routing
old_route = '''    elif text == "🌐 Tren Global":
        cmd = "/trending"'''
new_route = '''    elif text == "🌐 Tren Global":
        cmd = "/trending"
    elif text == "🐕 Radar Meme Coin":
        cmd = "/meme"
    elif text == "🤝 Link Referral":
        cmd = "/referral"'''
text = text.replace(old_route, new_route)

# 4. Add /start referral logic
old_start = '''    if cmd == "/start":
        msg = (
            "🚀 *Selamat datang di Whale Crypto VIP!*\\n\\n"
            "Gunakan tombol menu di bagian bawah layar untuk mulai menggunakan fitur bot."
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)'''
new_start = '''    if cmd == "/start":
        # Cek referral dari link (format: /start REF_chatid)
        if len(parts) >= 2 and parts[1].startswith("REF"):
            referrer_id = parts[1].replace("REF", "")
            if referrer_id != chat_id:
                if storage.record_referral(referrer_id, chat_id):
                    # Kasih bonus +7 hari VIP ke referrer
                    row = storage.get_subscriber(referrer_id)
                    if row:
                        storage.activate_premium(referrer_id, 7)
                        notifier.send_message(referrer_id, f"🎉 *BONUS REFERRAL!* Teman Anda baru saja bergabung. Anda mendapat *+7 Hari VIP GRATIS!*", parse_mode="Markdown")
        msg = (
            "🚀 *Selamat datang di Whale Crypto VIP!*\\n\\n"
            "Bot AI sinyal kripto terlengkap di Indonesia:\\n"
            "✅ Sinyal Entry + TP + SL Otomatis\\n"
            "✅ Radar Smart Money 20 Koin Top\\n"
            "✅ Radar Meme Coin DEX (Solana & ETH)\\n"
            "✅ Morning Briefing + Fear & Greed Index\\n\\n"
            "Gunakan tombol menu di bagian bawah layar untuk mulai! 👇"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)'''
text = text.replace(old_start, new_start)

# 5. Add /meme and /referral handlers before elif cmd == "/premium"
old_mark = '''    elif cmd == "/trending":'''
new_mark = '''    elif cmd == "/meme":
        if not storage.is_premium(chat_id):
            notifier.send_message(chat_id, "⚠️ Radar Meme Coin hanya untuk Member VIP/Trial. Klik [Klaim Free Trial] untuk mencoba gratis!", reply_markup=keyboard)
            return
        notifier.send_message(chat_id, "⏳ Memindai DEX radar untuk meme coin Solana & ETH...", reply_markup=keyboard)
        dex_screener.run_dex_radar(broadcast=False)
        # Kirim langsung ke user
        sol_pairs = dex_screener.get_trending_pairs("solana")
        eth_pairs = dex_screener.get_trending_pairs("ethereum")
        all_pairs = sol_pairs[:3] + eth_pairs[:2]
        if not all_pairs:
            notifier.send_message(chat_id, "❌ Tidak ada meme coin yang menarik saat ini. Coba lagi nanti!", reply_markup=keyboard)
            return
        for pair in all_pairs:
            msg = dex_screener.format_dex_alert(pair)
            notifier.send_message(chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True)

    elif cmd == "/referral":
        count = storage.get_referral_count(chat_id)
        ref_link = f"https://t.me/WhaleCryptoVIP_bot?start=REF{chat_id}"
        bonus_days = count * 7
        msg = (
            f"🤝 *PROGRAM REFERRAL VIP*\\n\\n"
            f"Ajak teman Anda bergabung dan dapatkan:\\n"
            f"✅ *+7 Hari VIP GRATIS* untuk setiap 1 teman yang join!\\n\\n"
            f"📊 Statistik Anda:\\n"
            f"👥 Total Teman Diajak: *{count} orang*\\n"
            f"🎁 Total Bonus: *+{bonus_days} Hari VIP*\\n\\n"
            f"🔗 *Link Referral Unik Anda:*\\n"
            f"{ref_link}\\n\\n"
            f"_Bagikan link ini ke teman, grup WA, atau postingan Threads Anda!_"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    elif cmd == "/trending":'''
text = text.replace(old_mark, new_mark)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)
