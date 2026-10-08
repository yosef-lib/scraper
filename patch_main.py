import re

with open('main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update alert_text to use format_copy_trade instead of format_line
old_alert = '''            alert_text = f"🚨 *VIP SIGNAL ALERT*\\\\n\\\\n{s.format_line()}"
            alert_text = alert_text.replace('\\\\n', '\\n')'''
new_alert = '''            alert_text = s.format_copy_trade()'''
text = text.replace(old_alert, new_alert)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)
