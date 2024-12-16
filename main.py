import telebot
from telebot import types
import threading
import time
from datetime import datetime, timedelta
import json
import os
import requests

API_TOKEN = ''
CHANNEL_USERNAME = '@kokobongaclub'  # Замените на имя вашего канала

bot = telebot.TeleBot(API_TOKEN)

# Увеличиваем время ожидания для запросов к API Telegram
telebot.apihelper.CONNECT_TIMEOUT = 30
telebot.apihelper.READ_TIMEOUT = 60

# Словарь для хранения времени отправки видео для каждого пользователя
user_video_times = {}

# Путь к файлу для хранения данных пользователей
USERS_FILE = 'users.json'

# Загрузка данных пользователей из файла
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r') as file:
        users_data = json.load(file)
else:
    users_data = {}


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Отправить контакт", request_contact=True)
    markup.add(button)

    bot.send_message(message.chat.id, """\
    Приветствую Вас на нашем мини-курсе «Личный Бренд с 0»! 🎙️

Здесь вы узнаете все о Личном Бренде: что это такое, для чего, кому он не нужен, разберетесь в атрибутах бренда и развеете все мифы «дорого», «долго» и многое другое.

Для доступа к мини-курсу нужно предоставить свои контакты.
    """, reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        user_id = message.contact.user_id
        phone_number = message.contact.phone_number
        user_link = message.from_user.username

        # Сохраняем данные пользователя в файл
        users_data[user_id] = {
            'phone_number': phone_number,
            'user_link': user_link,
        }
        with open(USERS_FILE, 'w') as file:
            json.dump(users_data, file, indent=4)

        # Отправляем сообщение с кнопкой "Начать"
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Далее", callback_data='startcourse')
        markup.add(button1)

        bot.send_message(message.chat.id, """\
        Регистрация прошла успешно!

Чтобы оставаться в курсе всех новостей в маркетинге, контенте и пиаре 👉 подписывайся на мой канал ⬇️
@kokobongaclub
        """, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'startcourse':
        if is_subscribed(call.message.chat.id):  # Замените на путь к вашему локальному видеофайлу
            bot.send_message(call.message.chat.id, """\
                    Это не просто мини-курс с информацией, сюда мы с командой вложили мои знания и опыт с 2009, который точно не рассказывают в рилсах 💡

Поэтому мы проработаем ваше мышление, снимем ваши «розовые очки» насчет ЛД

А в конце вас ждет СЕКРЕТНЫЙ БОНУСНЫЙ УРОК 🤫 который вы не получите даже на платных курсах 
                    """)
            try:
                video_id = 'BAACAgIAAxkBAAMNZ11j0nf9MmL1snDN-AagJE0tfKYAAlhcAAIriOlK88QSgNY4PdY2BA'
                bot.send_video(call.message.chat.id, video_id, caption="""\
                Мы с вами разберем что такое личный бренд, зачем он нужен, а также онлайн и офлайн инструменты для продвижения

(Обещанная ссылка на мой курс «Дизайн человека для себя» ⬇️)
http://kokobonga.ru/course

Следующее видео ты получишь через 24 часа""")
            except requests.exceptions.ReadTimeout:
                bot.send_message(call.message.chat.id,
                                 "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

            # Сохраняем время отправки видео для пользователя
            user_video_times[call.message.chat.id] = datetime.now()

            # Планируем отправку следующего видео через 24 часа
            threading.Thread(target=schedule_next_videos, args=(call.message.chat.id,)).start()

            # Отправляем клавиатуру с кнопкой "Когда я получу следующий урок"
            send_check_time_keyboard(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, "Вы не подписались на канал")

    elif call.data == 'check_time':
        if call.message.chat.id in user_video_times:
            next_video_time = user_video_times[call.message.chat.id] + timedelta(hours=24)
            time_left = next_video_time - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            bot.send_message(call.message.chat.id,
                             f"Следующий урок будет доступен через {hours} часов, {minutes} минут и {seconds} секунд.")
        else:
            bot.send_message(call.message.chat.id, "Вы еще не начали курс.")


def schedule_next_videos(chat_id):
    time.sleep(24 * 60 * 60)  # Ждем 24 часа
    send_second_video(chat_id)
    time.sleep(24 * 60 * 60)
    send_third_video(chat_id)


def send_second_video(chat_id):
    video_id = 'BAACAgIAAxkBAAMUZ11kW64bSDlxkQE-SvGChmMjT-4AAkVZAAIriOlKnfldt_39u0w2BA'  # Замените на путь к вашему локальному видеофайлу для следующего урока
    try:
        bot.send_video(chat_id, video_id, caption="""\
        24 часа прошло, держи следующий урок

Разбираем какие трудности могут возникнуть, психологические барьеры и как преодолеть все страхи

Последний урок ты получишь так же через 24 часа""")
    except requests.exceptions.ReadTimeout:
        bot.send_message(chat_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

    # Обновляем время отправки видео для пользователя
    user_video_times[chat_id] = datetime.now()


def send_third_video(chat_id):
    video_id = 'BAACAgIAAxkBAAMWZ11kc9UlRabdoQeZxrHxJSIbX04AAsFZAAIriOlKdZ7YVSn1NTs2BA'  # Замените на путь к вашему локальному видеофайлу для следующего урока
    bonus_video_id = 'BAACAgIAAxkBAAMYZ11kib8_TyrWZPzmlXGk72hvLjgAAiRZAAIriOlKYTX4pkbCFG02BA'
    try:
        bot.send_video(chat_id, video_id, caption="""\
        24 часа прошло, держи последний урок

Снимаем ваши розовые очки: обсуждаем управление личным брендом, ответственность и цели
""")
    except requests.exceptions.ReadTimeout:
        bot.send_message(chat_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

    try:
        bot.send_video(chat_id, bonus_video_id, caption="""\
        Бонусный урок, как и обещала

        Как я развивала личный бренд, как он поменял жизнь моей клиентки
        """)
    except requests.exceptions.ReadTimeout:
        bot.send_message(chat_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

    # Обновляем время отправки видео для пользователя
    user_video_times[chat_id] = datetime.now()


def send_check_time_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Когда я получу следующий урок")
    markup.add(button)
    bot.send_message(chat_id, "(Ты всегда можешь проверить когда ты получишь следующий урок нажав по кнопочке снизу)",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "Когда я получу следующий урок":
        if message.chat.id in user_video_times:
            next_video_time = user_video_times[message.chat.id] + timedelta(hours=24)
            time_left = next_video_time - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            bot.send_message(message.chat.id,
                             f"Следующий урок будет доступен через {hours} часов, {minutes} минут и {seconds} секунд.")
        else:
            bot.send_message(message.chat.id, "Вы еще не начали курс.")
    elif message.text == "Админ панель":
        with open(USERS_FILE, 'r') as file:
            users_data = json.load(file)
        users_info = "Данные всех пользователей:\n"
        for user_id, data in users_data.items():
            users_info += f"Телефон: {data['phone_number']}\n"
            users_info += f"Ссылка: @{data['user_link']}\n\n"
        bot.send_message(message.chat.id, users_info)


def is_subscribed(chat_id):
    try:
        user_status = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
        return user_status.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        if e.result_json['description'] == 'Bad Request: user not found':
            return False
        else:
            raise e


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice', 'video_note', 'sticker'])
def handle_files(message):
    file_id = None

    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id  # Берем последний элемент, так как фото может быть в разных разрешениях
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.video_note:
        file_id = message.video_note.file_id
    elif message.sticker:
        file_id = message.sticker.file_id

    if file_id:
        # Сохраните file_id, например, в базу данных или в файл
        bot.reply_to(message, f"file_id вашего файла: {file_id}")


# Запуск бота
bot.infinity_polling()