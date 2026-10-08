import re

with open('main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('?? *Ringkasan Harga*', '📊 *Ringkasan Harga*')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)
