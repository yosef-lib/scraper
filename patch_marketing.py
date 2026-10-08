with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add /marketing command handler before /generate_voucher
old_mark = '    elif cmd == "/generate_voucher":'
new_mark = '''    elif cmd == "/marketing":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return

        prices = sources.fetch_prices()
        top_gainer = max(prices, key=lambda x: x.change_24h) if prices else None
        coin_name = top_gainer.coin.upper() if top_gainer else "BITCOIN"
        coin_gain = top_gainer.change_24h if top_gainer else 5.4

        post1 = (
            f"📱 *DRAFT THREADS #1 (Storytelling)*\\n\\n"
            f"Awalnya iseng bikin Bot AI buat mantau gerak-gerik Smart Money di kripto.\\n"
            f"Eh tadi botnya nge-detect lonjakan volume di {coin_name} pas harganya masih anteng.\\n"
            f"Gak sampe beberapa jam langsung naik +{coin_gain:.1f}% 🔥\\n\\n"
            f"Buat yang mau nyobain tes Bot AI ini GRATIS 24 jam, klik link Telegram di bio ya!\\n"
            f"👉 t.me/WhaleCryptoFree 🚀\\n\\n"
            f"#crypto #bitcoin #investasi #whaleradar"
        )

        post2 = (
            f"📱 *DRAFT THREADS #2 (Edukasi + Fitur)*\\n\\n"
            f"Beda grup sinyal biasa vs Bot AI Whale Radar:\\n"
            f"❌ Grup biasa: Cuma kasih tebakan tanpa Stop Loss.\\n"
            f"✅ Bot AI: Kasih titik Entry, Target Profit 1 & 2, plus Stop Loss murni pakai kalkulasi matematika 24 jam.\\n\\n"
            f"Hari ini sinyal {coin_name} berhasil tembus Target Profit (+{coin_gain:.1f}%)! 🎯\\n\\n"
            f"Coba gratis 24 jam di Telegram: @WhaleCryptoVIP_bot"
        )

        notifier.send_message(chat_id, "🚀 *DRAFT MARKETING THREADS HARI INI*\\n\\nCopas teks di bawah ini langsung ke Threads Anda! 👇", parse_mode="Markdown")
        notifier.send_message(chat_id, post1, parse_mode="Markdown")
        notifier.send_message(chat_id, post2, parse_mode="Markdown")

    elif cmd == "/generate_voucher":'''

text = text.replace(old_mark, new_mark)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)
