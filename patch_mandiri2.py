with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''    elif cmd == "/premium":
        msg = (
            f"💎 *Akses Premium VIP*\n\n"
            f"Harga Promo: *Rp 50.000* / 30 hari\n"
            f"Fitur VIP:\n"
            f"✅ Auto-Chart: Kirim grafik saat volume melonjak!\n"
            f"✅ On-Demand Chart: Bebas minta grafik 24 jam!\n"
            f"✅ Akses Real-Time Top 20 Koin\n\n"
            f"👉 *Beli Otomatis 24 Jam:*\n"
            f"Klik link: https://lynk.id/whaleradar\n\n"
            f"Setelah bayar via QRIS/GoPay, Anda akan mendapat kode voucher.\n"
            f"Ketik kodenya di chat ini:\n/aktivasi PREM-XXXX"
        )'''

new_code = '''    elif cmd == "/premium":
        msg = (
            "💎 *AKSES PREMIUM WHALE CRYPTO VIP*\n\n"
            "Harga Promo: *Rp 50.000* / 30 Hari\n\n"
            "───────────────────\n"
            "💳 *METODE PEMBAYARAN:*\n\n"
            "1️⃣ *TRANSFER BANK (Bebas Biaya Admin):*\n"
            "🏦 Bank Mandiri: 1420019877454\n"
            "👤 a.n: YOSEF PASKAH WAHYUTO\n\n"
            "2️⃣ *OTOMATIS 24 JAM (QRIS / E-Wallet):*\n"
            "👉 https://lynk.id/whaleradar\n"
            "───────────────────\n\n"
            "📩 *SETELAH TRANSFER MANUAL:*\n"
            "Kirim bukti transfer ke Admin untuk mendapatkan Kode Voucher Aktivasi.\n\n"
            "Jika sudah menerima kode voucher, ketik di chat ini:\n"
            "/aktivasi PREM-XXXX"
        )'''

if old_code in text:
    text = text.replace(old_code, new_code)
    print("Replaced successfully!")
else:
    print("Old code not found")

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)
