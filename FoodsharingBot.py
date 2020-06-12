# -*- coding: utf-8 -*-

from config import token, shelve_name 
import storage_worker
import db_worker
from classes import User, Offer

import telebot
import requests
import time
import shelve
import json
import random
from datetime import datetime


rules = '''\
Фудшеринг - это хорошо
Правила:
1. Если вы хотите поделиться продуктами, нажмите "Поделиться" 
2. Если вы хотите забрать продукты, нажмите "Забрать"
3. Если вы хотите просмотреть список своих предложений, нажмите "Мои предложения"
'''

# Инициализация объекта бота
bot = telebot.TeleBot(token)

# Обработчик тестовой команды
@bot.message_handler(commands=['test'])
def test_message(message):
    # bot.send_location(message.chat.id, 56.018012, 92.868991)
    bot.send_message(message.chat.id, str(message))
    # uid = message.from_user.id
    # with shelve.open(shelve_name, flag='c') as db:
    #     print(db[str(uid)])
    

# Обработчик стартовой команды
@bot.message_handler(commands=['start'])
def start_message(message):
    
    cid = message.chat.id
    uid = message.from_user.id

    # Сохранение пользователя в хранилище
    storage_worker.save_user(uid)

    # Настройки клавиатуры
    keyboard_main = telebot.types.ReplyKeyboardMarkup()
    keyboard_main.row('Правила', 'Мои предложения','Поделиться', 'Забрать')
    keyboard_main.resize_keyboard = True

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в мир рационального использования ресурсов\nВыбери действие', reply_markup=keyboard_main)


# Обработчик вызова помощи
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, rules)


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
            telebot.types.InlineKeyboardButton('Карта доноров (1)' ,  url = 'http://192.168.0.4/fsmap'), 
                # url='https://2gis.ru/krasnoyarsk/firm/986145966616730?m=92.797081%2C55.994433%2F16')
            telebot.types.InlineKeyboardButton('Карта доноров (2)' ,  url = 'http://192.168.0.3/fsmap') 
        )     
        bot.send_message(cid, 'Карта:', reply_markup=markup_inline)

    elif message.text == 'Правила':
        bot.send_message(message.chat.id, rules)

    elif message.text == 'Мои предложения':
        answer_str = 'Ваши предложения:\n'
        
        with shelve.open(shelve_name, flag = 'c') as db:
            if str(uid) in db:
                for offer in db[str(uid)].offers:
                    answer_str += f"ID: {offer['id']}\nName: {offer['name']}\nDate: {offer['time_to_pickup']}\n\n"
            else:
                answer_str = 'У вас нет предложений' 


            # try:
            #     if not db[str(uid)].offers:
            #         raise KeyError
            #     for offer in db[str(uid)].offers:
            #         answer_str += f"ID: {offer['id']}\nName: {offer['name']}\nDate: {offer['time_to_pickup']}\n\n"
            # except KeyError:
            #     answer_str = 'У вас нет предложений'
                
        bot.send_message(cid, answer_str)

        # button_rules = telebot.types.InlineKeyboardButton('Правила', callback_data='test')
        
        # markup_inline.add(button_rules)     
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю :(')


# Ввод продуктов
# лажа тут
def donor_input_products(message):
    cid = message.chat.id
    uid = message.from_user.id

    # with shelve.open(shelve_name, flag='c') as db:
    #     user_db = db[str(uid)]
    #     for offer in user_db.offers:
    #         if offer.status = "new":



    # db = shelve.open(shelve_name, flag='c', writeback=True)
    # user = db[str(uid)]
    # db.close()

    # offer = {
    #     'id': random.getrandbits(16),
    #     'name': message.text,
    #     'desc': None, #'свежее',
    #     'time_to_pickup': None, #str(datetime.now()),
    #     'marker': None, #[1, 100], # lat, lon
    #     'address': None #'Пушкина-колотушкина'
    # }

    offer = Offer( 
        message.text,
        None,
        None,
        None,        
    )

    with shelve.open(shelve_name, flag='c', writeback=True) as db:
        # Так не должно быть
        if str(uid) in db:
            db[str(uid)].offers.append(offer)
        else:
        # Пользователь должен сохраняться на старте, это костыль для теста
            db[str(uid)] = User(cid, uid)
        
    bot.send_message(message.chat.id, f'Принято! Ваше предложение сохранено под номером {offer.id}\n\
        Его можно дополнить данными', )
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

if __name__ == '__main__':
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
