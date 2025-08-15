import threading
import time
from datetime import date, timedelta

from telebot.types import InlineKeyboardButton as InButton
from telebot.types import InlineKeyboardMarkup as InKeyboard
from telebot.types import KeyboardButton as Button
from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup as Keyboard

from constants import ADMIN_ID
from logger import logger
from core import check_activity, bot_unit, main_menu, last_active_time
from database.queries import fetch_users, insert_user, Order

bot = bot_unit
order = None

threading.Thread(target=check_activity, daemon=True).start()


@bot.message_handler(commands=['start'])
def start(message: Message):
    chat_id = message.chat.id
    global last_active_time
    last_active_time[chat_id] = time.time()
    keyboard = Keyboard(one_time_keyboard=True, resize_keyboard=True)

    # try:
    #     sql = "SELECT * FROM Tg_users WHERE telegram_id=%s"
    #     cursor.execute(sql, (chat_id,))
    #     result = cursor.fetchall()
    # except Exception as e:
    #     logger.error(f'Ошибка при поиске пользователя в БД: {e}')
    result = fetch_users(message)
    if result is None:
        button1 = Button('\U0001F386 Регистрация')
        keyboard.add(button1)
        bot.send_message(
            chat_id=chat_id,
            text=(
                'Привет! Я бот для заказа сапбордов в аренду. '
                'Для начала нужно пройти регистрацию:'
            ), reply_markup=keyboard
        )
    else:
        button2 = Button('\U0001F6F6 Заказать сапборд')
        button3 = Button('\U0001F92C Свяжитесь со мной')
        keyboard.add(button2, button3)
        if result.get('first_name', None):
            name = result.get('first_name', None)
        else:
            name = result.get('username', None)
        bot.reply_to(
            message, (
                f'С возвращением {name}! '
                'Выберите интересующий пункт меню:'
            ), reply_markup=keyboard
        )


@bot.message_handler(
        func=lambda message: message.text == '\U0001F386 Регистрация')
def register_user(message: Message):
    chat_id = message.chat.id
    global last_active_time
    last_active_time[chat_id] = time.time()
    try:
        keyboard = Keyboard(
            one_time_keyboard=True, resize_keyboard=True
        )
        contact_button = Button(
            text="Отправить мой контакт 📞", request_contact=True
        )
        keyboard.add(contact_button)
        bot.send_message(
            chat_id,
            'Подтвердите свой номер телефона',
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f'Ошибка при сохранении данных: {e}')
        bot.send_message(chat_id, 'Что-то пошло не так. Попробуйте позже.')


@bot.message_handler(content_types=["contact"])
def save_contact(message):
    global last_active_time
    last_active_time[message.chat.id] = time.time()

    try:
        insert_user(message)
    except Exception as e:
        logger.error(f'Ошибка при сохранении контакта в БД: {e}')
        return

    keyboard = Keyboard(one_time_keyboard=True, resize_keyboard=True)
    button2 = Button('\U0001F6F6 Заказать сапборд')
    button3 = Button('\U0001F92C Свяжитесь со мной')
    keyboard.add(button2, button3)
    bot.send_message(
        message.chat.id,
        "Сохранено! Спасибо!",
        reply_markup=keyboard
    )


@bot.message_handler(
    func=lambda message: message.text == '\U0001F92C Свяжитесь со мной'
)
def call_me(message: Message):
    global last_active_time
    last_active_time[message.chat.id] = time.time()
    logger.debug('Пользователь запросил обратную связь')
    bot.send_message(
        message.chat.id,
        'В ближайшее время с вами свяжется администратор.'
    )
    main_menu(message.chat.id)
    username = message.from_user.username
    bot.send_message(
        ADMIN_ID,
        f'Пользователь @{username} просит связаться с ним!'
    )
    result = fetch_users(message)
    if result is not None:
        bot.send_message(ADMIN_ID, f'Данные пользователя из БД {result}')


@bot.message_handler(
        func=lambda message: message.text == '\U0001F6F6 Заказать сапборд'
)
def order_sup(message: Message):
    global last_active_time
    last_active_time[message.chat.id] = time.time()
    result = fetch_users(message)
    if result is None:
        logger.error(
            f'Незарегистрированный пользователь {message.chat.id} '
            'пытается оформить заказ'
        )
        start(message)
        return
    global order
    order = Order(customer_id=result['id'])
    logger.debug(f'Пользователь {result} приступил к заказу.')
    keyboard = InKeyboard(row_width=2)
    buttons = []
    for i in range(1, 6):
        buttons.append(InButton(str(i), callback_data=f'qty_{i}'))
    keyboard.add(*buttons)
    bot.send_message(
        message.chat.id,
        'Выберите количество сапбордов:',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('qty_'))
def choose_qty(call):
    global last_active_time
    last_active_time[call.message.chat.id] = time.time()
    quantity = int(call.data.split('_')[1])
    global order
    order.order_quantity = quantity
    keyboard = InKeyboard(row_width=2)
    buttons = []
    for i in range(0, 6):
        day = date.today() + timedelta(days=i)
        buttons.append(
            InButton(str(day.strftime('%d.%m')),
                     callback_data=f'date_{day}'))
    keyboard.add(*buttons)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Количество выбрано: {quantity}\nТеперь выберите дату доставки:',
        reply_markup=keyboard
    )


@bot.callback_query_handler(
        func=lambda call: call.data.startswith('date_')
)
def choose_date(call):
    global last_active_time
    last_active_time[call.message.chat.id] = time.time()
    delivery_date = call.data.split('_')[1]
    global order
    order.order_date = delivery_date
    keyboard = InKeyboard(row_width=2)
    options = ['Спас.жилет', 'Электронасос', 'Без доп.оборудования']
    buttons = [InButton(
        opt, callback_data=f'opt_{opt.lower()}'
        ) for opt in options]
    keyboard.add(*buttons)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            f'Дата доставки: {delivery_date}\n'
            'Выберите дополнительное оборудование:'),
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('opt_')
)
def choose_option(call):
    global last_active_time
    last_active_time[call.message.chat.id] = time.time()
    option = call.data.split('_')[1].capitalize()
    global order
    order.order_options = option
    keyboard = InKeyboard()
    confirm_btn = InButton('Подтвердить заказ', callback_data='confirm')
    cancel_btn = InButton('Отмена', callback_data='cancel')
    keyboard.add(confirm_btn, cancel_btn)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(
            'Ваш заказ:\n'
            f'Кол-во сапбордов: {order.order_quantity}\n'
            f'Получение: {order.order_date}\n'
            f'Дополнительно: {order.order_options}\n'
            'Готовы подтвердить заказ?'
            ),
        reply_markup=keyboard
    )


@bot.callback_query_handler(
        func=lambda call: call.data == 'confirm')
def confirm_order(call):
    global last_active_time
    last_active_time[call.message.chat.id] = time.time()
    if order is not None and order.save_to_db():
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Ваш заказ успешно принят!'
        )
        bot.send_message(ADMIN_ID, f'Создан заказ {order}')
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text=(
                'При создании заказа произошла ошибка. '
                'Администратор свяжется с вами в ближайшее время.'
                )
        )
        bot.send_message(
            ADMIN_ID, f'Ошибка при заказе от @{call.message.chat.username}'
        )
    main_menu(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_order(call):
    global last_active_time
    last_active_time[call.message.chat.id] = time.time()
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Заказ отменен'
    )
    global order
    order = None

    main_menu(call.message.chat.id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
