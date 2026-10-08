import re

with open('notifier.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = """
def forward_message(chat_id: str, from_chat_id: str, message_id: int) -> bool:
    if not config.TELEGRAM_BOT_TOKEN:
        return False
    url = f"{config.TELEGRAM_API}/bot{config.TELEGRAM_BOT_TOKEN}/forwardMessage"
    payload = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
    try:
        resp = requests.post(url, json=payload, timeout=20)
        return resp.status_code == 200
    except requests.RequestException:
        return False
"""

if 'def forward_message' not in text:
    with open('notifier.py', 'a', encoding='utf-8') as f:
        f.write(new_func)
    print("notifier.py updated")
