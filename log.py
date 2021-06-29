import telegram

from config import tg_token, chat_id


tg_bot_token = tg_token  # токен  # id беседы
bot = telegram.Bot(token=tg_bot_token)


def log_to_tg(text, photo, video):
    text = text.replace('[31m ', '').replace('Зарепортил', '\nЗарепортил')
    try:
        if photo != None:
            bot.send_photo(chat_id=chat_id, photo=photo, caption=text)
        elif video != None:
            bot.send_message(chat_id=chat_id, text=text+'\n\n'+video)
        else:
            bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(e)
