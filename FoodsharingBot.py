import telebot
import requests
import time
from datetime import datetime

f = open('token.txt','r')
TOKEN = f.read()
f.close()

bot = telebot.TeleBot(TOKEN)

keyboard_main = telebot.types.ReplyKeyboardMarkup()
keyboard_main.row('Поделиться', 'Забрать')

keyboard_main.resize_keyboard = True

#telebot.types.

touch_count = 0

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыбери действие',  reply_markup=keyboard_main)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'not implemented')

@bot.message_handler(commands=['settings'])
def settings_message(message):
    bot.send_message(message.chat.id, 'not implemented')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    if message.text == 'тык':
        global touch_count
        touch_count = touch_count + 1
        bot.send_message(message.chat.id, 'тык'*touch_count)
    elif message.text == 'Поделиться':
        bot.send_message(chat_id, 'Введите продукты')
    elif message.text == 'Забрать':
        pass
    else:
        bot.send_message(message.chat.id, message.text)

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

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print('some problems')
        time.sleep(5)
#bot.infinity_polling()