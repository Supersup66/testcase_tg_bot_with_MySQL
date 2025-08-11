import os
from dotenv import load_dotenv
import pymysql.cursors
import telebot
from telebot.types import Message

# Загружаем переменные среды из .env файла
load_dotenv()

# Подключаемся к MySQL
connection = pymysql.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    db=os.getenv('MYSQL_DB'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Токен нашего бота
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(message, 'Привет! Чтобы зарегистрироваться, отправьте команду /register.')


@bot.message_handler(commands=['register'])
def register_user(message: Message):
    chat_id = message.chat.id

    with connection.cursor() as cursor:
        sql = "SELECT * FROM users WHERE telegram_id=%s"
        cursor.execute(sql, (chat_id,))
        result = cursor.fetchone()

        if result is not None:
            bot.send_message(chat_id, 'Вы уже зарегистрированы!')
        else:
            try:
                name = message.from_user.first_name
                username = message.from_user.username or ''

                insert_sql = """
                    INSERT INTO users (telegram_id, first_name, username)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (chat_id, name, username))
                connection.commit()

                bot.send_message(chat_id, f'Регистрация успешно завершена!\\nВаш ID: {chat_id}')
            except Exception as e:
                print(f'Ошибка при сохранении данных: {e}')
                bot.send_message(chat_id, 'Что-то пошло не так. Попробуйте позже.')

if __name__ == '__main__':
    bot.polling(none_stop=True)
