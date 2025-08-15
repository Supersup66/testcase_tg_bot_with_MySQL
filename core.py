import time
import telebot

from constants import TOKEN
from logger import logger


last_active_time = {}

try:
    bot_unit = telebot.TeleBot(TOKEN)
except Exception as e:
    logger.critical(f'Unable connect to Telegram API: {e}')
    raise telebot.apihelper.ApiTelegramException


def check_activity():
    while True:
        current_time = time.time()
        inactive_users = []
        global last_active_time
        for chat_id, last_active in list(last_active_time.items()):
            if current_time - last_active > 1800:
                inactive_users.append(chat_id)

        for chat_id in inactive_users:
            main_menu(chat_id=chat_id)
            last_active_time.pop(chat_id)

        time.sleep(12)


def main_menu(chat_id):
    bot_unit.send_message(
        chat_id, 'Вы вернулись в главное меню. Нажмите /start для начала.'
    )
