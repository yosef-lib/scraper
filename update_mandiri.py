import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'elif cmd == "/premium":.*?(?=elif cmd == "/aktivasi":)'

new_premium = '''elif cmd == "/premium":
        msg = """💎 *AKSES PREMIUM WHALE CRYPTO VIP*

Harga Promo: *Rp 50.000* / 30 Hari

───────────────────
💳 *METODE PEMBAYARAN:*

1️⃣ *TRANSFER BANK (Bebas Biaya Admin):*
🏦 Bank Mandiri: `1420019877454`
👤 a.n: YOSEF PASKAH WAHYUTO

2️⃣ *OTOMATIS 24 JAM (QRIS / E-Wallet):*
👉 https://lynk.id/whaleradar
───────────────────

📩 *SETELAH TRANSFER MANUAL:*
Kirim bukti transfer ke Admin untuk mendapatkan Kode Voucher Aktivasi.

Jika sudah menerima kode voucher, ketik di chat ini:
`/aktivasi PREM-XXXX`"""
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    '''

new_text = re.sub(pattern, new_premium, text, flags=re.DOTALL)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Triple quote update done!")
