with open('bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '/premium' in line:
        print(f'Line {idx+1}: {line}')
