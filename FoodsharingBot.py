# -*- coding: utf-8 -*-
import telebot
import requests
import time
from datetime import datetime

# Получение токена бота из файла
f = open('token.txt','r')
TOKEN = f.read()
f.close()

# Инициализация объекта бота
bot = telebot.TeleBot(TOKEN)

# Обработчик тестовой команды
@bot.message_handler(commands=['test'])
def test_message(message):
    bot.send_location(message.chat.id, 56.018012, 92.868991)

# Обработчик стартовой команды
@bot.message_handler(commands=['start'])
def start_message(message):
    
    # Настройки клавиатуры
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Правила', 'Главное меню','Поделиться', 'Забрать')
    keyboard_main.resize_keyboard = True
    
    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыбери действие', reply_markup=keyboard_main)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'not implemented')

@bot.message_handler(commands=['settings'])
def settings_message(message):
    bot.send_message(message.chat.id, 'not implemented')

# Обработчик всех сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    if message.text == 'Поделиться':
        bot.send_message(chat_id, 'Введите продукты')
    elif message.text == 'Забрать':
        pass
    elif message.text == 'Правила':
        pass
    elif message.text == 'Главное меню':
        markup_inline = telebot.types.InlineKeyboardMarkup()
    
        button_map = telebot.types.InlineKeyboardButton('Карта доноров', url='https://2gis.ru/krasnoyarsk/firm/986145966616730?m=92.797081%2C55.994433%2F16')
        # button_rules = telebot.types.InlineKeyboardButton('Правила', callback_data='test')
        
        # markup_inline.add(button_rules)
        markup_inline.add(button_map)

        bot.send_message(message.chat.id, 'Главное меню', reply_markup=markup_inline)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю :(')

'''
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    sender = message.from_user
    print(f'voice message from {sender.first_name}({sender.username})')
    file_info = bot.get_file(message.voice.file_id)

    voice_file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
    
    with open(f'saved_voices/voice{datetime.now().strftime("%d.%m.%Y-%H.%M.%S")}{sender.username}.ogg','wb') as file:
        file.write(voice_file.content)    

    bot.send_voice(message.chat.id, voice_file.content)
    bot.send_message(message.chat.id, message)
    
bot.polling()
'''

'''
while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print('some problems')
        time.sleep(5)
#bot.infinity_polling()
'''