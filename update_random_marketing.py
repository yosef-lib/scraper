import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'elif cmd == "/marketing":.*?(?=elif cmd == "/generate_voucher":)'

new_marketing = '''elif cmd == "/marketing":
        if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
            notifier.send_message(chat_id, "Akses ditolak.")
            return

        import random
        prices = sources.fetch_prices()
        top_gainer = max(prices, key=lambda x: x.change_24h) if prices else None
        coin_name = top_gainer.coin.upper() if top_gainer else "BITCOIN"
        coin_gain = top_gainer.change_24h if top_gainer else 5.4

        story_templates = [
            f"📱 *DRAFT THREADS (Story A)*\\n\\nAwalnya iseng bikin Bot AI buat mantau gerak-gerik Smart Money di kripto.\\nEh tadi botnya nge-detect lonjakan volume di {coin_name} pas harganya masih anteng.\\nGak sampe beberapa jam langsung naik +{coin_gain:.1f}% 🔥\\n\\nBuat yang mau nyobain tes Bot AI ini GRATIS 24 jam, klik link Telegram di bio ya!\\n👉 t.me/WhaleCryptoFree 🚀",
            f"📱 *DRAFT THREADS (Story B)*\\n\\nBanyak yang nanya gimana cara tau koin mau 'terbang' sebelum kejadian. Rahasianya? Lacak volume Paus (Smart Money) pakai algoritma AI.\\n\\nPagi ini sistem nangkap sinyal {coin_name} pas masih sepi, eh sekarang udah meroket +{coin_gain:.1f}% 🚀\\n\\nJangan trading pakai firasat. Tes pakai AI kita GRATIS 24 jam, cek link di bio: t.me/WhaleCryptoFree 👇",
            f"📱 *DRAFT THREADS (Story C)*\\n\\nDulu capek trading sering nyangkut karena fomo grup pom-pom. Sekarang murni pakai Bot AI pelacak anomali volume.\\n\\nData murni, no baper. Buktinya hari ini {coin_name} sukses hit profit +{coin_gain:.1f}% otomatis. 🎯\\n\\nMau nyicip keakuratan botnya gratis? Langsung ke Telegram @WhaleCryptoVIP_bot sekarang!"
        ]

        edu_templates = [
            f"📱 *DRAFT THREADS (Edukasi A)*\\n\\nBeda grup sinyal biasa vs Bot AI Whale Radar:\\n❌ Grup biasa: Cuma kasih tebakan arah tanpa Stop Loss.\\n✅ Bot AI: Kasih titik Entry, Target Profit 1 & 2, plus Stop Loss pakai matematika.\\n\\nHari ini sinyal {coin_name} berhasil tembus +{coin_gain:.1f}%! 🎯\\n\\nCoba gratis 24 jam di Telegram: @WhaleCryptoVIP_bot",
            f"📱 *DRAFT THREADS (Edukasi B)*\\n\\nStop nyumbang duit ke market! 📉\\nKalau trading nggak pakai Stop Loss & ngasal entry, mending setop. AI Whale Crypto ngasih sinyal lengkap (Entry s/d SL).\\n\\nBerkat kalkulasi mesin, {coin_name} sukses cuan +{coin_gain:.1f}% hari ini. Tes botnya gratis tanpa risiko di bio kita! 🤖",
            f"📱 *DRAFT THREADS (Edukasi C)*\\n\\nVolume adalah kunci di Crypto! 📊\\nBot Whale Radar mendeteksi lonjakan anomali di {coin_name} hari ini, dan boom: harganya naik +{coin_gain:.1f}% tersentuh dengan mulus.\\n\\nAI nggak pernah bohong soal data. Buktikan sendiri, ambil Free Trial 24 Jam di @WhaleCryptoVIP_bot 🚀"
        ]

        post1 = random.choice(story_templates)
        post2 = random.choice(edu_templates)
        
        hashtag = "\\n\\n#crypto #bitcoin #trading #investasi #whaleradar"

        notifier.send_message(chat_id, "🚀 *DRAFT MARKETING RANDOM HARI INI*\\n\\nBot telah mengacak template variasi untuk Anda. Copas teks di bawah ini ke Threads! 👇", parse_mode="Markdown")
        notifier.send_message(chat_id, post1 + hashtag, parse_mode="Markdown")
        notifier.send_message(chat_id, post2 + hashtag, parse_mode="Markdown")

    '''

new_marketing = new_marketing.replace('\\', '\\\\')

new_text = re.sub(pattern, new_marketing, text, flags=re.DOTALL)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Double-escaped marketing applied successfully!")
