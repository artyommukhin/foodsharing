# -*- coding: utf-8 -*-
import telebot
import requests
import time
import shelve
import json
import random
from datetime import datetime


class User:
    def __init__(self, chat_id, id, offers = []):
        self.chat_id = chat_id
        self.offers = offers
        self.id = id

    def __str__(self):
        return f'chat id:{self.chat_id}\nuser id:{self.id}\n{json.dumps(self.offers)}' 

class Offer:
    def __init__(self, id: int, name: str, descr, date, coords: list):
        self.id = id
        self.name = name
        self.date = date
        self.coords = coords
    
    def __str__(self):
        return {
        'id': self.id,
        'name': 'Мясо',
        'desc': 'свежее',
        'time_to_pickup': str(datetime.now()),
        'marker': [1, 100], # lat, lon
        'address': 'Пушкина-колотушкина'
    }

rules = '''\
Фудшеринг - это хорошо
Правила:
1. Если вы хотите поделиться продуктами, нажмите "Поделиться" 
2. Если вы хотите забрать продукты, нажмите "Забрать"
3. Если вы хотите просмотреть список своих предложений, нажмите "Мои предложения"
'''

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
    bot.send_message(message.chat.id, str(message))

# Обработчик стартовой команды
@bot.message_handler(commands=['start'])
def start_message(message):
    
    cid = message.chat.id
    uid = message.from_user.id

    # Настройки клавиатуры
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Правила', 'Мои предложения','Поделиться', 'Забрать')
    keyboard_main.resize_keyboard = True

    with shelve.open('storage', flag='c') as db:
        db[str(uid)] = User(cid, uid)

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыбери действие', reply_markup=keyboard_main)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, rules)

# @bot.message_handler(commands=['settings'])
# def settings_message(message):
#     bot.send_message(message.chat.id, 'not implemented')

# Обработчик всех сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    cid = message.chat.id
    uid = message.from_user.id
    if message.text == 'Поделиться':
        bot.send_message(cid, 'Введите продукты')      
        bot.register_next_step_handler_by_chat_id(cid, donor_input_products)  
    elif message.text == 'Забрать':
        markup_inline = telebot.types.InlineKeyboardMarkup()
        markup_inline.add(
            telebot.types.InlineKeyboardButton('Карта доноров' ,  url = 'http://192.168.0.4/foodsharing') 
                # url='https://2gis.ru/krasnoyarsk/firm/986145966616730?m=92.797081%2C55.994433%2F16')
        )     
        bot.send_message(cid, 'Карта:', reply_markup=markup_inline)
    elif message.text == 'Правила':
        bot.send_message(message.chat.id, rules)
    elif message.text == 'Мои предложения':
       
        answer_str = 'Ваши предложения:\n'
        with shelve.open('storage', flag = 'c') as db:
            try:
                if not db[str(uid)].offers:
                    raise KeyError

                for offer in db[str(uid)].offers:
                    answer_str += f"ID: {offer['id']}\nName: {offer['name']}\nDate: {offer['time_to_pickup']}\n\n"
            except KeyError:
                answer_str = 'У вас нет предложений'
                
        bot.send_message(cid, answer_str)

        # button_rules = telebot.types.InlineKeyboardButton('Правила', callback_data='test')
        
        # markup_inline.add(button_rules)     
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю :(')


def donor_input_products(message):
    cid = message.chat.id
    uid = message.from_user.id

    db = shelve.open('storage', flag='c', writeback=True)
    user = db[str(uid)]
    db.close()

    offer = {
        'id': random.getrandbits(16),
        'name': message.text,
        'desc': None, #'свежее',
        'time_to_pickup': None, #str(datetime.now()),
        'marker': None, #[1, 100], # lat, lon
        'address': None #'Пушкина-колотушкина'
    }

    with shelve.open('storage', flag='c') as db:
        offers = db[str(uid)].offers
        offers.append(offer)
    
    
    bot.send_message(message.chat.id, f'Принято! Ваше предложение сохранено под номером {offer.get("id")}\nЕго можно дополнить данными')
    # markup_inline = telebot.types.InlineKeyboardMarkup()

    # markup_inline.add(
    #     telebot.types.InlineKeyboardButton('Добавить фото') #, callback_data=)
    # )


    #, reply_markup=markup_inline)
    # except Exception:
    #     print('problem')
    #     bot.send_message(cid, 'Проюлема')

    # bot.register_next_step_handler_by_chat_id(message.chat.id, donor_input_photos)

# def donor_input_photos(message):
#     pass
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
'''    
# bot.polling()

bot.infinity_polling()

'''
while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print('some problems')
        time.sleep(5)
#bot.infinity_polling()
'''