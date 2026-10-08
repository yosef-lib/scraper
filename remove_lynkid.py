with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('elif cmd == "/premium":')
end_idx = text.find('elif cmd == "/aktivasi":')

if start_idx != -1 and end_idx != -1:
    new_block = """elif cmd == "/premium":
        msg = (
            "💎 *AKSES PREMIUM WHALE CRYPTO VIP*\\n\\n"
            "Harga Promo: *Rp 50.000* / 30 Hari\\n\\n"
            "───────────────────\\n"
            "💳 *METODE PEMBAYARAN:*\\n\\n"
            "🏦 Bank Mandiri: `1420019877454`\\n"
            "👤 a.n: YOSEF PASKAH WAHYUTO\\n\\n"
            "*(Bebas Biaya Admin, 100% Aman)*\\n"
            "───────────────────\\n\\n"
            "📩 *CARA AKTIVASI VIP:*\\n"
            "1. Lakukan transfer Rp 50.000 ke rekening Mandiri di atas.\\n"
            "2. Kirim screenshot bukti transfer ke Admin via chat.\\n"
            "3. Admin akan memberikan Kode Voucher VIP Anda.\\n\\n"
            "Jika sudah menerima kode voucher, ketik di chat ini:\\n"
            "`/aktivasi PREM-XXXX`"
        )
        notifier.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=keyboard)

    """
    new_text = text[:start_idx] + new_block + text[end_idx:]
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Replaced by slicing!")
else:
    print("Indexes not found!")
