import re

with open('morning_briefing.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix: escape asterisks in the f-string concatenation for feat_greed label
# The error is at offset 735 which is likely a markdown entity not closed properly
# Fix fg_text to escape asterisks by using separate var
old = '        fg_text = f"{fear_val} — *Extreme Greed*"'
new = '        fg_text = str(fear_val) + " — Extreme Greed (Sangat Serakah)"'
text = text.replace(old, new)

old = '        fg_text = f"{fear_val} — *Greed*"'
new = '        fg_text = str(fear_val) + " — Greed (Serakah)"'
text = text.replace(old, new)

old = '        fg_text = f"{fear_val} — *Neutral*"'
new = '        fg_text = str(fear_val) + " — Neutral"'
text = text.replace(old, new)

old = '        fg_text = f"{fear_val} — *Fear*"'
new = '        fg_text = str(fear_val) + " — Fear (Takut)"'
text = text.replace(old, new)

old = '        fg_text = f"{fear_val} — *Extreme Fear*"'
new = '        fg_text = str(fear_val) + " — Extreme Fear (Sangat Takut)"'
text = text.replace(old, new)

with open('morning_briefing.py', 'w', encoding='utf-8') as f:
    f.write(text)
