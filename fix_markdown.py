with open('bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('notifier.send_message(chat_id, post1 + hashtag, parse_mode="Markdown")', 'notifier.send_message(chat_id, post1 + hashtag)')
text = text.replace('notifier.send_message(chat_id, post2 + hashtag, parse_mode="Markdown")', 'notifier.send_message(chat_id, post2 + hashtag)')

text = text.replace('*DRAFT THREADS', 'DRAFT THREADS').replace(')*', ')')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Removed Markdown from drafts.")
