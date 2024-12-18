import telebot
from telebot import types
import threading
import time
import json
import os
import requests

API_TOKEN = ''
CHANNEL_USERNAME = '@kzn_code'  # Замените на имя вашего канала

bot = telebot.TeleBot(API_TOKEN)

# Увеличиваем время ожидания для запросов к API Telegram
telebot.apihelper.CONNECT_TIMEOUT = 30
telebot.apihelper.READ_TIMEOUT = 60

# Путь к файлу для хранения данных пользователей
USERS_FILE = 'users.json'

# Загрузка данных пользователей из файла
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r') as file:
        users_dataset = json.load(file)
else:
    users_dataset = {}

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

@bot.message_handler(commands=['tellall'])
def handle_command(message):
    text = message.text
    parts = text.split(' ', 1)
    command, params = parts
    for key in users_dataset.keys():
        bot.send_message(key, params)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        user_id = message.contact.user_id
        phone_number = message.contact.phone_number
        user_link = message.from_user.username
        chat_id = message.chat.id

        # Сохраняем данные пользователя в файл
        users_dataset[chat_id] = {
            'phone_number': phone_number,
            'user_link': user_link,
            'user_id': user_id,
            'chat_id': chat_id,
            'timetoget': 0,
            'secondl': 0,
        }
        with open(USERS_FILE, 'w') as file:
            json.dump(users_dataset, file, indent=4)

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
        if is_subscribed(call.message.chat.id):
            bot.send_message(call.message.chat.id, """\
                    Это не просто мини-курс с информацией, сюда мы с командой вложили мои знания и опыт с 2009, который точно не рассказывают в рилсах 💡

Поэтому мы проработаем ваше мышление, снимем ваши «розовые очки» насчет ЛД

А в конце вас ждет СЕКРЕТНЫЙ БОНУСНЫЙ УРОК 🤫 который вы не получите даже на платных курсах
                    """)
            try:
                video_id = 'BAACAgIAAxkBAAMNZ11j0nf9MmL1snDN-AagJE0tfKYAAlhcAAIriOlK88QSgNY4PdY2BA'
