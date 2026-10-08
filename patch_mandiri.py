with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

pattern = r'elif cmd == "/premium":\s+msg = \(\s+f"💎 \*Akses Premium VIP\*.*?\)'

replacement = '''elif cmd == "/premium":
        msg = (
            "💎 *AKSES PREMIUM WHALE CRYPTO VIP*\\n\\n"
            "Harga Promo: *Rp 50.000* / 30 Hari\\n\\n"
            "───────────────────\\n"
            "💳 *METODE PEMBAYARAN:*\\n\\n"
            "1️⃣ *TRANSFER BANK (Bebas Biaya Admin):*\\n"
            "🏦 Bank Mandiri: 1420019877454\\n"
            "👤 a.n: YOSEF PASKAH WAHYUTO\\n\\n"
            "2️⃣ *OTOMATIS 24 JAM (QRIS / E-Wallet):*\\n"
            "👉 https://lynk.id/whaleradar\\n"
            "───────────────────\\n\\n"
            "📩 *SETELAH TRANSFER MANUAL:*\\n"
            "Kirim bukti transfer ke Admin untuk mendapatkan Kode Voucher Aktivasi.\\n\\n"
            "Jika sudah menerima kode voucher, ketik di chat ini:\\n"
            "/aktivasi PREM-XXXX"
        )'''

text = re.sub(pattern, replacement, text, flags=re.DOTALL)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)
