import re
with open('main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the broken f-string
broken_str = 'header = f"📊 *Ringkasan Harga* ({now_str})\\n"'
text = re.sub(r'header = f"📊 \*Ringkasan Harga\* \(\{now_str\}\)\n"', broken_str, text)
text = text.replace('body = "\n".join(', 'body = "\\n".join(')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)
