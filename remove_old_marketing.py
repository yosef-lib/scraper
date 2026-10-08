with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Regex to find /marketing block up to the next elif
pattern = r'elif cmd == "/marketing":.*?(?=elif cmd == "/generate_voucher":)'

new_text = re.sub(pattern, '', text, flags=re.DOTALL)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Old /marketing command removed from bot.py")
