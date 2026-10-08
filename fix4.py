import re
with open('main.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = '''def build_summary(signals: list[analyzer.Signal]) -> str:
    wib = timezone(timedelta(hours=7))
    now_str = datetime.now(wib).strftime("%d-%m-%Y %H:%M WIB")
    header = f"📊 *Ringkasan Harga* ({now_str})\\n"
    body = "\\n".join(s.format_line() for s in signals)
    alerts = analyzer.only_alerts(signals)
    whales = [s for s in alerts if s.is_whale]
    
    footer = f"\\n\\n⚠️ {len(alerts)} sinyal alert ({len(whales)} Lonjakan Volume)."
    return f"{header}\\n{body}{footer}"'''

text = re.sub(r'def build_summary.*?return f"\{header\}\\n\{body\}\{footer\}"', new_func, text, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(text)
