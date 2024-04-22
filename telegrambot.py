import os
from telegram import Bot

def sendMessage(data):
    tg_bot = Bot(token=os.environ['TOKEN'])
    channel = os.environ['CHANNEL']
    try:
        print('--->Sending message to telegram')
        tg_bot.sendMessage(
            channel,
            data,
            parse_mode=None,  # Do not use Markdown or HTML
        )
        return True
    except Exception as e:
        print(f"[X] Telegram Error:\n> {e}")
    return False
