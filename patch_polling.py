import re

with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_polling = """def run_polling() -> None:
    config.require_telegram()
    storage.init_db()
    log.info("Bot polling dimulai.")
    offset = None
    while True:
        try:
            updates = _get_updates(offset)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                message = upd.get("message") or upd.get("edited_message")
                if not message:
                    continue
                chat = message.get("chat", {})
                chat_id = str(chat.get("id"))
                username = chat.get("username", "Unknown")
                text = message.get("text", "")
                if text:
                    handle_command(chat_id, username, text)
        except requests.RequestException as exc:
            log.warning("Error polling: %s", exc)
            time.sleep(5)
        except Exception as exc:
            log.exception("Kesalahan tak terduga: %s", exc)
            time.sleep(5)"""

new_polling = """def run_polling() -> None:
    config.require_telegram()
    storage.init_db()
    log.info("Bot polling dimulai.")
    offset = None
    while True:
        try:
            updates = _get_updates(offset)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                message = upd.get("message") or upd.get("edited_message")
                if not message:
                    continue
                chat = message.get("chat", {})
                chat_id = str(chat.get("id"))
                username = chat.get("username", "Unknown")
                
                if message.get("photo") or message.get("document"):
                    if str(chat_id) != str(config.TELEGRAM_ADMIN_CHAT_ID):
                        msg_id = message.get("message_id")
                        admin_id = config.TELEGRAM_ADMIN_CHAT_ID
                        if admin_id:
                            notifier.send_message(admin_id, f"💳 *BUKTI TRANSFER BARU*\\nDari: @{username}\\nID: `{chat_id}`\\n\\nSilakan cek foto di bawah ini. Jika valid, buat voucher dengan:\\n`/generate_voucher`\\nLalu kirimkan kodenya langsung ke user tersebut (Anda bisa klik ID-nya atau cari username-nya).", parse_mode="Markdown")
                            notifier.forward_message(admin_id, chat_id, msg_id)
                        notifier.send_message(chat_id, "✅ Bukti pembayaran Anda telah diteruskan ke Admin.\\n\\nMohon tunggu verifikasi. Kode Voucher akan segera dikirimkan ke Anda setelah dicek.")
                    continue

                text = message.get("text", "")
                if text:
                    handle_command(chat_id, username, text)
        except requests.RequestException as exc:
            log.warning("Error polling: %s", exc)
            time.sleep(5)
        except Exception as exc:
            log.exception("Kesalahan tak terduga: %s", exc)
            time.sleep(5)"""

if old_polling in text:
    new_text = text.replace(old_polling, new_polling)
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("bot.py updated with photo forwarding")
else:
    print("Could not find the run_polling block.")