#                 bot.send_video(call.message.chat.id, video_id, caption="""\
#                 Мы с вами разберем что такое личный бренд, зачем он нужен, а также онлайн и офлайн инструменты для продвижения
#
# (Обещанная ссылка на мой курс «Дизайн человека для себя» ⬇️)
# http://kokobonga.ru/course
#
# Следующее видео ты получишь через 24 часа""")
                bot.send_message(call.message.chat.id, "Урок 1")
                users_dataset[f'{call.message.chat.id}']["secondl"] = 1
                print(call.message.from_user.id)
                print(call.message.from_user.is_bot)
                users_dataset[f'{call.message.chat.id}']["timetoget"]=24*60*60
                print(f"{users_dataset[f'{call.message.chat.id}']['timetoget']}")
                print("Changed!")
            except requests.exceptions.ReadTimeout:
                bot.send_message(call.message.chat.id,
                                 "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

            with open(USERS_FILE, 'w') as file:
                json.dump(users_dataset, file, indent=4)

            send_check_time_keyboard(call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, "Вы не подписались на канал")
    elif call.data=='get_gift':
        bot.send_message(call.message.chat.id,"Ожидай, скоро с тобой свяжемся!")
        bot.send_message(call.message.chat.id, f"{users_dataset[str(call.message.chat.id)]['user_link']} ({users_dataset[str(call.message.chat.id)]['phone_number']}) нажал на кнопку Получить подарок")

def send_second_video(user_id, chat_id):
    video_id = 'BAACAgIAAxkBAAMUZ11kW64bSDlxkQE-SvGChmMjT-4AAkVZAAIriOlKnfldt_39u0w2BA'  # Замените на путь к вашему локальному видеофайлу для следующего урока
    try:
#         bot.send_video(user_id, video_id, caption="""\
#         24 часа прошло, держи следующий урок
#
# Разбираем какие трудности могут возникнуть, психологические барьеры и как преодолеть все страхи
#
# Последний урок ты получишь так же через 24 часа""")
        bot.send_message(user_id, "Урок 2")
        users_dataset[f'{chat_id}']["timetoget"] = 24*60*60
        print(f"{users_dataset[f'{chat_id}']['timetoget']}")
        print("Changed!")
        with open(USERS_FILE, 'w') as file:
            json.dump(users_dataset, file, indent=4)
    except requests.exceptions.ReadTimeout:
        bot.send_message(user_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

def send_third_video(user_id, chat_id):
    video_id = 'BAACAgIAAxkBAAMWZ11kc9UlRabdoQeZxrHxJSIbX04AAsFZAAIriOlKdZ7YVSn1NTs2BA'  # Замените на путь к вашему локальному видеофайлу для следующего урока
    bonus_video_id = 'BAACAgIAAxkBAAMYZ11kib8_TyrWZPzmlXGk72hvLjgAAiRZAAIriOlKYTX4pkbCFG02BA'
    try:
#         bot.send_video(user_id, video_id, caption="""\
#         24 часа прошло, держи последний урок
#
# Снимаем ваши розовые очки: обсуждаем управление личным брендом, ответственность и цели
# """)
        bot.send_message(user_id, "Урок 3")
    except requests.exceptions.ReadTimeout:
        bot.send_message(user_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

    try:
        # bot.send_video(user_id, bonus_video_id, caption="""\
        # Бонусный урок, как и обещала
        #
        # Как я развивала личный бренд, как он поменял жизнь моей клиентки
        # """)
        bot.send_message(user_id, "Урок 4")
        markup = types.InlineKeyboardMarkup()
        button2 = types.InlineKeyboardButton("Получить подарок", callback_data='get_gift')
        markup.add(button2)
        bot.send_message(user_id, """\
                Подарок 🎁 СТРАТЕГИЧЕСКАЯ СЕССИЯ со мной и моей командой 
Доступна 24 часа с получения подарка!
                """, reply_markup=markup)
        users_dataset[f'{chat_id}']["secondl"] = 0
        with open(USERS_FILE, 'w') as file:
            json.dump(users_dataset, file, indent=4)
    except requests.exceptions.ReadTimeout:
        bot.send_message(user_id, "Произошла ошибка при отправке видео. Пожалуйста, попробуйте позже.")

def send_check_time_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Когда я получу следующий урок")
    markup.add(button)
    bot.send_message(chat_id, "(Ты всегда можешь проверить когда ты получишь следующий урок нажав по кнопочке снизу)",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "Когда я получу следующий урок":
        for item in users_dataset.keys():
            if int(message.chat.id) == int(item):
                hours = int(users_dataset[f"{message.chat.id}"]["timetoget"])//3600
                minutes = (int(users_dataset[f"{message.chat.id}"]["timetoget"])%3600) //60
                seconds =int(users_dataset[f"{message.chat.id}"]["timetoget"])%60
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

def send_messages_to_all_users():
    while True:
        for key in users_dataset.keys():
            if users_dataset[f'{key}']["timetoget"]==0:
                if users_dataset[f'{key}']["secondl"]==0:
                    print(None)
                elif users_dataset[f'{key}']["secondl"]==1:
                    send_second_video(users_dataset[f'{key}']["user_id"], users_dataset[f'{key}']["chat_id"])
                    users_dataset[f'{key}']["secondl"]=2
                    print(f"Second lesson send to {users_dataset[f'{key}']['user_link']}")
                elif users_dataset[f'{key}']["secondl"]==2:
                    send_third_video(users_dataset[f'{key}']["user_id"], users_dataset[f'{key}']["chat_id"])
                    print(f"Third lesson send to {users_dataset[f'{key}']['user_link']}")
        with open(USERS_FILE, 'w') as file:
            json.dump(users_dataset, file, indent=4)
        time.sleep(10)

def minus_time():
    while True:
        for key in users_dataset.keys():
            if users_dataset[f'{key}']["timetoget"]!=0:
                users_dataset[f'{key}']["timetoget"]-=10
            print(f"{users_dataset[f'{key}']['timetoget']}")
            print("Changed!")
        with open(USERS_FILE, 'w') as file:
            json.dump(users_dataset, file, indent=4)
            print("Saved")
        time.sleep(10)

threading.Thread(target=send_messages_to_all_users).start()
threading.Thread(target=minus_time).start()

# Запуск бота
bot.infinity_polling()
