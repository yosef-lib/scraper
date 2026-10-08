with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Keyboard
old_kb = '''        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "💎 Upgrade VIP"}, {"text": "👤 Status Akun"}],
        ],'''
new_kb = '''        "keyboard": [
            [{"text": "🎫 Klaim Free Trial"}, {"text": "📈 Cek Grafik Koin"}],
            [{"text": "🌐 Tren Global"}, {"text": "💎 Upgrade VIP"}],
            [{"text": "👤 Status Akun"}],
        ],'''
text = text.replace(old_kb, new_kb)

# 2. Add routing
old_route = '''    elif text == "💎 Upgrade VIP":
        cmd = "/premium"'''
new_route = '''    elif text == "🌐 Tren Global":
        cmd = "/trending"
    elif text == "💎 Upgrade VIP":
        cmd = "/premium"'''
text = text.replace(old_route, new_route)

# 3. Add handler logic for /trending
import_str = 'import requests\\n'
# Find a place to insert the command
insert_marker = '    elif cmd == "/premium":'
trending_cmd = '''    elif cmd == "/trending":
        if not storage.is_premium(chat_id):
            notifier.send_message(chat_id, "⚠️ Fitur Tren Global (Pendeteksi Smart Money On-Chain) hanya untuk Member VIP atau Trial. Klik [Klaim Free Trial] untuk mencoba!", reply_markup=keyboard)
            return
            
        notifier.send_message(chat_id, "⏳ Sedang memindai radar global...", reply_markup=keyboard)
        try:
            resp = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=15)
            data = resp.json()
            coins = data.get("coins", [])[:5]
            
            lines = []
            for idx, c in enumerate(coins):
                item = c["item"]
                lines.append(f"{idx+1}. *{item['symbol'].upper()}* ({item['name']})")
                
            msg = "🌐 *TRENDING GLOBAL MINGGU INI* 🌐\\n\\nIni adalah 5 koin yang paling banyak diakumulasi dan dicari oleh Smart Money di seluruh dunia saat ini:\\n\\n"
            msg += "\\n".join(lines)
            msg += "\\n\\n_Gunakan perintah /chart <koin> untuk melihat grafiknya!_"
            msg = msg.replace('\\n', '\\n')
            notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)
        except Exception as e:
            notifier.send_message(chat_id, "❌ Gagal memindai radar global saat ini.", reply_markup=keyboard)

    elif cmd == "/premium":'''
trending_cmd = trending_cmd.replace('\\\\n', '\\n')
text = text.replace(insert_marker, trending_cmd)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)
